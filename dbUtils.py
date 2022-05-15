import os
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
    queryString = "SELECT firstName, lastName FROM userData WHERE phoneNumber=%s"

    cursor = connection.cursor(buffered = True, dictionary = True)
    cursor.execute(queryString, queryData)

    result = cursor.fetchall()

    userName = result[0]['firstName'] + " " + result[0]['lastName']
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

if __name__ == "__main__":
    print(getUserName("whatsapp:+919869368512"))