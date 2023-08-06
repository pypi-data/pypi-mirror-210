from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.utils import timezone

from celery.result import allow_join_result
from celery.states import SUCCESS
from oauth2_provider.oauth2_backends import get_oauthlib_core
from oauthlib.common import Request as OauthlibRequest
from rest_framework import generics, serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from aleksis.apps.kort.models import Card, CardPrinter, CardPrintJob
from aleksis.core.util.auth_helpers import AppScopes

admin.autodiscover()


class OAuth2ClientAuthentication(BaseAuthentication):
    """OAuth 2 authentication backend using client credentials authentication."""

    www_authenticate_realm = "api"

    def authenticate(self, request):
        """Authenticate the request with client credentials."""
        oauthlib_core = get_oauthlib_core()
        uri, http_method, body, headers = oauthlib_core._extract_params(request)
        oauth_request = OauthlibRequest(uri, http_method, body, headers)

        # Verify general authentication of the client
        if not oauthlib_core.server.request_validator.authenticate_client(oauth_request):
            # Client credentials were invalid
            return None

        request.auth = oauth_request

        return (oauth_request.client.client_id, oauth_request)


class ClientProtectedResourcePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verify scopes of configured application
        # The OAuth request was enriched with a reference to the Application when using the
        #  validator above.
        if not request.auth.client.allowed_scopes:
            # If there are no allowed scopes, the client is not allowed to access this resource
            return None

        required_scopes = set(self.get_scopes(request, view, obj) or [])
        allowed_scopes = set(AppScopes().get_available_scopes(request.auth.client) or [])
        return required_scopes.issubset(allowed_scopes)

    def get_scopes(self, request, view, obj):
        return view.get_scopes()


class CorrectPrinterPermission(ClientProtectedResourcePermission):
    """Check whether the OAuth2 application belongs to the printer."""

    def get_scopes(self, request, view, obj):
        return [obj.scope]


class CorrectJobPrinterPermission(BasePermission):
    """Check whether the OAuth2 application belongs to the job's printer."""

    def get_scopes(self, request, view, obj):
        return [obj.printer.scope]


class CardPrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardPrinter
        fields = (
            "id",
            "name",
            "description",
            "location",
            "status",
            "status_label",
            "status_color",
            "status_icon",
            "status_text",
            "last_seen_at",
            "cups_printer",
            "generate_number_on_server",
            "card_detector",
        )


class CardPrinterStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardPrinter
        fields = ("status", "status_text")


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ("id", "chip_number", "valid_until", "deactivated", "person", "pdf_file")


class CardPrintJobSerializer(serializers.ModelSerializer):
    card = CardSerializer()

    class Meta:
        model = CardPrintJob
        fields = ("id", "printer", "card", "status", "status_text")


class CardPrintJobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardPrintJob
        fields = ("id", "status", "status_text")


class CardChipNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ("chip_number",)


class CardPrinterDetails(generics.RetrieveAPIView):
    """Show details about the card printer."""

    authentication_classes = [OAuth2ClientAuthentication]
    permission_classes = [CorrectPrinterPermission]
    serializer_class = CardPrinterSerializer
    queryset = CardPrinter.objects.all()

    def get_object(self):
        token = self.request.auth
        return token.client.card_printers.all().first()


class CardPrinterUpdateStatus(generics.UpdateAPIView):
    """Update the status of the card printer."""

    authentication_classes = [OAuth2ClientAuthentication]

    permission_classes = [CorrectPrinterPermission]
    serializer_class = CardPrinterStatusSerializer
    queryset = CardPrinter.objects.all()

    def update(self, request, *args, **kwargs):
        r = super().update(request, *args, **kwargs)
        instance = self.get_object()
        instance.last_seen_at = timezone.now()
        instance.save()
        return r


class GetNextPrintJob(APIView):
    """Get the next print job."""

    authentication_classes = [OAuth2ClientAuthentication]

    permission_classes = [CorrectPrinterPermission]
    serializer_class = CardPrinterSerializer
    queryset = CardPrinter.objects.all()

    def get_object(self, pk):
        return get_object_or_404(CardPrinter, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        printer = self.get_object(pk)
        job = printer.get_next_print_job()
        if not job:
            return Response({"status": "no_job"})
        serializer = CardPrintJobSerializer(job)
        return Response(serializer.data)


class CardPrintJobUpdateStatusView(generics.UpdateAPIView):
    """Update the status of the card printer."""

    authentication_classes = [OAuth2ClientAuthentication]

    permission_classes = [CorrectJobPrinterPermission]
    serializer_class = CardPrintJobStatusSerializer
    queryset = CardPrintJob.objects.all()


class CardPrintJobSetChipNumberView(generics.UpdateAPIView):
    """Update the status of the card printer."""

    authentication_classes = [OAuth2ClientAuthentication]

    permission_classes = [CorrectJobPrinterPermission]
    serializer_class = CardChipNumberSerializer
    queryset = CardPrintJob.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        card = instance.card

        if card.chip_number:
            raise ValidationError

        serializer = self.get_serializer(card, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        result = instance.card.generate_pdf()

        with allow_join_result():
            result.wait()
            card.refresh_from_db()

        if result.status == SUCCESS and card.pdf_file:
            serializer = CardPrintJobSerializer(instance)
            instance.refresh_from_db()

            return Response(serializer.data)
        else:
            card.chip_number = None
            card.save()
            raise APIException("Error while generating PDF file")
