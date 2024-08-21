##### MODULE: VICI actuator for multiposition valves   ####
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
                                    timeout=10)     # open serial port
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

    # Check for user stop signal, abort if true
    if settings.getstopSignal():
        raise SystemExit("Stoping program mpv")

    positions = ["waste", "na_thisul", "sample2", "acid", "sample1", "media"]

    # Convert number to its name in liquid list(positions)
    if isinstance(position, int):
        # remove 1 to align with python 0-indexing - this is so the position sendt as argument, correspond to the valve enumeration of the MPV
        position = position - 1
        position = positions[position]
    
    # Get index of liquid(position) and add 1 to accomodate for the python 0-indexing
    pos = positions.index(position) + 1
    pos = str(pos)
    log.info(f"moving to position {pos}, {position}" )
    
    # Send command
    if pos:
        command = "GO" + pos + "\n"
        mpv.write(command.encode())
        time.sleep(1)
    else:
        log.error("Invalid argument for mpv.liquid component")
        return False
