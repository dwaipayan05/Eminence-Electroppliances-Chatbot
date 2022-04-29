import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import paymentUtils
import random


def random_number(min, max):
    return random.randint(min, max)

def calculatePrice(item, quantity):

    quantity = (int(quantity))
    if item == "Item 1":
        return quantity * 20
    
    if item == "Item 2":
        return quantity * 25
    
    return quantity * 10

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

        reResponse = re.match(incoming_msg, "Hello", re.IGNORECASE)
        introResponse = "Welcome to Emminence ! I am your personal assistant. I can help you with your Queries. Can you please confirm if you are a new user or an existing user ? \n\n 1. New User \n 2. Existing User \n \n Type 1 or 2 to confirm."
        reply_text = MessagingResponse()
        reply_text.message(introResponse)
        session['lastState'] = 'welcomeText'
        session['lastMenu'] = 'welcomeMenu'
        return str(reply_text)
    

    elif re.match(incoming_msg, "1", re.IGNORECASE):
        if session.get('lastMenu') == 'welcomeMenu':
            session['userType'] = 'newUser'
            session['lastMenu'] = 'newUserMenu'
            session['lastState'] = 'nu.enterName.newUser'
            response = "Hey ! We're happy to onboard you to the platform ! What's your name ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'existingUserMenu':
            session['lastState'] = 'ex.orderItem'
            response = "Hey ! What would you like to order ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        else:
            response = "Hey ! It Seems like you selected an invalid option. Please type Reset to start again."
    elif re.match(incoming_msg, "2", re.IGNORECASE):
        if session.get('lastMenu') == 'welcomeMenu':
            session['userType'] = 'existingUser'
            session['lastMenu'] = 'existingUserMenu'
            session['lastState'] = 'existingUserMenuDisplay'
            response = "Hey ! What do you need help with ? \n \n1. Place a New Order\n2. Updates on Order\n3. Catalogue\n4. Other "
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        else:
            response = "Hey ! It Seems like you selected an invalid option. Please type Reset to start again."
   
    elif re.match(incoming_msg, "Session Variables Check", re.IGNORECASE):
        lastMenu = session.get('lastMenu')
        lastState = session.get('lastState')
        userType = session.get('userType')
        response = "Current Session Variable Values : \n \n1. lastState : {} \n2. lastMenu : {} \n3. userType : {}".format(lastState, lastMenu, userType)
        reply_text = MessagingResponse()
        reply_text.message(response)
        return str(reply_text)
    
    else :
        if session.get('lastState') == '':
            response = "Sorry, I didn't understand that. Please type a Hi or Hello to start the conversation."
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastState') == 'ex.orderItem':
            session['orderItem'] = incoming_msg
            response = "Could you please enter the Quantity of the Order that you are placing ?"
            session['lastState'] = 'ex.orderQuantity'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderQuantity':
            session['orderQuantity'] = incoming_msg
            response = "Could you please enter the Delivery Address of the Order that you are placing ?"
            session['lastState'] = 'ex.orderAddress'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderAddress':
            session['orderAddress'] = incoming_msg
            response = "Could you please enter the expected Delivery Date of the Order that you are placing ?"
            session['lastState'] = 'ex.orderDeliveryDate'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderDeliveryDate':
            session['orderDeliveryDate'] = incoming_msg
            response = "Could you please enter the expected Delivery Time of the Order that you are placing ?"
            session['lastState'] = 'ex.orderDeliveryTime'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderDeliveryTime':
            session['orderDeliveryTime'] = incoming_msg

            price = calculatePrice(session.get('orderItem'), session.get('orderQuantity'))
            paymentLink = paymentUtils.genPaymentLink(session.get('orderItem'), price)
            response = "Hey ! Thank You for Placing the Order ! Here's the details of the Order : \n1. Item : {} \n2. Quantity : {} \n3. Delivery Address : {} \n4. Delivery Date : {} \n5. Delivery Time : {} \nThe total price of the order is *Rs. {}* , Pay the amount on the Razorpay Link Here {}".format(session.get('orderItem'), session.get('orderQuantity'), session.get('orderAddress'), session.get('orderDeliveryDate'), session.get('orderDeliveryTime'), price, paymentLink)
            session['lastState'] = 'ex.orderSummary'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        
if __name__ == "__main__":
    app.run(debug=True)
