from django.urls import path

from . import api, views

urlpatterns = [
    path("cards/", views.CardListView.as_view(), name="cards"),
    path("cards/create/", views.CardIssueView.as_view(), name="create_card"),
    path("cards/<int:pk>/", views.CardDetailView.as_view(), name="card"),
    path(
        "cards/<int:pk>/generate_pdf/",
        views.CardGeneratePDFView.as_view(),
        name="generate_card_pdf",
    ),
    path("cards/<int:pk>/deactivate/", views.CardDeactivateView.as_view(), name="deactivate_card"),
    path("cards/<int:pk>/print/", views.CardPrintView.as_view(), name="print_card"),
    path("cards/<int:pk>/delete/", views.CardDeleteView.as_view(), name="delete_card"),
    path("printers/", views.CardPrinterListView.as_view(), name="card_printers"),
    path("printers/create/", views.CardPrinterCreateView.as_view(), name="create_card_printer"),
    path("printers/<int:pk>/", views.CardPrinterDetailView.as_view(), name="card_printer"),
    path("printers/<int:pk>/edit/", views.CardPrinterEditView.as_view(), name="edit_card_printer"),
    path(
        "printers/<int:pk>/delete/",
        views.CardPrinterDeleteView.as_view(),
        name="delete_card_printer",
    ),
    path(
        "printers/<int:pk>/config/",
        views.CardPrinterConfigView.as_view(),
        name="card_printer_config",
    ),
    path("layouts/", views.CardLayoutListView.as_view(), name="card_layouts"),
    path("layouts/create/", views.CardLayoutCreateView.as_view(), name="create_card_layout"),
    path("layouts/<int:pk>/", views.CardLayoutDetailView.as_view(), name="card_layout"),
    path("layouts/<int:pk>/edit/", views.CardLayoutEditView.as_view(), name="edit_card_layout"),
    path(
        "layouts/<int:pk>/delete/",
        views.CardLayoutDeleteView.as_view(),
        name="delete_card_layout",
    ),
]

api_urlpatterns = [
    path("api/v1/printers/", api.CardPrinterDetails.as_view(), name="api_card_printer"),
    path(
        "api/v1/printers/<int:pk>/status/",
        api.CardPrinterUpdateStatus.as_view(),
        name="api_card_printer_status",
    ),
    path(
        "api/v1/printers/<int:pk>/jobs/next/",
        api.GetNextPrintJob.as_view(),
        name="api_get_next_print_job",
    ),
    path(
        "api/v1/jobs/<int:pk>/status/",
        api.CardPrintJobUpdateStatusView.as_view(),
        name="api_update_job_status",
    ),
    path(
        "api/v1/jobs/<int:pk>/chip_number/",
        api.CardPrintJobSetChipNumberView.as_view(),
        name="api_set_chip_number",
    ),
]
