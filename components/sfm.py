# Module to communicate with spectrometer - SpectroFotoMeter, SFM
# Author: Stian Ingebrigtsen

import seabreeze
seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
import settings
# from threading import Lock
import sys
import numpy as np
import time
import datetime
import logging
import os

# Fetch the current file's directory and get the parent added to sys.path
current_file_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.join(current_file_directory, "..")
sys.path.append(parent_directory)

# Logging errors to logfile
log = logging.getLogger("method_logger")

# Function to get connected devices as list - to populate dropdown in case of more than one spectrometer.
def get_connected_devices():
	global list
	list = sb.list_devices()
	return list

# Function to set the integration time of the spectrophotometer
def set_integration_time():
	global spec
	try:
		print("integration time SET")
		micro_seconds = settings.getIntegrationTime() * 1000 # convert micro to milliseconds seconds for the seabreeze lib
		spec.integration_time_micros(int(micro_seconds))	
	except:
		raise RuntimeError("Could not set the integration time")

# Initialize device - argument serial number, or first available device
def initialize(serial_number=None):
	global spec
	if serial_number == None:
		try:
			# Connect to first available device
			spec = sb.Spectrometer.from_first_available()
		except:
			log.error("Could not connect to spectrophotometer - first available")
			return False
	else:
		try:
			try:
				# Connect to device by serial number
				spec = sb.Spectrometer.from_serial_number(serial_number)
			except:
				# Try connecting again but close potential connection first
				spec.close()
				spec = sb.Spectrometer.from_serial_number(serial_number)
		except:
			log.error(f"Could not connect to spectrophotometer - by serial number {serial_number}")
			return False

	set_integration_time()
	log.info("spectrometer Initialized")
	return True


# Function to get spectral data from the device.
def request_spectra():
	global spec
	try:
		# Check for user stop from GUI to abort the current run, if true
		if settings.getstopSignal():
			raise SystemExit("Stoping program")
		# USB 4000 spectrometers - the old colifast spectrometers - are not supporting nonlinearity correction 
		# - so try with correction first in case of old spectrometer
		try:
			data = spec.intensities(correct_nonlinearity=True, correct_dark_counts=True)
		except:
			data = spec.intensities(correct_nonlinearity=False, correct_dark_counts=True)
		return data
	except:
		raise RuntimeError("Could not initialize spectrophotometer")

# Function to close the device connection
def close():
	global spec
	try:
		spec.close()
	except:
		raise RuntimeError("Could not close spectrophotometer")

# Function to get the wavelengths mapped to the spectrum intensities. 
def get_wavelength_mapping():
	global spec
	try:
		mapping = spec.wavelengths()
		return mapping
	except:
		raise RuntimeError("Could not get wavelength mapping from spectrophotometer")

# Function for reading spectrometer value, takes wavelength, bandwidth of desired wavelength, and amount of readings to average over as args
def sfm_read(wavelength, nm_bandwidth='1', readings_to_average_over='3'):
	# convert args from strings
	wavelength = int(wavelength)
	nm_bandwidth = float(nm_bandwidth)
	readings_to_average_over = int(readings_to_average_over)

	# Get the spectral intensity data and the wavelength mapping reset spectrophotometer if it is timed out.
	try:
		temp_y = request_spectra()
	except:
		initialize()
		temp_y = request_spectra()
	
	## AVERAGE OVER READINGS ##
	# Loop amount of readings to average over, and add together
	holder_y = [0]
	for i in range(readings_to_average_over):
		for index, value in enumerate(holder_y):
			temp_y[index] += value
		time.sleep(0.5)
		holder_y = request_spectra()
	# divide by amount of readings, to get the average
	y = [x / readings_to_average_over for x in temp_y]
	wavelength_mapping = get_wavelength_mapping()
		
	# Create a list of lists containing the wavelength and corresponding spectral intensity at that wavelength
	data = []
	timestamp = datetime.datetime.now().replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
	data.append(timestamp)

	# If a full spectrum is required skip the storing in data base, and return the spectrum
	if wavelength == 1:
		for i in range(len(y)):
			data.append([wavelength_mapping[i], y[i]])
		return timestamp, data

	# If a wavelength is specified, and a nm bandwidth (optional) store the average value of the band
	else:	   
		avg = 0
		summing_up = 0
		counter = 0
		# Add up all measurments in band and count amount
		for index, nm in enumerate(wavelength_mapping):
			if nm > wavelength - nm_bandwidth/2 and nm < wavelength + nm_bandwidth/2: # I think i bandwidth here is just half the bandwith in reality as I do the +/- here, check that out and consider doing +/- nm_bandwidth/2 for clairity, and increase the value from 0.5 to 1 default.
				summing_up += y[index]
				counter += 1
			else:
				if counter > 0:
					# Devide sum by counter for the resulting average 
					avg = summing_up/counter
					data_point = [wavelength, round(avg, 2)]
					return timestamp, data_point[1]
    