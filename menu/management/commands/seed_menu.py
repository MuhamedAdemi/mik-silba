from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, MenuItem

# Item names come 1:1 from the Luceed POS screenshots (Napici+Sok, Pivo+Vino,
# Alkohol, Ostalo, Coctails, Premium Gin tabs) so the button layout matches
# what staff already know.
#
# Prices come directly from screenshots of the real POS register ringing up
# each item one by one (Iznos column) — the actual current prices charged,
# which for a number of items turned out to differ from the printed paper
# menu (e.g. price updates that never made it into the printed menu). This
# is the authoritative source, so every price below is confirmed=True.
#
# Each entry is (name, price, confirmed). confirmed=False only remains as a
# mechanism for future additions where no price is known yet — currently
# nothing is in that state.

CATALOG = [
    ("Napici+Sok", [
        ("Espresso Kava", "1.80", True),
        ("Americano", "2.00", True),
        ("Macchiato", "2.00", True),
        ("Veliki Macchiato", "2.20", True),
        ("Cappuccino", "2.30", True),
        ("Kava Šlag", "2.30", True),
        ("Bijela Kava", "2.40", True),
        ("Kakao", "2.40", True),
        ("Nescafe", "2.50", True),
        ("Čaj", "2.00", True),
        ("Mlijeko 0,20", "1.60", True),
        ("Šlag Porcija", "1.50", True),
        ("Espresso B.Kofeina", "2.00", True),
        ("Macchiato B.Kofeina", "2.40", True),
        ("Bijela Kava B.Kofeina", "2.50", True),
        ("Ice Coffee Mlk", "3.50", True),
        ("Med", "0.50", True),
        ("Nes Hladni", "2.70", True),
        ("Coca Cola 0,25", "3.50", True),
        ("Fanta 0,25", "3.50", True),
        ("Sprite 0,25", "3.50", True),
        ("Shweppes 0,25", "3.50", True),
        ("Orangina 0,25", "3.50", True),
        ("Cockta 0,25", "3.50", True),
        ("Voćni Sok 0,20", "3.50", True),
        ("Maraska Sok 0,20", "3.50", True),
        ("Ledeni Čaj 0,33", "3.00", True),
        ("Limunada 0,20", "2.40", True),
        ("Limunada 0,30", "3.00", True),
        ("Limunada 0,50", "3.60", True),
        ("Cedevita 0,20", "3.00", True),
        ("Jed.Naranč 0,20", "4.00", True),
        ("Mineralna 1L", "5.50", True),
        ("Mineralna 0,25", "2.50", True),
        ("Remerqueue 0,33", "2.80", True),
        ("Limunska Trava 0,33", "2.80", True),
        ("Red Bull 0,33", "5.00", True),
        ("Prir. Voda 0,33", "2.20", True),
        ("Mineralna 0,10L", "0.90", True),
        ("Gazirani Sok 0,1", "1.40", True),
    ]),
    ("Pivo+Vino", [
        ("Karlovačko 0,33", "3.00", True),
        ("Karlovačko 0,50", "3.70", True),
        ("Karlovačko Crno 0,50", "3.70", True),
        ("Radler 0,50", "3.70", True),
        ("Heineken 0,33", "3.80", True),
        ("Budweiser 0,5", "3.50", True),
        ("Staropramen 0,5", "3.70", True),
        ("Paulaner 0,50", "4.00", True),
        ("Hidra", "3.70", True),
        ("Somersby 0,33", "4.50", True),
        ("Corona 0,35", "4.00", True),
        ("Ožujsko 0,5", "3.70", True),
        ("Pivo Točeno 0,30", "3.00", True),
        ("Pivo Točeno 0,50", "3.70", True),
        ("Vino Bj.0,10", "1.80", True),
        ("Vino Bj.1L", "18.00", True),
        ("Vino Crno 0,10", "1.80", True),
        ("Vino Crno 1L", "18.00", True),
        ("Bevanda 0,20", "2.00", True),
        ("Gemišt 0,20", "2.50", True),
        ("Gemišt 0,30", "3.50", True),
        ("Bambus 0,20", "3.00", True),
        ("Bambus 0,30", "3.50", True),
        ("Martini 0,10", "3.40", True),
        ("Astoria Prossecco", "30.00", True),
        ("Vrhunsko Vino", "35.00", True),
        ("Teranino", "3.00", True),
    ]),
    ("Alkohol", [
        ("Vodka 0,03", "2.30", True),
        ("Gin 0,03", "2.30", True),
        ("Stock 0,03", "2.70", True),
        ("Pelinkovac 0,03", "2.20", True),
        ("Travarica 0,03", "2.20", True),
        ("Orahovac 0,03", "2.10", True),
        ("Araro 0,03", "2.10", True),
        ("Viljamovka 0,03", "2.40", True),
        ("Bacardi 0,03", "2.60", True),
        ("Tequila 0,03", "2.60", True),
        ("Jegger 0,03", "2.60", True),
        ("Malibu 0,03", "2.50", True),
        ("Balantines 0,03", "2.60", True),
        ("Johnny Walker 0,03", "3.20", True),
        ("Jemeson 0,03", "3.40", True),
        ("Jack Daniels 0,03", "3.60", True),
        ("Martel 0,03", "4.80", True),
        ("Chivas 0,03", "4.00", True),
        ("Hennesy 0,03", "4.80", True),
        ("Carolans 0,03", "2.80", True),
        ("Doljev Alko.Piću", "1.40", True),
        ("Doljev Red Bull", "1.99", True),
        ("Gin Hendri", "4.00", True),
        ("Pelinkovac Antique", "2.80", True),
        ("Campari 0,03", "2.80", True),
        ("Domaća Rakija", "2.10", True),
        ("Johnnie Walker Black", "4.00", True),
        ("Johnnie Walker Green", "6.70", True),
        ("Vodka Smirnof", "2.80", True),
        ("Štrukani Pelin", "2.50", True),
    ]),
    ("Ostalo", [
        ("Sladoled Kuglica", "2.00", True),
        ("Eiskaffe", "5.50", True),
        ("Milk-Shake", "5.50", True),
        ("Smoothie", "5.00", True),
        ("Sendvič", "6.00", True),
        ("Croissant", "2.00", True),
        ("Snjeguljica", "3.50", True),
        ("Kontiki", "3.50", True),
        ("Macho", "4.50", True),
        ("King", "5.00", True),
        ("King Clasic", "4.50", True),
        ("Kornet", "4.50", True),
        ("Ledena Cedevita", "2.00", True),
    ]),
    ("Coctails", [
        ("Hawaiian Blue", "8.50", True),
        ("Hugo", "4.50", True),
        ("Aperol Spritz", "5.50", True),
        ("Blue Lagoon", "7.50", True),
        ("Mohito", "6.50", True),
        ("Tequila Sunrise", "7.50", True),
        ("Long Island", "7.00", True),
        ("Sex On The Beach", "7.00", True),
        ("Mai Tai", "8.50", True),
        ("Cuba Libre", "6.00", True),
        ("Zombie", "7.00", True),
        ("Black Cuba Libre", "7.00", True),
        ("Bahama Mama", "8.50", True),
        ("Caribbean Cruise", "8.50", True),
        ("Piña Colada", "8.50", True),
        ("Bezalkoholic Coctail", "7.00", True),
        ("B52", "4.00", True),
        ("Bloody Screaming Orgasm", "4.00", True),
        ("Kamikaza", "4.00", True),
        ("Woo-Woo", "4.00", True),
        ("Blow Job", "4.00", True),
    ]),
    ("Premium Gin", [
        ("Tanqueray London Dry", "6.50", True),
        ("Tanqueray Rangpur", "6.50", True),
        ("Tanqueray No.10", "7.00", True),
        ("Tanquery Sevilla", "6.50", True),
        ("Gordons Pink", "6.00", True),
        ("Gordons London Dry", "5.50", True),
    ]),
]


class Command(BaseCommand):
    help = (
        "Mbush/rifreskon kategoritë dhe artikujt fillestarë të menusë (nga fotot e "
        "POS-it Luceed dhe çmimet e verifikuara nga vetë arka). E sigurt të rindiget: "
        "rishkruan price/needs_price_review sipas CATALOG-ut çdo herë, PRA MOS e "
        "rindiz pasi stafi të ketë korrigjuar çmimet manualisht në /admin/ — do t'i "
        "mbishkruajë."
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
