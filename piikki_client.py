import RPi.GPIO as GPIO
import MFRC522
import signal
import sys
import getpass
import os
import json
from gadgets import gadgets
from os.path import expanduser
from database import database
from backend_access import backend_access

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

#initialize database
db = database(sqlite_path)

#initialize backend access
ba = backend_access(backend_address, default_header)

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    db.close()
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

            # Check if user is found in the database
            user = db.get_user([uid_combined])

            if user == None:
                # No card found from database
                g.flash(RED)
                print("Card not recognized. Setting up new card!")
                username = raw_input('Username: ')
                password = getpass.getpass('Password: ')

                # authenticate user against backend
                if not ba.authenticate(username, password):
                    continue

                if not ba.userInGroup(username):
                    continue

                #Save user to database
                db.save_user(username, uid_combined)

            else:
                #Card found from database, do transaction
                g.flash(GREEN)
                saldo = ba.doTransaction(user[1], default_amount)
                print(user[1] + ': ' + str(saldo))
