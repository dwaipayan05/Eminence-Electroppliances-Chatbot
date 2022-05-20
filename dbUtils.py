import os
import uuid
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

mysql_username = os.getenv('MYSQL_USERNAME')
mysql_password = os.getenv('MYSQL_PASSWORD')

config = {
    'user': mysql_username,
    'password': mysql_password,
    'host': 'localhost',
    'database': 'eminencedb',
    'raise_on_warnings': True
}

def toBinary(a):
  l,m=[],[]
  for i in a:
    l.append(ord(i))
  for i in l:
    m.append(int(bin(i)[2:]))
  return m

def checkUserExists(phoneNumber):
    phoneNumber = phoneNumber.split(":")[1]
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return False
    
    userExists = False

    userData = (phoneNumber,)
    userDataCheck = "SELECT * FROM userData WHERE phoneNumber = %s"

    cursor = connection.cursor(prepared=True)
    cursor.execute(userDataCheck, userData)
    result = cursor.fetchall()

    if result != []:
        userExists = True
    
    return userExists, result
    

def addUserToDB(phoneNumber, firstName, lastName, email, customerType, shippingAddress, billingAddress, GSTIN):
    userExists, result = checkUserExists(phoneNumber=phoneNumber)
    lastName = ""
    phoneNumber = phoneNumber.split(":")[1]
    try:
        connection = mysql.connector.connect(**config)
    
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    

    if userExists:
        userData = (firstName, lastName, email,
                    customerType, shippingAddress, billingAddress, GSTIN, phoneNumber)
        userDataAdd = "UPDATE userData SET firstName = %s, lastName = %s, emailID = %s, customerType = %s, shippingAddress = %s, billingAddress = %s, GSTIN = %s WHERE phoneNumber = %s"

    else:
        userData = (phoneNumber, firstName, lastName, email, customerType, shippingAddress, billingAddress, GSTIN)
        userDataAdd = "INSERT INTO userData (phoneNumber, firstName, lastName, emailID, customerType, shippingAddress, billingAddress, GSTIN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    connection.start_transaction()
    cursor = connection.cursor(prepared=True)

    try:
        cursor.execute(userDataAdd, userData)
    except mysql.connector.Error as error:
        print('Failed to add user to database: {}'.format(error))
        connection.rollback()
        cursor.close()
        return
    
    connection.commit()
    cursor.close()
    connection.close()
    return

def listUsers():
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryString = "SELECT phoneNumber FROM userData"

    cursor = connection.cursor(buffered = True, dictionary = True)
    cursor.execute(queryString)

    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return result

def getUserName(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])
    
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT firstName FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered = True, dictionary = True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    userName = result[0]['firstName']
    connection.commit()
    cursor.close()
    connection.close()

    return userName

def getProductList():
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryString = "SELECT productName FROM productsData"

    cursor = connection.cursor(buffered = True, dictionary = True)
    cursor.execute(queryString)

    result = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return result


def getGSTIN(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])

    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT GSTIN FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    GSTIN = result[0]['GSTIN']
    connection.commit()
    cursor.close()
    connection.close()

    return GSTIN

def getBillingAddress(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])

    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT billingAddress FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    billingAddress = result[0]['billingAddress']
    connection.commit()
    cursor.close()
    connection.close()

    return billingAddress

def getShippingAddress(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])

    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT shippingAddress FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    shippingAddress = result[0]['shippingAddress']
    connection.commit()
    cursor.close()
    connection.close()

    return shippingAddress


def updateGSTNumber(sender, GSTNumber):
    phoneNumber = str(sender.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (GSTNumber, phoneNumber)
    queryString = "UPDATE userData SET GSTIN = %s WHERE phoneNumber = %s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()

def updateBillingAddress(sender, billingAddress):
    phoneNumber = str(sender.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (billingAddress, phoneNumber)
    queryString = "UPDATE userData SET billingAddress = %s WHERE phoneNumber = %s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()

def updateShippingAddress(sender, shippingAddress):
    phoneNumber = str(sender.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (shippingAddress, phoneNumber)
    queryString = "UPDATE userData SET shippingAddress = %s WHERE phoneNumber = %s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()

def getUserType(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])

    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT customerType FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    customerType = result[0]['customerType']
    connection.commit()
    cursor.close()
    connection.close()

    return customerType

def getMinimumOrderQuantity(phoneNumber):
    customerType = getUserType(phoneNumber)
    phoneNumber = str(phoneNumber.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (customerType,)
    queryString = "SELECT minOrderQuantity FROM pricingmodel WHERE category=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    minOrderQuantity = result[0]['minOrderQuantity']
    connection.commit()
    cursor.close()
    connection.close()

    return minOrderQuantity

def getOrderPrice(phoneNumber, productOrdered, quantity):
    customerType = getUserType(phoneNumber)
    phoneNumber = str(phoneNumber.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (customerType,)
    queryString = "SELECT sellingPrice FROM pricingmodel WHERE category=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    price = int(result[0]['sellingPrice'])
    connection.commit()
    cursor.close()
    connection.close()

    return price * quantity

def getProductID(product):
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (product,)
    queryString = "SELECT productID FROM productsdata WHERE productName=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    productID = result[0]['productID']
    connection.commit()
    cursor.close()
    connection.close()

    return productID

def getSellingPrice(customerType):
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (customerType,)
    queryString = "SELECT sellingPrice FROM pricingmodel WHERE category=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    sellingPrice = int(result[0]['sellingPrice'])
    connection.commit()
    cursor.close()
    connection.close()

    return sellingPrice

def addOrderToDB(phoneNumber, productOrdered, quantity, price):
    productID = getProductID(productOrdered)
    customerType = getUserType(phoneNumber)
    sellingPrice = getSellingPrice(customerType)
    phoneNumber = str(phoneNumber.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (phoneNumber, quantity, price, sellingPrice)
    queryString = "INSERT INTO orderdata (orderID, userID, orderDate, productID, quantity, amount, sellingPrice) VALUES (UUID_TO_BIN(UUID()), %s, NOW(), UUID_TO_BIN(UUID()), %s, %s, %s)"
    print(queryString)
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()
    
    return "Hello"

def getEmail(phoneNumber):
    phoneNumber = str(phoneNumber.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return

    connection.start_transaction()
    queryData = (phoneNumber,)
    queryString = "SELECT emailID FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    emailID = result[0]['emailID']
    connection.commit()
    cursor.close()
    connection.close()

    return emailID

def addPaymentsToDB(paymentID, userID, amount):
    userID = str(userID.split(":")[1])
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (paymentID, userID, amount, "Created")
    queryString = "INSERT INTO paymentdata (paymentID, razorpayID, userID, amount, paymentDate, status) VALUES (UUID_TO_BIN(UUID()), %s, %s, %s, NOW(), %s)"
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()

def updatePaymentStatus(paymentID, status):
    try:
        connection = mysql.connector.connect(**config)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    connection.start_transaction()
    queryData = (status, paymentID)
    queryString = "UPDATE paymentdata SET status=%s WHERE razorpayID=%s"
    cursor = connection.cursor(buffered=True, dictionary=True)
    cursor.execute(queryString, queryData)

    connection.commit()
    cursor.close()
    connection.close()
if __name__ == "__main__":
    print(getUserName("whatsapp:+919869368512"))