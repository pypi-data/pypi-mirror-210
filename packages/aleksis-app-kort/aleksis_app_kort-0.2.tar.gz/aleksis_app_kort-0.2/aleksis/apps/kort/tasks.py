from celery.result import allow_join_result
from celery.states import SUCCESS

from aleksis.apps.kort.models import Card
from aleksis.core.celery import app
from aleksis.core.util.pdf import generate_pdf_from_html


@app.task
def generate_card_pdf(card_pk: int):
    card = Card.objects.get(pk=card_pk)

    html = card.layout.render(card)
    file_object, result = generate_pdf_from_html(html)

    with allow_join_result():
        result.wait()
        file_object.refresh_from_db()
        if result.status == SUCCESS and file_object.file:
            card.pdf_file.save("card.pdf", file_object.file.file)
            card.save()
