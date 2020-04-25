#Gold Price Tracker Everyday.
import sqlite3
import random
import numpy as np
from uuid import uuid4
import base64
import PyPDF2
import openpyxl as wb
import urllib.request,urllib.parse,urllib.error
from pdfminer.pdfdocument import PDFDocument
from matplotlib import pyplot as plt
import ssl
import os
import io
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
import sys
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage




from firebase_admin import credentials



account_sid='AC3c3a888a0163b34cefa087758fa5b687'
account_auth = "989d8ae13c77fce5abb67043a82dd403"

ctrx=ssl.create_default_context()
ctrx.check_hostname=False
ctrx.verify_mode=ssl.CERT_NONE

grams=1032.6/1000 # Denotes the number of grams that is present with you currently.
gold_prices=[]
print("Your Current Grams of Gold is %f"%grams)
global date



def get_price():

    '''This module is to get the price of gold online'''

    url='https://distributors.mmtcpamp.com/Downloads/PriceList.pdf'
    html=urllib.request.urlopen(url,context=ctrx).read()# Sending the request to the designated url
    memoryFile=io.BytesIO(html)
    reader = PyPDF2.PdfFileReader(memoryFile)

    contents = reader.getPage(0).extractText().split('\n')# Parsing the gold price
    gp=float(str(contents[298]).replace(',',''))# Today's gold price.
    gold_prices.append(gp)
    return gp  # Returns today's gold price.

def message():
    '''Prints the message that is required'''
    g_p=get_price()
    print("Selling at today's price will fetch Rs %f"%(g_p*grams))



def get_date_time():
    '''Function to get present date and time from appspot'''

    d=urllib.request.urlopen('http://just-the-time.appspot.com/')
    d1=d.read().split()
    date = str(d1[0]).replace('b','').replace('\'','')# Gets Date from appspot
    time = str(d1[1]).replace('b','').replace('\'','')
    return([date,time])#Returns today's date and time


def populate_database(today_date,today_price):
    # Used to update the database with the current price
     conn = sqlite3.connect('.\Price_tracker.db')
     conn.row_factory = lambda cursor, row: row[0]
     cur = conn.cursor()

     cur.execute('''INSERT INTO dp_tracker(Date,Price) VALUES (?,?) ''',(today_date,today_price,))

     dates_list=cur.execute('''SELECT Date FROM dp_tracker''').fetchall()
     price_list=cur.execute('''SELECT Price FROM dp_tracker''').fetchall()

     conn.commit()
     cur.close()


     return(dates_list,price_list)


def plot():

    ''' This function is used to plot the gold price scraped online'''
    gp=get_price()# Today's gold Price
    d=get_date_time()
    date=d[0]#Todya's date

    dp=populate_database(str(date),float(gp)) #Passing today's date and today's gold price and returns a list of all

    dx=dp[0] #A list of dates obtained from database
    dx_pos=np.arange(len(dx))
    py=dp[1]#A list of prices obtained from excel file
    fig = plt.figure()

    plt.bar(dx_pos, py, align='center', alpha=0.5,figure=fig)
    plt.xticks(dx_pos,dx,figure=fig)
    plt.xlabel("Dates",figure=fig)
    plt.ylabel("Price",figure=fig)
    plt.title("Gold Price Tracker",figure=fig)

    for i, v in enumerate(py):
        plt.text(dx_pos[i] - 0.15, v + 0.01, str(v),figure=fig)


    return fig



def upload2firebase():


    cred = credentials.Certificate(
        "./gold-price-tracker-caa9e-firebase-adminsdk-9e39d-72694e4d52.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'gold-price-tracker-caa9e.appspot.com'
    })

    img_src = "sample_image.png"
    bucket = storage.bucket()
    blob = bucket.blob(img_src)

    # Create new token
    new_token = uuid4()

    # Create new dictionary with the metadata
    metadata = {"firebaseStorageDownloadTokens": new_token}

    # Set metadata to blob
    blob.metadata = metadata

    # Upload file
    blob.upload_from_filename(filename="./Test.png", content_type='image/png')
    blob.make_public()
    return(blob.public_url)
        #
        #
        # bucket = storage.bucket()
        # image_data = ""
        # with open("./Test.png", "rb") as img_file:
        #     image_data = base64.b64encode(img_file.read())
        #
        # blob = bucket.blob('test.png')
        # blob.upload_from_string(image_data)
        # return blob.public_url



def send2Phone(gram,price,r):

    '''This function is to send the message to the phone'''
    client=Client(account_sid , account_auth)
    from_whats_app_number='whatsapp:+14155238886'
    to_what_app_number='whatsapp:+919731780732'
    a="Your current grams of gold is "+str(gram)+" g.\n Selling at today's price will fetch Rs "+str(gram*price)
    client.messages.create(body=a,media_url=r,from_=from_whats_app_number,to=to_what_app_number)





def loop():

    # t=get_date_time()
    # time=t[1].split(':')
    # count=0
    # if time[0] == '08' and time[1] == '57' and time[2]=='00' :
    #     count=1
    # else:
    #     count=0
    #
    # if count==1:
        message()
        q = plot()
        q.savefig('Test.png')
        r = upload2firebase()
        print(r)


        send2Phone(grams,gold_prices[-1],r)

while True:
    loop()
    sys.exit()
    break
