# Instagram photo import

Import photos from `@rupaulsoilrig` into the photo journal at `/photo-journal/`.

## Is ~600–700 photos too many?

**Locally: no.** Importing the full archive (~200MB / ~630 images) is fine for
curation. Postgres/SQLite and local `media/` can handle it.

**Production: do not host all of them.** Only keep/publish what you want on
`connorbrown.net`. Use:

- **Delete** in the photo modal (staff only) to remove photo + file permanently
- **Hide from public** to unpublish without deleting
- **Collections** in Django admin for curated sets (kitchen, garden, living room…)

Workflow:

1. Import everything locally
2. Curate (delete / hide / assign to collections)
3. Later upload only published/`media` survivors to S3 for Vercel

## Recommended: browser cookie login

Instagram often blocks password logins from scripts. Instead, log in normally
in your browser and reuse that session:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
```

1. Open **Chrome** and log into https://www.instagram.com/ as `@rupaulsoilrig`
2. Complete any security prompts in the browser
3. Download posts:

```bash
python manage.py fetch_instagram --username rupaulsoilrig --load-cookies chrome --fresh-login
```

If Chrome uses a non-Default profile (common), point at that Cookies DB
explicitly. Example for **Profile 1**:

```bash
python manage.py fetch_instagram --username rupaulsoilrig --load-cookies chrome \
  --cookie-file "$HOME/Library/Application Support/Google/Chrome/Profile 1/Cookies" \
  --fresh-login
```

4. Import into the site:

```bash
python manage.py import_instagram --username rupaulsoilrig
python manage.py createsuperuser   # once — required for delete/curation UI
python manage.py runserver
```

Open http://127.0.0.1:8000/photo-journal/ and log in at `/admin/`.
Staff users see curation controls in the photo modal.

## Collections

In `/admin/journal/photocollection/`:

1. Create collections like “Garden”, “Kitchen”, “Living room”
2. Use the entry picker to add photos
3. The photo journal shows collection filter chips at the top

## Fallback: official Instagram data export

```bash
python manage.py import_instagram_export --source-dir ~/Downloads/your-export-folder/
```

## Security

- Never paste your Instagram password into chat or commit it to git
- Session files live in `data/instagram/` (gitignored)
- Downloaded and imported media live under `data/` and `media/` (gitignored)
