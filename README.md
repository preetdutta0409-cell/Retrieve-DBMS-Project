# Retrieve — Lost & Found

Retrieve is a community lost-and-found web app built with Python, Flask, Flask-SQLAlchemy and MySQL. This package starts from the previously tested `Retrieve_UI_Fixed` feature set and replaces the visual system only, while retaining the existing route names and database models.

## Included features
- Registration, sign-in and sign-out with password hashing
- Lost/found reports, categories, search and filters
- Listing detail pages and private ownership claims
- User dashboard, incoming claim review and mark-as-returned action
- Rule-based match suggestions
- In-app notifications
- Claim-linked private messaging
- Admin dashboard, listing hide/restore and claim/user overview
- Responsive editorial UI inspired by the supplied references: warm cream and terracotta discovery pages, espresso panels, serif display typography, pastel category tiles, and dark cinematic authentication screens
- Responsive mobile navigation, page-entry motion, reduced-motion support, form loading states and accessible focus rings
- Custom 400/403/404/413/500 error pages
- `/robots.txt`, custom SVG favicon, lazy-loaded listing photos and WebP image compression on upload
- Full-height page layout so the footer stays at the bottom on short pages

## Requirements
- Python 3.10+
- MySQL 8+ or compatible server

## 1. Configure MySQL
Use your existing `retrieve_db` and `retrieve_user` if you already created them. Do not drop the database just to apply the UI update.

Example SQL for a new database only:
```sql
CREATE DATABASE retrieve_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'retrieve_user'@'localhost' IDENTIFIED BY 'choose_a_strong_password';
GRANT ALL PRIVILEGES ON retrieve_db.* TO 'retrieve_user'@'localhost';
FLUSH PRIVILEGES;
```

## 2. Set up the project
Open a terminal in the `retrieve_app` folder.

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If you already have a `.env` file, copy your existing file into this folder rather than overwriting it. Keep it private.

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your actual MySQL credentials. URL-encode special characters in passwords. Change `SECRET_KEY` to a long random value.

## 3. Initialize and run
Ensure MySQL is running, then:
```powershell
flask --app app init-db
flask --app app run --debug
```

Open http://127.0.0.1:5000. `init-db` creates missing tables and does not delete existing rows. The app expects to be run from this folder so Flask can find the templates and static assets.

## 4. Admin account
Set `ADMIN_NAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` in `.env`, then run:
```powershell
flask --app app create-admin
```
Visit `/admin` while signed in with that account.

## Image handling
Uploads accept PNG, JPG/JPEG and WEBP, up to 5 MB. Pillow normalizes image orientation, removes EXIF metadata, resizes large images to at most 1600×1600 and saves them as optimized WebP. Existing images are not batch-converted automatically.

## Important
- Smart matching is a transparent heuristic score, not proof of ownership or a diagnostic/AI service.
- Notifications are in-app only. Email/SMS and external OAuth providers are not configured.
- The login form uses email/password. Buttons for Google/Facebook/Apple are not included because no OAuth credentials/providers were supplied.
- Before public deployment, add CSRF protection, rate limiting, password reset/email verification, database migrations, automated tests, secure production secrets, HTTPS, backups and a production WSGI server. Never use Flask's debug server in production.
