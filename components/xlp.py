### MODULE FOR HANDLING THE SYRINGE PUMP, XLP6000 ###
### Author: Stian Ingebrigtsen ###

import serial
import time
import settings
import logging

# Enable logging from this file
log = logging.getLogger("method_logger")
pump_size = settings.getPumpSize()
total_steps = 3000

# Function for sending commands to pump (Tecan cavro's DT protocol - OEM protocol commands never seemed to work for me)
def send_command(command):
    global ser
    # Check for user stop from GUI to abort the current run, if true
    if settings.getstopSignal():
        raise SystemExit("Stopping program")
    # Command block wrapper and encoding
    command_block = "/1" + command + "\r"
    ser.write(command_block.encode(encoding="ascii", errors="ignore"))
    response = ser.readline().decode(encoding="ascii", errors="ignore")
    # Catch a failed response
    if not response:
        log.error("Syringe pump is not responding, in send command")
        raise RuntimeError("Syringe pump is not responding")
    time.sleep(0.1) # A delay was needed for the system to be able to handle the communication, the duration is chosen arbitrarily and might be optimized.
    return response.strip()


## Functions for pump operation
# Initialization 1/3 of plunger force to spare the valve head of the syringe (controlled by, 2 in the "Z2R" command)
def initialize(COM=None):
    global pump_size  # Declare that you're using the global pump_size
    pump_size = settings.getPumpSize()  # Assign a value to it

    if not COM:
        # Fetch pump variables
        COM = str(settings.getXLPcom())
        print(COM, "NONE")
    else:
        COM = str(COM)
        print(COM)

    global ser
    # Close previous initialiazations before opening a new one
    try:
        ser.close()
    except:
        pass

    # Loop for trying to initialize syringe pumpe 3 times before returning runtime error
    tries = 0
    while tries < 3: 
        try:
            # Serial communication settings
            ser = serial.Serial("COM" + COM,
                                    baudrate=9600,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=5)

            # Initialization command
            command = "Z25R"
            send_command(command)
            return True
        except:
            # one second delay inbetween tries
            time.sleep(1)
            tries += 1
        raise RuntimeError("Syringe pump failed to initialize")

# Aspirate volume "P" indicates relative position of syringe plunger
def aspirate(volume):
    _check_pump_status(ser) # Delay until done
    log.info(f"Aspirate {volume} ml")
    command = "P" + str(_convert_volume_to_pulses(volume)) + "R"
    send_command(command)
# Fill the syringe "A" indicates absolute position - go to maximum
def fill():
    global pump_size
    _check_pump_status(ser) # Delay until done
    log.info("Filling the syringe")
    command = "A" + str(_convert_volume_to_pulses(pump_size)) + "R"
    send_command(command)
# Dispense volume
def dispense(volume):
    _check_pump_status(ser) # Delay until done
    log.info(f"Dispense {volume} ml")
    command = "D" + str(_convert_volume_to_pulses(volume)) + "R"
    send_command(command)
# Empty pump - absoulute minimum position
def empty():
    _check_pump_status(ser) # Delay until done
    log.info("Emptying the syringe")
    command = "A" + str(_convert_volume_to_pulses(0)) + "R"
    send_command(command)
# Swich valve head to out position
def valve_out():
    _check_pump_status(ser)
    log.info("Switching the xlp valve to out")
    send_command("OR")
# Swich valve head to in position
def valve_in():
    _check_pump_status(ser) 
    log.info("Switching the xlp valve to in")
    send_command("IR")
# Set flowrate of the pump
def flowrate(rate):
    _check_pump_status(ser) 
    command = "S" +str(_nearest_speed_code(rate)) + "R"
    log.info(f"Flow rate is set to {rate} ul/sec") 
    send_command(command)
# Delay function to use from ALARM-program
def delay_until_done():
    _check_pump_status(ser)

# Function for checking if pump is active - Delays the pump until previous task is done
def _check_pump_status(ser):
    # Check for user stop from GUI to abort the current run, if true.
    if settings.getstopSignal():
        raise SystemExit("Stopping program now")
    busy = True
    while busy:
        response = send_command("Q")
        #print(response, "\t", response[2])
        #time.sleep(1)
        if not response:
            log.error("Syringe pump is not responding, in check pump status")
            raise RuntimeError("Syringe pump is not responding")
        try:
            if response[2] == "`":
                busy = False
        except:
            continue


## Functions for pump queries ##
# Valve configuration 
def valve_position():
    # Returns o for out to the mpv and i for in to the incubator chamber - I think verify this
    global ser
    command = "?" + str(6)
    response = send_command(command)
    return(response[3])
# Returns volume position of plunger based on pump size
def pump_position():
    global ser
    command = "?"
    response = send_command(command)
    pulses = ''
    i = 0
    val = response[3]
    # Loop to collect digits from response - might optimizeby using start and terminating char and fetch what is in between.
    while val.isdigit():
        pulses = pulses + val
        i += 1
        val = response[3+i]
    # Calculate volume
    volume = _convert_pulses_to_volume(int(pulses))
    return(volume)



# Functions to handle conversion between volume and pulses(steps)  
def _convert_volume_to_pulses(volume):
    global pump_size
    global total_steps
    pulses = volume/pump_size * total_steps
    return int(pulses)
def _convert_pulses_to_volume(pulses):
    global pump_size
    global total_steps
    volume = pulses/total_steps * pump_size
    return int(volume)

# Calculate speed code that corresponds to the amount of pulses/steps to be drawn per second
# Colifast was using 3000 XL as default for the instruments wit FIA-lab, if we no longer shall do that in this setup consider adjusting speed here. 
# Command for downgrading syringe pump to 3000 XL is: "/1U82R"
def _nearest_speed_code(flowrate):
    global pump_size
    # Convert flowrate to "pulse rate"
    global total_steps
    pulse_rate = flowrate/pump_size * 6000 # this table is set for a 6000 step syringe, so when setting that value to 3000(total_steps) it goes with half speed

    # tabulated values for speed to pulse
    speed_code_values = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
        10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
        20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 
        30, 31, 32, 33, 34, 35, 36
    ]
    pulses_per_sec_values = [
        6000, 5600, 5000, 4400, 3800, 3200, 2600, 2200, 2000, 1800, 
        1600, 1400, 1200, 1000, 800, 600, 400, 200, 190, 180, 
        170, 160, 150, 140, 130, 120, 110, 100, 90, 80, 
        70, 60, 50, 40, 30, 20, 18
    ]

    # Function to calculate the absolute difference between desired value and all values in the list
    def diff_from_desired(value):
        return abs(value - pulse_rate)

    # Find the index of the value with the smallest absolute difference
    nearest_index = min(range(len(pulses_per_sec_values)), key=lambda i: diff_from_desired(pulses_per_sec_values[i]))

    # Get the corresponding speed code value for the nearest pulse frequency
    nearest_speed = speed_code_values[nearest_index]

    return nearest_speed 
