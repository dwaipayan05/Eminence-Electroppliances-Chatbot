import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

razorpayKeyID = os.getenv('RAZORPAY_KEY_ID')
razorypaySecretKey = os.getenv('RAZORYPAY_KEY_SECRET')

client = razorpay.Client(auth=(razorpayKeyID, razorypaySecretKey))

def genPaymentLink(itemType, amount):
    descriptionString = "Payment for " + itemType
    amount = int(amount) * 100

    response = client.payment_link.create({
        "amount": amount,
        "currency": "INR",
        "accept_partial": True,
        "first_min_partial_amount": 100,
        "description": "{}".format(descriptionString),
        "customer": {
          "name": "Gaurav Kumar",
          "email": "",
          "contact": "
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

    return response['short_url']

