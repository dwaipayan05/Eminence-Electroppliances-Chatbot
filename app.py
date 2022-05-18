import os
import re
from socket import MsgFlag
import requests
import threading
import random
import dbUtils
import emailUtils
import paymentUtils
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, session


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
    isUserPresent, userData = dbUtils.checkUserExists(sender)
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
    

    elif incoming_msg == "Menu" or incoming_msg == "menu" :
        isUserPresent, userData = dbUtils.checkUserExists(sender)
        if isUserPresent:
             session['lastMenu'] = 'existingUserMenu'
             session['lastState'] = 'existingUserMenuDisplay'
             userName = userData[0][1] + " " + userData[0][2]
             response = "Hey {} ! What do you need help with ? \n \n1. Place a New Order\n2. Updates on Order\n3. Catalogue\n4. Other \n\nYou can always type _Menu_ to revisit this section.".format(
                 userName)
             reply_text = MessagingResponse()
             reply_text.message(response)
             return str(reply_text)
        else:
             response = "Hey ! It seems like you are not registered with us. Could you please enter your First Name ?"
             session['lastState'] = 'nu.enterName'
             reply_text = MessagingResponse()
             reply_text.message(response)
             return str(reply_text)
    
    elif incoming_msg.lower() == "contact":
        response = "Please feel free to contact us at +91-8989898989 or email us at sample.email@gmail.com in case you need support with any of our services."
        reply_text = MessagingResponse()
        reply_text.message(response)
        return str(reply_text)

    elif incoming_msg.lower() == "order" and isUserPresent:
        session['lastState'] = 'ex.orderItem'
        session['lastMenu'] = 'ex.productList'
        productList = dbUtils.getProductList()
        response = "Hey ! What would you like to order ? \n"
        idx = 1
        for product in productList:
             response += "\n" + str(idx) + ". " + \
                 str(product['productName'])
             idx += 1
        response += "\n\nType the Number of the Item you want to Order"
        reply_text = MessagingResponse()
        reply_text.message(response)
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
            session['lastMenu'] = 'ex.productList'
            productList = dbUtils.getProductList()
            response = "Hey ! What would you like to order ? \n"
            idx = 1
            for product in productList:
                response += "\n" + str(idx) + ". " + str(product['productName'])
                idx += 1
            response += "\n\nType the Number of the Item you want to Order"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'nu.enterCategoryMenu':
            session['nu.clientCategory'] = 'Manufacturer'
            session['lastState'] = 'nu.enterBillingAddress'
            response = "Could you please enter the default Billing Address ? \n\n\nType _NA_ in case you don't want to provide the same"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
    
        
        elif session.get('lastMenu') == 'ex.productList':
            session['productOrdered'] = "Roma 2.1"
            session['lastState'] = "ex.orderQuantity"
            minOrderQuantity = dbUtils.getMinimumOrderQuantity(sender)
            response = "Please Enter the Quantity you would like to Order. The minimum order quantity is {}".format(str(minOrderQuantity))
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'ex.orderGSTNumberMenu':
            response = "Please enter your GST Number"
            session['lastState'] = 'ex.orderGSTNumberEnter'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'ex.orderShippingAddressMenu':
            session['lastState'] = 'ex.orderSummary'
            billingAddress = dbUtils.getBillingAddress(sender)
            dbUtils.updateShippingAddress(sender, billingAddress)

            productOrdered = session.get('productOrdered')
            orderQuantity = int(session.get('orderQuantity'))
            billingAddress = dbUtils.getBillingAddress(sender)
            shippingAddress = dbUtils.getShippingAddress(sender)
            price = dbUtils.getOrderPrice(
                sender, productOrdered, orderQuantity)

            uniqueOrderID = dbUtils.addOrderToDB(
                sender, productOrdered, orderQuantity, price)
            paymentLink, paymentID = paymentUtils.genPaymentLink(
                sender, productOrdered, price)

            response = "Hey ! Thank you for Placing the Order. Your Order Summary is as follows : \n\nProduct Ordered : {} \nQuantity Ordered : {} \nBilling Address : {} \nShipping Address : {}\n\nThe total amount to be paid is *Rs. {}*. Please make the payment through the given Payment Link : {}. The Payment Link will expire in *5 Mins*".format(
                productOrdered, orderQuantity, billingAddress, shippingAddress, price, paymentLink)

            paymentThreadName = "paymentThread_" + str(paymentID)
            paymentStatusThread = threading.Thread(
                name=paymentThreadName, target=paymentUtils.paymentStatusCheck, args=(paymentID, sender))
            paymentStatusThread.start()
            dbUtils.addPaymentsToDB(paymentID, sender, price)
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        else:
            response = "Hey ! It Seems like you selected an invalid option. Please type Reset to start again."

    elif re.match(incoming_msg, "2", re.IGNORECASE):
        if session.get('lastMenu') == 'welcomeMenu':
            session['userType'] = 'existingUser'
            session['lastState'] = 'existingUserCheck'

            isUserPresent, userData = dbUtils.checkUserExists(sender)
            if isUserPresent:
                session['lastMenu'] = 'existingUserMenu'
                session['lastState'] = 'existingUserMenuDisplay'
                userName = userData[0][1] + " " + userData[0][2]
                response = "Hey {} ! What do you need help with ? \n \n1. Place a New Order\n2. Updates on Order\n3. Catalogue\n4. Other ".format(userName)
                reply_text = MessagingResponse()
                reply_text.message(response)
                return str(reply_text)

            else:
                response = "Hey ! It seems like you are not registered with us. Could you please enter your First Name ?"
                session['lastState'] = 'nu.enterName'
                reply_text = MessagingResponse()
                reply_text.message(response)
                return str(reply_text)

        elif session.get('lastMenu') == 'nu.enterCategoryMenu':
            session['nu.clientCategory'] = 'Distributor/Wholeseller'
            session['lastState'] = 'nu.enterBillingAddress'
            response = "Could you please enter the default Billing Address ? \n\n\nType _NA_ in case you don't want to provide the same"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastMenu') == 'ex.productList':
            session['productOrdered'] = "Roma 2.4"
            session['lastState'] = "ex.orderQuantity"
            minOrderQuantity = dbUtils.getMinimumOrderQuantity(sender)
            response = "Please Enter the Quantity you would like to Order. The minimum order quantity for you is {}".format(
                str(minOrderQuantity))
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'ex.orderGSTNumberMenu':
            BillingAddress = dbUtils.getBillingAddress(sender)
            if BillingAddress == "NA":
                    response = "Please Enter your Billing Address Below"
                    session['lastState'] = 'ex.orderEnterBillingAddress'
            else:
                ShippingAddress = dbUtils.getBillingAddress(sender)
                session['lastState'] = 'ex.orderShippingAddressConfirm'
                session['lastMenu'] = 'ex.orderShippingAddressMenu'
                response = "Please Confirm your Shipping Address Below \n" + \
                str(ShippingAddress) + "\n\n 1. Yes \n 2. No \n\n Type 1 or 2 to confirm."
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'ex.orderShippingAddressMenu':
            response = "Please Enter your Shipping Address Below"
            session['lastState'] = 'ex.orderEnterShippingAddress'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        else:
            response = "Hey ! It Seems like you selected an invalid option. Please type Reset to start again."
    
    elif re.match(incoming_msg, "3", re.IGNORECASE):
        if session.get('lastMenu') == 'existingUserMenu':
            session['lastState'] = 'ex.CatalogueDisplay'
            response = "Hey ! Please Find our Catalogue in the image attached above v. Feel free to reach out to us in case of any queries"
            reply = MessagingResponse()
            msg = reply.message()
            msg.body(response)
            msg.media(
                'https://images.unsplash.com/photo-1627395410076-15da6119fff9?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=722&q=80')
            return str(reply)
        
        elif session.get('lastMenu') == 'nu.enterCategoryMenu':
            session['nu.clientCategory'] = 'Retailer'
            session['lastState'] = 'nu.enterBillingAddress'
            response = "Could you please enter the default Billing Address ? \n\n\nType _NA_ in case you don't want to provide the same"
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastMenu') == 'ex.productList':
            session['productOrdered'] = "Roma Double"
            session['lastState'] = "ex.orderQuantity"
            minOrderQuantity = dbUtils.getMinimumOrderQuantity(sender)
            response = "Please Enter the Quantity you would like to Order. The minimum order quantity for you is {}".format(
                str(minOrderQuantity))
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
    elif re.match(incoming_msg, "4", re.IGNORECASE):
        if session.get('lastMenu') == 'existingUserMenu':
            session['lastState'] = 'ex.CustomQuery'
            response = "Please Enter your Custom Query below (Max Limit : 1600 Characters). We'll reach out to you soon."
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastMenu') == 'ex.productList':
            session['productOrdered'] = "Buddy"
            session['lastState'] = "ex.orderQuantity"
            minOrderQuantity = dbUtils.getMinimumOrderQuantity(sender)
            response = "Please Enter the Quantity you would like to Order. The minimum order quantity for you is {}".format(
                str(minOrderQuantity))
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

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
            response = "Could you please tell us under what category do you fall under ? \n \n1. Manufacturer \n2. Distributor/Wholeseller \n3. Retailer \n\nPlease Enter the Category Number"
            session['lastState'] = 'nu.enterCategory'
            session['lastMenu'] = 'nu.enterCategoryMenu'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
           
        elif session.get('lastState') == 'nu.enterBillingAddress':
            session['userBillingAddress'] = incoming_msg
            response = "Please enter your GST Number.\n\n\nType _NA_ in case you don't want to provide the same"
            session['lastState'] = 'nu.enterGSTNumber'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)

        elif session.get('lastState') == 'nu.enterGSTNumber':
            session['userShippingAddress'] = session.get('userBillingAddress')
            session['userGSTNumber'] = incoming_msg
            dbUtils.addUserToDB(sender, session.get('userFirstName'), session.get('userLastName'), session.get(
                'userEmail'), session.get('nu.clientCategory'), session.get('userShippingAddress'), session.get('userBillingAddress'), session.get('userGSTNumber'))
            response = "Thank you {} {} ! You have successfully registered with us. Please type *Menu* to explore our services further".format(
                session.get('userFirstName'), session.get('userLastName'))
            session['lastState'] = 'nu.ProfileSummary'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.CustomQuery':
            emailThreadName = "emailThread_" + str(sender)
            emailThread = threading.Thread(
                name=emailThreadName, target=emailUtils.sendEmail, args=(sender, incoming_msg))
            emailThread.start()
            response = "Your response has been recorded. We'll be reaching out to you soon with our response"
            session['lastState'] = 'ex.CustomQueryRecorded'
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderQuantity':
            session['orderQuantity'] = incoming_msg
            minOrderQuantity = dbUtils.getMinimumOrderQuantity(sender)
            intMinOrder = int(incoming_msg)

            if intMinOrder >= minOrderQuantity:
                GSTIN = dbUtils.getGSTIN(sender)
                if GSTIN == "NA":
                    response = "Hey ! We don't have your GST Number. Do you have GST Number ? \n\n 1. Yes \n 2. No \n\n Type 1 or 2 to confirm."
                    session['lastMenu'] = 'ex.orderGSTNumberMenu'
                    session['lastState'] = 'ex.orderGSTNumberConfirm'
                else:
                    BillingAddress = dbUtils.getBillingAddress(sender)
                    if BillingAddress == "NA":
                        response = "Please Enter your Billing Address Below"
                        session['lastState'] = 'ex.orderEnterBillingAddress'
                    else:
                        ShippingAddress = dbUtils.getBillingAddress(sender)
                        session['lastState'] = 'ex.orderShippingAddressConfirm'
                        session['lastMenu'] = 'ex.orderShippingAddressMenu'
                        response = "Please Confirm your Shipping Address Below \n" + str(ShippingAddress) + "\n\n 1. Yes \n 2. No \n\n Type 1 or 2 to confirm."
            else:
                response = "The Quantity entered is less than the Minimum Order Quantity, Please enter a Quantity greater than or equal to " + str(minOrderQuantity)
                session['lastState'] = 'ex.orderQuantity'
            
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderGSTNumberEnter':
            session['orderGSTNumber'] = incoming_msg
            dbUtils.updateGSTNumber(sender, session.get('orderGSTNumber'))
            BillingAddress = dbUtils.getBillingAddress(sender)
            if BillingAddress == "NA":
                    response = "Please Enter your Billing Address Below"
                    session['lastState'] = 'ex.orderEnterBillingAddress'
            else:
                ShippingAddress = dbUtils.getBillingAddress(sender)
                session['lastState'] = 'ex.orderShippingAddressConfirm'
                session['lastMenu'] = 'ex.orderShippingAddressMenu'
                response = "Please Confirm your Shipping Address Below \n" + \
                str(ShippingAddress) + "\n\n 1. Yes \n 2. No \n\n Type 1 or 2 to confirm."
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderEnterBillingAddress':
            session['orderBillingAddress'] = incoming_msg
            dbUtils.updateBillingAddress(sender, session.get('orderBillingAddress'))
            ShippingAddress = dbUtils.getBillingAddress(sender)
            session['lastMenu'] = 'ex.orderShippingAddressMenu'
            response = "Please Confirm your Shipping Address Below \n" + \
                str(ShippingAddress) + "\n\n 1. Yes \n 2. No \n\n Type 1 or 2 to confirm."
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
        
        elif session.get('lastState') == 'ex.orderEnterShippingAddress':
            session['orderShippingAddress'] = incoming_msg
            dbUtils.updateShippingAddress(
                sender, session.get('orderShippingAddress'))
            session['lastState'] = 'ex.orderSummary'

            productOrdered = session.get('productOrdered')
            orderQuantity = int(session.get('orderQuantity'))
            billingAddress = session.get('orderBillingAddress')
            shippingAddress = session.get('orderShippingAddress')
            price = dbUtils.getOrderPrice(sender, productOrdered, orderQuantity)

            uniqueOrderID = dbUtils.addOrderToDB(
                sender, productOrdered, orderQuantity, price)
            paymentLink, paymentID = paymentUtils.genPaymentLink(
                sender, productOrdered, price)
            
            response = "Hey ! Thank you for Placing the Order. Your Order Summary is as follows : \n\nProduct Ordered : {} \nQuantity Ordered : {} \nBilling Address : {} \nShipping Address : {}\n\nThe total amount to be paid is *Rs. {}*. Please make the payment through the given Payment Link : {}. The Payment Link will expire in *5 Mins*".format(
                productOrdered, orderQuantity, billingAddress, shippingAddress, price, paymentLink)
            
            paymentThreadName = "paymentThread_" + str(paymentID)
            paymentStatusThread = threading.Thread(
                name=paymentThreadName, target=paymentUtils.paymentStatusCheck, args=(paymentID, sender))
            paymentStatusThread.start()
            dbUtils.addPaymentsToDB(paymentID, sender, price)
            reply_text = MessagingResponse()
            reply_text.message(response)
            return str(reply_text)
             
if __name__ == "__main__":
    app.run(debug=True)
