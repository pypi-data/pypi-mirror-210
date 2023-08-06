from django.contrib import admin

from aleksis.apps.kort.models import Card, CardLayout, CardPrinter

admin.site.register(Card)
admin.site.register(CardPrinter)
admin.site.register(CardLayout)
