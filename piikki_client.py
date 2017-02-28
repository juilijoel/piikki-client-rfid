import RPi.GPIO as GPIO
import MFRC522
import signal
import sqlite3
import sys
import time
import requests
import getpass
import os
import json
from gadgets import gadgets
from os.path import expanduser

# Fetch settings from json file
with open('config.json') as json_config_file:
    config = json.load(json_config_file)

sqlite_path = os.path.dirname(os.path.abspath(__file__)) + "/piikki.db"
backend_address = config["backend_address"]
default_header = config["default_header"]
default_amount = config["default_amount"]

RED, GREEN = range(2)
GPIO.setmode(GPIO.BOARD)

# GREEN LED = 29, 
# RED LED = 32
# BEEPER = 36
g = gadgets(29, 32, 36)

continue_reading = True
conn = None

#Connect to database
try:
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (carduid TEXT, username TEXT)')
except sqlite3.Error as e:
    print("Error %s:" % e.args[0])
    sys.exit(1)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    conn.close()
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("Welcome to Piikki-client")
print("Press Ctrl-C to stop.")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            g.beep()
            # Combine UID
            uid_combined = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])

            # Check if card is found in the database
            c.execute('SELECT * FROM users WHERE carduid=?', [uid_combined])
            card = c.fetchone()

            if card == None:
                # No card found from database
                g.flash(RED)
                print("Card not recognized. Setting up new card!")
                username = raw_input('Username: ')
                password = getpass.getpass('Password: ')

                payload = {"username" : username, "password": password}
                r = requests.post(backend_address+'/users/authenticate', headers=default_header,  json = payload)
                json_data = json.loads(r.text)

                try:
                    #Authenticate user
                    if json_data["result"]["authenticated"] == True:
                        print("User authenticated!")

                        #Check if user exists in group
                        r = requests.get(backend_address+'/group/members/'+username, headers=default_header)
                        json_data = json.loads(r.text)
                        
                        if json_data["result"]["username"] == username:
                            print("User found from group! Adding card to database!")

                            #Save user to database
                            c.execute('INSERT INTO users VALUES (?,?)', (uid_combined, username))
                            conn.commit()

                except:
                    print("Error, user not added to database!")

            else:
                #Card found from database, do transaction
                g.flash(GREEN)
                payload = {"username":card[1],"amount":default_amount}
                r = requests.post(backend_address+'/transaction', headers=default_header, json=payload)
                json_data = json.loads(r.text)
                print(json_data["result"][0]["username"] + ": " + str(json_data["result"][0]["saldo"]))
