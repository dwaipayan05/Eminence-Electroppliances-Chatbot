import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import paymentUtils
import threading
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
            session['lastState'] = 'nu.enterName'
            response = "Hey ! We're happy to onboard you to the platform ! What's your first name ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'existingUserMenu':
            session['lastState'] = 'ex.orderItem'
            response = "Hey ! What would you like to order ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'nu.enterCategoryMenu':
            session['nu.clientCategory'] = 'Manufacturer'
            session['lastState'] = 'nu.enterShippingAddress'
            response = "Could you please enter the default Shipping Address ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'nu.enterBillingAddressQuestion':
            session['lastState'] = 'nu.enterBillingAddressYes'
            response = "Please enter your GST Number"
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

        elif session.get('lastMenu') == 'nu.enterCategoryMenu':
            session['nu.clientCategory'] = 'Wholeseller or Distributor'
            session['lastState'] = 'nu.enterShippingAddress'
            response = "Could you please enter the default Shipping Address ?"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastMenu') == 'nu.enterBillingAddressQuestion':
            session['lastState'] = 'nu.enterBillingAddressNo'
            response = "Could you please enter the default Billing Address ?"
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
            price = calculatePrice(session.get('orderItem'), session.get('orderQuantity'))
            paymentLink, paymentID = paymentUtils.genPaymentLink(session.get('orderItem'), price)
            response = "Hey ! Thank You for Placing the Order ! Here's the details of the Order : \n1. Item : {} \n2. Quantity : {} \n3. Delivery Address : {} \nThe total price of the order is *Rs. {}* , Pay the amount on the Razorpay Link Here {}. The payment link will be active only for 10 minutes".format(session.get('orderItem'), session.get('orderQuantity'), session.get('orderAddress'), price, paymentLink)
            session['lastState'] = 'ex.orderSummary'
            reply_text = MessagingResponse()
            reply_text.message(response)

            paymentThreadName = "paymentThread_" + str(paymentID)
            print(paymentID)
            paymentStatusThread = threading.Thread(
                name=paymentThreadName, target=paymentUtils.paymentStatusCheck, args=(paymentID, sender))
            paymentStatusThread.start()
            return str(reply_text)

        elif session.get('lastState') == 'nu.enterName':
            session['userFirstName'] = incoming_msg
            response = "Hey {} ! What's your last name ?".format(session.get('userFirstName'))
            session['lastState'] = 'nu.enterLastName'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'nu.enterLastName':
            session['userLastName'] = incoming_msg
            response = "Hey {} {} ! What's your email id ?".format(session.get('userFirstName'), session.get('userLastName'))
            session['lastState'] = 'nu.enterEmail'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'nu.enterEmail':
            session['userEmail'] = incoming_msg
            response = "Could you please tell us under what category do you fall under ? \n \n1. Manufacturer \n2. Wholeseller or Distributor \n3. Retailer \n4. Electrical Contractor \n5. Customer Please Enter the Category Number"
            session['lastState'] = 'nu.enterCategory'
            session['lastMenu'] = 'nu.enterCategoryMenu'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
           
        elif session.get('lastState') == 'nu.enterShippingAddress':
            session['userShippingAddress'] = incoming_msg
            response = "Do you want to keep your billing address same as your shipping address ? \n \n1. Yes \n2. No\nPlease Enter 1 or 2"
            session['lastMenu'] = 'nu.enterBillingAddressQuestion'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastState') == 'nu.enterBillingAddressNo':
            session['userBillingAddress'] = incoming_msg
            response = "Please enter your GST Number"
            session['lastState'] = 'nu.enterGSTNumber'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastState') == 'nu.enterBillingAddressYes':
            session['userBillingAddress'] = session.get('userShippingAddress')
            session['userGSTNumber'] = incoming_msg
            response = "Thank you {} {} ! You have successfully registered with us. You can now place orders for our existing products and connect with us anytime for your queries".format(
                session.get('userFirstName'), session.get('userLastName'))
            session['lastState'] = 'nu.ProfileSummary'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'nu.enterGSTNumber':
            session['userGSTNumber'] = incoming_msg
            response = "Thank you {} {} ! You have successfully registered with us. You can now place orders for our existing products and connect with us anytime for your queries".format(
                session.get('userFirstName'), session.get('userLastName'))
            session['lastState'] = 'nu.ProfileSummary'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
if __name__ == "__main__":
    app.run(debug=True)
