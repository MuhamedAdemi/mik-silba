# Caffe MiK — POS

Aplikacion Django për regjistrimin e porosive sipas tavolinave (Terasa A/B, Park, Unutra), printim shank/predračun/račun, dhe raporte shitjesh për Caffe MiK (Silba).

## Zhvillim lokal

```
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python manage.py migrate
venv\Scripts\python manage.py seed_tables
venv\Scripts\python manage.py seed_menu
venv\Scripts\python manage.py createsuperuser
venv\Scripts\python manage.py runserver
```

Hap `http://127.0.0.1:8000/`. Superuser-i i krijuar merr automatikisht rolin **Admin** (qasje te `/raporte/`); çdo user tjetër krijohet si **Konobar** (mund të ndryshohet te `/admin/accounts/staffprofile/` ose te inline-i i User-it).

## Struktura

- `accounts` — login/logout, rolet (Admin/Konobar)
- `venue` — zonat dhe tavolinat
- `menu` — kategoritë dhe artikujt (çmimet)
- `orders` — porositë, shporta, printimi (shank/predračun/račun)
- `reports` — dashboard live + raporti i shitjeve (vetëm Admin)

## Çmime që mungojnë

Shumë artikuj u importuan nga fotot e POS-it "Luceed" pa çmim të lexueshëm/të sigurt (foto e paqartë ose faqja e menusë s'e mbulonte atë artikull). Këta janë flaguar `needs_price_review=True` — plotësoi te `/admin/menu/menuitem/` (filtro "Needs price review").

## Deploy

Shiko [deploy.md](deploy.md) për GitHub → PythonAnywhere.
