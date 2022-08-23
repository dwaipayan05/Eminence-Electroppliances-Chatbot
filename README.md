## Documentation

### app.py

A Flask App running on 5000 port is deployed through this file. Majority of the functionality is on the `/whatsapp` route. 

#### General Workflow of Chatbot
- Before any message is processed the following details are processed 
```Python
    sender = request.form.get('From')
    incoming_msg = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    isUserPresent, userData = dbUtils.checkUserExists(sender)
```
- The `sender` contains details about the message sender. 
- The `incoming_msg` contains details about the incoming message body
- The `media_url` contains details about any media being sent across by the sender.
- The `isUserPresent, userData` contains details about the user from the backend Database.
- Once the following conditions are parsed, there are different `if else` conditions based on the `incoming_msg` conditions.
- There are different positions in the dialog flow where, options like `1` , `2` are chosen from a options menu.
- For this, a state needs to be maintained in the chat session.
- To carry that out, we have used `Flask Session Variables`.
- The following Session Variables are being used throughout the application recurringly :
```
  session['lastMenu'] : Stores the Last Menu the Chat Bot has Displayed
  session['lastState'] : Store the Last Action the Chat Bot has carried out
```
- There are more session variables used like billingAddress, shippingAddress, however those are stored in the database once the user is registered.
- Based on the option chosen `1` , `2` there are `if else` conditions to parse the option number based on the `lastMenu`.
- `Tip` : To Optimize this Approach and have Complete Dependency on lastMenu session variable, multiple session variables can be introduced to have more granular control over the session state.
- Various different functions are called inside the flow, mostly to write/read to the database.
- It's *important* that the flask app returns a response for any kind of incoming message. In case the flow breaks anywhere, the app will crash. So all edge cases needs to be handled.
- Any response / function call from inside the flow that takes more than 10 seconds will lead to a HTTPNoResponse basically cause of timeout.

### dbUtils.py

Basic Functions for reading / writing to the database are encompassed in this file

```
checkUserExists: Checks if a User with a given phoneNumber exists in the database or not.
addUserToDB : Adds a User to the Database with given details
listUsers: Lists All Users in the User Database
getUserName : Gives userName for a User with a Particular Phone Number
getProductList : Lists all Products in the Database
getGSTIN : Get GSTIN Number of a Particular User, given the phone Number
getBillingAddress : Get Billing Address of a Particular User, given the phone Number
getShippingAddress : Get Shipping Address of a Particular User, given the phone Number
updateGSTNumber : Update the GST Number of a Particular User, given the phone Number
updateBillingAddress : Update the Billing Address of a Particular User, given the phone Number
updateShippingAddress : Update the Shipping Address of a Particular User, given the phone Number
getUserType: Get the Type of the User, given the phone Number
getMinimumOrderQuantity: Get the Minimum Order Quantity, given the phone Number
getOrderPrice : Calculate the total Order Price, given the Product Ordered and the Quantity
getProductID : Get the Product ID, given the Product Name
getSeliingPrice : Get the Selling Price, given the Customer Type
addOrderToDB : Add Order Metadata to the Database, given the Order Details
getEmail : Get Use Email, given the phone Number
addPaymentsToDB : Add Payment Metadata to the Database, give the Payment Details
updatePaymentStatus : Update Payment Status, given the payment Status
```

### emailUTILs.py

Sends an Email to the a Required Email Addres. The Email Body is markdown supported. Gmail Credentials need to be stored in the .env file for the SMTP Server to use. 

### paymentUTILs.py

Carries out the following functionalities
- [genPaymentLink] Generates a Razorpay Payment Link given the Order Details. [Razorpay Documentation](https://razorpay.com/docs/api/payments/payment-links/#create-payment-link)
- [paymentStatusCheck] Check Payment Status, Every 20 Seconds and Send Text to Payee. Carries out only 10 retries. This process is launched from `app.py`. However, there would be a timeout in case it is spawned with the main process ID. Therefore, the payment check status is spawned on a different thread using the python threading library.

### utils.py

Carries out the following functionalities 
- [sendFreeFormText] Sends a Free Text to a particular sender registered under Twilio. This message is sent in free form. It's a standalone text, doesn't take into consideration whether the user is currently part of a session or not. 

### broadcast.py

Sends a broadcast message using the sendFreeFormText function to all the users in the DB, given the message. To send the message to users who have enabled broadcasting, the listUsers functions can be modified to list users with broadcast enabled, so that it will send message to users with broadcast boolean enabled. 

### Twilio Setup
- Setup a Twilio Sandbox for Whatsapp Account [If Not a Premium Twilio Acc]
- Add Incoming Message URL as the `/whatsapp` route of the Flask App [URL would be Either Deployed App URL or Local Host tunneled through ngrok]. The URL Should be Publicly Accessible
- Refer this documentation for [Twilio Setup](https://www.twilio.com/docs/whatsapp/sandbox)

### Installation Steps
- Install mysql Server + Client
- Setup the Databases from the `eminenceDB.sql` File
- Configure the Database Credentials in a `.env` File. Host is Considered to be Localhost, Can be changed in `dbUtils.py`
```
MYSQL_USERNAME=<username>
MYSQL_PASSWORD=<password>
```
- Install all Required Python Libraries using `pip`
- Use [ngrok](https://ngrok.com/) to tunnel localhost to a Public IP
- Run `python app.py` to start up the Flask App
- Run `ngrok http 5000` to get a Public IP of Localhost
- Add the Public URL to the Twilio Incoming Webhook
- Chat App is Ready

