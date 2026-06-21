import os

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError:  # pragma: no cover - sendgrid optional at dev time
    SendGridAPIClient = None
    Mail = None

FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@swingcheck.app")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://swingcheck.app")


def send_magic_link_email(to_email: str, token: str) -> bool:
    """Send a magic-link sign-in email via SendGrid.

    Returns True if sent. In dev (no SENDGRID_API_KEY), logs the link and
    returns False so the flow stays usable without external credentials.
    """
    link = f"{APP_BASE_URL}/auth/verify?email={to_email}&token={token}"
    api_key = os.getenv("SENDGRID_API_KEY")

    if not api_key or SendGridAPIClient is None:
        print(f"[email_service] (dev) magic link for {to_email}: {link}")
        return False

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="Your SwingCheck sign-in link",
        html_content=(
            f"<p>Tap the link below to sign in to SwingCheck:</p>"
            f"<p><a href=\"{link}\">Sign in</a></p>"
            f"<p>This link expires in 24 hours.</p>"
        ),
    )
    try:
        SendGridAPIClient(api_key).send(message)
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[email_service] failed to send magic link: {exc}")
        return False
