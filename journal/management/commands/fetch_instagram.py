import getpass
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def format_instagram_checkpoint_url(message: str) -> str | None:
    match = re.search(r"(https?://[^\s]+|/auth_platform/\?apc=[^\s]+)", message)
    if not match:
        return None
    url = match.group(1)
    if url.startswith("/"):
        return f"https://www.instagram.com{url}"
    return url


def chrome_cookie_candidates() -> list[Path]:
    base = Path.home() / "Library/Application Support/Google/Chrome"
    if not base.exists():
        return []
    paths = []
    for name in ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]:
        candidate = base / name / "Cookies"
        if candidate.exists():
            paths.append(candidate)
    return paths


def find_chrome_profile_with_instagram_session() -> Path | None:
    try:
        import browser_cookie3
    except ImportError:
        return None

    for cookie_file in chrome_cookie_candidates():
        try:
            cookies = list(browser_cookie3.chrome(cookie_file=str(cookie_file)))
        except Exception:
            continue
        if any(c.name == "sessionid" and "instagram" in (c.domain or "") for c in cookies):
            return cookie_file
    return None


class Command(BaseCommand):
    help = "Download Instagram posts using Instaloader (browser cookies or saved session)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="rupaulsoilrig",
            help="Instagram profile to download (default: rupaulsoilrig)",
        )
        parser.add_argument(
            "--output-dir",
            default="",
            help="Directory for downloaded images (default: data/instagram/<username>)",
        )
        parser.add_argument(
            "--login-user",
            default="",
            help="Expected Instagram login username (defaults to --username)",
        )
        parser.add_argument(
            "--load-cookies",
            default="",
            help="Import login from browser cookies (chrome, safari, firefox, edge, brave, etc.)",
        )
        parser.add_argument(
            "--cookie-file",
            default="",
            help="Optional path to a Chrome Cookies DB (use when logged into a non-Default profile)",
        )
        parser.add_argument(
            "--fresh-login",
            action="store_true",
            help="Ignore any saved session before logging in",
        )

    def handle(self, *args, **options):
        try:
            import instaloader
            from instaloader.exceptions import LoginException
        except ImportError as exc:
            raise CommandError(
                "Install dev dependencies: pip install -r requirements-dev.txt"
            ) from exc

        target_username = options["username"]
        login_user = options["login_user"] or target_username
        output_dir = Path(options["output_dir"] or settings.BASE_DIR / "data" / "instagram" / target_username)
        output_dir.mkdir(parents=True, exist_ok=True)

        session_dir = settings.BASE_DIR / "data" / "instagram"
        session_dir.mkdir(parents=True, exist_ok=True)
        session_path = session_dir / f"session-{login_user}"

        if options["fresh_login"] and session_path.exists():
            session_path.unlink()
            self.stdout.write("Removed saved session.")

        loader = instaloader.Instaloader(
            dirname_pattern=str(output_dir / "{target}"),
            filename_pattern="{date_utc}_UTC",
            download_pictures=True,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
            post_metadata_txt_pattern="",
        )

        try:
            logged_in = self._authenticate(
                loader,
                login_user,
                session_path,
                options["load_cookies"],
                options["cookie_file"],
                options["fresh_login"],
            )
        except LoginException as exc:
            self._print_auth_help(exc, options["load_cookies"])
            raise CommandError("Instagram login failed.") from exc
        except Exception as exc:
            self._print_auth_help(exc, options["load_cookies"])
            raise CommandError(f"Instagram login failed: {exc}") from exc

        if not logged_in:
            raise CommandError("Could not authenticate with Instagram.")

        profile = instaloader.Profile.from_username(loader.context, target_username)
        count = 0
        for post in profile.get_posts():
            loader.download_post(post, target=str(output_dir))
            count += 1
            if count % 10 == 0:
                self.stdout.write(f"Downloaded {count} posts...")

        self.stdout.write(
            self.style.SUCCESS(
                f"Downloaded {count} posts from @{target_username} into {output_dir}"
            )
        )
        self.stdout.write("Next: python manage.py import_instagram")

    def _authenticate(self, loader, login_user, session_path, browser, cookie_file, fresh_login):
        from instaloader.__main__ import import_session
        from instaloader.exceptions import LoginException

        if browser:
            cookie_path = cookie_file or ""
            if browser == "chrome" and not cookie_path:
                detected = find_chrome_profile_with_instagram_session()
                if detected:
                    cookie_path = str(detected)
                    self.stdout.write(f"Found Instagram session in: {detected}")

            self.stdout.write(
                f"Loading Instagram session from {browser} browser cookies..."
            )
            if cookie_path:
                self.stdout.write(f"Using cookie file: {cookie_path}")
            else:
                self.stdout.write(
                    "Make sure you are logged into instagram.com in that browser first."
                )

            import_session(browser, loader, cookie_path or None)
            username = loader.test_login()
            if not username:
                raise LoginException(
                    f"No active Instagram session found in {browser}. "
                    "Log into instagram.com in that browser profile, then retry."
                )
            loader.save_session_to_file(str(session_path))
            self.stdout.write(self.style.SUCCESS(f"Logged in as {username} via browser cookies."))
            return True

        if session_path.exists() and not fresh_login:
            self.stdout.write(f"Loading saved session for {login_user}...")
            loader.load_session_from_file(login_user, str(session_path))
            if loader.test_login():
                return True
            self.stdout.write("Saved session expired.")

        password = getpass.getpass(f"Instagram password for {login_user}: ")
        loader.login(login_user, password)
        loader.save_session_to_file(str(session_path))
        self.stdout.write(self.style.SUCCESS(f"Session saved for {login_user}"))
        return True

    def _print_auth_help(self, exc, browser=""):
        message = str(exc)
        if browser:
            self.stderr.write(self.style.ERROR(f"Could not use {browser} cookies: {message}"))
        else:
            self.stderr.write(self.style.ERROR(f"Instagram login failed: {message}"))

        self.stderr.write("")
        self.stderr.write("Most common cause on Chrome: you are logged into a non-Default profile.")
        self.stderr.write("This machine already has Instagram cookies in Profile 1. Try:")
        self.stderr.write(
            '  python manage.py fetch_instagram --load-cookies chrome '
            '--cookie-file "$HOME/Library/Application Support/Google/Chrome/Profile 1/Cookies" --fresh-login'
        )
        self.stderr.write("")
        self.stderr.write("Or let the command auto-detect:")
        self.stderr.write("  python manage.py fetch_instagram --load-cookies chrome --fresh-login")
        self.stderr.write("")
        self.stderr.write("Fallback — official Instagram export (no login script needed):")
        self.stderr.write("  python manage.py import_instagram_export --source-dir /path/to/export")

        checkpoint_url = format_instagram_checkpoint_url(message)
        if checkpoint_url:
            self.stderr.write("")
            self.stderr.write("Checkpoint URL:")
            self.stderr.write(checkpoint_url)
