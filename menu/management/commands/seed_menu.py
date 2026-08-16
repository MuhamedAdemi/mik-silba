from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, MenuItem

# Item names come 1:1 from the Luceed POS screenshots (Napici+Sok, Pivo+Vino,
# Alkohol, Ostalo, Coctails, Premium Gin tabs) so the button layout matches
# what staff already know.
#
# Each entry is (name, price, confirmed):
#   - price=None            -> no matching price found anywhere, seeded at 0.00
#   - confirmed=True        -> the paper-menu item name (and size, where shown)
#                              matched the POS button directly, high confidence
#   - confirmed=False       -> price comes from the "Alkoholna Pića/Spirits"
#                              photo, which was blurry — the name match is
#                              solid but individual digits are less certain
#
# needs_price_review is set whenever price is None OR confirmed is False, so
# everything worth a human glance still shows up filtered in
# /admin/menu/menuitem/ ("Needs price review" = Yes), but now with a real
# number to check instead of a blank 0.00 wherever a name match was found.

CATALOG = [
    ("Napici+Sok", [
        ("Espresso Kava", None, False),
        ("Americano", "2.30", True),
        ("Macchiato", None, False),
        ("Veliki Macchiato", None, False),
        ("Cappuccino", "2.50", True),
        ("Kava Šlag", "2.20", True),
        ("Bijela Kava", "2.50", True),
        ("Kakao", "2.50", True),
        ("Nescafe", "3.00", True),
        ("Čaj", "2.00", True),
        ("Mlijeko 0,20", "2.00", True),
        ("Šlag Porcija", "0.50", True),
        ("Espresso B.Kofeina", "2.50", True),
        ("Macchiato B.Kofeina", "2.50", True),
        ("Bijela Kava B.Kofeina", "2.70", True),
        ("Ice Coffee Mlk", None, False),
        ("Med", "3.50", True),
        ("Nes Hladni", "1.50", True),
        ("Coca Cola 0,25", None, False),
        ("Fanta 0,25", None, False),
        ("Sprite 0,25", None, False),
        ("Shweppes 0,25", "3.50", True),
        ("Orangina 0,25", "3.50", True),
        ("Cockta 0,25", None, False),
        ("Voćni Sok 0,20", None, False),
        ("Maraska Sok 0,20", None, False),
        ("Ledeni Čaj 0,33", None, False),
        ("Limunada 0,20", None, False),
        ("Limunada 0,30", None, False),
        ("Limunada 0,50", None, False),
        ("Cedevita 0,20", "3.50", True),
        ("Jed.Naranč 0,20", None, False),
        ("Mineralna 1L", "5.50", True),
        ("Mineralna 0,25", None, False),
        ("Remerqueue 0,33", None, False),
        ("Limunska Trava 0,33", None, False),
        ("Red Bull 0,33", None, False),
        ("Prir. Voda 0,33", "2.50", True),
        ("Mineralna 0,10L", "0.70", True),
        ("Gazirani Sok 0,1", None, False),
    ]),
    ("Pivo+Vino", [
        ("Karlovačko 0,33", "3.00", True),
        ("Karlovačko 0,50", "3.70", True),
        ("Karlovačko Crno 0,50", "3.70", True),
        ("Radler 0,50", "3.70", True),
        ("Heineken 0,33", "4.00", True),
        ("Budweiser 0,5", None, False),
        ("Staropramen 0,5", "3.70", True),
        ("Paulaner 0,50", "4.50", True),
        ("Hidra", None, False),
        ("Somersby 0,33", "4.50", True),
        ("Corona 0,35", None, False),
        ("Ožujsko 0,5", "3.70", True),
        ("Pivo Točeno 0,30", "3.00", True),
        ("Pivo Točeno 0,50", None, False),
        ("Vino Bj.0,10", "1.80", True),
        ("Vino Bj.1L", "18.00", True),
        ("Vino Crno 0,10", "1.80", True),
        ("Vino Crno 1L", "18.00", True),
        ("Bevanda 0,20", None, False),
        ("Gemišt 0,20", "2.50", True),
        ("Gemišt 0,30", "3.50", True),
        ("Bambus 0,20", "2.00", True),
        ("Bambus 0,30", "3.00", True),
        ("Martini 0,10", None, False),
        ("Astoria Prossecco", None, False),
        ("Vrhunsko Vino", None, False),
        ("Teranino", None, False),
    ]),
    ("Alkohol", [
        # E gjithë kjo kategori vjen nga foto e paqartë "Alkoholna Pića/Spirits" —
        # emrat përputhen, por shifrat e çmimit duhen konfirmuar me menunë fizike.
        ("Vodka 0,03", "2.30", False),
        ("Gin 0,03", "2.30", False),
        ("Stock 0,03", "2.50", False),
        ("Pelinkovac 0,03", "2.20", False),
        ("Travarica 0,03", "2.20", False),
        ("Orahovac 0,03", "2.70", False),
        ("Araro 0,03", "2.30", False),
        ("Viljamovka 0,03", "2.70", False),
        ("Bacardi 0,03", "2.60", False),
        ("Tequila 0,03", None, False),
        ("Jegger 0,03", "2.30", False),
        ("Malibu 0,03", "2.50", False),
        ("Balantines 0,03", "2.60", False),
        ("Johnny Walker 0,03", "3.20", False),
        ("Jemeson 0,03", "3.40", False),
        ("Jack Daniels 0,03", "3.60", False),
        ("Martel 0,03", "4.30", False),
        ("Chivas 0,03", "4.00", False),
        ("Hennesy 0,03", "4.30", False),
        ("Carolans 0,03", "2.90", False),
        ("Doljev Alko.Piću", None, False),
        ("Doljev Red Bull", None, False),
        ("Gin Hendri", "4.30", False),
        ("Pelinkovac Antique", "2.30", False),
        ("Campari 0,03", "2.30", False),
        ("Domaća Rakija", None, False),
        ("Johnnie Walker Black", "4.00", False),
        ("Johnnie Walker Green", None, False),
        ("Vodka Smirnof", None, False),
        ("Štrukani Pelin", None, False),
    ]),
    ("Ostalo", [
        ("Sladoled Kuglica", None, False),
        ("Eiskaffe", None, False),
        ("Milk-Shake", None, False),
        ("Smoothie", None, False),
        ("Sendvič", "5.00", True),
        ("Croissant", "2.00", True),
        ("Snjeguljica", None, False),
        ("Kontiki", None, False),
        ("Macho", None, False),
        ("King", None, False),
        ("King Clasic", None, False),
        ("Kornet", None, False),
        ("Ledena Cedevita", None, False),
    ]),
    ("Coctails", [
        ("Hawaiian Blue", None, False),
        ("Hugo", "6.50", True),
        ("Aperol Spritz", "6.50", True),
        ("Blue Lagoon", None, False),
        ("Mohito", "6.50", True),
        ("Tequila Sunrise", None, False),
        ("Long Island", None, False),
        ("Sex On The Beach", None, False),
        ("Mai Tai", None, False),
        ("Cuba Libre", "6.50", True),
        ("Zombie", None, False),
        ("Black Cuba Libre", None, False),
        ("Bahama Mama", None, False),
        ("Caribbean Cruise", None, False),
        ("Piña Colada", None, False),
        ("Bezalkoholic Coctail", None, False),
        ("B52", None, False),
        ("Bloody Screaming Orgasm", None, False),
        ("Kamikaza", None, False),
        ("Woo-Woo", None, False),
        ("Blow Job", None, False),
    ]),
    ("Premium Gin", [
        ("Tanqueray London Dry", None, False),
        ("Tanqueray Rangpur", None, False),
        ("Tanqueray No.10", None, False),
        ("Tanquery Sevilla", None, False),
        ("Gordons Pink", None, False),
        ("Gordons London Dry", None, False),
    ]),
]


