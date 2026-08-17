# Deploy: GitHub → PythonAnywhere

Repo: https://github.com/MuhamedAdemi/mik-silba (tashmë i pushuar ✓)
PythonAnywhere username: `miksilba`

Databaza: **SQLite** (jo MySQL) — plani Free i PythonAnywhere nuk e ka MySQL/Postgres pa upgrade me pagesë, dhe për një bar të vetëm SQLite e përballon plotësisht ngarkesën. Nëse ndonjëherë kaloni në plan me pagesë dhe doni MySQL, thjesht ndryshohet `config/settings/production.py`.

## Herën e parë

### 1. GitHub — ✓ e bërë
Kodi është tashmë në `github.com/MuhamedAdemi/mik-silba`, branch `main`.

### 2. PythonAnywhere — konto & kod
1. Kyçu në pythonanywhere.com me llogarinë `miksilba`.
2. Hap një **Bash console** nga dashboard-i (Consoles → Bash) dhe klono repon:
   ```
   git clone https://github.com/MuhamedAdemi/mik-silba.git
   cd mik-silba
   ```
3. Kontrollo versionet e Python të disponueshme: tab "Web" → kur krijon web app-in (hapi 4) do të shohësh listën. Krijo virtualenv me versionin më të ri të disponueshëm (idealisht 3.12+, pasi Django 6.1 e kërkon):
   ```
   mkvirtualenv --python=/usr/bin/python3.12 mikvenv
   pip install -r requirements.txt
   ```

### 3. Skedari `.env` në server
Në Bash console, brenda `mik-silba/`:
```
cp .env.example .env
nano .env
```
Plotëso:
```
DJANGO_SECRET_KEY=<çdo varg i gjatë i rastësishëm, p.sh. 50 karaktere>
DJANGO_ALLOWED_HOSTS=miksilba.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://miksilba.pythonanywhere.com
DJANGO_SECURE_SSL_REDIRECT=True
```
Ruaj: Ctrl+O, Enter, Ctrl+X.

### 4. Tab "Web"
1. "Add a new web app" → **Manual configuration** (jo "Django" wizard-in automatik, pasi ne e kemi vetë strukturën) → zgjidh versionin e Python që përputhet me virtualenv-in.
2. Në seksionin "Virtualenv" të faqes së web app-it, shto path-in: `/home/miksilba/.virtualenvs/mikvenv`.
3. Në seksionin "Code": "Source code" = `/home/miksilba/mik-silba`.
4. Kliko te "WSGI configuration file" (linku blu) dhe zëvendëso GJITHË përmbajtjen me:
   ```python
   import os
   import sys

   path = '/home/miksilba/mik-silba'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
   Ruaj (Save).
5. Seksioni "Static files" — s'ke nevojë të shtosh mapping, WhiteNoise i shërben vetë skedarët statikë përmes Django-s.

### 5. Migrate + seed + superuser + collectstatic
Në Bash console:
```
workon mikvenv
cd mik-silba
python manage.py migrate
python manage.py seed_tables
python manage.py seed_menu
python manage.py collectstatic --noinput
```
Krijo superuser-in real (Muhamed):
```
python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.create_superuser('muhamedademi', 'muhamed@example.com', 'Muki1234@')
u.profile.display_name = 'Muhamed Ademi'
u.profile.save()
"
```
(Blerimin dhe kamarierët i krijon më lehtë pas kësaj direkt nga aplikacioni, te `/stafi/`, i kyçur si `muhamedademi`.)

### 6. Reload
Tab "Web" → butoni jeshil **Reload**. Hap `https://miksilba.pythonanywhere.com` nga telefoni dhe nga PC.

### 7. Plotëso çmimet e munguara (nëse ka ndryshuar diçka që nga zhvillimi lokal)
Hyr te `/admin/menu/menuitem/` (kyçu me superuser-in), filtro sipas "Needs price review" = Yes.

---

## Përditësimet e ardhshme (pas çdo ndryshimi kodi)

Lokalisht:
```
git add .
git commit -m "..."
git push
```

Në PythonAnywhere (Bash console):
```
cd mik-silba
git pull
workon mikvenv
pip install -r requirements.txt   # vetëm nëse ka ndryshuar requirements.txt
python manage.py migrate           # vetëm nëse ka ndryshime modelesh
python manage.py collectstatic --noinput   # vetëm nëse ka ndryshime CSS/JS
```
Pastaj tab "Web" → **Reload**.

## Rezervë (backup) e të dhënave

Meqë databaza është SQLite (një skedar i vetëm `db.sqlite3` brenda `mik-silba/`), backup do të thotë thjesht ta shkarkosh atë skedar herë pas here: tab "Files" në PythonAnywhere → gjej `mik-silba/db.sqlite3` → shkarko. E rekomandueshme ta bësh këtë periodikisht (p.sh. një herë në javë).

## Shënime

- Plani **Free** i PythonAnywhere lejon vetëm domain-in `miksilba.pythonanywhere.com` (jo domain vetjak) dhe ka limit ditor CPU — i mjaftueshëm për një bar, por nëse ndjeni ngadalësim me shumë pajisje njëkohësisht, konsideroni upgrade në planin me pagesë ($5-12/muaj) — atëherë bëhet i mundur edhe MySQL/Postgres nëse doni bazë të dhënash më të fortë.
- `git clone`/`git pull` nga github.com funksionon në planin Free (është në listën e lejuar të internetit të jashtëm).
- `.env` dhe `db.sqlite3` NUK shkojnë kurrë në GitHub (janë në `.gitignore`) — çdo herë që ndryshon `.env` në server, e ndryshon vetëm atje.
- Kamarierët e thjeshtë të testit (`konobar1`/`1111`, `konobar2`/`2222`) janë vetëm për zhvillim lokal — mos i krijo me këto fjalëkalime të dobëta në prodhim; krijoji të vërtetët nga `/stafi/` me fjalëkalime të forta.
