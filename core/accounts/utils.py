from django.core.mail import EmailMessage
import threading
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()
    
        
class TemplateEmailThread(threading.Thread):

    def __init__(self,email,subject,msg_html):
        self.subject = subject
        self.msg_html=msg_html
        self.email = [email]
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
        self.subject,
        None,
        settings.DEFAULT_FROM_EMAIL,
        self.email,
        html_message=self.msg_html,
        fail_silently=True
    )
class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
    
    @staticmethod
    def send_templated_email(template_path,email,subject,data):
        msg_html = render_to_string(template_path, data)
        TemplateEmailThread(email,subject,msg_html).start()