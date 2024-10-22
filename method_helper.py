## MODULE FOR HANDLING A METHOD FILE ##
# Author Stian Eide Ingebrigtsen
# Packages
import sys, time, os
import datetime
import logging

# Own imports
from components.adu.adu import adu
import components.xlp as xlp
import components.sfm as sfm
import components.mpv as mpv
import settings as settings

from Colifast_ALARM_manager import WorkerThread as wt
from Colifast_ALARM_manager import DatabaseHandler
from Colifast_ALARM_manager import ErrorDialog

#PyQt imports
from PyQt5.QtCore import QCoreApplication, QDateTime, QThread, pyqtSignal, QEventLoop
from PyQt5.QtWidgets import QGraphicsScene, QDialog, QMessageBox

log = logging.getLogger("method_logger")

## Globals
folder_path = None
sampleID = None
plottr = None
error_message = None
status = None
alarm_turb = None
alarm_bact = None

### RUNNING THE METHOD ###
def run_method(self, filename, sample_id, status_message, update_plot, error_msg, startTime, bactAlarm, turbAlarm, finished_signal, warning_signal, dialog_result_signal):  # Check if all/some of these args could be replaced by importing from CA!!

	# Globals
	global folder_path
	global sampleID
	global plottr
	global error_message
	global status
	global alarm_turb
	global alarm_bact
	global warning
	global response
	warning = warning_signal
	response = dialog_result_signal
	sampleID = sample_id
	alarm_turb = turbAlarm
	alarm_bact = bactAlarm
	plottr = update_plot
	error_message = error_msg
	status = status_message
	
	startTime.emit(now())
	# Code that interpret the method file directly as python code
	with open(filename, 'r', newline='') as file:
		method = file.read()

	# Create a dictionary containing the desired global and local variables
	globals_dict = globals().copy()
	locals_dict = locals().copy()
	try:
		exec(method, globals_dict, locals_dict)
		finished_signal.emit()
		settings.setstopSignal(0)
	except RuntimeError as e:
		settings.setstopSignal(0)
		message = str(e)
		# If the error is with the ADU, there is no use in trying to switch relays
		if not "ADU" in str(e):
			instrument_stop()
		else:
			message = message + "\nTherby the instrument also fails to signal through LEDs and PLS."
		status.emit(message)
		error_message.emit(message)
	except ErrorMsg as e:
		settings.setstopSignal(0)
		instrument_stop()
		status.emit(str(e))
		error_message.emit(e.message)
	except SystemExit as e:
		settings.setstopSignal(0)
		instrument_stop()
		return
		#status.emit("Stopping Run...")
	except TimeoutError as e:
		settings.setstopSignal(0)
		instrument_stop()
		status.emit(str(e))
		error_message.emit(e.message)

## Functions for code in method file interpretation ##
class ErrorMsg(Exception):
	def __init__(self, message):
		self.message = message
		log.error(message)
		super().__init__(self.message)


# If the instrument stops for some reason, set the stop/error signal 
def instrument_stop():
	adu.on(2) # SK2
	delay(1)
	adu.off(7) # RK7 

# Functino for extracting full spectrum, or single wavelength reading, with the option of averaging over more readings and 
# getting an average of the readings over a, nm_bandwidth of wavelengths
def sfm_read(wavelength, store_data=True, nm_bandwidth = 1, readings_to_average_over=None, series_id=1):
	global plottr
	global sampleID
	
	if store_data:
		db = DatabaseHandler()
		# Get runID
		query = 'SELECT run_id FROM SampleInfo WHERE id = ?'
		run_id = db.fetch_data(query, sampleID)[0][0]
		print("RUNID: ", run_id)

	# Fetch the value of readings to average over from settings
	if not readings_to_average_over:
		readings_to_average_over = settings.getAvrSampleNr()

	if wavelength == 1:
		time, data = sfm.sfm_read(wavelength, nm_bandwidth, readings_to_average_over)
		# A full spectrum will store all the wavelengths in the database - this has not been fully tested and are sure to create lots of entries in the DB.
		for wavelength, intensity in data:
			db.store_data(series_id, sampleID, run_id, time, wavelength, intensity, nm_bandwidth, readings_to_average_over)
			
	else:
		time, data_point = sfm.sfm_read(wavelength, nm_bandwidth, readings_to_average_over)
		if store_data:
			# store data in database
			args = series_id, sampleID, run_id, time, wavelength, data_point, nm_bandwidth, readings_to_average_over
			db.store_data(*args)
			delay(5)
			print("id from sfm read in method helper: ", sampleID)
			plottr.emit(sampleID)
		return data_point

## Collecting functions to reduce coding for frequently used functions ##
# Function for initializing components
def LogOn():
	# component = str(component) idea to deal with the "" signs, that i rather not use in the method file
	device = None
	try:
		print(settings.getXLPcom(), settings.getMPVcom())
		device = "Multiposition Valve"
		status.emit("Logging on multiposition valve")
		mpv.initialize()
		mpv.liquid(1)
		delay(3)
		device = "Syringe pump"
		status.emit("Logging on syringe pump")
		xlp.initialize()
		delay(5)
		device = "ADU"
		status.emit("Logging on adu")
		if not adu.initialize():
			raise Exception
		delay(5)
		device = "Spectrophotometer"
		status.emit("Logging on spectrophotometer")
		if not sfm.initialize():
			try:
				sfm.close()
				if not sfm.initialize():
					raise Exception
			except:
				log.info("SFM not initialized on first try, and exception met before conductiong a second try.")
		delay(5)
	except:
		status.emit("Logging on " + device + " failed")
		raise ErrorMsg(device + " not found")
		
# now time string
def now():
	now = datetime.datetime.now().strftime('%H:%M %m/%d')
	return now

# delay function
def delay(seconds):
	if settings.getstopSignal():
		raise SystemExit()
	else:
		if seconds < 1:
			time.sleep(seconds)
		else:
			for i in range(int(seconds)):
				time.sleep(1)

### Variables to strings that enables the removal of quots, "", in the method file as an aestetic feature ###
# mpv positions
waste = 1
extsamp = 2
nats = 3
acid = 4
sample = 5
media = 6

water = "water"

# Variables for error messages
spill = "spill"
temp = "temp"
IRtest = "IRtest"
UVtest = "UVtest"

# Error presets
def error(message):
	if message == spill:
		msg = "Liquid in Spill-tray/Overfill-flask was detected check instrument for liquid spill."
	elif message == temp:
		msg = "Temperature has droped below 30 degrees Celsius control the incubator block."
	elif message == IRtest:
		msg = "Problem with IR reading, check spectrometer and lightsource and restart analysis."
	elif message == UVtest:
		msg = "Problem with UV reading, check spectrometer, lightsource and liquid (150 ml half full) in chamber and restart analysis."
	else:
		msg = message
	raise ErrorMsg(msg)

# Send out warning to halt program - used for programs that need some interaction with the user like contamination wash etc.
def warning_message(message):
	
	# Emit signal to show the dialog
	warning.emit(message)
	print("Worker is waiting for user response...")

	# Create a local event loop to pause the worker thread until dialog result is received
	loop = QEventLoop()
	response.connect(loop.quit)  # When dialog result is received, exit the loop
	loop.exec_()  # Start the local event loop, pausing worker here
