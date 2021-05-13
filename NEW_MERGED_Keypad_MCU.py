import RPi.GPIO as GPIO    
import serial
import random
from time import sleep
GPIO.setmode(GPIO.BCM) # configure GPIO numbering
GPIO.setwarnings(False)

######################################################################
# Global Variables 
r1 = 0
count = 0
electro = 0
passcode_blur = 0
######################################################################

######################################################################
# Functions

# Set GPIO for Keypad
COL = [18,23,24,25]
ROW = [4,17,27,22]
GPIO.setup(16, GPIO.OUT)

for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j], 1)
for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Keypad Function
def check_keypad(length):

    COL = [18,23,24,25]
    ROW = [4,17,27,22]

    MATRIX = [["1","2","3","A"],
              ["4","5","6","B"],
              ["7","8","9","C"],
              ["*","0","#","D"]]
    result = ""
    global passcode_blur
    # Display keypad input
    if (passcode_blur == 0):
        while True:
            # Output a 0 to the column ports
            for j in range(4):
                GPIO.output(COL[j], 0)

                for i in range(4):
                    if (GPIO.input(ROW[i]) == 0):
                        sleep(0.02)
                        result = result + MATRIX[i][j]
                        print(result)
                        while(GPIO.input(ROW[i]) == 0):
                            sleep(0.02)

                GPIO.output(COL[j], 1)
                if len(result) >= length:
                    return result
    else:
        while True:
            # Output a 0 to the column ports
            for j in range(4):
                GPIO.output(COL[j], 0)

                for i in range(4):
                    if (GPIO.input(ROW[i]) == 0):
                        sleep(0.02)
                        result = result + MATRIX[i][j]
                        print("*")
                        while(GPIO.input(ROW[i]) == 0):
                            sleep(0.02)

                GPIO.output(COL[j], 1)
                if len(result) >= length:
                    return result

# Passcode Generator
def rcode():
    global r1
    r1 = random.randint(100,999)
    print("Your new passcode is:", r1)
######################################################################

######################################################################
# Generate an access code at start-up
# Get ready status from communicating microcomputer
# Turn on Electromagnet device
rcode()
port = serial.Serial ("/dev/serial0", 9600)
GPIO.output(16, True)
######################################################################

while True:
    ######################################################################
    # Get welcome message from MCU1
     print("Waiting for response from MCU1...")
     r_data = port.readline(1)
     sleep(0.3)
     data_left = port.inWaiting()
     r_data += port.readline(data_left)
     print(r_data)
    ######################################################################
    
    ######################################################################
    # Main User Menu
    print("Press 0 to test electromagnet is functioning")
    print("Press 1 to expand or retract your device")
    print("Press 2 to open or close your device's panel")
    print("Press # to use the barcode scanner")
    m_menu = check_keypad(1)
    while ((m_menu != "0") and (m_menu != "1") and (m_menu != "2") and (m_menu != "#")):
            print("Enter only a 0, 1, 2, or #\n ")
            m_menu = check_keypad(1)
    ######################################################################
    
    ######################################################################
    # Access barcode scanner
    if (m_menu == "#"):
        print("Place your barcode in front of the camera")
        u = 'bar'
        b = bytes(u,'ascii')
        port.write(b)
    ######################################################################
    
    ######################################################################
    # Test electromagnet is turning on/off
    elif (m_menu == "0"):
        # Turn electro off
        if (electro == 1):
            GPIO.output(16,False)
            print("Front panel is unlocked")
            u = 'e'
            b = bytes(u,'ascii')
            port.write(b)
            electro = 0
        # Turn electro on
        else:
            GPIO.output(16,True)
            print("Front panel is locked")
            u = 'e'
            b = bytes(u,'ascii')
            port.write(b)
            electro = 1
    ######################################################################
    
    ######################################################################
    # Access motors
    elif (m_menu == "1"):
        u = '1'
        b = bytes(u,'ascii')
        port.write(b)
        
        ######################################################################
        # Functionality Menu 
        print("Press A to Expand or B to Retract")
        print("and simultaneously enter a range between 0 - 10 in the form xx \n")
        s_menu = check_keypad(3) # Enter three characters
        while (((s_menu[0] != "A") and (s_menu[0] != "B")) or ((s_menu[2] == "0") and (s_menu[1] == "0"))):        
            if ((s_menu[1] == "0") and (s_menu[2] == "0")):
                print("Dimensions need to be greater than 0\n")
       
            elif((s_menu[0] != "A") and (s_menu[0] != "B")):
                print("Enter in the correct format Axx\n")
            s_menu = check_keypad(3)
        ######################################################################
        # Increment based on input
        if (s_menu == "A01"):
            u = 'Aone'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "A02"):
            u = 'Atwo'
            b = bytes(u,'ascii')
            port.write(b)
       
        elif (s_menu == "A03"):
            u = 'Athree'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "A04"):
            u = 'Afour'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "A05"):
            u = 'Afive'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif(s_menu == "A10"):
            u = 'Aten'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "B01"):
            u = 'Bone'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "B02"):
            u = 'Btwo'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "B03"):
            u = 'Bthree'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "B04"):
            u = 'Bfour'
            b = bytes(u,'ascii')
            port.write(b)

        elif (s_menu == "B05"):
            u = 'Bfive'
            b = bytes(u,'ascii')
            port.write(b)
        
        elif (s_menu == "B10"):
            u = 'Bten'
            b = bytes(u,'ascii')
            port.write(b)
    ######################################################################
   
    ######################################################################
    # Open/close front door 
    elif (m_menu == "2"):
        u = '2'
        b = bytes(u,'ascii')
        port.write(b)
        
        ######################################################################
        # Passcode Menu
        passcode_blur = 1
        print("Please enter your passcode to unlock and open front panel")
        print("or enter 000 to close")
        in_code = check_keypad(3)
        result2 = int(in_code, 10) # Convert to int base 10
        while ((result2 != r1) and (in_code != "000") and (count < 11)):
            count = count + 1
            if (count == 10):
                print("You have entered the code incorrectly too many times and are momentarily locked out!\n ")
                sleep(5500)
                count = 0
            else:
                print("Invalid code!")
                print("You have entered the passcode incorrectly this many times", count)
                print("If you continue to enter an invalid code you will be locked out!")
                print("Please enter the correct passcode to unlock and open")
                print("or enter 000 to close ")
                in_code = check_keypad(1)
                result2 = int(in_code, 10)
        ######################################################################
        passcode_blur = 0
        # Code matched, ok to open panel
        if (result2 == r1): 
            GPIO.output(16, False) # Turn off electromagnet 
            u = 'o'
            b = bytes(u,'ascii')
            port.write(b)
        # close door
        elif (in_code == "000"):
            GPIO.output(16, True) # Turn it back on
            u = 'c'
            b = bytes(u,'ascii')
            port.write(b)
       
        else:
            print("Something went wrong!")
            sleep(5)
    ######################################################################

    
