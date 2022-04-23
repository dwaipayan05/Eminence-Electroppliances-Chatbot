import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def hello():
    return 'Running Emminence Whatsapp Bot on /whatsapp !'


@app.route("/whatsapp", methods=['POST'])
def reply():
    sender = request.form.get('From')
    incoming_msg = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')

    if re.match(incoming_msg, "Hello", re.IGNORECASE) or \
        re.match(incoming_msg, "Hi", re.IGNORECASE) or \
        re.match(incoming_msg, "Hey", re.IGNORECASE):
        intro_response = "Welcome to Emminence ! Please tell me if you are an existing or new customer by typing *existing* or *new* !"
        reply_text = MessagingResponse()
        reply_text.message(intro_response)
        responded = True
        return str(reply_text)

    elif re.match(incoming_msg, "existing", re.IGNORECASE) or \
        re.match(incoming_msg, "existing customer", re.IGNORECASE):
        response = "What do you need help with ? \n 1. Place New Order \n 2. Order Updates \n 3. New Products \n 4. Other"
        session['typeOfCustomer'] = "Existing"
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
    
    elif re.match(incoming_msg, "new", re.IGNORECASE) or \
        re.match(incoming_msg, "new customer", re.IGNORECASE ):
        response = "We're not ready to face this Query"
        session['typeOfCustomer'] = "New"
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
    
    elif re.match(incoming_msg, "Place New Order", re.IGNORECASE) or \
         re.match(incoming_msg, "New Order", re.IGNORECASE):
        
        typeOfCustomer = session.get("typeOfCustomer")
        response = "Please Fill this Form to Place a New Order. Form Link. You're a {} customer".format(typeOfCustomer)
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)

    elif re.match(incoming_msg, "Order Updates", re.IGNORECASE) or \
        re.match(incoming_msg, "Updates on Order", re.IGNORECASE) or \
        re.match(incoming_msg, "Updates for Order", re.IGNORECASE):
        response = "Enter your Order ID to get updates on your Order. Please Type *Order ID : <order_id>* to get details on your Order ID"
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
    
    elif re.match(incoming_msg, "New Products", re.IGNORECASE) or \
        re.match(incoming_msg, "New Items", re.IGNORECASE):
        response = "Here are the New Product Items that we have recently launched. \n 1. Item 1 \n 2. Item 2 \n 3. Item 3"
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
    
    elif re.match(incoming_msg, "Other", re.IGNORECASE):
        response = "Hey, Please Enter your Custom Query below starting with the phrase Custom Query, we'll get back to you soon !"
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)

    elif "Custom Query" in incoming_msg:
        response = "Your Custom Query has been recorded ! We'll get back to you soon."
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
    
    elif re.match(incoming_msg, "Type of Customer", re.IGNORECASE):
        typeOfCustomer = session.get("typeOfCustomer")
        response = "You are {} customer".format(typeOfCustomer)
        reply_text = MessagingResponse()
        reply_text.message(response)
        responded = True
        return str(reply_text)
        
if __name__ == "__main__":
    app.run(debug=True)
