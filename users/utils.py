from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)

email_verification_token = EmailVerificationTokenGenerator()

def send_activation_email(user, current_site):
    subject = 'Activate your Phimart account'
    
    # Generate activation link
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    activation_link = f"{settings.DJOSER['EMAIL_FRONTEND_PROTOCOL']}://{settings.DJOSER['EMAIL_FRONTEND_DOMAIN']}/{settings.DJOSER['ACTIVATION_URL'].format(uid=uid, token=token)}"
    
    # Render email template
    message = render_to_string('users/activation_email.html', {
        'user': user,
        'activation_link': activation_link,
        'site_name': settings.DJOSER['EMAIL_FRONTEND_SITE_NAME']
    })
    
    # Send email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=False,
    )