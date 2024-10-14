##### MODULE: Actuator for multiposition valves   ####
##### Author: Stian Ingebrigtsen - and Julie Knapstad & Jon Sebastian Kaupang   ####

""" To run this module, run your IDE as administrator"""

import time
import serial
import settings
import logging

# Enable logging from this file
log = logging.getLogger("method_logger")

# Fetch MPV variables
mpv = None
com = str(settings.getMPVcom())

# Initialize Multi Position Valve
def initialize(COM=com):
    print("Initializes")
    # 9600 baud, no parity, 8 data bits, 1 stop bit, no hardware or software handshaking.
    global mpv
    # Close previous initialiazations before opening a new one
    try:
        mpv.close()
    except:
        pass

    # Loop for trying to initialize MPV 3 times before returning runtime error
    tries = 0
    while tries < 3: 
        try:
            # Serial communication settings
            mpv = serial.Serial("COM" + COM,
                                    baudrate=9600,
                                    bytesize=serial.EIGHTBITS,
                                    stopbits=serial.STOPBITS_ONE,
                                    parity=serial.PARITY_NONE,
                                    timeout=1)     # open serial port
            # Initialization command
            mpv.reset_input_buffer()
            mpv.write('NP06\n'.encode())    # sets 6 positions for multiposition valve
            mpv.write('GO1\n'.encode())     # Sets the valve to position 1 - waste
            return True
        except:
            time.sleep(1)
            tries += 1
        raise RuntimeError("Multiposition valve not responding")


# Function for setting valve position takes both position and liquid associated with the position as arguments
def liquid(position):
    # Initialize MPV if it is not already done.
    if mpv == None:
        initialize()
    else:
        pass

    # Check for user stop from GUI to abort the current run, if true
    if settings.getstopSignal():
        raise SystemExit("Stopping program mpv")

    pos = str(position)
    log.info(f"moving to position {pos}")
    
    # Send command
    if pos:
        command = "GO" + pos + "\n"
        mpv.write(command.encode())
        print("Moving to pos: ", pos)
        
        # Attempt to read a response from the MPV after sending the command
        mpv.write("STATUS\n".encode())  # Check if there's a status 
        response = mpv.read_until('\r')
        # Check if channel in status response matches the pos, command variable
        # Rais an error if then there is no response from the MPV.
        channel = f"CP0{pos}"
        if channel.encode() in response:
            print("OK")
        else:
            if not response:
                log.error("No response from MPV after sending command.")
                #return False
                raise RuntimeError("Multiposition valve not responding")
            print("initialization response: ", response)

    else:
        log.error("Invalid argument for mpv.liquid component")
        # return False
        raise RuntimeError("Multiposition valve not responding")