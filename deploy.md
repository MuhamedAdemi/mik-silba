# Deploy: GitHub → PythonAnywhere

## Herën e parë

### 1. GitHub
```
git init
git add .
git commit -m "Fillimi i aplikacionit Caffe MiK"
```
Krijo një repo bosh në github.com (p.sh. `caffe-mik-pos`), pastaj:
```
git remote add origin https://github.com/<username-yt>/caffe-mik-pos.git
git branch -M main
git push -u origin main
```

### 2. PythonAnywhere — konto & kod
1. Krijo konto në pythonanywhere.com (plani Free mjafton për fillim).
2. Hap një **Bash console** nga dashboard-i dhe klono repon:
   ```
   git clone https://github.com/<username-yt>/caffe-mik-pos.git
   cd caffe-mik-pos
   ```
3. Krijo virtualenv (nga tab-i "Consoles" ose direkt në bash):
   ```
   mkvirtualenv --python=/usr/bin/python3.12 mikvenv
   pip install -r requirements.txt
   ```
   *(Kontrollo te tab-i "Web" → "Virtualenv" cila version Python ofron PythonAnywhere aktualisht; nëse s'ka 3.12, përdor versionin më të ri të disponueshëm dhe njofto — mund të duhet të fiksohet Django në një version paksa më të vjetër në requirements.txt.)*

### 3. Databaza MySQL
1. Tab "Databases" → cakto fjalëkalim MySQL → krijo databazën (do të quhet diçka si `<username>$mik`).
2. Shënoji: emrin e databazës, host-in (`<username>.mysql.pythonanywhere-services.com`), user (=username-i yt), fjalëkalimin.

### 4. Skedari `.env` në server
Në Bash console, brenda `caffe-mik-pos/`:
```
cp .env.example .env
nano .env
```
Plotëso `DJANGO_SECRET_KEY` (çdo varg i gjatë i rastësishëm), `DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://<username>.pythonanywhere.com`, dhe DB_* nga hapi 3. Ruaj (Ctrl+O, Enter, Ctrl+X).

### 5. Tab "Web"
1. "Add a new web app" → **Manual configuration** → Python version = ajo e virtualenv-it.
2. "Virtualenv" → shto path-in e plotë (p.sh. `/home/<username>/.virtualenvs/mikvenv`).
3. "Code" → "Source code" = `/home/<username>/caffe-mik-pos`.
4. Hap "WSGI configuration file" dhe zëvendëso përmbajtjen me:
   ```python
   import os
   import sys

   path = '/home/<username>/caffe-mik-pos'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
5. Në pjesën "Static files" të tab-it Web, s'ke nevojë të shtosh mapping — WhiteNoise i shërben vetë statikat.

### 6. Migrate + seed + collectstatic
Në Bash console:
```
workon mikvenv
cd caffe-mik-pos
python manage.py migrate
python manage.py seed_tables
python manage.py seed_menu
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Reload
Tab "Web" → butoni jeshil **Reload**. Hap `https://<username>.pythonanywhere.com` nga telefoni dhe nga PC.

### 8. Plotëso çmimet e munguara
Hyr te `/admin/menu/menuitem/`, filtro sipas "Needs price review" = Yes, plotëso çmimet reale (kolona është e redaktueshme direkt në listë).

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
cd caffe-mik-pos
git pull
workon mikvenv
pip install -r requirements.txt   # vetëm nëse ka ndryshuar requirements.txt
python manage.py migrate           # vetëm nëse ka ndryshime modelesh
python manage.py collectstatic --noinput   # vetëm nëse ka ndryshime CSS/JS
```
Pastaj tab "Web" → **Reload**.

## Shënime

- Plani **Free** i PythonAnywhere lejon vetëm domain-in `<username>.pythonanywhere.com` (jo domain vetjak) dhe ka limit ditor CPU — i mjaftueshëm për një bar, por nëse ka shumë pajisje të lidhura gjatë gjithë ditës e ndjeni ngadalësim, konsideroni upgrade në planin me pagesë ($5-12/muaj).
- `git clone`/`git pull` nga github.com funksionon në planin Free (është në listën e lejuar të internetit të jashtëm).
- `.env` dhe `db.sqlite3` NUK shkojnë kurrë në GitHub (janë në `.gitignore`) — çdo herë që ndryshon `.env` në server, e ndryshon vetëm atje.
