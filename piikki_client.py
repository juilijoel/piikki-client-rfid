import RPi.GPIO as GPIO
import MFRC522
import signal
import sys
import getpass
import os
import json
from gadgets import gadgets
from display import display
from os.path import expanduser
from database import database
from backend_access import backend_access
from getch import _Getch

# Fetch settings from json file
with open('config.json') as json_config_file:
    config = json.load(json_config_file)

# initializations
# green led 29, red led 32, beeper 36
getch = _Getch()
gads = gadgets(29, 32, 36)
disp = display(config["messages"]["default"])
db = database(os.path.dirname(os.path.abspath(__file__)) + "/piikki.db")
ba = backend_access(config["backend_address"], config["default_header"])

RED, GREEN = range(2)
GPIO.setmode(GPIO.BOARD)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    GPIO.cleanup()
    db.close()
    continue_reading = False

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

continue_reading = True

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
            gads.beep()
            # Combine UID
            uid_combined = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])

            # Check if user is found in the database
            user = db.get_user([uid_combined])

            if user == None:
                # No card found from database
                gads.flash(RED)
                print("Card not recognized. Setting up new card!")
                username = ""
                hidden = ""

                disp.show_message(config["messages"]["user"]+" ")
                ch = getch()
                while ch != '\r':
                    try:
                        if (ch == '\x08' or ch == '\x7f') and len(username) > 0:
                            username = username[:-1]
                            disp.backspace()
                        else:
                            username += ch
                            disp.add_str(ch)
                        ch = getch()
                    except:
                        ch = getch()

                disp.indent_line()

                password = ""
                disp.add_str("\n"+config["messages"]["pass"]+" ")
                ch = getch()
                while ch != '\r':
                    try:
                        if ch == '\x08' or ch == '\x7f' and len(password) > 0:
                            hidden = hidden[:-1]
                            password = password[:-1]
                            disp.backspace()
                        else:
                            hidden += "*"
                            password += ch
                            disp.add_str('*')
                        ch = getch()
                    except:
                        ch = getch()

                # authenticate user against backend
                if not ba.authenticate(username, password):
                    disp.show_temp_message(config["messages"]["auth_fail"])
                    
                    # create new user
                    disp.show_message(config["messages"]["pass"]+" ")
                    
                    # ask password again
                    hidden = ""
                    passwordcheck = ""
                    ch = getch()
                    while ch != '\r':
                        try:
                            if ch == '\x08' or ch == '\x7f' and len(password) > 0:
                                hidden = hidden[:-1]
                                passwordcheck = passwordcheck[:-1]
                                disp.backspace()
                            else:
                                hidden += "*"
                                passwordcheck += ch
                                disp.add_str('*')
                            ch = getch()
                        except:
                            ch = getch()

                    if(password == passwordcheck and ba.createUser(username, password) == True):
                        ba.addUserToGroup(username)
                        disp.show_temp_message(config["messages"]["create_user"])
                        db.save_user(username, uid_combined)

                    else:
                        disp.show_temp_message(config["messages"]["user_create_fail"])
                    continue

                if not ba.userInGroup(username):
                    ba.addUserToGroup(username)
                    db.save_user(username, uid_combined)
                    disp.show_temp_message(config["messages"]["user_not_found"])
                    continue

                #Save user to database
                db.save_user(username, uid_combined)
                disp.show_temp_message(config["messages"]["card_saved"])

            else:
                #Card found from database, do transaction
                gads.flash(GREEN)
                saldo = ba.doTransaction(user[1], config["default_amount"])
                disp.show_saldo(user[1], saldo)
                print(user[1] + ': ' + str(saldo))