class Command(BaseCommand):
    help = (
        "Mbush/rifreskon kategoritë dhe artikujt fillestarë të menusë (nga fotot e "
        "POS-it Luceed). E sigurt të rindiget: rishkruan price/needs_price_review "
        "sipas CATALOG-ut çdo herë, PRA MOS e rindiz pasi stafi të ketë korrigjuar "
        "çmimet manualisht në /admin/ — do t'i mbishkruajë."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        created_categories = 0
        created_items = 0
        updated_items = 0
        flagged_items = 0

        for order, (category_name, items) in enumerate(CATALOG, start=1):
            category, was_created = Category.objects.get_or_create(
                name=category_name, defaults={"order": order}
            )
            if was_created:
                created_categories += 1

            for sort_order, (item_name, price, confirmed) in enumerate(items, start=1):
                needs_review = price is None or not confirmed
                if needs_review:
                    flagged_items += 1
                item, was_created = MenuItem.objects.update_or_create(
                    category=category,
                    name=item_name,
                    defaults={
                        "price": price or "0.00",
                        "sort_order": sort_order,
                        "needs_price_review": needs_review,
                    },
                )
                if was_created:
                    created_items += 1
                else:
                    updated_items += 1

        self.stdout.write(self.style.SUCCESS(
            f"U krijuan {created_categories} kategori të reja, {created_items} artikuj të rinj, "
            f"{updated_items} artikuj ekzistues u rifreskuan."
        ))
        if flagged_items:
            self.stdout.write(self.style.WARNING(
                f"{flagged_items} artikuj kanë çmim ende të pakonfirmuar (needs_price_review=True). "
                "Kontrolloi te /admin/menu/menuitem/ (filtro sipas 'Needs price review')."
            ))
