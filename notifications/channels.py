import os
from typing import List
from django.core.mail import EmailMessage
#from twilio.rest import Client

def send_email_notification(subject: str, body: str, recipients: List[str], sender: str = 'System', 
                            cc: List[str] = None, bcc: List[str] = None, attachments: List[str] = None) -> None:
    """
    Sends an email notification to the specified recipients.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        recipients (List[str]): A list of email addresses to send the email to.
        sender (str, optional): The name of the sender. Defaults to 'System'.
        cc (List[str], optional): A list of email addresses to carbon copy the email to. Defaults to None.
        bcc (List[str], optional): A list of email addresses to blind carbon copy the email to. Defaults to None.
        attachments (List[str], optional): A list of file paths to attach to the email. Defaults to None.
    """
    email = EmailMessage(subject=subject, body=body, from_email=sender, to=recipients, cc=cc, bcc=bcc)
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment)
    email.send()

def send_sms_notification(subject: str, body: str, recipients: List[str], sender: str = 'System') -> None:
    """
    Sends an SMS notification to the specified recipients.

    Args:
        subject (str): The subject of the SMS. This argument is ignored.
        body (str): The body of the SMS.
        recipients (List[str]): A list of phone numbers to send the SMS to.
        sender (str, optional): The name of the sender. Defaults to 'System'.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    client = Client(account_sid, auth_token)
    for recipient in recipients:
        client.messages.create(to=recipient, from_=twilio_number, body=f'{sender}: {body}')
