from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(user):
    subject = 'Verify your email address'
    html_message = render_to_string('email_verification.html', {'user': user})
    plain_message = strip_tags(html_message)
    from_email = 'your_email@example.com'
    to = user.email
    
    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
 
