import RPi.GPIO as GPIO
import MFRC522
import signal
import sqlite3
import sys
import time
import requests
from os.path import expanduser

#raspi pins (BOARD mode)
green_led = 29
red_led = 32
beeper = 36

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(0)

sqlite_path = expanduser("~") + "/piikki-client/piikki.db"
backend_address = "https://dev.spinni.org"

RED, GREEN = range(2)

def flash(color):
    if(color == RED):
        GPIO.setup(red_led, GPIO.OUT)
        GPIO.output(red_led, 1)
        time.sleep(0.5)
        GPIO.output(red_led, 0)
    elif(color == GREEN):
        GPIO.setup(green_led, GPIO.OUT)
        GPIO.output(green_led, 1)
        time.sleep(0.5)
        GPIO.output(green_led, 0)

def beep():
    GPIO.setup(beeper, GPIO.OUT)
    GPIO.output(beeper, 1)
    time.sleep(0.2)
    GPIO.output(beeper, 0)

continue_reading = True
conn = None
#Connect to database
try:
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()
    
    c.execute('CREATE TABLE IF NOT EXISTS  users (carduid TEXT, username TEXT)')
except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to Piikki-client"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    
    # If a card is found
    if status == MIFAREReader.MI_OK:
        beep()
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        
        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            # Combine UID
            uid_combined = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])

            # Check if card is found in the database
            card = c.execute('SELECT * FROM users WHERE carduid=?', [uid_combined])

            if card.fetchall() == []:
                #No card found from database
                flash(RED)
                print "Card not recognized. Setting up new card!"
                username = raw_input('Enter your Piikki Username: ')
                password = raw_input('Enter your Piikki Password: ')

                #TODO Check if user is in backend database

                #Save user to database
                c.execute('INSERT INTO users VALUES (?,?)', (uid_combined, username))
            else:
                #Card found from database
                flash(GREEN)
                print "Card recognized! Doing transaction"
                pass
                
            