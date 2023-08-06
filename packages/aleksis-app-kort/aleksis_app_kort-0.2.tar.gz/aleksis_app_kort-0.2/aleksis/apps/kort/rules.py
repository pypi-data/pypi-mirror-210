from rules import add_perm

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import Card, CardLayout, CardPrinter

view_card_printers_predicate = has_person & (
    has_global_perm("kort.view_cardprinter") | has_any_object("kort.view_cardprinter", CardPrinter)
)
add_perm("kort.view_cardprinters_rule", view_card_printers_predicate)

view_card_printer_predicate = has_person & (
    has_global_perm("kort.view_cardprinter") | has_object_perm("kort.view_cardprinter")
)
add_perm("kort.view_cardprinter_rule", view_card_printer_predicate)

create_card_printer_predicate = view_card_printers_predicate & has_global_perm(
    "kort.add_cardprinter"
)
add_perm("kort.create_cardprinter_rule", create_card_printer_predicate)

edit_card_printer_predicate = view_card_printer_predicate & (
    has_global_perm("kort.change_cardprinter") | has_object_perm("kort.change_cardprinter")
)
add_perm("kort.edit_cardprinter_rule", edit_card_printer_predicate)

delete_card_printer_predicate = view_card_printer_predicate & (
    has_global_perm("kort.delete_cardprinter") | has_object_perm("kort.delete_cardprinter")
)
add_perm("kort.delete_cardprinter_rule", delete_card_printer_predicate)

view_card_layouts_predicate = has_person & (
    has_global_perm("kort.view_cardlayout") | has_any_object("kort.view_cardlayout", CardLayout)
)
add_perm("kort.view_cardlayouts_rule", view_card_layouts_predicate)

view_card_layout_predicate = has_person & (
    has_global_perm("kort.view_cardlayout") | has_object_perm("kort.view_cardlayout")
)
add_perm("kort.view_cardlayout_rule", view_card_layout_predicate)

create_card_layout_predicate = view_card_layouts_predicate & has_global_perm("kort.add_cardlayout")
add_perm("kort.create_cardlayout_rule", create_card_layout_predicate)

edit_card_layout_predicate = view_card_layout_predicate & (
    has_global_perm("kort.change_cardlayout") | has_object_perm("kort.change_cardlayout")
)
add_perm("kort.edit_cardlayout_rule", edit_card_layout_predicate)

delete_card_layout_predicate = view_card_layout_predicate & (
    has_global_perm("kort.delete_cardlayout") | has_object_perm("kort.delete_cardlayout")
)
add_perm("kort.delete_cardlayout_rule", delete_card_layout_predicate)

view_cards_predicate = has_person & (
    has_global_perm("kort.view_card") | has_any_object("kort.view_card", Card)
)
add_perm("kort.view_cards_rule", view_cards_predicate)

view_card_predicate = has_person & (
    has_global_perm("kort.view_card") | has_object_perm("kort.view_card")
)
add_perm("kort.view_card_rule", view_card_predicate)

create_card_predicate = view_cards_predicate & has_global_perm("kort.add_card")
add_perm("kort.create_card_rule", create_card_predicate)

edit_card_predicate = view_card_predicate & (
    has_global_perm("kort.change_card") | has_object_perm("kort.change_card")
)
add_perm("kort.edit_card_rule", edit_card_predicate)

delete_card_predicate = view_card_predicate & (
    has_global_perm("kort.delete_card") | has_object_perm("kort.delete_card")
)
add_perm("kort.delete_card_rule", delete_card_predicate)

print_card_predicate = edit_card_predicate
add_perm("kort.print_card_rule", print_card_predicate)

deactivate_card_predicate = edit_card_predicate
add_perm("kort.deactivate_card_rule", deactivate_card_predicate)

view_menu_predicate = (
    view_cards_predicate | view_card_printers_predicate | view_card_layouts_predicate
)
add_perm("kort.view_menu_rule", view_menu_predicate)
