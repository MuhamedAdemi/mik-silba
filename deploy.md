# Deploy: GitHub → PythonAnywhere

Repo: https://github.com/MuhamedAdemi/mik-silba (tashmë i pushuar ✓)
PythonAnywhere username: `miksilba`

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
3. Kontrollo versionet e Python të disponueshme: tab "Web" → kur krijon web app-in (hapi 5) do të shohësh listën. Krijo virtualenv me versionin më të ri të disponueshëm (idealisht 3.12+, pasi Django 6.1 e kërkon):
   ```
   mkvirtualenv --python=/usr/bin/python3.12 mikvenv
   pip install -r requirements.txt
   ```
   Nëse `pip install` dështon te `mysqlclient` (rrallë ndodh), instalo më parë: `pip install --upgrade pip setuptools wheel` dhe provo sërish.

### 3. Databaza MySQL
1. Tab "Databases" → në fushën "Password" cakto një fjalëkalim MySQL → "Set password".
2. Do të krijohet automatikisht databaza `miksilba$default` (ose e krijon vetë me emër tjetër nga po ai tab nëse do).
3. Shëno: emri i databazës (p.sh. `miksilba$default`), host (`miksilba.mysql.pythonanywhere-services.com`), user = `miksilba`, fjalëkalimi që vendose.

### 4. Skedari `.env` në server
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

DB_NAME=miksilba$default
DB_USER=miksilba
DB_PASSWORD=<fjalëkalimi i MySQL nga hapi 3>
DB_HOST=miksilba.mysql.pythonanywhere-services.com
DB_PORT=3306
```
Ruaj: Ctrl+O, Enter, Ctrl+X.

### 5. Tab "Web"
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

### 6. Migrate + seed + superuser + collectstatic
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

### 7. Reload
Tab "Web" → butoni jeshil **Reload**. Hap `https://miksilba.pythonanywhere.com` nga telefoni dhe nga PC.

### 8. Plotëso çmimet e munguara (nëse ka ndryshuar diçka që nga zhvillimi lokal)
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

## Shënime

- Plani **Free** i PythonAnywhere lejon vetëm domain-in `miksilba.pythonanywhere.com` (jo domain vetjak) dhe ka limit ditor CPU — i mjaftueshëm për një bar, por nëse ka shumë pajisje të lidhura gjatë gjithë ditës e ndjeni ngadalësim, konsideroni upgrade në planin me pagesë ($5-12/muaj).
- `git clone`/`git pull` nga github.com funksionon në planin Free (është në listën e lejuar të internetit të jashtëm).
- `.env` dhe `db.sqlite3` NUK shkojnë kurrë në GitHub (janë në `.gitignore`) — çdo herë që ndryshon `.env` në server, e ndryshon vetëm atje.
- Kamarierët e thjeshtë të testit (`konobar1`/`1111`, `konobar2`/`2222`) janë vetëm për zhvillim lokal — mos i krijo me këto fjalëkalime të dobëta në prodhim; krijoji të vërtetët nga `/stafi/` me fjalëkalime të forta.
