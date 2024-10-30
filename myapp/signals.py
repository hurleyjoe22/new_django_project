# signals.py in 'myapp' directory
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging
from datetime import datetime
import socket

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    # Email content for successful login
    subject = f"Successful Login Notification - {user.username}"
    message = f"""
    Hello,

    There was a successful login to your account.
    Details:
    Username: {user.username}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    IP Address: {request.META.get('REMOTE_ADDR')}
    Hostname: {socket.gethostname()}

    If this wasn't you, please secure your account immediately.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['cooroibah.greens.reports@gmail.com'],  # Replace with your email address to receive notifications
        fail_silently=False,
    )
    logger.info(f"Successful login by user: {user.username}")

@receiver(user_login_failed)
def login_failed(sender, credentials, request, **kwargs):
    # Email content for failed login
    subject = f"Failed Login Attempt"
    message = f"""
    Hello,

    There was a failed login attempt.
    Details:
    Username Attempted: {credentials.get('username')}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    IP Address: {request.META.get('REMOTE_ADDR')}
    Hostname: {socket.gethostname()}

    Please monitor any unusual activity.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['cooroibah.greens.reports@gmail.com'],  # Replace with your email address to receive notifications
        fail_silently=False,
    )
    logger.warning(f"Failed login attempt for username: {credentials.get('username')}")
