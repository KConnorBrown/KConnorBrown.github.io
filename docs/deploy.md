# Deployment to connorbrown.net (Vercel + Squarespace DNS)

Production domain: **connorbrown.net**

## Stack

- **Hosting**: Vercel (Django detected via `manage.py`)
- **Domain registrar**: Squarespace
- **Site database**: Neon Postgres via Vercel Marketplace
- **Playground database**: Second database (`sql_playground`) on the same Neon project
- **Media** (later): S3-compatible storage when you start uploading journal photos

## 1. Push code to GitHub

```bash
git add .
git commit -m "Deploy Django site with PostgreSQL playground"
git push origin master
```

## 2. Create the Vercel project

1. Go to [vercel.com/new](https://vercel.com/new) and import `KConnorBrown/KConnorBrown.github.io`.
2. Framework preset should auto-detect Django.
3. Deploy once with placeholder env vars, or set them before the first deploy (step 3).

## 3. Environment variables

In Vercel → Project → Settings → Environment Variables:

| Variable | Value |
|---|---|
| `DJANGO_SECRET_KEY` | Long random string (`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_ALLOWED_HOSTS` | `connorbrown.net,www.connorbrown.net` |
| `CSRF_TRUSTED_ORIGINS` | `https://connorbrown.net,https://www.connorbrown.net` |
| `DATABASE_URL` | From Neon (Vercel Marketplace → Storage → Neon) |
| `PLAYGROUND_DB_NAME` | `sql_playground` |

In Neon, create a second database named `sql_playground` in the same project.
Vercel will use the same connection credentials with that database name for the playground.

Redeploy after setting variables.

## 4. Initialize production data

```bash
npx vercel login
npx vercel link
npx vercel env pull .env.production
set -a && source .env.production && set +a
source .venv/bin/activate
python manage.py migrate
python manage.py seed_playground
python manage.py bootstrap_portfolio
python manage.py createsuperuser
```

## 5. Connect connorbrown.net (Squarespace DNS)

### In Vercel

1. Project → Settings → Domains
2. Add `connorbrown.net`
3. Add `www.connorbrown.net`
4. Copy the DNS records Vercel shows you

### In Squarespace

1. [domains.squarespace.com](https://domains.squarespace.com) → select **connorbrown.net**
2. DNS → DNS Settings
3. Either use the **Vercel DNS preset** (Add Preset → Vercel), or add records manually:

| Type | Host / Name | Value |
|---|---|---|
| A | `@` | `76.76.21.21` |
| CNAME | `www` | `cname.vercel-dns.com` |

4. Remove conflicting A/CNAME records that point to Squarespace hosting (if any).
5. Do **not** remove MX or TXT records if you use email on this domain.

DNS propagation usually takes a few minutes to 48 hours.

## 6. Verify

- https://connorbrown.net/
- https://www.connorbrown.net/
- https://connorbrown.net/playground/sql/
- https://connorbrown.net/development/
- https://connorbrown.net/writing/

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew services start postgresql@14
createdb connor_site
createdb sql_playground
python manage.py migrate
python manage.py seed_playground
python manage.py runserver
```

## Fallback: Render / Railway

The `Procfile` (`web: gunicorn config.wsgi`) works on Render or Railway if you prefer
a long-running dyno over Vercel serverless. Point Squarespace DNS to that host instead.
