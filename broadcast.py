import os
import sys
import dbUtils
from util import sendFreeFormText
from dotenv import load_dotenv

load_dotenv()

fromWhatsapp = os.getenv('FROM_WHATSAPP')
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

def sendBroadcast(message):
    userPhoneNumber = dbUtils.listUsers()
    for user in userPhoneNumber:
        phoneNumber = "whatsapp:" + user['phoneNumber']
        sendFreeFormText(account_sid=account_sid,auth_token=auth_token, sender=fromWhatsapp, recipient=phoneNumber, message=message)  
if __name__ == "__main__":
    message = sys.argv[1]
    sendBroadcast(message)