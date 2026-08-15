from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, MenuItem

# Item names come 1:1 from the Luceed POS screenshots (Napici+Sok, Pivo+Vino,
# Alkohol, Ostalo, Coctails, Premium Gin tabs) so the button layout matches
# what staff already know.
#
# Prices are filled in ONLY where a price could be read with confidence from
# the printed paper menu photos AND the item name+size matched the POS button
# exactly. Everything else is seeded at 0.00 with needs_price_review=True —
# the Alkoholna Pića/Spirits photo in particular was too blurry to transcribe
# reliably, and the Topla Pića/Hot drinks photo's price column didn't line up
# unambiguously with its item list. Fix flagged items in /admin/menu/menuitem/
# (price is inline-editable in the list view).

CATALOG = [
    ("Napici+Sok", [
        ("Espresso Kava", None),
        ("Americano", None),
        ("Macchiato", None),
        ("Veliki Macchiato", None),
        ("Cappuccino", None),
        ("Kava Šlag", None),
        ("Bijela Kava", None),
        ("Kakao", None),
        ("Nescafe", None),
        ("Čaj", None),
        ("Mlijeko 0,20", None),
        ("Šlag Porcija", None),
        ("Espresso B.Kofeina", None),
        ("Macchiato B.Kofeina", None),
        ("Bijela Kava B.Kofeina", None),
        ("Ice Coffee Mlk", None),
        ("Med", None),
        ("Nes Hladni", None),
        ("Coca Cola 0,25", None),
        ("Fanta 0,25", None),
        ("Sprite 0,25", None),
        ("Shweppes 0,25", "3.50"),
        ("Orangina 0,25", "3.50"),
        ("Cockta 0,25", None),
        ("Voćni Sok 0,20", None),
        ("Maraska Sok 0,20", None),
        ("Ledeni Čaj 0,33", None),
        ("Limunada 0,20", None),
        ("Limunada 0,30", None),
        ("Limunada 0,50", None),
        ("Cedevita 0,20", "3.50"),
        ("Jed.Naranč 0,20", None),
        ("Mineralna 1L", "5.50"),
        ("Mineralna 0,25", None),
        ("Remerqueue 0,33", None),
        ("Limunska Trava 0,33", None),
        ("Red Bull 0,33", None),
        ("Prir. Voda 0,33", "2.50"),
        ("Mineralna 0,10L", "0.70"),
        ("Gazirani Sok 0,1", None),
    ]),
    ("Pivo+Vino", [
        ("Karlovačko 0,33", "3.00"),
        ("Karlovačko 0,50", "3.70"),
        ("Karlovačko Crno 0,50", "3.70"),
        ("Radler 0,50", "3.70"),
        ("Heineken 0,33", "4.00"),
        ("Budweiser 0,5", None),
        ("Staropramen 0,5", "3.70"),
        ("Paulaner 0,50", "4.50"),
        ("Hidra", None),
        ("Somersby 0,33", "4.50"),
        ("Corona 0,35", None),
        ("Ožujsko 0,5", "3.70"),
        ("Pivo Točeno 0,30", "3.00"),
        ("Pivo Točeno 0,50", None),
        ("Vino Bj.0,10", "1.80"),
        ("Vino Bj.1L", "18.00"),
        ("Vino Crno 0,10", "1.80"),
        ("Vino Crno 1L", "18.00"),
        ("Bevanda 0,20", None),
        ("Gemišt 0,20", "2.50"),
        ("Gemišt 0,30", "3.50"),
        ("Bambus 0,20", "2.00"),
        ("Bambus 0,30", "3.00"),
        ("Martini 0,10", None),
        ("Astoria Prossecco", None),
        ("Vrhunsko Vino", None),
        ("Teranino", None),
    ]),
    ("Alkohol", [
        ("Vodka 0,03", None),
        ("Gin 0,03", None),
        ("Stock 0,03", None),
        ("Pelinkovac 0,03", None),
        ("Travarica 0,03", None),
        ("Orahovac 0,03", None),
        ("Araro 0,03", None),
        ("Viljamovka 0,03", None),
        ("Bacardi 0,03", None),
        ("Tequila 0,03", None),
        ("Jegger 0,03", None),
        ("Malibu 0,03", None),
        ("Balantines 0,03", None),
        ("Johnny Walker 0,03", None),
        ("Jemeson 0,03", None),
        ("Jack Daniels 0,03", None),
        ("Martel 0,03", None),
        ("Chivas 0,03", None),
        ("Hennesy 0,03", None),
        ("Carolans 0,03", None),
        ("Doljev Alko.Piću", None),
        ("Doljev Red Bull", None),
        ("Gin Hendri", None),
        ("Pelinkovac Antique", None),
        ("Campari 0,03", None),
        ("Domaća Rakija", None),
        ("Johnnie Walker Black", None),
        ("Johnnie Walker Green", None),
        ("Vodka Smirnof", None),
        ("Štrukani Pelin", None),
    ]),
    ("Ostalo", [
        ("Sladoled Kuglica", None),
        ("Eiskaffe", None),
        ("Milk-Shake", None),
        ("Smoothie", None),
        ("Sendvič", "5.00"),
        ("Croissant", "2.00"),
        ("Snjeguljica", None),
        ("Kontiki", None),
        ("Macho", None),
        ("King", None),
        ("King Clasic", None),
        ("Kornet", None),
        ("Ledena Cedevita", None),
    ]),
    ("Coctails", [
        ("Hawaiian Blue", None),
        ("Hugo", "6.50"),
        ("Aperol Spritz", "6.50"),
        ("Blue Lagoon", None),
        ("Mohito", "6.50"),
        ("Tequila Sunrise", None),
        ("Long Island", None),
        ("Sex On The Beach", None),
        ("Mai Tai", None),
        ("Cuba Libre", "6.50"),
        ("Zombie", None),
        ("Black Cuba Libre", None),
        ("Bahama Mama", None),
        ("Caribbean Cruise", None),
        ("Piña Colada", None),
        ("Bezalkoholic Coctail", None),
        ("B52", None),
        ("Bloody Screaming Orgasm", None),
        ("Kamikaza", None),
        ("Woo-Woo", None),
        ("Blow Job", None),
    ]),
    ("Premium Gin", [
        ("Tanqueray London Dry", None),
        ("Tanqueray Rangpur", None),
        ("Tanqueray No.10", None),
        ("Tanquery Sevilla", None),
        ("Gordons Pink", None),
        ("Gordons London Dry", None),
    ]),
]


class Command(BaseCommand):
    help = "Mbush kategoritë dhe artikujt fillestarë të menusë (nga fotot e POS-it Luceed)."

    @transaction.atomic
    def handle(self, *args, **options):
        created_categories = 0
        created_items = 0
        flagged_items = 0

        for order, (category_name, items) in enumerate(CATALOG, start=1):
            category, was_created = Category.objects.get_or_create(
                name=category_name, defaults={"order": order}
            )
            if was_created:
                created_categories += 1

            for sort_order, (item_name, price) in enumerate(items, start=1):
                needs_review = price is None
                if needs_review:
                    flagged_items += 1
                item, was_created = MenuItem.objects.get_or_create(
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

        self.stdout.write(self.style.SUCCESS(
            f"U krijuan {created_categories} kategori të reja dhe {created_items} artikuj të rinj."
        ))
        if flagged_items:
            self.stdout.write(self.style.WARNING(
                f"{flagged_items} artikuj nuk kanë çmim të konfirmuar (needs_price_review=True). "
                "Plotësoi te /admin/menu/menuitem/ (filtro sipas 'Needs price review')."
            ))
