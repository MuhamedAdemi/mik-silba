"""Lightweight UI translations (HR default, EN and SQ optional).

Menu/category names are NOT translated here on purpose — drink and brand
names (Cappuccino, Karlovačko, Aperol Spritz...) read the same in every
language and matching what's on the POS buttons matters more than
translating them. Only the surrounding interface chrome is translated.
"""

DEFAULT_LANGUAGE = "hr"
LANGUAGES = [
    ("hr", "HR"),
    ("en", "EN"),
    ("sq", "SHQ"),
]

TRANSLATIONS = {
    "nav_reports": {"hr": "Izvještaji", "en": "Reports", "sq": "Raportet"},
    "nav_logout": {"hr": "Odjava", "en": "Log out", "sq": "Dilni"},
    "nav_staff": {"hr": "Osoblje", "en": "Staff", "sq": "Stafi"},
    "nav_history": {"hr": "Povijest", "en": "History", "sq": "Historiku"},

    "history_title": {"hr": "Povijest stolova", "en": "Table history", "sq": "Historiku i tavolinave"},
    "history_search_table": {"hr": "Stol", "en": "Table", "sq": "Stoli"},
    "history_search_placeholder": {"hr": "npr. A1", "en": "e.g. A1", "sq": "p.sh. A1"},
    "history_status": {"hr": "Status", "en": "Status", "sq": "Statusi"},
    "history_closed": {"hr": "zaključen", "en": "closed", "sq": "mbyllur"},
    "history_cancelled": {"hr": "otkazan", "en": "cancelled", "sq": "anuluar"},
    "history_view": {"hr": "Pogledaj", "en": "View", "sq": "Shiko"},
    "history_no_results": {
        "hr": "Nema stolova u ovom razdoblju/pretrazi.",
        "en": "No tables in this period/search.",
        "sq": "Nuk ka tavolina në këtë periudhë/kërkim.",
    },
    "history_opened": {"hr": "Otvoren", "en": "Opened", "sq": "Hapur"},
    "history_closed_at": {"hr": "Zatvoren", "en": "Closed", "sq": "Mbyllur"},

    "staff_title": {"hr": "Osoblje", "en": "Staff", "sq": "Stafi"},
    "staff_add": {"hr": "Dodaj osoblje", "en": "Add staff", "sq": "Shto staf"},
    "staff_display_name": {"hr": "Ime za prikaz", "en": "Display name", "sq": "Emri për ekran"},
    "staff_role": {"hr": "Uloga", "en": "Role", "sq": "Roli"},
    "staff_delete": {"hr": "Obriši", "en": "Delete", "sq": "Fshi"},
    "staff_delete_confirm": {
        "hr": "Sigurno obrisati/deaktivirati ovog korisnika?",
        "en": "Really delete/deactivate this user?",
        "sq": "Je i sigurt që do ta fshish/çaktivizosh këtë përdorues?",
    },
    "staff_inactive_badge": {"hr": "deaktiviran", "en": "deactivated", "sq": "i çaktivizuar"},
    "staff_you": {"hr": "(ti)", "en": "(you)", "sq": "(ti)"},
    "staff_save": {"hr": "Spremi", "en": "Save", "sq": "Ruaj"},
    "staff_back": {"hr": "← Osoblje", "en": "← Staff", "sq": "← Stafi"},

    "login_error": {
        "hr": "Pogrešno korisničko ime ili lozinka.",
        "en": "Wrong username or password.",
        "sq": "Username ose fjalëkalim i gabuar.",
    },
    "login_username": {"hr": "Korisničko ime", "en": "Username", "sq": "Username"},
    "login_password": {"hr": "Lozinka", "en": "Password", "sq": "Fjalëkalimi"},
    "login_button": {"hr": "Prijava", "en": "Log in", "sq": "Kyçu"},

    "table_free": {"hr": "slobodan", "en": "free", "sq": "e lirë"},
    "table_occupied": {"hr": "zauzet", "en": "occupied", "sq": "e zënë"},

    "col_item_name": {"hr": "Naziv artikla", "en": "Item name", "sq": "Emri i artikullit"},
    "col_qty": {"hr": "Količina", "en": "Qty", "sq": "Sasia"},
    "col_amount": {"hr": "Iznos", "en": "Amount", "sq": "Shuma"},

    "cart_back": {"hr": "← Stolovi", "en": "← Tables", "sq": "← Stolovi"},
    "cart_empty": {"hr": "Još nema stavki.", "en": "No items yet.", "sq": "Ende s'ka artikuj."},
    "cart_total": {"hr": "Ukupno", "en": "Total", "sq": "Total"},
    "cart_sent_to_bar": {"hr": "poslano šanku", "en": "sent to bar", "sq": "te bari"},
    "cart_print_shank": {"hr": "🖨 Šank", "en": "🖨 Bar ticket", "sq": "🖨 Shank"},
    "cart_print_predracun": {"hr": "Predračun", "en": "Pro-forma bill", "sq": "Predračun"},
    "cart_close_order": {"hr": "Zaključi narudžbu", "en": "Close order", "sq": "Mbyll porosinë"},
    "cart_cancel_confirm": {
        "hr": "Otkažeš cijeli stol?",
        "en": "Cancel the whole table order?",
        "sq": "Anulo krejt porosinë e stolit?",
    },
    "cart_cancel_table": {"hr": "Otkaži stol", "en": "Cancel table", "sq": "Anulo stolin"},

    "action_open_table": {"hr": "Otvori stol", "en": "Open table", "sq": "Hap stolin"},
    "action_delete_item": {"hr": "Obriši stavku", "en": "Delete item", "sq": "Fshi artikullin"},
    "action_cash_state": {"hr": "Stanje kase", "en": "Cash state", "sq": "Gjendja e arkës"},
    "select_item_first": {
        "hr": "Prvo odaberi stavku na popisu.",
        "en": "Select an item from the list first.",
        "sq": "Zgjidh një artikull nga lista fillimisht.",
    },

    "close_title": {"hr": "Zaključi narudžbu — Stol", "en": "Close order — Table", "sq": "Mbyll porosinë — Stoli"},
    "close_total": {"hr": "Ukupno:", "en": "Total:", "sq": "Total:"},
    "close_no_items": {
        "hr": "Stol nema stavki, ne može se zaključiti.",
        "en": "The table has no items, it can't be closed.",
        "sq": "Stoli s'ka artikuj, nuk mund të mbyllet.",
    },
    "close_payment_method": {"hr": "Način plaćanja", "en": "Payment method", "sq": "Mënyra e pagesës"},
    "close_cash": {"hr": "Gotovina", "en": "Cash", "sq": "Para në dorë"},
    "close_card": {"hr": "Kartica", "en": "Card", "sq": "Kartë"},
    "close_back": {"hr": "← Natrag na stol", "en": "← Back to table", "sq": "← Kthehu te stoli"},

    "print_button": {"hr": "🖨 Ispiši", "en": "🖨 Print", "sq": "🖨 Printo"},
    "shank_confirm_send": {"hr": "Potvrdi slanje šanku", "en": "Confirm sent to bar", "sq": "Konfirmo dërgimin te bari"},
    "back": {"hr": "← Natrag", "en": "← Back", "sq": "← Kthehu"},
    "shank_all_sent": {
        "hr": "Sve stavke su već poslane šanku.",
        "en": "All items have already been sent to the bar.",
        "sq": "Të gjithë artikujt janë dërguar tashmë te bari.",
    },

    "predracun_label": {
        "hr": "PREDRAČUN — nije fiskalni račun",
        "en": "PRO-FORMA BILL — not a fiscal receipt",
        "sq": "PREDRAČUN — nuk është faturë fiskale",
    },
    "total_caps": {"hr": "UKUPNO", "en": "TOTAL", "sq": "TOTAL"},

    "racun_label": {
        "hr": "RAČUN (interni) — nije fiskalni račun",
        "en": "RECEIPT (internal) — not a fiscal receipt",
        "sq": "RAČUN (intern) — nuk është faturë fiskale",
    },
    "racun_waiter": {"hr": "Konobar:", "en": "Waiter:", "sq": "Konobari:"},
    "racun_payment": {"hr": "Način plaćanja:", "en": "Payment:", "sq": "Pagesa:"},

    "dashboard_title": {"hr": "Trenutno stanje", "en": "Live status", "sq": "Gjendja live"},
    "dashboard_sales_link": {"hr": "Izvještaj prodaje →", "en": "Sales report →", "sq": "Raporti i shitjeve →"},
    "dashboard_occupied": {"hr": "zauzetih stolova", "en": "tables occupied", "sq": "tavolina zënë"},
    "dashboard_open_tables": {"hr": "Trenutno otvoreni stolovi", "en": "Currently open tables", "sq": "Tavolina hapur tani"},
    "dashboard_table": {"hr": "Stol", "en": "Table", "sq": "Stoli"},
    "dashboard_zone": {"hr": "Zona", "en": "Zone", "sq": "Zona"},
    "dashboard_waiter": {"hr": "Konobar", "en": "Waiter", "sq": "Konobari"},
    "dashboard_opened": {"hr": "Otvoren prije", "en": "Opened", "sq": "Hapur prej"},
    "dashboard_total_so_far": {"hr": "Ukupno do sada", "en": "Total so far", "sq": "Total deri tani"},
    "dashboard_open_btn": {"hr": "Otvori", "en": "Open", "sq": "Hap"},
    "dashboard_no_open": {
        "hr": "Trenutno nema otvorenih stolova.",
        "en": "No tables currently open.",
        "sq": "Asnjë tavolinë e hapur momentalisht.",
    },
    "dashboard_note": {
        "hr": "Redak postaje žut nakon 30 min, a crven nakon 60 min otvoren — signal da stol možda treba pažnju.",
        "en": "A row turns yellow after 30 min and red after 60 min open — a signal the table may need attention.",
        "sq": "Rreshti bëhet i verdhë pas 30 min dhe i kuq pas 60 min hapur — sinjal që tavolina mund të ketë nevojë për vëmendje.",
    },

    "sales_title": {"hr": "Izvještaj prodaje", "en": "Sales report", "sq": "Raporti i shitjeve"},
    "sales_live_link": {"hr": "← Trenutno stanje", "en": "← Live dashboard", "sq": "← Live dashboard"},
    "sales_from": {"hr": "Od", "en": "From", "sq": "Nga"},
    "sales_to": {"hr": "Do", "en": "To", "sq": "Deri"},
    "sales_filter": {"hr": "Filtriraj", "en": "Filter", "sq": "Filtro"},
    "sales_total_revenue": {"hr": "Ukupna prodaja", "en": "Total sales", "sq": "Total shitje"},
    "sales_closed_tables": {"hr": "Zaključenih stolova", "en": "Closed tables", "sq": "Stolove të mbyllura"},
    "sales_busy_hours": {"hr": "Sati s najviše posla", "en": "Busiest hours", "sq": "Orët me më shumë punë"},
    "sales_top_items": {"hr": "Top 10 artikala", "en": "Top 10 items", "sq": "Top 10 artikuj"},
    "sales_item": {"hr": "Artikl", "en": "Item", "sq": "Artikulli"},
    "sales_qty": {"hr": "Količina", "en": "Qty", "sq": "Sasia"},
    "sales_revenue": {"hr": "Prihod", "en": "Revenue", "sq": "Të ardhura"},
    "sales_no_data": {
        "hr": "Nema prodaje u ovom razdoblju.",
        "en": "No sales in this period.",
        "sq": "Nuk ka shitje në këtë periudhë.",
    },
    "sales_by_category": {"hr": "Prodaja po kategoriji", "en": "Sales by category", "sq": "Shitje sipas kategorisë"},
    "sales_category": {"hr": "Kategorija", "en": "Category", "sq": "Kategoria"},
    "sales_by_waiter": {"hr": "Prodaja po konobaru", "en": "Sales by waiter", "sq": "Shitje sipas konobarit"},
    "sales_orders": {"hr": "Stolova", "en": "Orders", "sq": "Stolove"},
    "sales_qty_sold_axis": {"hr": "Prodanih artikala", "en": "Items sold", "sq": "Artikuj të shitur"},

    "cash_state_title": {"hr": "Stanje kase", "en": "Cash state", "sq": "Gjendja e arkës"},
    "cash_state_today": {"hr": "Danas", "en": "Today", "sq": "Sot"},
    "cash_state_your_closed": {"hr": "Tvoji zaključeni stolovi", "en": "Your closed tables", "sq": "Stolovet e tua të mbyllura"},
    "cash_state_cash": {"hr": "Gotovina", "en": "Cash", "sq": "Para në dorë"},
    "cash_state_card": {"hr": "Kartica", "en": "Card", "sq": "Kartë"},
    "cash_state_total": {"hr": "Ukupno", "en": "Total", "sq": "Total"},
}


def translate(key, lang):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANGUAGE) or key
