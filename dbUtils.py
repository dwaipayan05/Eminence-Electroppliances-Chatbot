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
    userDataCheck = "SELECT * FROM eminenceusers WHERE phoneNumber = %s"

    cursor = connection.cursor(prepared=True)
    cursor.execute(userDataCheck, userData)
    result = cursor.fetchall()

    if result != []:
        userExists = True
    
    return userExists, result
    

def addUserToDB(phoneNumber, firstName, lastName, email, customerType, shippingAddress, billingAddress, GSTIN):

    phoneNumber = phoneNumber.split(":")[1]
    try:
        connection = mysql.connector.connect(**config)
    
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL: {}".format(error))
        return
    
    userData = (phoneNumber, firstName, lastName, email, customerType, shippingAddress, billingAddress, GSTIN)
    userDataAdd = "INSERT INTO eminenceusers (phoneNumber, firstName, lastName, emailID, customerType, shippingAddress, billingAddress, GSTIN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

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
    queryString = "SELECT phoneNumber FROM eminenceUsers"

    cursor = connection.cursor(buffered = True, dictionary = True)
    cursor.execute(queryString)

    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return result