#Random Number Generator
import random
import os
from twilio.rest import Client

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilioClient = Client(account_sid, auth_token)
def sendFreeFormText(account_sid, auth_token, sender, recipient, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=sender,
        to=recipient
    )
    return message.sid

def random_number(min, max):
    return random.randint(min, max)