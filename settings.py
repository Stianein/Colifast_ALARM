##### SETTINGS - VALUES STORED BETWEEN RUNS #####
##### Author: Stian Ingebrigtsen and Julie Knapstad & Are Pettersen
from PyQt5.QtCore import QCryptographicHash, QSettings
from PyQt5.QtCore import QSettings

def storePassword(username, password):
    hash = QCryptographicHash.hash(password.encode(), QCryptographicHash.Sha256)
    settings = QSettings("Colifast", "ALARM")
    settings.setValue(f"{username}_password", hash)

def getPassword(username, password):
    settings = QSettings("Colifast", "ALARM")
    stored_hash = settings.value(f"{username}_password", None)
    
    if stored_hash is None:
        # Handle case where there is no stored hash (e.g., account does not exist)
        return False

    # Ensure stored_hash is a QByteArray, if not convert it
    if isinstance(stored_hash, str):
        stored_hash = QByteArray.fromHex(stored_hash.encode())

    hash = QCryptographicHash.hash(password.encode(), QCryptographicHash.Sha256)

    # Compare the hashes
    if stored_hash == hash:
        return True
    else:
        return False


    
# SETUP_FLAG
def storeSetupFlag(setup):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('setup', setup)
def getSetupFlag():
    settings = QSettings("Colifast", "ALARM")
    setup = settings.value('setup')
    return setup

# Last method loaded
def storeMethod(filename):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('method', filename)
def getMethod():
    settings = QSettings("Colifast", "ALARM")
    filename = settings.value('method')
    return filename

# Signal across threads for when user has aborted run in main gui thread (should not be a problem with thread safety, as it is only altered through main)
def setstopSignal(bool):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('stopsignal', bool)
def getstopSignal():
    settings = QSettings("Colifast", "ALARM")
    stopsignal = settings.value('stopsignal')
    return stopsignal

## LOGGING STUFF ##
def storeCurrentRun(time):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('current_run', time)
def getCurrentRun():
    settings = QSettings("Colifast", "ALARM")
    start_time = settings.value('current_run')
    return start_time
# LOG
# Are the following two superfluous?
def storeLogsFolder(path):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('logs_folder', path)
def getLogsFolder():
    settings = QSettings("Colifast", "ALARM")
    directory = settings.value('logs_folder')
    return directory
def storeLogPath(path):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('logs_path', path)
def getLogPath():
    settings = QSettings("Colifast", "ALARM")
    directory = settings.value('logs_path')
    return directory

# RESULTS
def storeResultFolder(path):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('result_folder', path)
def getResultFolder():
    settings = QSettings("Colifast", "ALARM")
    directory = settings.value('result_folder')
    return directory
# DataBase folder
def storeDBFile(path):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('db', path)
def getDBFile():
    settings = QSettings("Colifast", "ALARM")
    file = settings.value('db')
    return file

def storeEmail(email): # receiver email
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('email', email)
def getEmail():
    settings = QSettings("Colifast", "ALARM")
    stored_email = settings.value("email")
    return stored_email
# Receiver name
def storeReceiver(rec): # name of reciever
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('receiver', rec)
def getReceiver():
    settings = QSettings("Colifast", "ALARM")
    stored_rec = settings.value('receiver')
    return stored_rec
# String containing the time of "log sent"
def storeLogTime(time):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('log_time', time)
def getLogTime():
    settings = QSettings("Colifast", "ALARM")
    log_time = settings.value('log_time')
    return log_time

def storeSender(sender):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('sender', sender)
def getSender():
    settings = QSettings("Colifast", "ALARM")
    stored_rec = settings.value('sender')
    return stored_rec

def storeSenderPass(senderpass):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('sender_password', senderpass)
def getSenderPass():
    settings = QSettings("Colifast", "ALARM")
    stored_rec = settings.value('sender_password')
    return stored_rec

## STYLE AND COLORS ##
# Style
def storeStyle(style):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('style', style)
def getStyle():
    settings = QSettings("Colifast", "ALARM")
    style = settings.value('style')
    return(style)
# Colors #
def storeColors(colors):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('Colors', colors)
def getColors():
    settings = QSettings("Colifast", "ALARM")
    colors = settings.value('Colors')
    return(colors)


