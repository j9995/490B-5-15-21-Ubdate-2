import cv2
import serial
from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
from time import sleep
from picamera import Color
from subprocess import call
from pyzbar import pyzbar
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# GPIO Inputs
pir = MotionSensor(25)
GPIO.setup(12, GPIO.IN)
camera = PiCamera()
# GPIO Outputs
GPIO.setup(18, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

# Set camera settings camera.resolution(2592,1944)
camera.annotate_text_size = 50
camera.annotate_background = Color('black')
camera.annotate_foreground = Color('white')
camera.exposure_mode = "auto"
camera.awb_mode = "auto"
camera.framerate = 30

def rescale_frame(frame, percent=100):
    width = int(frame.shape[1] * percent/100)
    height = int(frame.shape[0] * percent/100)
    dim = (width,height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

def scanner(frame,barcode_data):
    barcodes = pyzbar.decode(frame)
    if len(barcodes) != 0:
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            #print(barcode.rect)
            if x>0 or y>0 or w>0 or h>0:
                GPIO.output(18,True)   #SUCCESS
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                barcode_dataraw = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                text = "{} ({})".format(barcode_dataraw, barcode_type)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print("Found {} barcode: {}".format(barcode_type, barcode_data))
                barcode_data = barcode_dataraw[9::]
                return frame,barcode_data
    else:
        GPIO.output(5,True)        #FAILURE
        print("No barcode detected, try again!")
    return frame, barcode_data

def BarcodeReader():
    barcode_data = str(" ")
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        input_state = GPIO.input(12)
        ret, frame = cap.read()
        frame150 = rescale_frame(frame,percent=100)
        if input_state == False:
            frame,barcode = scanner(frame,barcode_data)
            print(barcode)
            #print(type(barcode).__name__)
        cv2.imshow('Barcode Scanner', frame150)
        GPIO.output(18,False)
        GPIO.output(5,False)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Define function that enables camera to run
def CameraCapture():
    #while True:
    enable = True
    #    pir.wait_for_motion()
    if (GPIO.input(25) == True):
        
        print("Device not ready for use")
        camera.start_preview()
        date = datetime.now().strftime("%m.%d.%Y")        
        timestamp = datetime.now().strftime("%H.%M.%S")                    #get time
        camera.start_recording('/home/pi/Desktop/'+timestamp+'.h264')      #start recording
        file_h264 = timestamp+'.h264'                  #
        file_mp4 = date+'.'+timestamp+'.mp4'
        print(file_h264)
        print(file_mp4)
        print("Motion Detected")
        print("Recording...")
        GPIO.output(18,True)
        while enable:
            timestamp = datetime.now().strftime("%m.%d.%Y_%H:%M:%S")
            camera.annotate_text = timestamp
            if(GPIO.input(25) == False):
                enable = False
        #pir.wait_for_no_motion()
        camera.stop_recording()
        camera.stop_preview()
        print("No Motion")
        print("Stop Recording...")
        print(file_h264)
        print(file_mp4)
        GPIO.output(18,False)
        print("current directory files: ")
        command = "ls"
        call([command],shell=True)
        command = "MP4Box -add " + file_h264 + " " + file_mp4
        call([command],shell=True)
        command = "rm "+file_h264  
        call([command],shell=True)
        print("Device is ready for use")
  
# set up a class for the motors
class Motor():
    def __init__(self, In1, In2):
        self.In1 = In1
        self.In2 = In2
        GPIO.setup(self.In1,GPIO.OUT)
        GPIO.setup(self.In2,GPIO.OUT)
        
        self.pwm1 = GPIO.PWM(self.In1, 100) # Apply full voltage to device
        self.pwm2 = GPIO.PWM(self.In2, 100) # Apply full voltage to device
        self.pwm1.start(0) # start with motor off
        self.pwm2.start(0) # start with motor off
        
    def moveForward(self, speed, t=0): # 'speed' allows the user to input spee
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        self.pwm2.ChangeDutyCycle(speed)
        sleep(t)                        # delay
        
    def moveBackward(self, speed, t=0): # 'speed' allows the user to input spee
        GPIO.output(self.In1, GPIO.HIGH)
        GPIO.output(self.In2, GPIO.LOW)
        self.pwm1.ChangeDutyCycle(speed)
        sleep(t)                        # delay
    
    def stop(self):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)

###################################################################### 
port = serial.Serial ("/dev/ttyS0", 9600)    #Open port with baud rate
motor1  = Motor(13, 6)
motor2  = Motor(17, 27)
motor3  = Motor(23, 24)
parcel_position = 0
door_position = 0
######################################################################

while True:
    ######################################################################
    # Always check to record
    #CameraCapture()
    ######################################################################
    
    ######################################################################
    # Send message to MCU2
    u = 'Ready to accept input from keypad'
    b = bytes(u, 'ascii')
    port.write(b)
    ######################################################################
    
    ######################################################################
    # Read one line from the serial port
    received_data = port.readline (1)           
    sleep(0.03)
    data_left = port.inWaiting()          #check for remaining byte
    received_data += port.read(data_left)                 
    print("Data received", received_data) #print received data USED FOR DEBUG
    ######################################################################
    
    if (received_data == b'bar'):
        print("entered barcode function") # debug
        BarcodeReader()
    
    ######################################################################
    elif (received_data == b'1'):
        print("MCU2 is now controlling motor functionality")
        ######################################################################
        received_data2 = port.readline(1) # read serial port
        sleep(0.03)
        data_left = port.inWaiting() # check for remaining byte
        received_data2 += port.read(data_left)
        print(received_data2) # debug
        ######################################################################
        
        # User entered an A, move motors forwards
        if (received_data2 == b'Aone'):
            print("incrementing by one second")
            motor1.moveForward(100, 1) # Move Forward with 100% voltage for 1 second(s)
            sleep(1)
            motor1.stop()
            # Check if front parcel has already been expanded
            # If not, default expand is 3 seconds
            # Else do nothing
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1 # Indicate new position
            else:
                motor2.stop()
       
        elif (received_data2 == b'Atwo'):
            print("incrementing by two seconds")
            motor1.moveForward(100, 2)
            sleep(1)
            motor1.stop()
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1
            else:
                motor2.stop()
       
        elif (received_data2 == b'Athree'):
            print("incrementing by three seconds")
            motor1.moveForward(100, 3)
            sleep(1)
            motor1.stop()
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1
            else:
                motor2.stop()
        
        elif (received_data2 == b'Afour'):
            print("incrementing by four seconds")
            motor1.moveForward(100, 4)
            sleep(1)
            motor1.stop()
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1 # Indicate new position
            else:
                motor2.stop()
        
        elif (received_data2 == b'Afive'):
            print("incrementing by five seconds")
            motor1.moveForward(100, 5)
            sleep(1)
            motor1.stop()
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1
            else:
                motor2.stop()
        
        elif (received_data2 == b'Aten'):
            print("incrementing by ten seconds")
            motor1.moveForward(100, 10)
            sleep(1)
            motor1.stop()
            if (parcel_position == 0):
                motor2.moveForward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 1
            else:
                motor2.stop()
        
        # User entered a B, move motors backwards    
        elif (received_data2 == b'Bone'):
            print("Decrementing by one second")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 1) # Move Backward with 100% voltage for 1 second(s)
            sleep(1)
            motor1.stop()
            # Check if front parcel has already been retracted
            # If not, default retract is 3 seconds
            # Else do nothing
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
       
        elif (received_data2 == b'Btwo'):
            print("Decrementing by two seconds")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 2)
            sleep(1)
            motor1.stop()
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
        
        elif (received_data2 == b'Bthree'):
            print("Decrementing by three seconds")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 3)
            sleep(1)
            motor1.stop()
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
        
        elif (received_data2 == b'Bfour'):
            print("Decrementing by four seconds")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 4)
            sleep(1)
            motor1.stop()
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
        
        elif (received_data2 == b'Bfive'):
            print("Decrementing by five seconds")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 5)
            sleep(1)
            motor1.stop()
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
       
        elif (received_data2 == b'Bten'):
            print("Decrementing by ten seconds")
            if (door_position == 1):
                # Close the door first
                motor3.moveBackward(100, 10)
                motor3.stop()
            motor1.moveBackward(100, 10)
            sleep(1)
            motor1.stop()
            if (parcel_position == 1):
                motor2.moveBackward(100, 3)
                sleep(1)
                motor2.stop()
                parcel_position = 0 # Indicate new position
            else:
                motor2.stop()
        
        else:
            print("Something doesn't look right...")
    ######################################################################

    ######################################################################
    # Control front panel when a 2 is entered on Keypad
    elif (received_data == b'2'):
        print("In panel")
        # Get user input to open or close
        received_data2 = port.readline(1)
        sleep(0.03)
        data_left = port.inWaiting()
        received_data2 += port.read(data_left)
        
        # Only open if front panel has moved forward
        if ((received_data2 == b'o') and (door_position == 1)):
            print("Front panel is already open")
           
        elif ((received_data2 == b'o') and (parcel_position == 1)):
            motor3.moveForward(100, 10)
            motor3.stop()
            door_position = 1 # Indicate front panel is open
            
        # Cannot open pancel while front parcel is retracted
        elif ((received_data2 == b'o') and (parcel_position == 0)):
            # Move front section out
            motor2.moveForward(100, 3)
            sleep(1)
            motor2.stop()
            # Open front panel
            motor3.moveForward(100, 10)
            motor3.stop()
            parcel_position = 1 # Indicate front parcel is out
            door_position = 1 # Indicate front panel is open
       
        elif ((received_data2 == b'c') and (door_position == 1)):
            # Move front section out
            motor3.moveBackward(100, 11)
            motor3.stop()
            door_position = 0 # door closed
      
        else:
            print("Front panel is already closed")
    ######################################################################
    
    else:
        sleep(2)
        print ("that operation is not listed try again")