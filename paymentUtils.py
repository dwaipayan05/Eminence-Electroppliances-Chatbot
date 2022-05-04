import os
import time
import razorpay
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

razorpayKeyID = os.getenv('RAZORPAY_KEY_ID')
razorypaySecretKey = os.getenv('RAZORYPAY_KEY_SECRET')
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

razorPayclient = razorpay.Client(auth=(razorpayKeyID, razorypaySecretKey))
twilioClient = Client(account_sid, auth_token)
# Things to Do:
# 1. Make Customer Details dynamic
# 2. Make Order Details : Order ID, Quantity, Amount, Currency

def sendFreeFormText(account_sid, auth_token, sender, recipient, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=sender,
        to=recipient
    )
    return message.sid

def genPaymentLink(itemType, amount):
    descriptionString = "Payment for " + itemType
    amount = int(amount) * 100

    response = razorPayclient.payment_link.create({
        "amount": amount,
        "currency": "INR",
        "accept_partial": True,
        "first_min_partial_amount": 100,
        "description": "{}".format(descriptionString),
        "customer": {
          "name": "XYZ",
          "email": "dwaipayanmunshi2001@gmail.com",
          "contact": "+91-9518777694"
        },
        "notify": {
          "sms": True,
          "email": True
        },
        "reminder_enable": True,
        "notes": {
          "ITEM Name": "{}".format(itemType)
        }
    })      

    return response['short_url'], response['id']

def paymentStatusCheck(paymentID,sender):
  retryCount = 10

  fromWhatsapp = os.getenv('FROM_WHATSAPP')
  while retryCount > 0:
    response = razorPayclient.payment_link.fetch(paymentID)
    status = response['status']

    print(status)
    if status == 'paid':
      amount = response['amount']
      message = "Your payment for amount Rs. {} is successful. For order updates and any queries, feel free to reach out to us.".format(
          amount/100)
      sendFreeFormText(account_sid, auth_token, fromWhatsapp, sender, message)
      return
    elif status == 'failed':
      amount = response['amount']
      message = "Your payment for amount Rs. {} has failed. Please Retry your Order".format(amount/100)
      sendFreeFormText(account_sid, auth_token, fromWhatsapp, sender, message)
      return
    
    retryCount -= 1
    time.sleep(20)
  
  razorPayclient.payment_link.cancel(paymentID)
  message = "Your payment for amount Rs. {} wasn't completed within the time frame. We're deactivating the Payment Link".format(amount/100)
  sendFreeFormText(account_sid, auth_token, fromWhatsapp, sender, message)
  return

if __name__ == "__main__":
    paymentStatusCheck("plink_JPwJAG25oZs1bH", "whatsapp:+919869368512")