#### START VALUES ####
# Delay Start Time checkbox
def storeDelayStart(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('delay', state)
def getDelayStart():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('delay')
    return(state)
# Sodium Thiosulfate checkbox
def storeSodiumThio(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('SodiumThio', state)
def getSodiumThio():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('SodiumThio')
    return(state)
# Exernal Sample checkbox
def storeExtSamp(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('ExtSamp', state)
def getExtSamp():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('ExtSamp')
    return(state)
# Remote start from cellphone checkbox
def storeRemoteStart(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('RemoteStart', state)
def getRemoteStart():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('RemoteStart')
    return(state)
# Remote start from cellphone checkbox
def storeDualSamples(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('DualSamples', state)
def getDualSamples():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('DualSamples')
    return(state)
# Bottle Size step size option
def storeBottleSizeStep(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('BottleStepSize', state)
def getBottleSizeStep():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('BottleStepSize')
    return(state)
# Checkboxes - and ther hide state in user mode
def storeCheckBoxStates(states):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('checkboxstate', states)
def getCheckBoxStates():
    settings = QSettings("Colifast", "ALARM")
    states = settings.value('checkboxstate')
    return(states)


# Test frequency chosen by user: (index)
def storeFrequency(freq):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('frequency', freq)
def getFrequency():
    settings = QSettings("Colifast", "ALARM")
    stored_freq = settings.value("frequency")
    return stored_freq
# Analysis index:
def storeTargetBacteria(bact):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('bacteria', bact)
def getTargetBacteria():
    settings = QSettings("Colifast", "ALARM")
    bact = settings.value('bacteria')
    return bact
# Number of samples to execute: (index)
def storeSamplesNr(samples_nr):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('samples', samples_nr)
def getSamplesNr():
    settings = QSettings("Colifast", "ALARM")
    samples_nr = settings.value('samples')
    return samples_nr
# Number of samples in Bottle: (index)
def storeBottleSize(bottle_size):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('bottle_size', bottle_size)
def getBottleSize():
    settings = QSettings("Colifast", "ALARM")
    samples_nr = settings.value('bottle_size')
    return samples_nr
# Number of samples remaining in media:
def storeRemaining(samples_medium):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('remaining samples', samples_medium)
def getRemaining():
    settings = QSettings("Colifast", "ALARM")
    samples_medium = settings.value('remaining samples')
    return samples_medium
# Number of samples executed by the method_handler:
def storeSamplesDone(samples_done):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('samples_done', samples_done)
def getSamplesDone():
    settings = QSettings("Colifast", "ALARM")
    samples_done = settings.value('samples_done')
    return samples_done
# Time of executing the method_handler:
def storeStartTime(time):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('time', time)
def getStartTime():
    settings = QSettings("Colifast", "ALARM")
    time = settings.value('time')
    return time

# Sample source variable
def storeSampleSource(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('SampleSource', state)
def getSampleSource():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('SampleSource')
    return(state)
# series plot vs. n-samples to plot
def storePlotSeries(state):
    settings = QSettings("Colifast", "ALARM")  # ("Company", "Product")
    settings.setValue('PlotSeries', state)
def getPlotSeries():
    settings = QSettings("Colifast", "ALARM")
    state = settings.value('PlotSeries')
    return(state)

### SFM VALUES ###
def storeCalTurb10(CalTurb):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Calturb10", CalTurb)
    #stored_email = settings.value("Calturb10")
def getCalTurb10():
    settings = QSettings("Colifast", "ALARM")
    stored_email = settings.value("Calturb10")
    return stored_email

def storeCalTurb5(CalTurb):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Calturb5", CalTurb)
def getCalTurb5():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Calturb5")
    return stored_value

def storeCalTurb0(CalTurb):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Calturb0", CalTurb)
def getCalTurb0():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Calturb0")
    return stored_value

def storeWavelengthTurb(Wavelength):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("WLTurb", Wavelength)
def getWavelengthTurb():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("WLTurb")
    return stored_value

def storeWavelengthFluo(Wavelength):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("WLFluo", Wavelength)
def getWavelengthFluo():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("WlFluo")
    return stored_value

def storeIntegrationTime(value):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Integration", value)
def getIntegrationTime():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Integration")
    return stored_value

def storeThresholdTurb(Value):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("ThTurb", Value)
def getThresholdTurb():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("ThTurb")
    return stored_value

def storeThresholdFluo(Value):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("ThFluo", Value)
def getThresholdFluo():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("ThFluo")
    return stored_value

def storeAvrSampleNr(Value):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("avrSampleNr", Value)
def getAvrSampleNr():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("avrSampleNr")
    return stored_value

## Liquid Handling ##
def storeMPVcom(mpv):    # store string
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("mpv_com", mpv)
def getMPVcom():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("mpv_com")
    return stored_value

def storeXLPcom(xlp):    # store integer
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("xlp_com", xlp)
def getXLPcom():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("xlp_com")
    return stored_value

def storePumpSize(volume):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Pump_size", volume)
def getPumpSize():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Pump_size")
    return stored_value

def storeVolume(volume):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Volume", volume)
def getVolume():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Volume")
    return stored_value

def storeFlowrate(flow):
    settings = QSettings("Colifast", "ALARM")
    settings.setValue("Flowrate", flow)
def getFlowrate():
    settings = QSettings("Colifast", "ALARM")
    stored_value = settings.value("Flowrate")
    return stored_value



## Set default values of settings ##
# Set initial colors of colorful theme, if never done before
def preset_values():
    if not getColors():
        tup = tuple(['#0c81c4', '#c47b0c', '#0c6bc4', '#0cc481', '#0c25c4', 196, 239])
        storeColors(tup)
    # Values
    # Turbidity
    if not getThresholdTurb():
        storeThresholdTurb(4)
    # Fluorescence
    if not getThresholdFluo():
        storeThresholdFluo(1.5)
    # CHECKBOXES
    if not getCheckBoxStates():
        storeCheckBoxStates(["0", "0", "0", "0", "0"])
    # # Bottle size
    # if not getBottleSize():
    #     storeBottleSize(21)
    #     storeRemaining(21)
        # self.update_medium_progress_bar(new_flask=True)  
    # Sample source
    if not getSampleSource():
        storeSampleSource("sample")      
    # Frequency
    if getFrequency() == None:
        storeFrequency(1)
    # Target Bacteria
    if not getTargetBacteria():
        storeTargetBacteria("E.coli - 37 °C")
    # sodium thio
    if not getSodiumThio():
        storeSodiumThio(0)
    # Ext sample
    if not getExtSamp():
        storeExtSamp(0)
    # Wavelength - Fluo
    if not getWavelengthFluo():
        storeWavelengthFluo(int(430))
    # Wavelength - Turb
    if not getWavelengthTurb():
        storeWavelengthTurb(int(860))
    # Turb cal 0
    if not getCalTurb0():
        storeCalTurb0(int(1711.0))
    # Turb cal 10
    if not getCalTurb10():
        storeCalTurb10(int(4038.833))
    # Step size for bottles
    if not getBottleSizeStep():
        storeBottleSizeStep(0)
    # Syringe pumpe size
    if not getPumpSize():
        storePumpSize(25000)



mainWindow = None

stop_after_this = False

emergency_exit = False

end_sample_time = None