import os
import smtplib
from dotenv import load_dotenv
from dbUtils import getUserName
load_dotenv()

senderEmailID = os.getenv('EMAIL_ID')
senderEmailPass = os.getenv('EMAIL_PASSWORD')

def sendEmail(phoneNumber, message):
    smtpServer = smtplib.SMTP('smtp.gmail.com', 587)
    smtpServer.starttls()
    smtpServer.login(senderEmailID, senderEmailPass)

    userName = getUserName(phoneNumber=phoneNumber)
    messageBody = '''Hey ! 

    Here's the custom query from {}
    Custom Query : {}

    From : {}
    '''.format(userName, message, phoneNumber)

    smtpServer.sendmail(senderEmailID, "dwaipayanmunshi.181mn010@nitk.edu.in", messageBody)
    smtpServer.quit()

if __name__ == "__main__":
    sendEmail("312321321", "dadadasd")