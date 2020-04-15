#Gold Price Tracker Everyday.
import numpy as np

import datetime
import PyPDF2
import urllib.request,urllib.parse,urllib.error
from pdfminer.pdfdocument import PDFDocument
from matplotlib import pyplot as plt
import ssl
import os
import io
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant

account_sid='xxxx'
account_auth = "xxxxx"

ctrx=ssl.create_default_context()
ctrx.check_hostname=False
ctrx.verify_mode=ssl.CERT_NONE

grams=1032.6/1000 # Denotes the number of grams that is present with you currently.
gold_prices=[]
print("Your Current Grams of Gold is %f"%grams)



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
    return([date,time])#Returns todays date and time


def plot():

    ''' This function is used to plot the gold price scraped online'''
    gp=get_price()
    d=get_date_time()
    date=d[0]
    d_p={}
    d_p[date]=gp
    dx=list(d_p.keys())
    dx_pos=np.arange(len(dx))
    py=list(d_p.values())
    fig = plt.figure()

    plt.bar(dx_pos, py, align='center', alpha=0.5,figure=fig)
    plt.xticks(dx_pos,dx,figure=fig)
    plt.xlabel("Dates",figure=fig)
    plt.ylabel("Price",figure=fig)
    plt.title("Gold Price Tracker",figure=fig)

    for i, v in enumerate(py):
        plt.text(dx_pos[i] - 0.15, v + 0.01, str(v),figure=fig)


    return fig





def send2Phone(gram,price):

    '''This function is to send the message to the phone'''
    client=Client(account_sid , account_auth)
    from_whats_app_number='whatsapp:+14155238886'
    to_what_app_number='whatsapp:+91xxxxxxxxxx'
    a="Your current grams of gold is "+str(gram)+" g.\n Selling at today's price will fetch Rs "+str(gram*price)
    client.messages.create(body=a,from_=from_whats_app_number,to=to_what_app_number)



def loop():

    t=get_date_time()
    time=t[1].split(':')
    count=0
    if time[0] == '13' and time[1] == '49' and time[2]=='00' :
        count=1
    else:
        count=0

    if count==1:


        message()
        q=plot()
        q.savefig('Test.png')
        send2Phone(grams,gold_prices[-1])


while True:
    loop()
