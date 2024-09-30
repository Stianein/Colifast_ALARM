## MANAGER FILE FOR Colifast ALARM GUI ##
# Author: Stian Eide Ingebrigtsen

""" Colifast ALARM MANAGER 
Displays the full Colifast ALARM GUI. It contains or call the component interfaces, found in python designer files folder. 
It Calls the method_helper file to start a long running sample analysis in a separate thread. 
"""

from python_designer_files.Colifast_ALARM import Ui_MainWindow

# PyQt related
from PyQt5.QtGui import (
    QPainter, QPixmap, QMouseEvent, QPalette, QTextCharFormat, QIcon, QColor, QBrush
)
from PyQt5.QtCore import (
    Qt, QPoint, QCoreApplication,
    QThread, pyqtSignal, QDate, QTimer, QFile, QTextStream, QUrl
)
from PyQt5.QtWidgets import (
    QLineEdit, QGroupBox, QGraphicsProxyWidget, QGraphicsLinearLayout, QSlider,
    QHBoxLayout, QVBoxLayout, QLabel, QButtonGroup, QRadioButton, QInputDialog,
    QPushButton, QGraphicsPixmapItem, QGraphicsView, QGraphicsScene, QTabBar,
    QMainWindow, QMessageBox, QToolButton, QDockWidget, QGraphicsItem,
    QWidget, QApplication, QSizePolicy, QDialog, QFileDialog, QCheckBox, QMenu, QAction,
    QTextBrowser
)
from PyQt5.QtSvg import QSvgRenderer
# from PyQt5.QtWebEngineWidgets import QWebEngineView

# PyQt helper modules
import pyqtgraph as pg

# Packages
import sys
import time
import os
import matplotlib.pyplot as plt
import glob
import logging
from logging import FileHandler
import datetime
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
from collections import deque
from resource_path import resource_path
import traceback

# COMPONENT IMPORTS #
import settings
import method_helper
from components.adu.adu import adu
import components.xlp as xlp
import components.sfm as sfm
import components.mpv as mpv

## ADVANCED MODE IMPORTS ##
from python_designer_files.ADUadv_generator import ADUadv

from python_designer_files.spectrometer import Ui_Form as spectrometer_window
from python_designer_files.LogIn import Ui_Dialog as Ui_login
from python_designer_files.Error_message_dialog import Ui_Dialog as Ui_ErrorDialog
import python_designer_files.clock_time_picker as time_pckr
import python_designer_files.editor as editor


# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_directory = os.path.dirname(current_file_directory)
# Relative path to file location with resource path compiling to exe with pyinstaller
path = resource_path(current_file_directory)

## CREATE FOLDERS UPON FIRST TIME USE ##
# Base directory for app - location for storing reports, database(APPDATA), methods, and logs.
base_dir = "C:\\Colifast"
# Check if the directory exists
if not os.path.exists(base_dir):
    # Create the base directory if it doesn't exist
    os.mkdir(base_dir)
# Reports directory
results_folder_path = os.path.join(base_dir, "Reports")
if not os.path.exists(results_folder_path):
    # Create the subdirectory if it doesn't exist
    os.mkdir(results_folder_path)
# Save path to settings file
settings.storeResultFolder(results_folder_path)
# Logs directory
Logs_path = os.path.join(base_dir, "Logs")
# Check if the subdirectory exists
if not os.path.exists(Logs_path):
    # Create the subdirectory if it doesn't exist
    os.mkdir(Logs_path)
# Save path to settings file
settings.storeLogsFolder(Logs_path)
# Methods directory
method_files_path = os.path.join(base_dir, "Methods")
if not os.path.exists(method_files_path):
    os.mkdir(method_files_path)
# Save an initial method file path
if not settings.getMethod():
    settings.storeMethod(method_files_path)

# MainWindow class
class Colifast_ALARM(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.max = False
        # size

        # Assignments
        self.setupUi(self)
        # Hidden menues at start up
        self.leftSubContainer.hide()
        self.leftContainer.hide()
        # self.moreOptions.hide()
        # self.methodOptions.hide()
        # self.bottleSize.hide()
        # self.historyOptions.hide()
        # self.advancedMenu.hide()
        # self.hideCheckBox.hide()

        # Set color manually
        self.headerContainer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headerContainer.customContextMenuRequested.connect(self.show_context_menu)

        # Run initial setting of values upon first time use
        settings.preset_values()

        ### GET VALUES FROM SETTINGS ###
        ## Sample numbers ##
        # Bottle size #
        if not settings.getBottleSize() or settings.getBottleSize() == 0:
            # force show objects for choosing bottle size, if not set
            self.bottleSize.show()
            self.leftSubContainer.show()
            self.leftContainer.show()
            self.moreOptions.show()
            self.bottleSizeWarning.show()
            # progressBar
            self.remainingSamples.setMaximum(0)
            self.remainingSamples.setFormat("0/0")
        else:
            self.bottleSizeWarning.hide()
        # Resett run stop signal upon start up in case program was closed before reset
        settings.setstopSignal(0)
        # Update the progress bar for medium consumption
        self.update_medium_progress_bar()

        ### Logger, and Data Visualization ###
        ## LOG ##
        self.setup_logging()
        # Initialize classes
        self.worker_thread = WorkerThread(self)
        self.scheduler = BackgroundScheduler()
        self.mobileRemoteToggle = GSM_listner(self)
        # Status bar signal from worker thread long running bact sample
        self.worker_thread.status_message.connect(self.setStatus)
        # Update plot signal from worker thread to plot data in GUI
        self.worker_thread.update_plot.connect(self.plot_historic_data)

        # Warning signal from worker - pause execution until user has done somehting
        self.worker_thread.warning_signal.connect(self.warning_message)

        # initialize id variable
        self.sample_id = None
        # Starting Time text
        self.worker_thread.startTime.connect(self.startTime)
        self.startingTime.setText("Start Time")
        # ALARM fields text
        self.worker_thread.bactAlarm.connect(self.bactAlarm)
        self.worker_thread.turbAlarm.connect(self.turbAlarm)
        # Status browser queue variable
        self.status_queue = deque(maxlen=2)

        ### BUTTONS, CHECKBOXES AND DROP-DOWNS ###
        # Lay a hidden button under the progressbar to enable resetting of bottle upon changing to a new flask
        self.hiddenButton = QPushButton(self.remainingSamples)
        self.hiddenButton.setObjectName("hiddenButton")
        # Set the geometry of the hidden button to match the progress bar
        self.hiddenButton.setGeometry(self.remainingSamples.geometry())
        # Tooltip
        self.hiddenButton.setToolTip("Medium indicator - click to update bottle")
        # Style the button to be hidden
        self.hiddenButton.setStyleSheet("background-color: transparent; border: none; text-align: center;")

        ## Side menu ##
        # Show
        self.menuBtn.clicked.connect(self.show_menu)
        # Hidden button for new flask update below progressbar
        self.hiddenButton.clicked.connect(self.progBar_clicked)
        # Medium #
        # Bottle menu click
        # Connect menu actions to toggle_menu
        self.bottleSizeBtn.clicked.connect(lambda: self.toggle_menu("bottle"))
        self.methodBtn.clicked.connect(lambda: self.toggle_menu("method"))
        self.historyBtn.clicked.connect(lambda: self.toggle_menu("history"))
        self.reportBtn.clicked.connect(lambda: self.toggle_menu("report"))


        # self.bottleSizeBtn.clicked.connect(lambda: self.toggle_more_options_menu(0))
        # Change value for bottle size
        self.bottleSize.valueChanged.connect(lambda: self.bottle_changer(False))
        # method options #
        # self.methodBtn.clicked.connect(lambda: self.toggle_more_options_menu(1))
        # history options
        # self.historyBtn.clicked.connect(lambda: self.toggle_more_options_menu(2))
        # Report options
        # self.reportBtn.clicked.connect(lambda: self.toggle_more_options_menu(3))
        # other values for bottle size than are dividable by the 7 (days of the week)
        self.otherValues.clicked.connect(self.update_bottle_size_manual_option)
        # Styling buttons
        self.dark_mode.clicked.connect(lambda: self.change_stylesheet("dark_mode"))
        self.classic_style.clicked.connect(lambda: self.change_stylesheet("classic"))
        self.colorfull.clicked.connect(lambda: self.change_stylesheet("color"))
        # Initial loading of style, if not stored in settings load classic theme
        try:
            style = settings.getStyle()
        except:
            style = "classic"
        print("Style: ", style)
        self.change_stylesheet(style)

        ## SET CHECKBOX STATE AT STARTUP ##
        # Sodium Thiosulfate - set status of check box
        sodium_thio = settings.getSodiumThio()
        if sodium_thio is not None:
            self.sodiumThio.setChecked(sodium_thio)

        # External Sample -  set status of check box
        external_sample = settings.getExtSamp()
        if external_sample is not None:
            self.externalSample.setChecked(external_sample)

        # Delay Start Time - set status of check box
        delay = settings.getDelayStart()
        if delay is not None:
            self.delayStartTime.setChecked(delay)

        # Plotting option for series - set status of check box
        plot_series = settings.getPlotSeries()
        if plot_series is not None:
            self.fullSeries.setChecked(plot_series)

        # Remote control from phone - set status of check box
        remote = settings.getRemoteStart()
        if remote is not None:
            self.remoteStart.setChecked(remote)
            self.update_remote_start()

        # Dual sampling from two sources - set status of check box
        dual = settings.getDualSamples()
        if dual is not None:
            self.dualSamples.setChecked(dual)

        # Set the sample source settings value and label
        source = settings.getSampleSource()
        if source is not None and dual:
            if source == 5:
                next_source = "sample 2"
            else:
                next_source = "sample 1"
            self.sampleSource.show()
            string = f"next source: {next_source}"
            self.sampleSource.setText(string)
        else:
            self.sampleSource.hide()

        # bottle option step size checkbox
        stepchecked = settings.getBottleSizeStep()
        if stepchecked is not None:
            self.otherValues.setChecked(stepchecked)
        self.update_bottle_size_manual_option()

        self.checkBoxes = [self.hideAlternateSample, self.hideDelayStart, self.hideExtSamp, self.hideRemoteStart, self.hideSoduimThio]
        self.checkBoxes_options = [self.frame_23, self.frame_19, self.frame_11, self.frame_22, self.frame_10]
        # make common update function for checkboxes that should be hidden in user mode
        for i, checkbox in enumerate(self.checkBoxes):
            list = settings.getCheckBoxStates()
            if list[i] == "2":
                self.checkBoxes_options[i].hide()
            checkbox.setChecked(int(list[i]))
            if checkbox:
                checkbox.stateChanged.connect(self.update_checkbox_state)

        ## Options & choices ##
        # sodium thiosulfat
        self.sodiumThio.clicked.connect(self.update_sodium_thio_status) # Upon cliking the checkbox emit new signal
        # Delay Start Time
        self.delayStartTime.clicked.connect(self.update_delay_start_time) # Upon cliking the checkbox emit new signal
        # External sample #
        self.externalSample.clicked.connect(self.update_external_sample_status) # Upon cliking the checkbox emit new signal
        # Remote cellphone start
        self.remoteStart.clicked.connect(self.update_remote_start) # Upon cliking the checkbox emit new signal
        # Dual samples alternating
        self.dualSamples.clicked.connect(self.update_dual_samples)
        # GSM listner for mobile start toggle signal
        self.call_start = False
        self.mobileRemoteToggle.call_start.connect(self.call_start_toggler)
        # Deciding/accepting a bottle size
        self.acceptBottleSize.clicked.connect(lambda: self.bottle_changer(True)) # function to get bottle size

        # Target bacterium to analyse
        self.target_bact = self.bact_box.currentIndexChanged.connect(self.target_bact_changer)
        # Frequency of sampling
        self.freq_box.currentIndexChanged.connect(self.sample_frequency_changer)
        ## Set the initial values for the Combo Boxes ##
        # Target bacteria
        self.bact_box.setCurrentText(settings.getTargetBacteria())
        # Frequency
        frequency = self.get_frequency()
        self.freq_box.setCurrentIndex(frequency)
        #self.sample_frequency_changer()

        ## History menu ##
        # update the chosen date
        self.historyCalendar.selectionChanged.connect(self.handleDateSelection)
        # Deactivate dates by default
        self.historyCalendar.setDateEditEnabled(False)  # Disable date editing for all dates
        # Date variable
        self.selected_date = None
        # Update calendar with dates with data upon launche
        self.handleDateSelection()
        # Plot the chosen date from calendar when clicked
        self.plotBtn.clicked.connect(lambda: self.plot_historic_data(date=self.selected_date))
        # Create report for chosen date from calendar
        self.createReport.clicked.connect(lambda: self.data_collection_for_report(date=self.selected_date))
        # Slider for choosing multiple dates changed
        self.horizontalSlider.valueChanged.connect(self.n_samples)
        self.fullSeries.stateChanged.connect(self.update_slider_state)

        ## SCHEDUALING ##
        # Slider for schedualing sample runs
        # self.dayScheduler.valueChanged.connect(self.sched_samples)
        # self.dayScheduler.setValue(settings.getBottleSize())
        # Hide schedualer menu
        # self.shedualerMenu.hide()

        ## Method File ##
        # populate the method file drop-down #
        self.methodDropDown()
        # Update the selected method file #
        method_file = self.methodSelector.currentIndexChanged.connect(self.method_file_changer)

        # Advanced settings #
        self.advancedMenu.hide()
        self.advSettingsBtn.clicked.connect(self.adv_settings)
        # self.advanced_settings = None

        # Show the right page for the right menu chosen in advanced menu
        self.backBtn.clicked.connect(lambda: self.advmenu_button_click(0))
        self.manualBtn.clicked.connect(lambda: self.advmenu_button_click(1))
        self.aduBtn.clicked.connect(lambda: self.advmenu_button_click(1))#lambda: self.stackedWidget.setCurrentIndex(1))
        self.sfmBtn.clicked.connect(lambda: self.advmenu_button_click(2))
        self.liquidBtn.clicked.connect(lambda: self.advmenu_button_click(3))
        self.txteditorBtn.clicked.connect(lambda: self.advmenu_button_click(4))
        

        ## Start/stop Buttons ##
        self.startNewMethod.clicked.connect(self.toggle_worker)
        self.worker_thread.error_msg.connect(self.show_error_message)
        self.worker_thread.finished_signal.connect(self.finished_run)
        # Variable for stoping program after current samples end
        self.stop_after_current_sample = False 
        # Context menu for right-clicking start/stop button to allow for multiple options: abort run, or stop after sample has finnished
        self.startNewMethod.setContextMenuPolicy(Qt.CustomContextMenu)
        # Right-click for options; abort_or_stop_after_current method
        self.startNewMethod.customContextMenuRequested.connect(self.abort_or_stop_after_current)

        # Initialize variables for tracking the window position ### GUI Design ## Window control # Moving
        self.dragging = False
        self.resizing = False
        self.diagonal = False
        self.horisontal = False
        self.vertical = False
        self.offset = QPoint(0, 0)

        # Window control buttons #
        self.closebtn.clicked.connect(self.close_all_windows)
        self.restorebtn.clicked.connect(self.toggle_maximized)
        self.minimizebtn.clicked.connect(self.minimize_window)


        # Load manual html file and attach it to the manual page
        with open(resource_path(os.path.join(path, "docs", "manual.html"))) as file:
            html_content = file.read()

        # Load the HTML into the QTextBrowser from the designer file
        self.manualBrowserText.setHtml(html_content)
        # set the size of the window  on opening
        self.resize(800, 600)
        self.setMaximumSize(800, 600)

    ### Method Start/Stop functions ###
    ## Start/Stop current run ##
    def start_updater(self):
        # Update icon and tooltip
        self.icon_changer_for_color_maintenance([self.startNewMethod], ["square.svg"])
        self.startNewMethod.setToolTip("Stop Run")
        # Clear previous status browsing
        self.status_queue.clear()

    def stop_updater(self):
        # Update icon and tooltip
        self.icon_changer_for_color_maintenance([self.startNewMethod], ["play.svg"])
        self.startNewMethod.setToolTip("Start Run")

    def toggle_worker(self):
        # TURN ON - START METHOD
        # There is not a sample run scheduled
        if not self.startNewMethod.isChecked():
            # Abort/return if there are no more medium left and the user has not inserted a new bottle
            if not self.check_medium_status():
                return
            # Prompt the user for delay before start if that option is checked
            if self.delayStartTime.checkState():
                dialog = TimeSelectorDialog(self)
                start_delay = dialog.get_chosen_time()
                if start_delay:
                    print("Start time:", start_delay)
                # Abort if the user exits the delay window
                else:
                    # ReCheck the button as the click UnChecked it, but the user aborted
                    self.startNewMethod.setChecked(True)
                    # self.call_start = True
                    return

            # Set stopsignal to False  upon starting a new run
            settings.setstopSignal(0)

            # Change icon as run has started
            self.startNewMethod.setChecked(False)
            # self.call_start = False # Can't call to start when a run is already started
            self.start_updater()

            # Start run with delay
            if self.delayStartTime.checkState():
                self.sample_scheduler(start_time=start_delay)
                string = f"Delay first sample, {self.datetimestringler(start_delay)}"
                self.setStatus(string)
            # Start run without delay
            else:
                self.sample_scheduler(start_time=datetime.datetime.now())


        # TURN OFF - STOP
        # There are already a scheduler running
        else:
            # Warn the user one extra time before stoping
            accept = self.show_error_message("You are about to stop the run.")
            if accept:
                # Set stopsignal high
                settings.setstopSignal(1)
                self.setStatus("Stoped")
                self.stop_updater()
                self.setStatus("Aborting all scheduled runs...")

                if not settings.getFrequency() == 0:
                    try:
                        self.scheduler.remove_all_jobs()
                        self.scheduler.shutdown()
                    except:
                        pass
                    # Start up scheduler again for next start
                    self.scheduler = BackgroundScheduler()
                # Reset the stop after current sample parameter
                self.stop_after_current_sample = False

            else:
                # UnCheck the button as the click checked it, but the user reconsidered by X ing out the stop window
                self.startNewMethod.setChecked(False)
                
                return

    # Function to activate a stop after current sample
    def delete_future_samples_and_stop_after_current(self):
        # If there is a current run
        if not self.startNewMethod.isChecked():
            # Update status browser
            self.setStatus("The run is stopping after current sample")
            current_text = self.startingTime.text()
            self.startTime(f"The run is stopping after current sample \n\n{current_text}")

            if self.startNewMethod.isChecked():
                self.stop_updater()
            # Set the stop after current variable to true
            self.stop_after_current_sample = True
        else:
            self.setStatus("Future runs have been aborted, run was ended")
        # Update the call_Start variable
        self.call_start = False
        # Remove futur runs, and restart scheduler for next run
        self.future_samples = []
        # Try to shut down scheduler and reopen it if that does not work, it is allready shut down, so reopen the instance
        try:
            self.scheduler.remove_all_jobs()
            self.scheduler.shutdown()
            # Start up scheduler again for next start
            self.scheduler = BackgroundScheduler()
        except:
            # Start up scheduler again for next start
            self.scheduler = BackgroundScheduler()


    # Function to allow the user to stop the run after the current run has ended
    def abort_or_stop_after_current(self, position):
        # If the method is not running you can't stop it - return
        if not self.startNewMethod.isChecked():
            # Make a menu when right-click
            context_menu = QMenu(self)
            context_menu.setObjectName("customContextMenu")
            how_to_stop_action = QAction("Stop run after current sample has ended", self)
            how_to_stop_action.triggered.connect(self.delete_future_samples_and_stop_after_current)
            context_menu.addAction(how_to_stop_action)
            
            # Temporarily disable the button to prevent triggering
            self.startNewMethod.setEnabled(False)
            
            # Get the global position for the context menu
            global_position = self.startNewMethod.mapToGlobal(position)
            context_menu.exec_(global_position)
            
            # Re-enable the button after the menu closes
            self.startNewMethod.setEnabled(True)



    ## Scheduler preset functions ##
    def sample_scheduler(self, samples=None, start_time=None):
        """Starts the scheduler for running samples
        
        :param samples: Amount of samples the program shall run.
        :type samples: int 
        :param start_time: Delay time for when the first scheduled sample is to be started.
        :type start_time: datetime.datetime
        """
               
        # Update samples if it is not passed as argument
        if samples == None:
            samples=settings.getSamplesNr()

        # Log and Data handling
        if not self.database_and_logging_run(start_time, samples):
            settings.setstopSignal(1)
            self.setStatus("Stoped")
            self.stop_updater()
            return

        # get the frequency preset
        interval = settings.getFrequency()

        # Continuous sample runs are started again imediately after end of run
        if interval == 0:
            self.scheduler.add_job(self.start_new_sample, 'date', run_date=start_time, misfire_grace_time=30)

        # Interval runs are stored in the scheduler and runs are calculated in the future_samples list
        else:
            # caclculate the future runs based on intervall and samples as well as the start time
            self.update_future_samples(samples, start_time)
            # Add run to the scheduler
            self.scheduler.add_job(self.start_new_sample, 'date', run_date=self.future_samples[0], misfire_grace_time=30)

        # Start the scheduler and therby the first sample of the current run
        self.scheduler.start()
        print("starting scheduler")


    # Function to update the future_samples (interval/non-continuous runs),
    # to allow for mobile start/stop control of the runs
    def update_future_samples(self, samples, start_time):
        interval = settings.getFrequency()
        # For scheduler
        self.future_samples = []
        # Store relevant data for each run as well as adding the strating point for future runs to the scheduler
        for i in range(samples):
            # Calculate the next run
            self.future_samples.append(start_time + datetime.timedelta(days=i*interval))

    # Function collect data, and handle continuation of scheduled runs when
    # a sample is finished and handle icon change when run has finished
    def finished_run(self):
        # In case the method is not meant to create datapoints in the database, 
        # this try/except wrapping makes the program ignore all the lacking data values.
        try:
            print("IN Finished_run!!!  samp, remain; ", settings.getSamplesNr(), settings.getRemaining())
            # Get data from sample id
            db  = DatabaseHandler()
            data = db.fetch_data("SELECT sample_start_time, sample_number FROM SampleInfo WHERE id = ?", self.sample_id)

            # Calculate run time from end time - start time
            start_time = self.datetimestringler(data[0][0])
            sample_number = data[0][1]
            end_time = datetime.datetime.now()
            sample_time = end_time - start_time

            # Update to database with total sample time
            db.execute_query("UPDATE SampleInfo SET full_sample_time = ? WHERE id = ?", str(sample_time), self.sample_id)


            # Update progressbar and change sample running icon
            self.update_medium_progress_bar()

            # Update the alternating sample source if that option is checked
            if self.dualSamples.checkState():
                self.update_dual_samples()

            self.log.info(f"sample_nmb: {sample_number} settings: {settings.getSamplesNr()} Settings remain: {settings.getRemaining()}")
            # THE LAST SAMPLE HAS FINISHED #
            if sample_number >= settings.getSamplesNr() or settings.getRemaining() <= 0:
                print("sample_nmb: ", sample_number, "settings: ", settings.getSamplesNr(), "Settings remain: ", settings.getRemaining())
                self.mobileRemoteToggle.stop()
                # Update start/stop button
                self.startNewMethod.setChecked(True)
                self.stop_updater()
                # if not settings.getFrequency() == 0:
                if not settings.getFrequency() == 0:
                    self.scheduler.remove_all_jobs()
                    self.scheduler.shutdown()
                    self.scheduler = BackgroundScheduler()

                self.setStatus("All the scheduled runs have finished, add a new bottle of medium and start a new run")

            # THERE ARE MORE SAMPLES IN THE RUN #
            else:
                # Aborting run now after this sample as the user has clicked/called for it 
                if self.stop_after_current_sample:
                    # Reset the stop after current sample parameter
                    self.stop_after_current_sample = False
                    self.setStatus("The run was stoped now, after ended sample")
                    # Print awaiting remote start to status browser if there are more samples left in the medium container
                    if settings.getRemaining() > 0:
                        time.sleep(1)
                        self.setStatus("Awaiting remote start...")
                    self.stop_updater()
                    self.startNewMethod.setChecked(True)
                    return
                # If the run is continuous the next sample is just started imediately.
                if settings.getFrequency() == 0:
                    # A control check if the user has stoped the program without it being handled by the software
                    if self.startNewMethod.isChecked():
                        self.setStatus("The user has stoped the run")
                        return
                    else:
                        self.start_new_sample()
                # If the run is following intervals between samples, the next run is started with a delay.
                else:
                    try:
                        # Pop the old futur sample from the list, so that the next is executed
                        self.future_samples.pop(0)
                    except:
                        self.log.info("No future samples found")
                    # If remote start is set, check if it is activated, or wait for activation
                    if settings.getRemoteStart():
                        if not self.call_start:
                            self.future_samples = []
                            self.setStatus("Awaiting remote start...")
                            return
                        else:
                            pass
                    # ADD the next job to the scheduler - this way the only info about futur run is kept in future_samples list,
                    # and can thus be modified here, before it is added to the scheduler(mobstart or other features for start/stop)
                    
                    # TESTING
                    self.log.info(f"Future samples: {self.future_samples} LEngth: {len(self.future_samples)}")

                    self.scheduler.add_job(self.start_new_sample, 'date', run_date=self.future_samples[0], misfire_grace_time=30)
                    # TESTING
                    self.log.info("scheduler has done its job")

                    next_sample = self.datetimestringler(self.future_samples[0])
                    # Update next sample in status browser
                    string = f"Next sample is scheduled at: {next_sample}"
                    self.setStatus(string)

        except Exception as e:
            self.log.error("An unexpected error occurred while scheduling a job.")
            self.log.error(traceback.format_exc())
            print("The finish run function stalled, you might be running a calibration method, or other service methods?")
        return


    # Start a new run in the worker thread
    def start_new_sample(self):
        # Update medium status and icon
        self.update_medium_progress_bar()
        db = DatabaseHandler()
        # Update the start/stop button
        self.startNewMethod.setChecked(False)
        self.start_updater()

        ## COLLECT AND STORE DATA ##
        # Sample
        try:
            # Increase the previous sample number by one for this sample
            sample_number = db.fetch_data("SELECT sample_number FROM SampleInfo WHERE id = ?", self.sample_id)[0][0]
            print(sample_number, "DB")
            #sample_number = settings.getSamplesNr() -
        except:
            if settings.getRemaining() != 0 and settings.getRemaining() != settings.getSamplesNr():
                sample_number = db.fetch_data("SELECT MAX(sample_number) FROM SampleInfo WHERE id IN(SELECT MAX(id) FROM SampleInfo)")[0][0] + 1
            else:
                sample_number = 1
                print(sample_number, "set to 1")
        # Timing
        timing = self.datetimestringler(datetime.datetime.now())
        ## STORE SAMPLE INFO FOR THE CURRENT SAMPLE ##
        query = "INSERT INTO SampleInfo (sample_number, run_id, date, sample_start_time, external_sample, sodium_thiosulfate) VALUES (?, ?, ?, ?, ?, ?)"
        args = (sample_number, self.run_id, timing[:10], timing, settings.getExtSamp(), settings.getSodiumThio())
        db.execute_query(query, *args)
        # Get sample id
        self.sample_id =  db.fetch_data("SELECT id FROM SampleInfo WHERE sample_start_time = ?", timing)[0][0]
        # Start the sample in its separate thread
        self.worker_thread.set_sample_id(self.sample_id)
        self.worker_thread.start()
        # Logging sample
        number = (settings.getSamplesNr() + 1) - settings.getRemaining()
        print("number: ", number)
        string_1 = f"\n\n\nSTARTING RUN\nSample number {number} of {settings.getSamplesNr()}"
        self.log.info(string_1)
        string_2 = f"Sample id:\t\t\t{self.sample_id}\nStart time:\t\t\t{timing}"
        self.log.info(string_2)


    # Function to start the Logger, and store relevant data in run info - executed at start of scheduler
    def database_and_logging_run(self, start_time, samples):
        global path
        # Open access to data base
        db = DatabaseHandler()

        ## Fetch the latest bottle number value ##
        result = db.fetch_data("SELECT MAX(bottle_number) FROM RunInfo")
        print("result bottles: ", result)
        try:
            max_bottle_number = result[0][0] if result and result[0][0] is not None else 0
        except:
            # Bottle nmb 1 if there is no earlier data
            self.bottle_number = 1

        # Capture start time
        self.start_pressed = datetime.datetime.now()

        ## LOGGING ##
        # Check if a log handler already exists; if so, close it if it is not a continuation of an ongoing bottle.
        if settings.getRemaining() != settings.getBottleSize():
            try:
                # Print to log
                string = f"\n\n\nTHE ABORTED RUN WAS RESTARTED\There is {settings.getRemaining()} sample(s) left out of {settings.getBottleSize()} total samples"
                self.log.info(string)
            except:
                # look for the latest log file
                log_files = glob.glob(os.path.join(settings.getLogsFolder(), "*.log"))
                print(settings.getLogsFolder())

                if not log_files:
                    print("Thats weired No log files to be found, but a run has been conducted...")
                    return None  # No log files found

                # Sort log files by modification time (most recent first)
                log_files.sort(key=os.path.getmtime, reverse=True)

                # Create a new log handler for the current sample run
                self.log_handler = self.create_log_handler(file=log_files[0])

                # Create a logger if not already created
                try:
                    self.log.addHandler(self.log_handler)
                except AttributeError:
                    # Logger object doesn't exist, create a new one
                    self.log = logging.getLogger("method_logger")
                    self.log.setLevel(logging.INFO)
                    self.log.addHandler(self.log_handler)

                # Print to log
                string_2 = f"\n\n\nTHE ABORTED RUN WAS RESTARTED\nThere is {settings.getRemaining()} sample(s) left out of {settings.getBottleSize()} total samples"
                self.log.info(string_2)

                self.bottle_number = max_bottle_number
                self.run_id = db.fetch_data("SELECT id FROM RunInfo WHERE bottle_number = ?", self.bottle_number)[0][0]

        # Store log and data for a New Run
        else:
            try:
                self.log_handler.close()
            except:
                pass

            # Create a new log handler for the current sample run
            self.log_handler = self.create_log_handler(start_time=self.start_pressed)

            # Create a logger if not already created
            try:
                self.log.addHandler(self.log_handler)
            except AttributeError:
                # Logger object doesn't exist, create a new one
                self.log = logging.getLogger("method_logger")
                self.log.setLevel(logging.INFO)
                self.log.addHandler(self.log_handler)

            self.log.info("### NEW SAMPLE RUN ###")

            # Get spectrophotometer serial number
            try:
                sfm_serial_number = sfm.get_connected_devices()[0].serial_number
            except:
                dialog = ErrorDialog("The spectrophotometer is not connected")
                accepted = dialog.exec_()
                if accepted == QDialog.Accepted:
                    self.startNewMethod.setChecked(True)
                    return False
                else:
                    sfm_serial_number = "Not connected"
            # Update bottle number for this new run
            self.bottle_number = max_bottle_number + 1

            ## STORE RUN INFO FOR THE WHOLE BOTTLE ##
            db.execute_query('''
            INSERT INTO RunInfo (
                bottle_number, media_bottle_size, run_start_time,
                fluorescent_threshold_ratio, turbidity_threshold, turbidity_raw0, turbidity_raw5,
                turbidity_raw10, target_bacteria, method_file, sample_frequency, spectrometer_serial_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                self.bottle_number, settings.getBottleSize(), self.datetimestringler(start_time),
                settings.getThresholdFluo(), settings.getThresholdTurb(), settings.getCalTurb0(),
                settings.getCalTurb5(), settings.getCalTurb10(), settings.getTargetBacteria(),
                settings.getMethod(), settings.getFrequency(), sfm_serial_number
            )

            serial_number = db.fetch_data("SELECT instrument_serial_number FROM InstrumentInfo")[0][0]
            if self.delayStartTime.checkState():
                delay_info = start_time
            else:
                delay_info = "No delay"
            # Fetch the id of current run
            self.run_id = db.fetch_data("SELECT id FROM RunInfo WHERE bottle_number = ?", self.bottle_number)[0][0]
            # Run info
            string_3 = f"RUN INFO\tBottle number: {self.bottle_number}\tRun_id: {self.run_id}\nBottle size:\t\t\t\t{settings.getBottleSize()}\
\nRun started:\t\t\t\t{self.datetimestringler(self.start_pressed)}\nDelay:\t\t\t\t\t{delay_info}"
            self.log.info(string_3)
            # Method info
            string_4 = f"\nDETECTION VALUES\nFLUORESCENSE\nFluorescent threshold ratio:\t\t{settings.getThresholdFluo()}\nTURBIDITY\n\
Turbidity threshold:\t\t\t{settings.getThresholdTurb()}\nTurbidity raw zero value:\t\t{settings.getCalTurb0()}\n\
Turbidity raw 5 value:\t\t\t{settings.getCalTurb5()}\nTurbidity raw 10 value:\t\t\t{settings.getCalTurb10()}\n"
            self.log.info(string_4)
            # Method info
            string_5 = f"METHOD INFO\nMethod file:\t\t\t\t{os.path.basename(settings.getMethod())}\nTarget Bacteria:\
\t\t\t{settings.getTargetBacteria()}\n"
            self.log.info(string_5)
            # Instrument info
            string_6 = f"INSTRUMENT INFO\nInstrument serial number:\t\t{serial_number}\nSpectrometer serial number:\t\t{sfm_serial_number}"
            self.log.info(string_6)
        return True


    # MOBILE START TOGGLING FUNCITON
    def call_start_toggler(self):
        # Toggle the value of call_start and start run if it is not allready running,
        # If it is running remove futer runs and set stop_after_current_sample parameter to true 
        if not self.call_start and self.startNewMethod.isChecked():
            self.setStatus("System has been remotely activated")
            self.startNewMethod.setChecked(False)
            self.call_start = True
            # Reset stopsignal
            settings.setstopSignal(0)
            self.toggle_worker()
        else:
            self.delete_future_samples_and_stop_after_current()
            # self.call_start = False
            # self.setStatus("System has been remotely deavtivated")



    ### GUI DESIGN ###
    ## Window control, max/restore, resizing, and moving ##
    # Moving #
    def mousePressEvent(self, event):
        self.handleMousePress(event)

    def mouseMoveEvent(self, event):
        self.handleMouseMove(event)

    def mouseReleaseEvent(self, event):
        self.handleMouseRelease(event)

    def handleMousePress(self, event):
        # Check for resizing (by where the mouse is)
        if event.button() == Qt.LeftButton:
            if self.horisontal or self.vertical or self.diagonal:
                self.resizing = True
                self.dragging = False
            else:
                self.resizing = False
                self.dragging = True
                # Close menu if clicked outside of it
                side_menu = self.leftContainer.geometry()
                if not side_menu.contains(event.pos()):
                    self.hideMenuIfClickedOutside(event.globalPos())
            self.offset = event.pos()

    # Resize if option is activated (mouseclikced when resize cursor active)
    def handleMouseMove(self, event):
        # Resizing
        if self.resizing:
            if self.horisontal:
                self.resize(self.width() - (self.offset.x() - event.pos().x()), self.height())
                self.offset = event.pos()
            elif self.vertical:
                self.resize(self.width(), self.height() + event.pos().y() - self.offset.y())
                self.offset = event.pos()
            else:
                self.resize(self.width() + (event.pos().x() - self.offset.x()), self.height() + (event.pos().y() - self.offset.y()))
                self.offset = event.pos()
            self.offset = event.pos()
        # Moving the window
        elif self.dragging:
            self.restorebtn.setToolTip("Maximize Window")
            self.max = False
            self.move(self.mapToParent(event.pos() - self.offset))
        # Change cursor settings based on where the mouse is
        else:
            # Change cursor to a resize cursor when hovering over the edges... right-bottom corner
            if event.pos().x() >= self.width() - 10 and event.pos().y() >= self.height() - 10:
                self.setCursor(Qt.SizeFDiagCursor)
                self.diagonal = True
                self.vertical = False
                self.horisontal = False
            elif event.pos().x() >= self.width() - 5:
                self.setCursor(Qt.SizeHorCursor)
                self.diagonal = False
                self.vertical = False
                self.horisontal = True
            elif event.pos().y() >= self.height() - 5:
                self.setCursor(Qt.SizeVerCursor)
                self.diagonal = False
                self.vertical = True
                self.horisontal = False
            else:
                self.diagonal = False
                self.vertical = False
                self.horisontal = False
                self.setCursor(Qt.ArrowCursor)

    # Reset all the mouse options/cursor types upon release of the mouse button
    def handleMouseRelease(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.diagonal = False
            self.horisontal = False
            self.vertical = False
            self.offset = None
            self.setCursor(Qt.ArrowCursor)
            self.icon_changer_for_color_maintenance([self.restorebtn], ["square.svg"])

    # Function to hide the menues if mouse click occurs outside of them
    def hideMenuIfClickedOutside(self, global_pos):
        # Check if the menu is open
        if not self.leftSubContainer.isHidden():
            # Get the geometry of the menu and more options widgets
            left_menu_rect = self.leftSubContainer.geometry()
            more_options_rect = self.moreOptions.geometry()
            united_rect = left_menu_rect.united(more_options_rect)

            for w in self.leftSubContainer.findChildren(QWidget):
            #    print(w)
               united_left = left_menu_rect.united(w.geometry())

            # Check if the click is outside of the menu and inside the more options area
            if self.moreOptions.isHidden():
                if left_menu_rect.contains(global_pos):
                    pass
                else:
                    self.menuBtn.click()
            else:
                # print(global_pos)
                if united_rect.contains(global_pos.x(), global_pos.y()):
                    pass
                else:
                    self.menuBtn.click()
            # Temporary solution to solve the program expanding out of the monitor - this will create a little strange behaviour when not ran on an industrial computer.

    # Toggle maximize/normal window size #
    def toggle_maximized(self):
        if self.max:
            self.showNormal()
            self.icon_changer_for_color_maintenance([self.restorebtn], ["square.svg"])
            self.restorebtn.setToolTip("Maximize Window")
        else:
            self.showMaximized()
            self.icon_changer_for_color_maintenance([self.restorebtn], ["copy.svg"])
            self.restorebtn.setToolTip("Restore Window Size")
            # Ensure the window fills the entire screen when restored
            available_geometry = QApplication.desktop().availableGeometry(self)
            self.setGeometry(available_geometry)

        self.max = not self.max

    # Window minimizing
    def minimize_window(self):
        self.showMinimized()

    # Closing the program and all its widgets, so nothing is left running in the background.
    def close_all_windows(self):
        app = QApplication.instance()
        for widget in app.topLevelWidgets():
            try:
                widget.close()
            except:
                continue

    ## Menu's and Animations ##
    # # Toggle side menu visability #
    def toggle_menu(self, menu):
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_1.setCurrentIndex(0)
        stylesheet_color = "background-color: " + self.btn_press + ";"
        button = self.sender()
        if menu == "bottle":
            index = 0
        elif menu == "method":
            index = 1
        elif menu == "history":
            index = 2
        elif menu == "report":
            index = 3


        """Toggle between different option menus contained in the QStackedWidget."""
        if self.moreOptions.isHidden():
            self.moreOptions.show()
            self.moreOptions.setCurrentIndex(index)
        else:
            current_index = self.moreOptions.currentIndex()
            if current_index == index:
                self.moreOptions.hide()
            else:
                self.moreOptions.setCurrentIndex(index)

        # You can also reset any additional states (if needed)
        self.reset_button_styles()
        button.setStyleSheet(stylesheet_color)

    # Switch between pages of the advanced menus
    def advmenu_button_click(self, index):
        self.moreOptions.hide()
        stylesheet_color = "background-color: " + self.btn_press + ";"
        # self.toggle_menu()
        pressed_button = self.sender()
        if pressed_button == self.backBtn:
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_1.setCurrentIndex(0)
        elif pressed_button == self.manualBtn:
            self.stackedWidget.setCurrentIndex(0)
            self.stackedWidget_1.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(1)
            self.stackedWidget.setCurrentIndex(index)
            # Update adu button status
            self.aduWindow.update_adu_relay_buttons()

        self.reset_button_styles()
        pressed_button.setStyleSheet(stylesheet_color)

    # Clear all styling of previously clicked buttons 
    def reset_button_styles(self):
        """Reset the style of all buttons to clear any previous selection."""
        for button in self.findChildren(QPushButton):
            if button.parentWidget() == self.menuButtons or button.parentWidget() == self.advancedMenu:
                button.setStyleSheet("")


    def show_menu(self):
        if self.leftSubContainer.isHidden():
            # # Show the menu
            for w in self.leftSubContainer.findChildren(QWidget):
                w.show()
            self.leftSubContainer.show()
            self.leftContainer.show()
            if ADUadv.instantiated:
                self.advancedMenu.show()
                self.hideCheckBox.show()
                for box in self.checkBoxes_options:
                    box.show()
            else:
                self.advancedMenu.hide()
                self.hideCheckBox.hide()
                self.checkbox_hiding()
        else:
            # Hide all menus before opening a chosen menu
            self.leftContainer.hide()
            self.leftSubContainer.hide()
            self.reset_button_styles()


    ## STYLING ##
    # Change and Load stylesheet
    def change_stylesheet(self, mode): #, bac="#03601F", fore="#157933", btn="#004415", cont="#C3813D", txt="#fff"):
        global path
        # Set colors for the modes on features outside of stylesheets(button-pressed, )
        settings.storeStyle(mode)

        # Set colors for the different Style modes
        if mode == "dark_mode":
            self.background = "#2d2d2d"
            self.foreground = "#404040"
            self.btn_press = "#2d2d2d"
            self.contrast = "#00bcd4"
            self.color = "#fff"

        elif mode == "color":
            hex_colors = settings.getColors()
            self.background = hex_colors[0]
            self.foreground = hex_colors[1]
            self.btn_press = hex_colors[2]
            self.contrast = hex_colors[3]
            self.color = hex_colors[4]

        else:
            self.background = "#fff"
            self.foreground = "#f2f3f4"
            self.btn_press = "#fff"
            self.contrast = "#02a7a9"
            self.color = "#000"


        # Change the chosen styling color (text color) for all the icons in the GUI
        icons = [self.menuBtn, self.advSettingsBtn, self.minimizebtn, self.restorebtn, self.closebtn, self.startNewMethod, self.backBtn]
        icon_paths = ["align-justify.svg", "settings.svg", "minus.svg", "square.svg", "x.svg", "play.svg", "arrow-left.svg", ]
        self.icon_changer_for_color_maintenance(icons, icon_paths)

        # Sett the chosen styling propertis for the stacked, and tab widgets too
        self.stackedWidget.setStyleSheet("background-color: " + self.background + ";")
        self.stackedWidget_1.setStyleSheet("background-color: " + self.background + ";")
        self.tabWidget.setStyleSheet("""
            QTabWidget{{
                background-color: {}; /* Set the background color */
                color: {};
            }}
            QTabBar::tab{{
                background-color: {};
            }}
        """.format(self.background, self.color, self.foreground))

        # Load style sheet from a file
        style_file = QFile(resource_path(os.path.join(path, "styles\\style.css")))

        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.stylesheet = stream.readAll()

            # Replace placeholders with actual color values
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_BACKGROUND_COLOR", self.background)
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_FOREGROUND_COLOR", self.foreground)
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_DARKER_PRESS_BUTTON_COLOR", self.btn_press)
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_CONTRAST_COLOR", self.contrast)
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_TEXT_COLOR", self.color)
            self.stylesheet = self.stylesheet.replace("PLACEHOLDER_COLORFULL_COLOR", settings.getColors()[0])

            style_file.close()
            self.setStyleSheet(self.stylesheet)



    # Function for changing icons colors to the current text color of the program
    def icon_changer_for_color_maintenance(self, icons, icon_filenames, color=""):
        global path
        # Loop over the provided list of icons
        for i, widget in enumerate(icons):
            # Fetch the icon file path and open it
            icon_path = os.path.join(path, ("icons\\" + icon_filenames[i]))
            with open(resource_path(icon_path), 'r') as file:
                svg_content = file.read()

            # Replace the color placeholder with the desired hex color
            if color == "":
                color = self.color
            svg_content = svg_content.replace("currentColor", color)

            # Create a QSvgRenderer from the modified SVG content
            renderer = QSvgRenderer(svg_content.encode('utf-8'))

            # Convert the SVG renderer to a QPixmap
            pixmap = QPixmap(24, 24)        # Set the size to be filled by the icon
            pixmap.fill(Qt.transparent)     # Set background transparent
            # Do the magic of combining the pixmap with the rendered svg
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            # Set the QPixmap as the new icon for the widget
            new_icon = QIcon(pixmap)
            widget.setIcon(new_icon)

    ## Color change menu ##
    # Right click the header to get access to the color change option
    def show_context_menu(self, position):
        # Make a menu when rightclick
        context_menu = QMenu(self)
        # Set object name to allow for the stylesheet to apply to the menu
        context_menu.setObjectName("customContextMenu")
        change_color_action = QAction("Change Color", self)
        change_color_action.triggered.connect(self.show_color_picker)
        context_menu.addAction(change_color_action)
        context_menu.exec_(self.mapToGlobal(position))

    # Show the color sliders for the colorfull style
    def show_color_picker(self):
        # Open instance of the ColorPicker
        self.color_picker = ColorPicker(self)
        self.color_picker.show()


    ## Plotting historic data ##
    # Make the dates of the calendar that have data, interactive
    def historic_data_availability_to_calender(self, calendar):
        interactive_format = QTextCharFormat()
        interactive_format.setForeground(Qt.black)
        interactive_format.setBackground(Qt.white)

        list_of_dates_with_data = self.find_dates_with_data_from_db()
        if list_of_dates_with_data:
            print(list_of_dates_with_data)

            # Check data availability for specific dates
            for date_with_data in list_of_dates_with_data:
                date = QDate.fromString(date_with_data, 'yyyy-MM-dd')
                calendar.setDateTextFormat(date, interactive_format)
        else:
            return

    # Query the database to find dates with available data
    def find_dates_with_data_from_db(self):
        db = DatabaseHandler()
        try:
            # Query database for dates
            # Maybe check for data in spectraldata and that it has more readings than 0 or 1/ more than those initial test reads
            query = 'SELECT DISTINCT date FROM SampleInfo WHERE full_sample_time is not NULL'
            results = db.fetch_data(query)
            # Extract date strings from the results
            date_strings = [result[0] for result in results if result[0] is not None]
            return date_strings
        except:
            return False

    # Get the selected date
    def handleDateSelection(self):
        selected_date = self.historyCalendar.selectedDate()
        year = selected_date.year()
        month = selected_date.month()
        day = selected_date.day()
        date_string = f"{year}-{month:02d}-{day:02d}"
        # date_string = year + "-" + month + "-" + day
        self.selected_date = date_string
        self.updateCalendar()

    # CheckBox that activates full series and thus deactivates n-samples
    def update_slider_state(self, state):
        self.horizontalSlider.setValue(1)
        self.horizontalSlider.setEnabled(not state)
        settings.storePlotSeries(state)
        self.updateCalendar()

    # Update when slider is changed
    # historic plot slider
    def n_samples(self):
        string = f"samples to plot = {self.horizontalSlider.value()}"
        self.nSamples.setText(string)
        self.updateCalendar()
    # # Schedual slider
    # def sched_samples(self):
    #     self.dayScheduler.setMaximum(settings.getBottleSize())
    #     value = self.dayScheduler.value()
    #     string = f"n={value}"
    #     self.schedSamples.setText(string)
    #     settings.storeSamplesNr(value)
    #     self.update_medium_progress_bar()

    # Update the calendar to visually indicate selected dates
    def updateCalendar(self):
        self.resetCalendarColors()
        self.historic_data_availability_to_calender(self.historyCalendar)
        self.historic_data_availability_to_calender(self.reportCalendar)

        multiple_days_format = QTextCharFormat()
        # Get highlight color of calendar
        palette = self.historyCalendar.palette()
        highlight_color = palette.color(QPalette.Active, QPalette.Highlight)
        multiple_days_format.setBackground(highlight_color)
        # Convert the selected date from string to QDate
        selected_qdate = QDate.fromString(self.selected_date, 'yyyy-MM-dd')
        # Add dates if multiple dates selector is active
        n_days = self.horizontalSlider.value() - 1                                #### THis mmight max out on 20 not 21

        # Select the dates that are included in the sample series that the selected date is part of
        if self.fullSeries.isChecked():
            # Get amount of samples of selected run series
            try:
                db = DatabaseHandler()
                sampleID = db.fetch_data("SELECT id FROM SampleInfo WHERE date = ? ORDER BY id DESC", self.selected_date)[0][0]
                query = 'SELECT date FROM SampleInfo WHERE run_id IN(SELECT run_id FROM SampleInfo WHERE id = ?)'
                rows = db.fetch_data(query, sampleID)
                selected_qdate = QDate.fromString(rows[-1][-1], 'yyyy-MM-dd')
                n_days =  len(rows) - 1
            except:
                n_days = 1

        start_date = selected_qdate.addDays(-n_days)

       # Iterate through the date range and set each date as selected                       ### Might want to have this only mark dates that has data, so as to work well with every other day runs...
        current_date = start_date
        while current_date <= selected_qdate:
            self.historyCalendar.setDateTextFormat(current_date, multiple_days_format)
            current_date = current_date.addDays(1)

    # Reset the colors of the calendar for +/- 1 month of selected month
    def resetCalendarColors(self):
        # Reset the colors of all dates in the calendar
        format = QTextCharFormat()
        format.setBackground(QBrush(QColor(Qt.gray).lighter(150)))  # Get the default gray color

        currentDate = self.historyCalendar.selectedDate()
        for month in range(-1, 2):
            sel_date = currentDate.addMonths(month)
            for day in range(1, 32):
                date = QDate(sel_date.year(), sel_date.month(), day)
                self.historyCalendar.setDateTextFormat(date, format)


    # collect the DB-entries that have the data from the specified date
    def plot_historic_data(self, id="", date=""):
        db = DatabaseHandler()
        n_samples = self.horizontalSlider.value()
        if date == "":
            print("id from plot_hist function: ", id)
            sample_id = id
        else:
            # Check all dates of the selection before giving an error of no data
            if not self.fullSeries.isChecked() and self.horizontalSlider.value() > 1:
                try:
                    # Start loop at earliest date
                    date = self.date_looper(date, (1 - n_samples))
                    sample_id  = self.get_sample_id_from_date(date)
                    days = 1
                    while not sample_id:
                        # Add a day each itteration
                        date = self.date_looper(date, 1)
                        sample_id  = self.get_sample_id_from_date(date)
                        # If there are no dates in the selection that has data, raise error
                        if days >= self.horizontalSlider.value():
                            raise RuntimeError
                        # Update counters each itteration
                        days += 1
                        n_samples = n_samples + 1
                except:
                    self.show_error_message("There seem to be no data from those dates")
                    return
            else:
                sample_id  = self.get_sample_id_from_date(date)
                if not sample_id:
                    return
            # Catch dates with multiple data instances, and prompt the user to select instance.
            if len(sample_id) > 1 and self.horizontalSlider.value() > 1:
                items = [str(sid) for sid in sample_id]
                item, ok_pressed = QInputDialog.getItem(self, "Multiple Samples", "Select the sample you want to plot:", items, 0, False)
                if ok_pressed and item:
                    index = items.index(item)
                else:
                    return
            else:
                index = 0


            sample_id = sample_id[index]

        # Fetch wavelengths
        query = "SELECT DISTINCT wavelength_id FROM SpectralData WHERE sample_id = ?"
        arg = sample_id
        rows = db.fetch_data(query, arg)
        # Check if there are done readings for the sample run, and make tabs for each wavelength in that case.
        try:
            print("ROWS: ", rows)
            tab_name = ""
            if rows[0][0]:
                # Loop over wavelengths to plot
                for wavelength in rows:
                    if wavelength[0] == settings.getWavelengthFluo():
                        tab_name = "Bacterial plot " + date
                    elif wavelength[0] == settings.getWavelengthTurb():
                        tab_name = "Turbidity plot " + date
                    else:
                        tab_name = str(wavelength[0]) + " " + date
                    # Check if the full Series checkbox is checked
                    if self.fullSeries.isChecked():
                        print("full Series")
                        self.signal_to_plot(sample_id, wavelength[0], tab_name)
                    else:
                        self.signal_to_plot(sample_id, wavelength[0], tab_name, n_samples)
        except IndexError:
            string = f"There seem to be no readings for the sample from {date}"
            self.show_error_message(string)

    # Function to loop over days in a string format(YYYY-MM-DD)
    def date_looper(self, date, days):
        # Convert the string to a datetime object
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        date = date + datetime.timedelta(days=days)
        date = date.strftime("%Y-%m-%d")
        return date

    # Look for associated sample id's from a date
    def get_sample_id_from_date(self, selected_date):
        db = DatabaseHandler()
        try:
            id = db.fetch_data("SELECT id FROM SampleInfo WHERE date = ? ORDER BY id DESC", selected_date)[0]
            return id
        except:
            # If more than one date is to be plotted, avoid the error message of
            # no data, as it will itterate to the next date with posible data.
            if not self.fullSeries.isChecked() and self.horizontalSlider.value() > 1:
                return False
            self.show_error_message("No data from that date")
            return False

    # Collect data from database to generate the report
    def data_collection_for_report(self, date):
        fluo_wl = str(settings.getWavelengthFluo())
        turb_wl = str(settings.getWavelengthTurb())

        db = DatabaseHandler()
        serial_number = db.fetch_data("SELECT instrument_serial_number FROM InstrumentInfo")[0][0]
        RunInfo = db.fetch_data("SELECT * FROM RunInfo WHERE id IN(SELECT run_id FROM SampleInfo WHERE date = ?)", date)[0]
        SampleInfo = db.fetch_data("SELECT * FROM SampleInfo WHERE date = ?", date)[0]
        SpectralData = db.fetch_data("SELECT * FROM SpectralData WHERE sample_id IN(SELECT id FROM SampleInfo WHERE date = ?)", date)

        print("1. TEST DATE: ", str(SampleInfo[3]))

        # Create report and page
        pdf = PDFReport(SampleInfo[3])
        pdf.add_page()
        ## FETCH INFO FROM DB AND PRINT TO PDF ##
        # Technical info section
        string = f"{24*int(RunInfo[-2])} h"
        tech_info = ["1", serial_number, RunInfo[-1], os.path.basename(RunInfo[-3]), "Yes" if SampleInfo[-4] != 0 else "No", "Yes" if SampleInfo[-3] != 0 else "No",\
        "Continuous" if 0 else string, RunInfo[-4].split(" - ")[0], RunInfo[-4].split(" - ")[1]]
        info = ["Software Version", "Instrument Serial Number", "Spectrometer Serial Number", "Method File", "External Sample", "Sodium Thiosulfate", \
        "Sample Frequency", "Target Bacteria", "Incubation Temperature"]
        pdf.report_section("Technical Info", 45, info, tech_info)

        # Run Info
        run_info = [str(RunInfo[1]), str(RunInfo[2]), str(RunInfo[3]) ]
        info = ["Bottle Number", "Bottle Size", "Run Start Time"]
        pdf.report_section("Run Details", 102, info, run_info)

        # Sample info
        string_2 = f"{SampleInfo[1]}/{RunInfo[2]}"
        sample_info = [string_2, str(SampleInfo[3][:-9]), str(SampleInfo[3][-8:]), fluo_wl, turb_wl]
        info = ["Sample Number", "Date", "Sample Start Time", "Fluorescent Wavelength", "Turbidity Wavelength"]
        pdf.report_section("Sample Details", 130, info, sample_info)

        sample_id = db.fetch_data("SELECT id, sample_start_time FROM SampleInfo WHERE date = ?", date)
        # Catch dates with multiple data instances, and prompt the user to select instance.
        if len(sample_id) > 1:
            items = [str(sid[1]) for sid in sample_id]
            print(items)
            item, ok_pressed = QInputDialog.getItem(self, "Multiple Samples", "Select the sample you want to plot:", items, 0, False)
            if ok_pressed and item:
                index = items.index(item)
                print("index: ", index)
            else:
                return
        else:
            index = 0

        sample_id = sample_id[index][0]

        # Data to plot Info
        table_data = db.fetch_data("SELECT intensity, time_measured, readings_to_average_over, nm_bandwidth FROM SpectralData \
                             WHERE sample_id IN(SELECT id FROM SampleInfo WHERE date = ? AND wavelength_id = ?)", date, fluo_wl)
        # Plot and Table
        data = self.fetch_data_to_plot(sample_id, int(fluo_wl), 1)
        if not data:
            return
        try:
            pdf.plot_section(data, table_data)
        except:
            return
        # Interpret the valence of the result and print to pdf
        if SampleInfo[4] == 1:
            result_f = "PRESSENT"
        else:
            result_f = "ABSENT"

        if SampleInfo[5] == 1:
            result_t = "POSITIVE"
        else:
            result_t = "NEGATIVE"
        pdf.result_section(RunInfo[10], result_f, result_t)

        # Create The right folder to store the report in
        print("TEST DATE: ", str(SampleInfo[4]))
        folder = self.create_year_month_folders(self.datetimestringler(str(SampleInfo[4])))
        string_3 = f"/{date}.pdf"
        pdf.output(folder + string_3)


    # Create folder system in the stored result/report folder if is is not there already. 
    def create_year_month_folders(self, date):
        # Extract year and month from the date
        year = date.year
        # Create the year folder if it doesn't exist
        year_folder = os.path.join(settings.getResultFolder(), str(year))
        if not os.path.exists(year_folder):
            print(year_folder)
            os.mkdir(year_folder)
        # Create the month folder if it doesn't exist
        month_name = date.strftime("%B")
        month_folder = os.path.join(year_folder, month_name)  # Format month as two digits (e.g., 01, 02, ..., 12)
        if not os.path.exists(month_folder):
            os.mkdir(month_folder)
        return month_folder


    ## Option & Choices functions ##
    # Bottle Size changed funciton #
    def bottle_changer(self, accept):
        if not self.startNewMethod.isChecked():
            self.startNewMethod.setChecked(False)
            method_running = ErrorDialog("There is a method running, please stop the run before updating the bottle size")
            accept = method_running.exec_()
            if accept:
                return
            
        bottle_size = self.bottleSize.value()
        print("bot, samp, remain; ", bottle_size, settings.getSamplesNr(), settings.getRemaining())
        settings.storeSamplesNr(bottle_size)
        settings.storeBottleSize(bottle_size)
        # self.dayScheduler.setValue(settings.getSamplesNr())
        settings.storeRemaining(bottle_size)
        self.update_medium_progress_bar(True)

        print("IN Bottle Changer!! bot, samp, remain; ", bottle_size, settings.getSamplesNr(), settings.getRemaining())


        # Start the remote GSM listner if a new bottle is inserted and mobile remote toggle is checked
        if settings.getRemoteStart():
            self.mobileRemoteToggle.start()

        # Warn the user if no bottle size is selected.
        if accept:
            self.update_medium_progress_bar(True) # superfluous?
            self.bottleSizeWarning.hide()
            self.leftSubContainer.hide()
            self.moreOptions.hide()

    # Update the GUI progressbar for bottle size and new flask(optional set to True)
    def update_medium_progress_bar(self, new_flask = False):
        try:
            bottle_size = settings.getBottleSize()
            self.bottleSize.setValue(bottle_size)
            # Bottle size number medium progressBar
            self.remainingSamples.setMaximum(bottle_size)
            # Update the remaining samples, newflask or remainings of the bottle
            if new_flask:
                remaining_samples = bottle_size
            else:
                remaining_samples = settings.getRemaining()
            # Display the value in the progressBar 
            self.remainingSamples.setProperty("value", remaining_samples)
            # Not sure if this parameter(settings.getSamplesNr) is useful, but 
            # it is for an option where sample number of a run could be set 
            # regardless of the bottle size. But the same result is achievable 
            # by using the bottle size parameter.
            if settings.getBottleSize() != settings.getSamplesNr():
                self.remainingSamples.setFormat("  {}/{}              n={}".format(remaining_samples, bottle_size, settings.getSamplesNr()))
            else:
                self.remainingSamples.setFormat("  {}/{}".format(remaining_samples, bottle_size))
        except:
            return

    # Change Target bacteria for the analysis #
    def target_bact_changer(self):
        selected_analysis = self.bact_box.currentText()
        settings.storeTargetBacteria(selected_analysis)

    # Sample frequency changer #
    def sample_frequency_changer(self):
        sample_freq = self.freq_box.currentText()
        delay = None
        if "Continuous" in sample_freq:
            delay = 0
        elif "24 hours cycle" in sample_freq:
            delay = 1
        elif "48 hours cycle" in sample_freq:
            delay = 2
        elif "Custom interval" in sample_freq:
            if settings.getFrequency() > 2:
                delay = settings.getFrequency()
            else:
                delay, ok_pressed = QInputDialog.getInt(self, 
                                                        "Sample Run Scheduler", 
                                                        "Enter the number of days between sample runs:", 
                                                        value=3, 
                                                        min=3)

            self.freq_box.setItemText(3, f"Custom interval ({delay})")

        settings.storeFrequency(delay)
        print(settings.getFrequency())

    # Function to handle manual option of sample frequency
    def get_frequency(self):
        frequency = settings.getFrequency()
        if frequency == None:
            return 3
        elif frequency > 2:
            return 3
        else:
            return frequency

    ## CHECKBOXES METHOD ##
    # Status of Sodium thiosulfate checkbox #
    def update_sodium_thio_status(self):
        sodium_thio = self.sodiumThio.checkState()# == Qt.Checked
        settings.storeSodiumThio(sodium_thio)

    # Status of External Sample checkbox  - mutually exclusive with dual sampling #
    def update_external_sample_status(self):
        ext_samp = self.externalSample.checkState()# == Qt.Checked
        if ext_samp:
            self.dualSamples.setChecked(0)
            settings.storeDualSamples(0)
            self.sampleSource.hide()

        settings.storeExtSamp(ext_samp)

    # Status of Delay before start checkbox - mutually exclusive with remote start #
    def update_delay_start_time(self):
        delay = self.delayStartTime.checkState()
        if delay:
            self.remoteStart.setChecked(0)
            settings.storeRemoteStart(0)
            try:
                self.mobileRemoteToggle.stop()
            except:
                pass
        settings.storeDelayStart(delay)

    # Status of Remote start checkbox - mutually exclusive with delay before start #
    def update_remote_start(self):
        remote_start = self.remoteStart.checkState() # == Qt.Checked
        # Twice to remove the "awaiting remote start..." text from the status bar
        self.setStatus("")
        self.setStatus("")
        if remote_start:
            self.delayStartTime.setChecked(0)
            settings.storeDelayStart(0)

            # Check if adu is connected before starting GSM listner thread
            if not adu._validate_connection():
                no_adu = ErrorDialog("The ADU is not connected, so remote signal is not accesible.")
                accept = no_adu.exec_()
                if accept:
                    self.remoteStart.setChecked(0)
                    settings.storeRemoteStart(0)
                    return False
            # Start the remote GSM listner
            self.mobileRemoteToggle.start()
            self.setStatus("Awaiting remote start...")

        else:
            try:
                # Stop the remote GSM listner
                self.mobileRemoteToggle.stop()
            except:
                pass
        settings.storeRemoteStart(remote_start)

    # Status of dual sample checkbox - mutually exclusive with External Sample #
    def update_dual_samples(self):
        dual_samp = self.dualSamples.checkState()
        if settings.getSampleSource() == None:
            # Switch in method file lead to start at sample1 - first run
            settings.storeSampleSource(5)
        if dual_samp:
            self.externalSample.setChecked(0)
            settings.storeExtSamp(0)
            self.sampleSource.show()
            # Get the last ran sample
            source = settings.getSampleSource()
            # As this is designed to alternate in method file the source 
            # of the next sample would be the oposite of current source.
            if source == 5:
                next_source = "sample 2"
            else:
                next_source = "sample 1"

            string = f"Next source: {next_source}"
            self.sampleSource.setText(string)
        else:
            self.sampleSource.hide()
        settings.storeDualSamples(dual_samp)


    # Toggle all/interval-of-7 samples in a row.
    def update_bottle_size_manual_option(self):
        settings.storeBottleSizeStep(self.otherValues.checkState())
        if self.otherValues.checkState():
            self.bottleSize.setSingleStep(1)
        else:
            self.bottleSize.setSingleStep(7)
            current_value = self.bottleSize.value()
            closest_divisible_by_7 = round(current_value / 7) * 7
            self.bottleSize.setValue(closest_divisible_by_7)


    # Check for samples left in the media bottle
    def check_medium_status(self):
        # if a run is started when there likely is a bottle with leftovers in the instrument
        result = QDialog.Accepted
        if settings.getRemaining() <= 0:
            result = self.show_error_message("Have you inserted a new media bottle?", True)
        elif settings.getRemaining() != 0 and settings.getRemaining() != settings.getBottleSize():
            samples_left = settings.getRemaining()
            # If the remote start is chosen skip the error message, as there is no one there to check it
            if settings.getRemoteStart():
                return 1
            string = f"Last run was stoped midway, and there are {samples_left} samples left in the medium bottle"
            result = self.show_error_message(string, True)
        # in case of changing - update the progress bar to reflect the now newly inserted bottle
        if result == QDialog.Accepted:
            self.update_medium_progress_bar()
            print("medium check returns true")
            return 1
        else:
            print("medium check returns false")
            return 0

    # Update the hide options for checkboxes - which is to be shown in user mode
    def update_checkbox_state(self, state):
        checkbox_states = [checkbox.checkState() for checkbox in self.checkBoxes]
        settings.storeCheckBoxStates(checkbox_states)
    # Hide checkboxes after advanced menu has been closed
    def checkbox_hiding(self):
        list = settings.getCheckBoxStates()
        for i, state in enumerate(list):
            if state == "2":
                self.checkBoxes_options[i].hide()

    # Update the medium level - samples left
    def progBar_clicked(self):
        self.show_error_message("Have you inserted a new media bottle?", True)
        self.update_medium_progress_bar()

    # Function to open the custom error message window
    def show_error_message(self, error_message, stop=False):
        dialog = ErrorDialog(error_message)
        accepted = dialog.exec_()
        if accepted == QDialog.Accepted:
            accepted = True
            if stop:
                # Ensure the stopping of the run in case it is started
                self.startNewMethod.setChecked(True)
                # self.call_start = False
                # Update start/stop button
                self.stop_updater()


        else:
            print("rejected dialog")
            pass
        return accepted


    ## Method File ##
    # Update selected method file selected in the drop down #
    def method_file_changer(self, index):
        global method_files_path
        # Access the selected text
        file = self.methodSelector.currentText()
        # Make sure it is the full path to the file
        if not os.path.isabs(file):
            file_path = os.path.join(method_files_path, file)
        else:
            file_path = os.path.normpath(file)
        # Perform the desired action based on the selected item
        if file == "Browse...":
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Select Method File", method_files_path)
            # Only method files (.CFAST) shows
            if file_path and file_path.endswith(".CFAST"):
                print("Browsed file: ", file_path)
                # Add the path browsed if it is not already part of the selector
                path_in_selector = False
                for index in range(self.methodSelector.count()):
                    if file_path == self.methodSelector.itemText(index) and os.path.isFile(file_path):
                        path_in_selector = True
                if not path_in_selector:
                    self.methodSelector.addItem(file_path)
                # Set the browsed file as the selected file of the selector
                self.methodSelector.setCurrentText(file_path)
            else:
                print("choose a valid file")
                return
        settings.storeMethod(file_path)

        # Allow the user to save the edited file in editor if it has ben altered, before switching file
        if hasattr(self, 'Editor'):
            # Check if there are unsaved changes
            if self.Editor.is_modified:
                reply = QMessageBox.question(
                    None,
                    'Unsaved Changes',
                    'You have unsaved changes. Do you want to save before loading a new file?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )

                if reply == QMessageBox.Cancel:
                    return  # User canceled the operation
                elif reply == QMessageBox.Yes:
                    self.save_text()  # Save the changes before loading

            # Reset the modified flag
            self.Editor.is_modified = False
            self.Editor.load_text(file_path)

    # Method File Selector - Populate the combo box with .CFAST files from the method_files_folder
    def methodDropDown(self):
        global method_files_path
        # Clear existing items
        self.methodSelector.clear()

        if os.path.exists(method_files_path):

            # Add files from the folder to the dropdown
            for file in os.listdir(method_files_path):
                if file.endswith(".CFAST"):
                    self.methodSelector.addItem(file)
            # Fetch stored method
            method = settings.getMethod()
            # Add to dropdown list, the stored method, if it is not in the Method folder
            path_in_selector = False
            for index in range(self.methodSelector.count()):
                if os.path.basename(method) == os.path.basename(self.methodSelector.itemText(index)):
                    path_in_selector = True

            if not path_in_selector:
                self.methodSelector.addItem(method)
                self.methodSelector.setCurrentText(method)

            elif method:
                self.methodSelector.setCurrentText(os.path.basename(method))
        
        # Add the 'Browse' option
        self.methodSelector.addItem("Browse...")

    ## CALLING ALL THE ADVANCED MENU CLASSES INTO THE MAIN GUI ##
    # Advanced Settings #
    def adv_settings(self):
        if ADUadv.instantiated:
            logout = ErrorDialog("You are about to log out the advanced menu")
            accept = logout.exec_()
            try:
                # Check if there are unsaved changes
                if self.Editor.is_modified:
                    reply = QMessageBox.question(
                        None,
                        'Unsaved Changes',
                        'You have unsaved changes. Do you want to save before exiting the advanced menu?',
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                    )
                    if reply == QMessageBox.Cancel:
                        return  # User canceled the operation
                    elif reply == QMessageBox.Yes:
                        self.save_text()  # Save the changes before loading

                # Reset the modified flag
                self.Editor.is_modified = False
            except:
                pass
            # Closing the advanced menu options upon accept
            if accept:
                try:
                    # Trigger back button click to remove the advanced screen displayed
                    self.backBtn.click()
                    # remove advanced menu bar
                    self.advancedMenu.hide()
                    self.hideCheckBox.hide()
                    self.checkbox_hiding()
                    # # Hide schedualer menu
                    # self.shedualerMenu.hide()
                    # Remove all pages from the stacked widget starting from index 1
                    try:
                        index = 1
                        while index < self.stackedWidget.count():
                            page = self.stackedWidget.widget(index)
                            if page:
                                self.stackedWidget.removeWidget(page)
                                page.deleteLater()  # Delete the page
                            else:
                                index += 1            # self.advancedMenu.hide()
                    except:
                        print("could not remove stacked pages")
                    # Delete the window class instances
                    try:
                        del self.sfmWindow
                    except:
                        print("could not remove sfmWindow")
                    try:
                        del self.aduWindow
                    except:
                        print("could not remove aduWindow")
                    ADUadv.instantiated = False
                except:
                    print("\n\nCould not close ADVANCED MENU\n\n")
        
        else:
            self.login = LogIn()
            if self.login.exec() == QDialog.Accepted:
                print("accepted")
                # Show advanced features in menu
                self.advancedMenu.show()
                self.hideCheckBox.show()
                # Show all the checkboxes when in advanced mode
                for box in self.checkBoxes_options:
                    box.show()

            # Not sure if this parameter(schedulerMenu) is useful, but 
            # it is for an option where sample number of a run could be set 
            # regardless of the bottle size. But the same result is achievable 
            # by using the bottle size parameter, so I have commented it out for now.
                # Show schedualer menu
                # self.shedualerMenu.show()

                # ADU
                # Create an instance of the class
                self.aduWindow = ADUadv(self)  # Create an instance of the advanced ADU class
                # Create a QDockWidget for the advanced page
                self.adu_docker = QDockWidget("ADU", self)
                self.adu_docker.setWidget(self.aduWindow)
                # Add the docker to the stacked widget
                self.stackedWidget.addWidget(self.aduWindow)

                # SFM
                # Create an instance of the class
                self.sfmWindow = SFMadv(self)
                # Create a QDockWidget for the advanced page
                self.sfm_docker = QDockWidget("SFM", self)
                self.sfm_docker.setWidget(self.sfmWindow)
                # Add the docker to the stacked widgetf
                self.stackedWidget.addWidget(self.sfmWindow)

                # Liquid Handling
                # Create an instance of the class
                self.LqHWindow = LiquidHandling(self)
                # Create a QDockWidget for the advanced page
                self.LqH_docker = QDockWidget("Liquid Handling", self)
                self.LqH_docker.setWidget(self.LqHWindow)
                # Add the docker to the stacked widget
                self.stackedWidget.addWidget(self.LqHWindow)
                # self.stackedWidget.addWidget(sfmWindow)

                # Editor
                self.Editor = editor.Editor(self)
                self.Editor.setStyleSheet("""
                    *{
                        background-color: #92C5DE;
                    }
                    #button_container, #func_container{
                        background-color: #66899b;
                        max-height: 100px;
                    }
                    QLineEdit {
                        background-color: #C2E2F2;
                    }
                    QListWidget {
                        background-color: white;
                        color: black;
                    }
                    QPushButton {
                            border: none;
                            padding: 10px;
                            background-color: #66A4C2;
                            color: black;
                            border-radius: 5px;
                            /*box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);*/
                        }
                        QPushButton:hover {
                            background-color: #C2E2F2;
                            /*box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.3);*/
                        }
                        QPushButton:pressed {
                            background-color: #4081A0;
                            /*box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.3);*/
                        }
                    QDockWidget::title {
                        background-color: #66899b;  /* Set the background color */
                        # color: #ffffff;  /* Set the text color */
                        # font-size: 10px;  /* Set the font size */
                        # font-weight: bold;  /* Set the font weight */
                    }
                """)

                self.editor_docker = QDockWidget(self)
                self.editor_docker.setTitleBarWidget(QWidget())
                self.editor_docker.setFeatures(QDockWidget.NoDockWidgetFeatures)  # Disable moving and closing
                self.editor_docker.setWidget(self.Editor)
                # self.editor_docker.setStyleSheet("background-color: #92C5DE;")
                self.stackedWidget.addWidget(self.editor_docker)

                # Open ADU window first
                self.aduBtn.click()
                self.stackedWidget.setCurrentIndex(1)
                # Set teh button color
            else:
                print("REJECTED")

    ## LOGGING ##
    # Set up the logging features
    def setup_logging(self):
        self.log_formatter = logging.Formatter('%(message)s')# logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.log_handler = None
        log = logging.getLogger("method_logger")
        log.setLevel(logging.DEBUG)
    # Create a new log file for a sample run
    def create_log_handler(self, start_time=None, file=None):
        if file == None:
            string = f'logger_{start_time:%Y-%m-%d_%H%M}.log'
            log_filename = os.path.join(settings.getLogsFolder(), string)
        else:
            log_filename = file
        log_handler = FileHandler(log_filename)
        log_handler.setFormatter(self.log_formatter)
        return log_handler

    ## Data visualisation & Results ##
    # Program status update from the underlying method file #
    def setStatus(self, status_message):
        # Update progress bar as a status message comes in from the worker to ensure it is up to date.
        self.update_medium_progress_bar()
        # Try writing the status message to the Log file
        try:
            self.log.info("Status message\t-\t" + status_message)
        except:
            print("No log file to append status message to")
        # Put the status message in queue for the status browser - to ensure 
        # that all messages are displayed, despite of them comming in too quick 
        # to be viewed.
        self.status_queue.appendleft(status_message)
        self.statusQueueHandler()

    # Status queue handler, for ensuring delay between messages
    def statusQueueHandler(self):
        print(len(self.status_queue))
        new_text = ""
        for message in self.status_queue:
            new_text = new_text + message + "\n\n"
        # Set updated text back to the QTextBrowser
        self.status_browser.setText(new_text)

    ## Handle warnings from worker thread.
    def warning_message(self, message):
        # Show the dialog and capture the result (this happens on the main thread)
        dialog = ErrorDialog(message)
        result = dialog.exec_()  # This will block the main thread until user response (OK or Cancel)

        # Emit the result back to the worker (True if accepted, False if rejected)
        self.worker_thread.dialog_result = (result == QDialog.Accepted)
        self.worker_thread.dialog_result_signal.emit(True)

    # set text in startTime field
    def startTime(self, txt):
        self.startingTime.setText(txt)

    # set text in lastBactAlarm field
    def bactAlarm(self, txt):
        self.lastBactAlarm.setText(txt)
        db = DatabaseHandler()
        db.execute_query("UPDATE SampleInfo SET bact_pos = 1 WHERE id = ?", self.sample_id)

    # set text in lastTurbAlarm field
    def turbAlarm(self, txt):
        self.lastTurbAlarm.setText(txt)
        db = DatabaseHandler()
        db.execute_query("UPDATE SampleInfo SET turb_pos = 1 WHERE id = ?", self.sample_id)

    # TURBIDITY CALCULATOR - Raw value to FNU
    def turb_FNU_calculator(self, raw_value, sample_id):
        db = DatabaseHandler()
        query = "SELECT turbidity_raw0, turbidity_raw10 FROM RunInfo WHERE id IN(SELECT run_id FROM SampleInfo WHERE id = ?)"
        arg = sample_id
        zero_value, ten_value = db.fetch_data(query, arg)[0]
        FNU_increment_raw_value_level = (ten_value - zero_value)/10
        turbidity = (raw_value - zero_value)/FNU_increment_raw_value_level
        return round(turbidity, 3)

    # Function that converts between datetime and string and vice versa - for storing in database and maintain same format
    def datetimestringler(self, obj):
        if isinstance(obj, datetime.datetime):
            # Convert datetime object to string
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, str):
            # Convert string to datetime object
            return datetime.datetime.strptime(obj.split('.')[0], '%Y-%m-%d %H:%M:%S')
        else:
            raise ValueError("Unsupported input type. Pass either a datetime object or a string.")


    # Plot update function for aquired data - signal from sample thread to update plot
    # and generate tabWidget for each wavelength that has data in main GUI#

    ## PLOTTING DATA IN THE GUI ##
    # SIGNAL (spectral data wavelength and tab name)
    def signal_to_plot(self, sample_id, wavelength, tab_name, n_samples="samples_in_current_run"):
        # Try closing any existing tabs with same name
        self.close_tab_by_name(tab_name)
        # Create tab and widget for the plot
        widget = self.create_plot_tab(tab_name)
        # fetch data
        x, y = self.fetch_data_to_plot(sample_id, wavelength, n_samples)
        # Set threshold line
        if wavelength == settings.getWavelengthFluo():
            baseline = y[0]
            threshold = baseline * float(settings.getThresholdFluo())
        elif wavelength == settings.getWavelengthTurb():
            y = [(self.turb_FNU_calculator(intensity, sample_id)) for intensity in y]
            threshold = float(settings.getThresholdTurb())
        try:
            self.threshold_infinite_line(threshold, widget)
        except:
            print("No threshold line to plot")
        # Plot the data
        padding_factor = 1.5
        try:
            self.plot_data(x, y, widget, (threshold*padding_factor))
        except:
            self.plot_data(x, y, widget)


    # FETCH DATA FROM DATABASE
    def fetch_data_to_plot(self, sample_id, wavelength, samples_to_plot):
        db = DatabaseHandler()
        # Fetch all samples in series
        if samples_to_plot == "samples_in_current_run":
            rows = db.get_spectral_data_series(sample_id, wavelength)
        # Get all data n-samples forward from sample ID
        else:
            # Get the data from database
            rows = db.get_n_spectral_data_samples(sample_id, wavelength, samples_to_plot)
        
        # Catch the instance of no data from a sample
        if not rows:
            self.show_error_message("There seem to be no readings from that sample")
            return False

        # Extract time_measured and convert it to datetime object and intensity
        time_measured = []
        intensity = []

        # Make separate lists for time and intensity
        for elem in rows:
            time_measured.append(self.datetimestringler(elem[0]))
            intensity.append(elem[1])

        # Convert the datetime variables to hours difference to make them plotable
        mod_time_measured = [(((t - time_measured[0]).total_seconds())/3600) for t in time_measured]
        return mod_time_measured, intensity


    # CREATE TAB AND WIDGET FOR PLOT(tab name)
    def create_plot_tab(self, tab_name):
        # Create a new page for each wavelength
        page = QWidget()
        layout = QVBoxLayout(page)
        page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        page.setObjectName(tab_name)

        # Add a close button to the tab
        close_button = QToolButton()
        close_button.setIcon(QIcon(resource_path(os.path.join(path, "Icons\\x.svg"))))
        close_button.clicked.connect(lambda: self.close_tab(page))

        # Get the index of the added tab
        index = self.tabWidget.addTab(page, tab_name)

        # Set the close button for the tab and go to the new tab
        self.tabWidget.tabBar().setTabButton(index, QTabBar.RightSide, close_button)
        self.tabWidget.setCurrentIndex(index)

        # Create the plot widget
        graphWidget = CustomPlot(self)
        graphWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        graphWidget.setBackground(QColor(self.background))
        layout.addWidget(graphWidget)
        return graphWidget

    # Close function for closing the tabs (plot)
    def close_tab(self, tab_page):
        index = self.tabWidget.indexOf(tab_page)
        print("Page has index: ", index)
        if index != -1:
            self.tabWidget.removeTab(index)
            return True
        else:
            print("such Tab-index dont exist")
            return False
    # Close tab from name, function to avoid two tabs with same name and content
    def close_tab_by_name(self, name):
        tab_count = self.tabWidget.count()
        for index in range(tab_count):
            tab_text = self.tabWidget.tabText(index)
            if tab_text == name:
                self.tabWidget.removeTab(index)

    # ADD DATA TO PLOT
    # Function that plots data, x, y to the given widget, graph_widget.
    def plot_data(self, x, y, graph_widget, threshold=0):
        # Create the scatter plot item
        pen = pg.mkPen(color=QColor(self.color))
        scatter = pg.ScatterPlotItem(pen=pen, symbol="x", size=10)
        scatter.setData(x, y)
        graph_widget.addItem(scatter)
        # Threshold line
        y_thresh = y
        y_thresh.append(threshold)
        # Adjust range of plot
        padding=10
        graph_widget.setYRange(min(y) - padding, max(y_thresh) + padding) # X-axis
        graph_widget.setXRange(min(x) - padding, max(x) + padding) # Y-axis
        
        # Sett colors of the axis
        color = QColor(self.color)
        x_axis = graph_widget.getAxis('bottom')
        y_axis = graph_widget.getAxis('left')
        x_axis.setPen(color=color)
        y_axis.setPen(color=color)

        # Add data to plot
        scatter_data = [{'pos': (x, y)} for x, y in zip(x, y)]
        scatter.setData(scatter_data)
        graph_widget.addItem(scatter)

        # Add the scatter plot item to the plot widget
        graph_widget.addItem(scatter)

        # Switch tab to plot tab to display the plotted graph
        self.backBtn.click()

    # PLOT THRESHOLD LINE
    def threshold_infinite_line(self, threshold, widget):
        pen=pg.mkPen(color=QColor(self.contrast))
        threshold_line = pg.InfiniteLine(pos=threshold, angle=0, pen=pen)
        widget.addItem(threshold_line)


from fpdf import FPDF
# Class for generating PDF report
class PDFReport(FPDF):
    def __init__(self, date):
       super().__init__()
       self.date = date

    # Function for making the Header of the report 
    def header(self):
        # Add logo
        logo = resource_path(os.path.join(path, 'images\Colifast_50pix.png'))
        self.image(logo, 11, 18, 50)
        # Set font for header
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(98, 50, 'Colifast ALARM Sample Result Report', 0, 0, 'C')

    # Function for making a section in the report
    def report_section(self, header_name, pos, var_name_list, var_list):
        # Set the header of the technical info report section
        self.set_font('Arial', '', 12)
        self.set_y(pos)
        self.cell(0, 5, header_name, 0, 1)
        self.draw_line(102)
        # Populate the section with the var names and date points
        self.set_font('Arial', '', 9)
        self.ln(2)

        indentation = 1 # Indent relative to the header
        for i, elem in enumerate(var_name_list):
            print(i)
            self.cell(indentation, 5, '', 0, 0)
            self.cell(10, 5, elem + ":", 0, 0)
            self.cell(80, 5, var_list[i], 0, 1, 'R')
        self.draw_line(102)
    
    # Function to create table in report 
    def table_section(self, pos, data, timing):
        indentation = 4
        self.set_y(pos)
        # Right side of the repport
        self.set_x((self.w/2)+indentation)
        # Print the header row
        self.set_font_size(9)
        self.cell(12, 5, "Hours", 1)
        self.cell(15, 5, 'Intensity', 1)
        self.cell(35, 5, 'Time Measured', 1)
        self.set_font_size(5)
        self.cell(15, 5, 'Readings to Avg', 1)
        self.cell(15, 5, 'nm Bandwidth', 1)
        self.set_font_size(7)
        self.ln()
        # Write data rows to table
        row_nmb = 0
        for row in data:
            column = 0
            self.set_x((self.w/2)+indentation)
            self.cell(12, 5, str(timing[row_nmb]), 1)
            row_nmb += 1
            for item in row:
                if column == 0:
                    width = 15
                elif column == 1:
                    width = 35
                else:
                    width = 15
                # Adjust the cell width as needed
                self.cell(width, 5, str(item), 1)
                column += 1
            self.ln()  # Move to the next row

    # Function to create plot in report
    def plot_section(self, data, table_data):
        try:
            global path
            # Header
            self.set_font_size(12)
            self.set_y(self.h-110)
            self.cell(0, 5, "Growth Curve", 0, 1)
            self.draw_line()

            # Limit and threshold values
            alarm_threshold = float(settings.getThresholdFluo()) * float(data[1][0])
            maximum = max(data[1])
            top = maximum * 1.1 if maximum > 30000 else 30000
            width = max(data[0]) * 1.1
            timing = [int(x) for x in data[0]]
            # Generate plot
            plt.plot(timing, data[1], '-^')
            plt.axhspan(alarm_threshold, top, color='red', alpha=0.8)
            plt.xlim(0, width)
            plt.ylim(0, top)
            plt.xlabel('Incubation Time (h)')
            plt.ylabel('Fluorescence')
            # Threshold value
            plt.text(width, alarm_threshold + 200, 'Threshold: {}'.format(round(alarm_threshold, 1)), fontsize=10, ha='right')
            # Save plot to temporary image file
            plot_path = resource_path(os.path.join(path, settings.getResultFolder() + "plot_image.png"))
            plt.savefig(plot_path, format='png')
            # Clear the plot to prevent it from being displayed
            plt.clf()
            # Print the image file to the PDF
            self.image(plot_path, x=10, y=(self.h-103), w=100, h=75)
            # Delete plot image
            os.remove(plot_path)
            # Make table with data
            self.table_section(200, table_data, timing)
        except:
            return
    # Function to create result section
    def result_section(self, type, result_fluo, result_turb):
        self.set_fill_color(211, 211, 211)
        self.set_font('Arial', '', 12)
        self.set_y(170)
        self.set_x(11)
        right_margin = self.w - 21
        self.cell(right_margin, 5, "Analysis Results", 0, 1, fill=True)
        # Fluorescense results
        typ = type + ":"
        self.set_font('Arial', '', 10)
        self.set_x(11)
        self.cell(40, 5, typ, 0, 0, fill=True)
        self.cell(35, 5, result_fluo, 0, 0, 'R', fill=True)
        # Turb results
        self.cell(29, 5, "", 0, 0, fill=True)
        string = f"Turbidity ALARM ({settings.getThresholdTurb()} NTU):"
        self.cell(55, 5, string, 0, 0, fill=True)
        self.cell(30, 5, result_turb, 0, 1, 'R', fill=True)
    
    # Function to draw line between sections
    def draw_line(self, width=None):
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        if not width:
            width = self.w - 10
        self.line(10, self.get_y(), width, self.get_y())
    
    # Function to create the report footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Footer with name and date
        string = f"COLIFAST {self.date}"
        self.cell(0, 10, string, 0, 0, 'C')


import sqlite3
from threading import Lock

# Class for handling the database and storage of report info, data, and logging
class DatabaseHandler:
    def __init__(self):
        # Create the database folder if not there
        base_path = os.path.normpath("C:/Colifast/APPDATA/")
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        # Initialize a database
        db_path = os.path.join(base_path, "database.db")
        self._initialize_database(db_path)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = Lock()

    def execute_query(self, query, *args):
        with self.lock:
            self.cursor.execute(query, args)
            self.conn.commit()

    def fetch_data(self, query, *args):
        with self.lock:
            self.cursor.execute(query, args)
            return self.cursor.fetchall()

    def close_connection(self):
        with self.lock:
            self.conn.close()

    ## FUNTIONS THAT USES OTHER CLASS FUNCTIONS AND THUS DO NOT NEED TO BE LOCKED ##
    # Function to store data 
    def store_data(self, *args):
        query = "INSERT INTO SpectralData(series_id, sample_id, run_id, time_measured, \
            wavelength_id, intensity, nm_bandwidth, readings_to_average_over) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, *args)
    
    # Function to get the data series from this run all samples from the current bottle
    def get_spectral_data_series(self, sample_id, wavelength):
        # Fetch spectral data for a specific sample
        query = '''SELECT time_measured, intensity
                    FROM SpectralData
                    WHERE run_id IN (
                        SELECT run_id
                        FROM SampleInfo
                        WHERE run_id IN(SELECT run_id FROM Sampleinfo WHERE id = ?) AND wavelength_id = ?
                        ORDER BY sample_number DESC
                    )
                    ORDER BY id ASC'''

        args = (sample_id, wavelength)
        rows = self.fetch_data(query, *args)
        return rows

    # Function to get a sample series with n samples
    def get_n_spectral_data_samples(self, sample_id, wavelength, n):
        # Fetch spectral data for a specific sample/samples(n)
        query = '''SELECT time_measured, intensity
                    FROM SpectralData
                    WHERE sample_id IN (
                        SELECT id
                        FROM SampleInfo
                        WHERE id >= ? AND wavelength_id = ?
                        ORDER BY id ASC
                        LIMIT ?
                    )
                    ORDER BY id ASC'''

        args = (sample_id, wavelength, n)
        rows = self.fetch_data(query, *args)
        return rows

    # Initialization of database upon class call, only creates file if file does not already exist
    def _initialize_database(self, db_path):
        if not os.path.exists(db_path):
            print(f"The database file '{db_path}' does not exist. Creating a new one.")
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Create InstrumentInfo table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS InstrumentInfo (
                        id INTEGER PRIMARY KEY,
                        instrument_serial_number TEXT NOT NULL
                    )
                ''')

                # Prompt user for instrument information
                serial, ok_pressed = QInputDialog.getText(None, "Enter Serial Number", "Serial Number:", QLineEdit.Normal, "")
                if ok_pressed:
                    instrument_serial_number = serial
                else:
                    instrument_serial_number = ""

                # spectrophotometer_serial_number = input("Enter spectrophotometer serial number: ")

                # Insert instrument information into InstrumentInfo table
                cursor.execute('''
                    INSERT INTO InstrumentInfo (instrument_serial_number)
                    VALUES (?)
                ''', (instrument_serial_number,))


                # Create RunInfo table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS RunInfo (
                        id INTEGER PRIMARY KEY,
                        bottle_number INTEGER NOT NULL,
                        media_bottle_size INTEGER NOT NULL,
                        run_start_time TEXT NOT NULL,
                        fluorescent_threshold_ratio REAL NOT NULL,
                        fluorescent_baseline_limit INTEGER,
                        turbidity_threshold REAL NOT NULL,
                        turbidity_raw0 REAL NOT NULL,
                        turbidity_raw5 REAL,
                        turbidity_raw10 REAL NOT NULL,
                        target_bacteria TEXT NOT NULL,
                        method_file TEXT NOT NULL,
                        sample_frequency TEXT NOT NULL,
                        spectrometer_serial_number TEXT NOT NULL
                    )
                ''')
                # Create SampleInfo table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS SampleInfo (
                        id INTEGER PRIMARY KEY,
                        sample_number INTEGER NOT NULL,
                        run_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        sample_start_time TEXT NOT NULL,
                        bact_pos BOOLEAN NOT NULL DEFAULT 0,
                        turb_pos BOOLEAN NOT NULL DEFAULT 0,
                        time_to_detect REAL,
                        fluorescent_baseline REAL,
                        turbidity_reading REAL,
                        external_sample BOOLEAN NOT NULL,
                        sodium_thiosulfate BOOLEAN NOT NULL,
                        full_sample_time TEXT,
                        FOREIGN KEY (run_id) REFERENCES RunInfo (id)

                    )
                ''')

                # Create SpectralData table                                                         !!!!!NEED A SERIES IDENTIFYER TO ALLOW FOR MULTIPLE SERIES IN ONE RUN EG. GROWTH VS RAPID METHOD DATA!!!!
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS SpectralData (
                        id INTEGER PRIMARY KEY,
                        series_id INTEGER,
                        sample_id INTEGER,
                        run_id INTEGER,
                        time_measured TEXT NOT NULL,
                        wavelength_id INTEGER NOT NULL,
                        intensity REAL NOT NULL,
                        nm_bandwidth REAL NOT NULL,
                		readings_to_average_over REAL NOT NULL,
                        FOREIGN KEY (sample_id) REFERENCES SampleInfo (id)
                        FOREIGN KEY (run_id) REFERENCES RunInfo (id)
                    )
                ''')

### Class to listen for signal from the gsm modem into the adu         ###
### in separate thread than both the gui and the workerthread (method) ###
class GSM_listner(QThread):
    # Signal to main thread
    call_start = pyqtSignal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.running = False
        self.lock = Lock()
    # Funcion to start listner
    def run(self):
        with self.lock:
            self.running = True
        n = 10
        interval = 0.1
        counter = 0
        while self.is_running():
            result = adu.read("RPA0")
            print("PA0 result: ", result)
            counter += 1
            if result == 1:
                self.call_start.emit(True)
                print("Signal received from ADU...")
            for _ in range(int(n / interval)):
                if not self.is_running():
                    break
                time.sleep(interval)

    def stop(self):
        with self.lock:
            self.running = False
        self.wait()

    def is_running(self):
        with self.lock:
            return self.running



#### Class for running a full length sample in a separate thread to maintain interoperability of the main GUI thread ####
class WorkerThread(QThread):
    # Signals to GUI
    status_message = pyqtSignal(str)
    update_plot = pyqtSignal(int)
    error_msg = pyqtSignal(str)
    finished_signal = pyqtSignal()
    startTime = pyqtSignal(str)
    bactAlarm = pyqtSignal(str)
    turbAlarm = pyqtSignal(str)
    warning_signal = pyqtSignal(str)
    dialog_result_signal = pyqtSignal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def set_sample_id(self, sample_id):
        self.sample_id = sample_id

    def run(self, method=None):
        # Check that a bottle size is selected
        if settings.getBottleSize() == 0 or settings.getBottleSize() == None:
            ## MESSAGE with Ok button TO FORCE A CHOICE FROM USER ON BOTTLE SIZE ##
            self.error_msg.emit("Bottle size is set to 0. \nPlease choose a bottle size, and remember to insert your media bottle.")
            return

        # Control for settings values that are needed by the method, stop if no values are stored
        elif settings.getSodiumThio() == None or settings.getExtSamp() == None:
            self.error_msg.emit("No saved value for sodium thiosulfate or external sample")

        # Check if there is a method selected
        else:
            self.status_message.emit('Starting new test, please wait')
            QCoreApplication.processEvents()

            #settings.storeMethod('.\Methods\metode_test.txt')
            if method:
                f_name = method
                # Start the long running method
                method_helper.run_method(self, f_name, self.sample_id, self.status_message, self.update_plot\
                                         , self.error_msg, self.startTime, self.bactAlarm, self.turbAlarm, \
                                         self.finished_signal, self.warning_signal, self.dialog_result_signal)
            elif settings.getMethod() is not None or settings.getMethod() == "":
                f_name = settings.getMethod()
                # Start the long running method
                method_helper.run_method(self, f_name, self.sample_id, self.status_message, self.update_plot\
                                         , self.error_msg, self.startTime, self.bactAlarm, self.turbAlarm, \
                                         self.finished_signal, self.warning_signal, self.dialog_result_signal)
            else:
                self.error_msg.emit("Failed to load method file")
            return


# Delay time selector
class TimeSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Window, title, and layout
        self.resize(320, 460)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowTitle("Delay Start Time")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        central_widget = QWidget(self)
        # Naming ensures the stylesheet also applies to this window
        central_widget.setObjectName("centralwidget")
        layout = QVBoxLayout(central_widget)
        header = QHBoxLayout(central_widget)
        # Styling
        style = settings.getStyle()
        if style == "dark_mode":
            self.color = "#fff"
        elif style == "color":
            hex_colors = settings.getColors()
            self.color = hex_colors[4]
        else:
            self.color = "#000"

        # Create Title and Close button
        title = QLabel("Delay Start Time")
        header.addWidget(title, 0, Qt.AlignLeft)
        self.close_btn = QPushButton(central_widget)
        icon_path = resource_path(os.path.join(path, "icons\\x.svg"))
        self.close_btn.setIcon(QIcon(icon_path))
        Colifast_ALARM.icon_changer_for_color_maintenance(self, [self.close_btn], ["x.svg"], self.color)
        self.close_btn.clicked.connect(self.reject)
        header.addWidget(self.close_btn, 0, Qt.AlignRight)
        layout.addLayout(header)

        # Add time selector to the window
        self.time_selector = time_pckr.TimeSelectorWidget(settings.getStyle())
        layout.addWidget(self.time_selector)

        # Create Accept button
        self.accept_button = QPushButton("Set Start Time")
        self.accept_button.clicked.connect(self.accept)
        layout.addWidget(self.accept_button)

        # Wrap everything in the main_layout to get the correct styling
        main_layout.addWidget(central_widget)
        self.setLayout(main_layout)

    # Function for extracting the start time
    def get_chosen_time(self):
        if self.exec_() == QDialog.Accepted:
            return self.time_selector.return_chosen_time()
        else:
            return None

# LogIn window load
class LogIn(QDialog, Ui_login):
    def __init__(self):
        super(LogIn, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        self.login_ok.clicked.connect(self.loginOk)
        self.login_cancel.clicked.connect(self.reject)

    def loginOk(self):
        if self.login_user.text() == '' and settings.getPassword(self.login_pass.text()):
            self.accept()   # Hides the modal dialog and sets the result code to Accepted.
            self.login_user.clear()
            self.login_pass.clear()
        else:
            login_error = ErrorDialog("Username or Password is incorrect")
            accept = login_error.exec_()

    def loginCancel(self):
        self.reject()
        self.login_user.clear()
        self.login_pass.clear()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False


# Custom error message dialog class
class ErrorDialog(QDialog):
    def __init__(self, error_message):
        super(ErrorDialog, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        # Instantiate the UI class from the generated Python file
        self.ui = Ui_ErrorDialog()  # Instantiate the class, not the module
        self.ui.setupUi(self)
        self.ui.errorLabel.setText(error_message)
        self.ui.closebtn.clicked.connect(self.reject)
        self.ui.minimizebtn.clicked.connect(self.showMinimized)
        self.ui.bottleSize.hide()
        self.ui.frameMethod.hide()


        if error_message == "No saved value for sodium thiosulfate or external sample":
            # Create a QVBoxLayout for the customFrame widget
            layout = QHBoxLayout()
            layout_2 = QHBoxLayout()
            # Add checkboxes to the layout
            # Sodium thio check
            self.sodium_checkbox = QCheckBox("Sodium Thiosulfate")
            layout.addWidget(self.sodium_checkbox)
            # # Ext Samp check
            self.external_checkbox = QCheckBox("External Sample")
            layout.addWidget(self.external_checkbox)
            # Create the OK button
            self.ok_button = QPushButton("OK")
            layout_2.addWidget(self.ok_button)
            # Set the layout for the customFrame widget
            self.ui.customFrame.setLayout(layout)
            self.ui.acceptFrame.setLayout(layout_2)
            # Connect the OK button to the accept() slot
            self.ok_button.clicked.connect(self.register_selections)

        elif "Last run was stoped midway," in error_message:
            layout = QHBoxLayout()
            # add buttons Continue, and inserted a new bottle option
            self.continueBtn = QPushButton("Continue with the remaining medium")
            layout.addWidget(self.continueBtn)
            self.newBottle = QPushButton("I have added a new bottle")
            layout.addWidget(self.newBottle)
            self.ui.acceptFrame.setLayout(layout)
            # New bottle - update the remaining value through the new_bottle function,
            # Continue - accept the dialog imediatly
            self.newBottle.clicked.connect(self.new_bottle)
            self.continueBtn.clicked.connect(self.accept)

        elif error_message == "Have you inserted a new media bottle?":
            layout = QHBoxLayout()
            # Add New bottle option
            self.yesBtn = QPushButton("YES")
            layout.addWidget(self.yesBtn)
            self.ui.acceptFrame.setLayout(layout)
            # If clicked - run new_bottle function
            self.yesBtn.clicked.connect(self.new_bottle)

        elif error_message == "Bottle size is set to 0. \nPlease choose a bottle size, and remember to insert your media bottle.":
            layout = QHBoxLayout()
            self.ok = QPushButton("OK")
            layout.addWidget(self.ok)
            self.ui.acceptFrame.setLayout(layout)
            self.customFrame.setLayout(QVBoxLayout())
            self.bottleSize.show()
            # Update bottle size from error dialog
            self.bottleSize.valueChanged.connect(lambda: settings.storeBottleSize(self.ui.bottleSize.value()))
            self.ok.clicked.connect(self.bottle_changer)

        elif error_message == "Failed to load method file":
            layout = QHBoxLayout()
            # Continue push button for when a file is selected
            self.Continue = QPushButton("Continue")
            layout.addWidget(self.Continue)
            self.ui.acceptFrame.setLayout(layout)
            # populate dropdown, and update choice/brows for more
            self.errBox_methodDropDown()
            self.methodSelector.currentIndexChanged.connect(self.errBox_method_file_changer)
            # Make the drop-down frame visible
            self.frameMethod.show()
            # Start a run over, if a valid file is selected.
            self.Continue.clicked.connect(self.new_run)
        else:
            layout_2 = QHBoxLayout()

            # Create the OK button
            self.ok_button = QPushButton("OK")
            layout_2.addWidget(self.ok_button)

            self.ok_button.clicked.connect(self.accept)
            self.ui.acceptFrame.setLayout(layout_2)


    def new_run(self):
        ca = Colifast_ALARM()
        ca.start_new_sample()
        self.accept()

    # Method File selector tree view - Populate the combo box with files from a folder
    def errBox_methodDropDown(self):
        global method_files_path
        # Clear existing items
        self.ui.methodSelector.clear()
        # Add files from the folder to the dropdown
        for file in os.listdir(method_files_path):
            if file.endswith(".txt"):
                self.methodSelector.addItem(file)
        # Add the 'Browse' option
        self.ui.methodSelector.addItem("Browse...")

    ## Method File ##
    # Update selected method file #
    def errBox_method_file_changer(self, index):
        global method_files_path
        # Access the selected text
        file = self.methodSelector.currentText()
        if not os.path.isabs(file):
            file_path = os.path.join(method_files_path, file)
        else:
            file_path = os.path.normpath(file)

        # Perform the desired action based on the selected item
        if file == "Browse...":
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Select Method File", method_files_path)
            if file_path and file_path.endswith(".CFAST"):
                # Add the path browsed if it is not already part of the selector
                path_in_selector = False
                for index in range(self.methodSelector.count()):
                    if file_path == self.methodSelector.itemText(index) and os.path.isFile(file_path):
                        path_in_selector = True

                if not path_in_selector:
                    self.methodSelector.addItem(file_path)
                    # Set the browsed file as the selected file of the selector

                self.methodSelector.setCurrentText(file_path)
            else:
                print("choose a valid file")
                return
        settings.storeMethod(file_path)

        # Check if there are unsaved changes
        if hasattr(self, 'Editor'):
            if self.Editor.is_modified:
                reply = QMessageBox.question(
                    None,
                    'Unsaved Changes',
                    'You have unsaved changes. Do you want to save before loading a new file?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )

                if reply == QMessageBox.Cancel:
                    return  # User canceled the operation
                elif reply == QMessageBox.Yes:
                    self.save_text()  # Save the changes before loading

            # Reset the modified flag
            self.Editor.is_modified = False
            self.Editor.load_text(file_path)

    # Functions for error dialog actions #
    def bottle_changer(self, accept):
        Colifast_ALARM().bottle_changer(accept)
        self.new_run()
        self.accept()
    # Update bottle statusof GUI
    def new_bottle(self):
        settings.storeRemaining(settings.getBottleSize())
        self.accept()
    # Store the dialog input of sodium thiosulfate and external sample
    def register_selections(self):
        settings.storeSodiumThio(self.sodium_checkbox.checkState())
        settings.storeExtSamp(self.external_checkbox.checkState())
        self.accept()

    ## Window control ##
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False


## Spectrometer class ##
class SFMadv(QWidget, spectrometer_window):
    def __init__(self, main, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.main = main

        # SFM buttons and settings
        if settings.getWavelengthTurb() is not None:
            self.nm_turb.setText(str(settings.getWavelengthTurb()))
        else:
            self.nm_turb.setText('860')
            settings.storeWavelength(860)
        if settings.getWavelengthFluo():
            self.nm_flur.setText(str(settings.getWavelengthFluo()))
        else:
            self.nm_flur.setText('430')
        if settings.getIntegrationTime() is not None:
            self.int_time.setText(str(settings.getIntegrationTime()))
        else:
            self.int_time.setText('500')
            settings.storeIntegrationTime(500)
        if settings.getAvrSampleNr() is not None:
            self.avg_nr.setText(str(settings.getAvrSampleNr()))
        else:
            self.avg_nr.setText('3')
            settings.storeAvrSampleNr(int(3))
        if settings.getThresholdFluo() is not None:
            self.thresh_flur.setText(str(settings.getThresholdFluo()))
        else:
            self.thresh_flur.setText('1.5')
            settings.storeThresholdFluo(1.5)
        if settings.getThresholdTurb() is not None:
            self.thresh_turb.setText(str(settings.getThresholdTurb()))
        else:
            self.thresh_turb.setText('4')
            settings.storeThresholdTurb(4)

        self.int_time.returnPressed.connect(self.integrationTime)
        self.avg_nr.returnPressed.connect(self.avgSamples)
        self.nm_flur.returnPressed.connect(self.setFlur)
        self.nm_turb.returnPressed.connect(self.setTurb)
        self.thresh_turb.returnPressed.connect(self.setThreshTurb)
        self.thresh_flur.returnPressed.connect(self.setThreshFlur)

        # Add Ocean Optics devices to the drop down
        try:
            self.update_device_list()
        except:
            pass

        # Button click actions
        self.calib_btn.clicked.connect(self.calibrate)
        self.graph_btn.clicked.connect(self.graphButton)
        self.refreshDeviceList.clicked.connect(self.refresh_device_list)
        self.UVLED.clicked.connect(self.UV_LED)
        self.IRLED.clicked.connect(self.IR_LED)

    # Spectrometer interface for turning on the LEDs - for a simple service controll of the spectrophotometer.
    def UV_LED(self):
        self.main.aduWindow.K3_btn.click()
    def IR_LED(self):
        self.main.aduWindow.K4_btn.click()

    # Give out error message when user tries to update divice list and there are no detected devices
    def refresh_device_list(self):
        if not self.update_device_list():
            no_spectrometer = ErrorDialog("Can't detect any spectrometers, please make sure a device is connected.")
            accept = no_spectrometer.exec_()
            if accept:
                return
    # Update device list if there are any detected - don't give error messages on start up if no devices are connected
    def update_device_list(self):
        self.oceanOpticsDevices.clear()
        self.oceanOpticsDevices.addItem("Spectrometer")
        list = sfm.get_connected_devices()
        if not list:
            return False
        for i in list:
            print(i.serial_number)
            self.oceanOpticsDevices.addItem(i.serial_number)

    ### SFM ###
    ## PLOT A LIVE VIEW OF THE READING FROM THE SPECTROPHOTOMETER ##
    def graphButton(self):
        # Variables for calculating the scaling of the x-and y-axes - scale average over 10 consecutive readings
        self.min_avg = None
        self.max_avg = None
        self.avg_count = 3  # number of updates to average over

        # Toggle live view on or off
        if self.graph_btn.text() == 'Spectrometer LiveView':
            self.graph_btn.setText('Stop LiveView')
        else:
            self.graph_btn.setText('Spectrometer LiveView')
            self.live_view(1)
            return

        # Make a scene for the plot
        self.scene = QGraphicsScene()
        # Assign that scene to a graphicsView layout
        self.graphicsView.setScene(self.scene)

        # Fetch the data from the spectrophtometer
        try:
            self.sfm_initialize()
        except:
            self.graph_btn.setText('Spectrometer LiveView')
            self.live_view(1)
            return

        # Initialize the x and y values
        self.y = sfm.request_spectra()
        self.x = sfm.get_wavelength_mapping()

        ## PLOTTING and DESIGN ##
        # Add pyqtgraph plot instance, and direct it to a graphwidget
        self.graphWidget = CustomPlot(self.main)

        # Color the background of the plot white
        self.graphWidget.setBackground('w')

        # Assign a color to the line
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

        # Add graphWidget to the scene
        self.proxy_widget = self.scene.addWidget(self.graphWidget)

        # Button call for the starting of the liveview of the spectrophotometer
        self.live_view(0)

    ## FUNCTIONS TO LIVE UPDATE PLOT ##
    # Function to continuously update plot with intervall of update
    def live_view(self, stop):
        if stop:
            self.timer.stop()
            sfm.close()
            del self.graphWidget
        else:
            self.timer = QTimer()
            self.timer.setInterval(settings.getIntegrationTime()+10) # milliseconds to hold for next update
            self.timer.timeout.connect(self.update)
            self.timer.start()
            self.update()

    # Function that fetches new data to update the plot in live view
    def update(self):
        # get specter from spectrophotometer
        x = sfm.get_wavelength_mapping()
        y = sfm.request_spectra()
        # Update the data
        self.data_line.setData(x, y)

        # find the minimum and maximum y value if none is found before
        if self.min_avg is None:
            self.min_avg = np.min(y)
            self.max_avg = np.max(y)
        # average together the last 10 values to make the x- and y-scaling of the plot
        else:
            self.min_avg = (self.min_avg * (self.avg_count - 1) + np.min(y)) / self.avg_count
            self.max_avg = (self.max_avg * (self.avg_count - 1) + np.max(y)) / self.avg_count
            # If there is no substantial amount of lighting, set the scale to minimum
            # show 1000 on y axis so that the plot does not jump too much
            if self.max_avg < 1000:
                self.max_avg = 1000
        # otherwise set the plot to fit over the last 10, min and max values.
        self.graphWidget.setYRange(self.min_avg, self.max_avg, padding=0)
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    ## Functions to set values ##
    def integrationTime(self):
        try:
            txt = self.int_time.text()
            print(txt)
            settings.storeIntegrationTime(int(txt))
            sfm.set_integration_time()
        except:
            integration_error = ErrorDialog("Integration time must be a whole number!")
            accept = integration_error.exec_()
    def avgSamples(self):
        try:
            txt = self.avg_nr.text()
            settings.storeAvrSampleNr(int(txt))
        except:
            sample_number_error = ErrorDialog("Sample Number must be a whole number")
            accept = sample_number_error.exec_()
    
    # Open a calibration window for Turbidity
    def calibrate(self):
        cal = CalibrationDialog(self.main)
        cal.exec_()
    
    # Initialize spectrometer from serial number(SN), and then try 
    # first available if SN does not work
    def sfm_initialize(self):
        serial_number = self.oceanOpticsDevices.currentText()
        print(serial_number)
        if not sfm.initialize(serial_number):
            try:
                if not sfm.initialize():
                    spectrometer_error = ErrorDialog("Could not initialize the Spectrophotometer")
                    accept = spectrometer_error.exec_()
            except:
                pass

    # Set the value of turbidity field
    def setTurb(self):
        try:
            nr = int(self.nm_turb.text())
            settings.storeWavelengthTurb(nr)
        except:
            if self.nm_turb.text() == "":
                return
            turbvalue_error = ErrorDialog("Turbidity Nm, Must be a whole number!")
            accept = turbvalue_error.exec_()
    
    # Set the value of fluorescense field
    def setFlur(self):
        try:
            nr = int(self.nm_flur.text())
            settings.storeWavelengthFluo(nr)
        except:
            fluorescensvalue_error = ErrorDialog("Flourescens Nm, Must be a whole number!")
            accept = fluorescensvalue_error.exec_()
    
    # Set the value of Turb threshold field    
    def setThreshTurb(self):
        try:
            nr = int(self.thresh_turb.text())
            settings.storeThresholdTurb(nr)
        except:
            turbthresvalue_error = ErrorDialog("Turbidity Threshold, Must be an integer number!")
            accept = turbthresvalue_error.exec_()
    
    # Set the value of Fluo threshold field    
    def setThreshFlur(self):
        try:
            nr = float(self.thresh_flur.text())
            settings.storeThresholdFluo(nr)
        except:
            turbthresvalue_error = ErrorDialog("Florescence Threshold, Must be a number!")
            accept = turbthresvalue_error.exec_()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.new_window()

    def new_window(self):
        if not hasattr(self, 'wind') or not self.wind.isVisible():
            if hasattr(self, 'free_sfmWindow'):
                self.free_sfmWindow.setParent(None)  # Remove from current parent
            else:
                self.free_sfmWindow = SFMadv(self.main)

            self.wind = QMainWindow()
            self.wind.setCentralWidget(self.free_sfmWindow)
            self.wind.show()
        else:
            self.wind.hide()  # hide the window if it's already visible

# Turbidity calibration class for making a window for calibration
class CalibrationDialog(QDialog):
    def __init__(self, main, parent=None):
        super(CalibrationDialog, self).__init__(parent)
        self.main = main
        self.old_value_label = QLabel("Old Value:")
        self.new_value_label = QLabel("New Value:")

        self.turbidity = QLabel("Turbidity: ")
        self.calibration_group = QButtonGroup(self)

        self.radio_0 = QRadioButton("0")
        self.radio_5 = QRadioButton("5")
        self.radio_10 = QRadioButton("10")
        # Radio buttons for turb solution
        self.calibration_group.addButton(self.radio_0, 0)
        self.calibration_group.addButton(self.radio_5, 5)
        self.calibration_group.addButton(self.radio_10, 10)

        self.old_value = None
        self.new_value = None
        self.calibration_group.buttonClicked.connect(self.cal_val_changed)

        self.use_new_button = QPushButton("Save New Value to settings")
        self.turbReadBtn = QPushButton("Read Turbidity")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.turbidity)
        self.layout.addWidget(self.old_value_label)
        self.layout.addWidget(self.new_value_label)
        self.layout.addWidget(self.radio_0)
        self.layout.addWidget(self.radio_5)
        self.layout.addWidget(self.radio_10)
        self.layout.addWidget(self.use_new_button)
        self.layout.addWidget(self.turbReadBtn)
        self.setLayout(self.layout)

        # Connect button clicks to slots
        self.use_new_button.clicked.connect(self.use_new_value)
        self.turbReadBtn.clicked.connect(self.turbidity_reading)


        self.old_value_label.setText(f"Old Value: {self.old_value}")

    # Change the selected turbidity solution 0, 5, or 10
    def cal_val_changed(self):
        if self.radio_0.isChecked():
            self.old_value = settings.getCalTurb0()
        elif self.radio_10.isChecked():
            self.old_value = settings.getCalTurb10()
        else:
            self.old_value = settings.getCalTurb5()
        self.old_value_label.setText(f"Old Value: {self.old_value}")
        return
    # Store the new read value to settings, for futer use.
    def use_new_value(self):
        if self.radio_10.isChecked():
            settings.storeCalTurb10(int(self.new_value))
        elif self.radio_5.isChecked():
            settings.storeCalTurb5(int(self.new_value))
        elif self.radio_0.isChecked():
            settings.storeCalTurb0(int(self.new_value))

        # Run the background program with the selected calibration value
        # Update the old and new values accordingly
        self.new_value_label.setText("New Value: Calculated")
        self.old_value_label.setText(f"New Value: {self.new_value}")
        self.turbidity.setText("Turbidity: ")

    # Consider running this with a Worker instead, now that warnings 
    # can be printet andcontinuation of program halted until user interact.
    # FUNCTION for running file containing turbidity read
    def turbidity_reading(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Method File", method_files_path)
        if file_path and file_path.endswith(".CFAST"):
            print("Browsed file: ", file_path)
            filename = file_path
        else:
            print("choose a valid file")
            return

        self.main.worker_thread.set_sample_id(None)
        self.main.worker_thread.run(filename)
        self.new_value = float(self.main.startingTime.toPlainText())

        turb_cal_zero_value = settings.getCalTurb0()
        turb_cal_10_value = settings.getCalTurb10()
        turb_threshold = settings.getThresholdTurb()
        # Calculated values based off of the settings variables
        FNU_increment_raw_value_level = (turb_cal_10_value - turb_cal_zero_value)/10
        turb_alarm_level = FNU_increment_raw_value_level * turb_threshold + turb_cal_zero_value

        self.new_value_label.setText(f"New Value: {self.new_value}")
        self.turbidity.setText(f"Turbidity: {round((self.new_value - turb_cal_zero_value)/FNU_increment_raw_value_level, 3)}")

        return self.new_value

# Custom plot and GraphicsView is made to control plot
# actions and to Direct mouse release to main gui from
# objects that have their own implementation of mouse
# actions.

# Custom Plot
class CustomPlot(pg.PlotWidget):
    def __init__(self, self_main, *args, **kwargs):
        super(CustomPlot, self).__init__(*args, **kwargs)
        self.main = self_main
        self.setAspectLocked(False)

    def checkRanges(self, *args, **kwargs):
        # Check and adjust the X and Y ranges if they go into the negative part
        x_range = self.viewRange()[0]
        y_range = self.viewRange()[1]

        if x_range[0] < 0:
            self.setXRange(0, x_range[1])

        if y_range[0] < 0:
            self.setYRange(0, y_range[1])

    def mouseReleaseEvent(self, event):
        # Handle mouse release event here
        if event.button() == Qt.LeftButton:
            self.main.handleMouseRelease(event)
            super().mouseReleaseEvent(event)

    def wheelEvent(self, ev):
        # Custom wheel event handling for zooming in one direction and out in the other
        factor = 1.1  # Zoom factor
        angle = ev.angleDelta().y()

        if angle > 0:
            # Scrolling up, zoom in
            self.getViewBox().scaleBy((factor, 1))
        else:
            # Scrolling down, zoom out
            self.getViewBox().scaleBy((1 / factor, 1))
        ev.accept()

# GraphicsView
class CustomGraphicsView(QGraphicsView):
    def __init__(self, instance, *args, **kwargs):
        super(CustomGraphicsView, self).__init__(*args, **kwargs)
        self.instance = instance

    def mouseReleaseEvent(self, event):
        # Handle mouse release event here
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item and isinstance(item, QGraphicsItem):
                print("Mouse released on item:", item)

        # Propagate the event to the aduadv class
        self.instance.handleMouseRelease(event)
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        # Handle mouse release event here
        if event.button() == Qt.LeftButton:
            print("Mouse Pressed on the graphics view")

            # Example: Check if there's an item at the release position
            item = self.itemAt(event.pos())
            if item and isinstance(item, QGraphicsPixmapItem):
                self.instance.handleMousePress(event)
            elif item and isinstance(item, QGraphicsItem):
                print("Mouse pressed on item:", item)
                super().mousePressEvent(event)
                self.instance.handleMousePress(event)
            else:
                # Propagate the event to the aduadv class
                self.instance.handleMousePress(event)

    def mouseMoveEvent(self, event):
        # Propagate the event to the aduadv class
        self.instance.handleMouseMove(event)
        super().mouseMoveEvent(event)


## Liquid handling class ##
class LiquidHandling(QWidget):
    def __init__(self, main):
        super().__init__()
        self.initUI()
        self.main = main
    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        # self.page = QWidget()
        self.layout = QVBoxLayout(self)
        # self.page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.page.setLayout(self.layout)

        # Set a scene for the images
        self.graphicsView = CustomGraphicsView(self)
        # self.page.addWidget((self.graphicsView))
        self.graphicsView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.layout.addWidget(self.graphicsView)

        # Load the image as a QPixmap and add it to the scene
        image_path = resource_path(os.path.join(path, "images\\Liquid HAndling.jpg"))
        pixmap = QPixmap(image_path)
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)

        # Initialize buttons
        self.initialize_xlp_btn = QPushButton()
        self.custom_command = QPushButton()
        self.dispense_btn = QPushButton()
        self.aspirate_btn = QPushButton()
        self.fill_btn = QPushButton()
        self.empty_btn = QPushButton()
        self.valve_changer_btn = QPushButton()
        # ToolTips
        self.valve_changer_btn.setToolTip("Shift valve")
        self.dispense_btn.setToolTip("Dispense syringe volume")
        self.aspirate_btn.setToolTip("Aspirate syringe volume")
        self.fill_btn.setToolTip("Fill up the whole syringe")
        self.empty_btn.setToolTip("Empty the whole syringe")
        ## Other elements ##
        # SYRINGE PUMP
        # COM details
        if not settings.getXLPcom():
            settings.storeXLPcom(1)
        self.xlp_com = QWidget()
        self.com_xlp = QLineEdit(str(settings.getXLPcom()))
        com_xlp_label = QLabel("Syringe COM Port")
        self.com_xlp.setMaximumWidth(50)
        com_mpv_layout = QHBoxLayout()
        com_mpv_layout.addWidget(self.com_xlp)
        com_mpv_layout.addWidget(com_xlp_label)
        com_mpv_layout.addSpacing(160)
        self.xlp_com.setLayout(com_mpv_layout)

        self.xlp_volume_display = QLabel()

        # Send command
        self.command = QLineEdit()
        self.command.setMaximumWidth(50)
        com_mpv_layout.addWidget(self.command)

        self.group_box = QGroupBox("Pump Specs")
        groupboxLayout = QVBoxLayout()

        volume_box = QHBoxLayout()
        flowrate_box = QHBoxLayout()

        label1 = QLabel("Syringe Volume [μl]")
        self.syringeVolume_input = QLineEdit()
        self.syringeVolume_input.setMaximumWidth(50)
        volume_box.addWidget(label1)
        volume_box.addWidget(self.syringeVolume_input)

        label2 = QLabel("Flowrate [μl/s]")
        self.flowrate_input = QLineEdit()
        self.flowrate_input.setMaximumWidth(50)
        flowrate_box.addWidget(label2)
        flowrate_box.addWidget(self.flowrate_input)

        vol = QWidget()
        vol.setLayout(volume_box)
        flow = QWidget()
        flow.setLayout(flowrate_box)
        groupboxLayout.addWidget(vol)
        groupboxLayout.addWidget(flow)
        self.group_box.setLayout(groupboxLayout)

        # MULTIPOSITION VALVE
        self.initialize_btn_mpv = QPushButton()
        # Valve buttons
        self.V1_btn = QRadioButton("1")
        self.V2_btn = QRadioButton("2")
        self.V3_btn = QRadioButton("3")
        self.V4_btn = QRadioButton("4")
        self.V5_btn = QRadioButton("5")
        self.V6_btn = QRadioButton("6")
        # Create a button group for Valve buttons
        self.valve_button_group = QButtonGroup(self)

        # Add radio buttons to the group
        self.valve_button_group.addButton(self.V1_btn)
        self.valve_button_group.addButton(self.V2_btn)
        self.valve_button_group.addButton(self.V3_btn)
        self.valve_button_group.addButton(self.V4_btn)
        self.valve_button_group.addButton(self.V5_btn)
        self.valve_button_group.addButton(self.V6_btn)

        # Set the exclusive property of the group
        self.valve_button_group.setExclusive(True)
        self.setStyleSheet(
            "QRadioButton {"
            "   background-color: transparent;"
            "   border-radius: 13px;"
            "   border: 2px solid gray;"
            "   color: green;"
            "}"
            "QRadioButton::indicator {"
            "   width: 0;"
            "   border: 1px solid red;"
            "}"
            "QRadioButton::indicator:checked {"
            "   background-color: darkergray;"
            "   border-radius: 13px;"
            "   border: 1px solid red;"
            "}"
            "QRadioButton:hover {"
            "   background-color: grey;"
            "   border-radius: 13px;"
            "}"
        )

        ## Set tooltip ##
        self.V1_btn.setToolTip("Waste")
        self.V2_btn.setToolTip("Sample Out")
        self.V3_btn.setToolTip("Reagent B")
        self.V4_btn.setToolTip("Acid")
        self.V5_btn.setToolTip("Sample")
        self.V6_btn.setToolTip("Medium")

        # COM details
        if not settings.getMPVcom():
            settings.storeMPVcom(2)
        self.mpv_com = QWidget()
        self.com_mpv = QLineEdit(str(settings.getMPVcom()))
        self.com_mpv.setMaximumWidth(50)
        com_mpv_label = QLabel("MPV COM Port")
        com_mpv_layout = QHBoxLayout()
        com_mpv_layout.addWidget(self.com_mpv)
        com_mpv_layout.addWidget(com_mpv_label)
        self.mpv_com.setLayout(com_mpv_layout)

        # Peristaltic Pump
        self.periPump = QPushButton()
        self.periPump.setToolTip("Peristaltic Pump")

        # Couple to licking functions
        self.valve_button_group.buttonClicked.connect(self.updateRadioButtons)
        self.dispense_btn.clicked.connect(self.dispSyringe)
        self.aspirate_btn.clicked.connect(self.aspSyringe)
        self.fill_btn.clicked.connect(self.fillSyringe)
        self.empty_btn.clicked.connect(self.emptySyringe)
        self.com_xlp.textChanged.connect(self.update_xlpCom)
        self.initialize_xlp_btn.clicked.connect(self.xlp_initialize) # might not work
        self.custom_command.clicked.connect(self.send_command) # might not work
        self.com_mpv.textChanged.connect(self.update_mpvCom)
        self.initialize_btn_mpv.clicked.connect(self.mpv_initialize) # might not work
        self.valve_changer_btn.clicked.connect(self.valve_changer)
        self.periPump.clicked.connect(self.toggle_periPump)

        # Button details dictionary
        self.widget_data = {
             'Initialize Syringe': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.initialize_xlp_btn,
                 'position': (130, -35),  # Y-value decreased by 90
             },
            'Custom command': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.custom_command,
                 'position': (245, -10),  # Y-value decreased by 90
             },
             'Dispense': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.dispense_btn,
                 'icon': os.path.join(path, "icons/chevron-up.svg"),
                 'style': "QPushButton {width: 20; height: 40;} QPushButton:hover{width: 20; height: 40; background-color: green}",
                 'position': (220, 130),  # Y-value decreased by 90
             },
             'Aspirate': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.aspirate_btn,
                 'icon': os.path.join(path, "icons/chevron-down.svg"),
                 'style': "QPushButton {width: 20; height: 40;} ",
                 'position': (220, 180),  # Y-value decreased by 90
             },
             'Fill': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.fill_btn,
                 'style': "QPushButton { width: 30; height: 25;}",
                 'position': (40, 180),  # Y-value decreased by 90
             },
             'Empty': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.empty_btn,
                 'style': "QPushButton {width: 30; height: 25;}",
                 'position': (40, 140),  # Y-value decreased by 90
             },
             'valve changer': {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.valve_changer_btn,
                # 'icon': "images/peri p.gif",
                 'style': "QPushButton {background-color: transparent; width: 75; height:75; border-radius: 37; color: transparent; } QPushButton:hover {background-color: transparent; width: 75; height:75; border: 6px solid lightblue; border-radius: 37; }",
                 # 'style': "QPushButton { background-color: transparent; border: none; text-align: center;}",# border-radius: 50px; width: 75px; height: 75px; }",
                 'position': (130, 3),
             },
             'Pump Specs':  {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.group_box,
                 'style': "QGroupBox {background-color: transparent; width: 50; height:40;}",
                 'position': (260, 110),
             },
             'volume display':  {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.xlp_volume_display,
                 'style': "QLabel {background-color: transparent; width: 50; height:40; color: transparent; }",
                 'position': (125, 101),
             },
             'COM XLP':  {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.xlp_com,
                 'style': "QWidget {background-color: transparent; width: 50; height:20;}",
                 'position': (-50, -46),
             },
             'COM MPV':  {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.mpv_com,
                 'style': "QWidget {background-color: transparent; width: 50; height:20;}",
                 'position': (360, -46),
             },
             'Initialize MPV':  {
                 'proxy': QGraphicsProxyWidget(),
                 'button': self.initialize_btn_mpv,
                 'position': (520, -35),
             },
             'V1': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V1_btn,
                # 'icon': "images/ring_red.png",
                'position': (517, 29),  # Y-value decreased by 90
            },
            'V2': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V2_btn,
                # 'icon': "images/ring_red.png",
                'position': (493, 77),  # Y-value decreased by 90
            },
            'V3': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V3_btn,
                # 'icon': "images/ring_red.png",
                'position': (519, 122),  # Y-value decreased by 90
            },
            'V4': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V4_btn,
                # 'icon': "images/ring_red.png",
                'position': (578, 122),  # Y-value decreased by 90
            },
            'V5': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V5_btn,
                # 'icon': "images/ring_red.png",
                'position': (602, 74),  # Y-value decreased by 90
            },
            'V6': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.V6_btn,
                # 'icon': "images/ring_red.png",
                'position': (578, 29),  # Y-value decreased by 90
            },
            'Peristaltic Pump': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.periPump,
                # 'icon': "images/peri p.gif",
                'style': "QPushButton {background-color: transparent; width: 100; height:100; border-radius: 50; color: transparent; } QPushButton:hover {background-color: transparent; width: 100; height:100; border: 6px solid lightblue; border-radius: 50; }",
                'position': (302, 320),  # Y-value decreased by 90
            },
             # Add more buttons as needed
        }


        # Set the overlay layout to contain the ProxyWidgets
        self.overlay_layout = QGraphicsLinearLayout()

        for elem_name, data in self.widget_data.items():
            proxy = data['proxy']
            button = data['button']
            position = data['position']
            # Set the objectName property of the QPushButton

            if 'style' in data:
                button.setStyleSheet(data['style'])  # Apply the style to the button

            if 'icon' in data:
                icon = QIcon(data['icon'])
                button.setIcon(icon)
                # button.setStyleSheet("QPushButton{width: 100; height: 100; }")
                button.setFlat(True)
            else:
                try:
                    if elem_name[0] == 'V':
                        button.setFixedSize(30, 30)
                        # icon.addPixmap(icon.pixmap(button.size(), mode=Qt.TransparentMode))
                        button.setStyleSheet("""
                            QRadioButton {
                                background-color: transparent;
                                border: 6px solid lightblue;
                                border-radius: 13px;
                            }
                            QRadioButton::indicator {
                                width: 0;
                            }
                            QRadioButton:hover{
                                background-color: transparent;
                                border: 6px solid lightgreen;
                                border-radius: 13px;
                            }
                        """)
                        # Set the style sheet to make it transparent initially

                        # Connect a slot to the toggled signal to change the background when checked
                    else:
                        button.setText(elem_name)
                except:
                    pass
            # Set the widget for the proxy
            proxy.setWidget(button)

            # Set the position
            proxy.setPos(*position)

            self.overlay_layout.addItem(proxy)
            self.scene.addItem(proxy)

    def update_xlpCom(self):
        settings.storeXLPcom(int(self.com_xlp.text()))
    def update_mpvCom(self):
        settings.storeMPVcom(int(self.com_mpv.text()))

    def updateRadioButtons(self, button):
        try:
            for btn in self.valve_button_group.buttons():
                if btn == button:
                    try:
                        mpv.liquid(int(btn.text()))
                    except:
                        mpv.initialize()
                        mpv.liquid(int(btn.text()))

                    btn.setStyleSheet("""
                        QRadioButton{
                            background-color: transparent;
                            border-radius: 13px;
                            color: red;
                        }
                        QRadioButton::indicator{
                            width: 0;
                            color: red;
                        }
                    """)
                        #background-color: darkgrey; width: 22; height: 22; border-radius: 11px;
                else:
                    btn.setStyleSheet("""
                        QRadioButton {
                            background-color: transparent;
                            border: 6px solid lightblue;
                            border-radius: 13px;
                        }
                        QRadioButton::indicator {
                            width: 0;
                        }
                        QRadioButton:hover{
                            background-color: transparent;
                            border: 6px solid lightgreen;
                            border-radius: 13px;
                        }
                    """)
        except:
            initialization_failure = ErrorDialog("Could not initialize Multiposition Valve")
            accept = initialization_failure.exec_()

    # Functions for the button clicks
    # Peristaltic Pump
    def toggle_periPump(self):
        def on_off(peri_pump):
            if peri_pump:
                adu.off(0)
                self.periPump.setToolTip("Turn Peristaltic Pump ON")
            else:
                adu.on(0)
                self.periPump.setToolTip("Turn Peristaltic Pump OFF")

        try:
            peri_pump = adu.read("RPK0")
        except:
            try:
                adu.initialize()
                peri_pump = adu.read("RPK0")
            except:
                initialization_failure = ErrorDialog("ADU is not detected")
                accept = initialization_failure.exec_()
                return False

        on_off(peri_pump)
    # MPV
    def mpv_initialize(self):
        try:
            mpv.initialize()
        except:
            initialization_failure = ErrorDialog("Could not initialize Multiposition Valve")
            accept = initialization_failure.exec_()
            return False

    # Syringe Pump
    def xlp_initialize(self):
        try:
            xlp.initialize()
        except:
            initialization_failure = ErrorDialog("Could not initialize Syringe Pump")
            accept = initialization_failure.exec_()
            return False
    def send_command(self):
        try:
            if self.command.text() == "":
                send_command_failure = ErrorDialog("Please type in a command")
                accept = send_command_failure.exec_()
                return False
            response = xlp.send_command(self.command.text())
            send_command_response = ErrorDialog(f"Response from syringe: {response}")
            accept = send_command_response.exec_()
        except:
            send_command_failure = ErrorDialog("Could not send command, is syringe pump initialized?")
            accept = send_command_failure.exec_()
            return False
    def valve_changer(self):
        try:
            valve = str(xlp.valve_position())
            if valve == "o":
                xlp.valve_in()
                self.valve_changer_btn.setToolTip("Shift valve out")
            elif valve == "i":
                xlp.valve_out()
                self.valve_changer_btn.setToolTip("Shift valve in")
            else:
                print("not o or i, but: ", valve)
        except:
            initialization_failure = ErrorDialog("Could not initialize Syringe Pump")
            accept = initialization_failure.exec_()
    def aspSyringe(self):
        try:
            print('aspirating syringe volume')
            asp_vol = int(self.syringeVolume_input.text())
            print(asp_vol)
            if not isinstance(asp_vol, int):
                number_error = ErrorDialog("Volume must be a number")
                accept = number_error.exec_()
                return False
            if 5 <= asp_vol <= 25000:
                try:
                    xlp.flowrate(int(self.flowrate_input.text()))
                    xlp.aspirate(asp_vol)
                    try:
                        xlp.delay_until_done()
                        stat = xlp.pump_position()
                        self.xlp_volume_display.setText(str(stat))
                    except:
                        self.xlp_volume_display.setText('-')
                except:
                    asp_error = ErrorDialog("Could not aspirate")
                    accept = asp_error.exec_()
            else:
                volume_error = ErrorDialog("Aspirate volume must be between 5 µL and 25000 µL")
                accept = volume_error.exec_()
        except:
            initialization_failure = ErrorDialog("Could not initialize Syringe Pump")
            accept = initialization_failure.exec_()
    def dispSyringe(self):
            try:
                print('dispensing syringe volume')
                disp_vol = int(self.xlp_volume_display.text())
                if not isinstance(disp_vol, int):
                    number_error = ErrorDialog("Volume must be a number")
                    accept = number_error.exec_()
                    return False
                if 5 <= disp_vol <= 25000:
                    try:
                        xlp.flowrate(int(self.flowrate_input.text()))
                        xlp.dispense(disp_vol)
                        try:
                            xlp.delay_until_done()
                            stat = xlp.pump_position()
                            self.xlp_volume_display.setText(str(stat))
                        except:
                            self.xlp_volume_display.setText('-')
                    except:
                        dispense_error = ErrorDialog("Could not dispense volume")
                        accept = dispense_error.exec_()
                        # QMessageBox.warning(self, 'XLP', 'Could not dispense volume')
                else:
                    volume_error = ErrorDialog("Dispense volume must be between 5 µL and 25000 µL")
                    accept = volume_error.exec_()
                    # QMessageBox.warning(self, 'XLP', 'Dispense volume must be between 5 µL and 25000 µL')
            except:
                initialization_failure = ErrorDialog("Could not initialize Syringe Pump")
                accept = initialization_failure.exec_()
    def emptySyringe(self):
        print("empty syringe")
        try:
            xlp.flowrate(int(self.flowrate_input.text()))
            xlp.empty()
            try:
                xlp.delay_until_done()
                stat = xlp.pump_position()
                self.xlp_volume_display.setText(str(stat))
            except:
                self.xlp_volume_display.setText('-')
        except:
            empty_error = ErrorDialog("Could not empty pump")
            accept = empty_error.exec_()
            # QMessageBox.warning(self, 'XLP', 'Could not empty pump')
    def fillSyringe(self):
        print("fill syringe")
        try:
            xlp.flowrate(int(self.flowrate_input.text()))
            xlp.fill()
            try:
                xlp.delay_until_done()
                stat = xlp.pump_position()
                self.xlp_volume_display.setText(str(stat))
            except:
                self.xlp_volume_display.setText('-')
        except:
            fill_error = ErrorDialog("Could not fill pump")
            accept = fill_error.exec_()
            # QMessageBox.warning(self, 'XLP', 'Could not fill pump')

    # resize graphics view along with window size
    def resizeEvent(self, event):
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    #
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.new_window()

    def new_window(self):
        if not hasattr(self, 'wind') or not self.wind.isVisible():
            if hasattr(self, 'free_LqHwindow'):
                self.free_LqHwindow.setParent(None)  # Remove from current parent
            else:
                self.free_LqHwindow = LiquidHandling(self.main)

            self.wind = QMainWindow()
            self.wind.setCentralWidget(self.free_LqHwindow)
            self.wind.show()
        else:
            self.wind.hide()  # hide the window if it's already visible

    def handleMousePress(self, event):
        # Your custom handling of mouse release event
        self.main.handleMousePress(event)

    def handleMouseMove(self, event):
        # Your custom handling of mouse release event
        self.main.handleMouseMove(event)

    def handleMouseRelease(self, event):
        # Your custom handling of mouse release event
        self.main.handleMouseRelease(event)


# Class for selecting the custom color class of the GUI
class ColorPicker(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        hex_colors = settings.getColors()
        print(hex_colors)
        values = []
        for color in hex_colors:
            hue, _,_ = self.hex_to_hsv(color)
            values.append(hue)
            print("Color: ", color, hue)

        # Create sliders containing all the hsv color values for each object in gui
        self.background_slider = self.create_slider("Background", values[0])
        self.foreground_slider = self.create_slider("Foreground", values[1])
        self.btn_press_slider = self.create_slider("Button Press", values[2])
        self.contrast_slider = self.create_slider("Contrast", values[3])
        self.color_slider = self.create_slider("Text Color", values[4])
        # Create general HSV saturation and
        self.value_slider = self.create_V_slider("Value", hex_colors[5])
        self.saturation_slider = self.create_V_slider("Saturation", hex_colors[6])

        self.sliders = [self.background_slider[1], self.foreground_slider[1], self.btn_press_slider[1], self.contrast_slider[1], self.color_slider[1]]

        layout.addWidget(self.background_slider[0])  # Add the label to the layout
        layout.addWidget(self.background_slider[1])  # Add the slider to the layout
        layout.addWidget(self.foreground_slider[0])
        layout.addWidget(self.foreground_slider[1])
        layout.addWidget(self.btn_press_slider[0])
        layout.addWidget(self.btn_press_slider[1])
        layout.addWidget(self.contrast_slider[0])
        layout.addWidget(self.contrast_slider[1])
        layout.addWidget(self.color_slider[0])
        layout.addWidget(self.color_slider[1])
        # Horisontal Saturation and Value sliders
        h_layout.addWidget(self.value_slider[0])
        h_layout.addWidget(self.value_slider[1])
        h_layout.addWidget(self.saturation_slider[0])
        h_layout.addWidget(self.saturation_slider[1])

        # Create a widget to hold the layouts
        central_layout = QHBoxLayout()
        central_layout.addLayout(layout)
        central_layout.addLayout(h_layout)

        self.setLayout(central_layout)
        self.setWindowTitle('Color Picker')
        self.setGeometry(100, 100, 500, 300)


    def create_slider(self, label_text, initial_value):
        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 359)  # Hue values range from 0 to 359 in HSV
        slider.setValue(initial_value)

        slider.valueChanged.connect(lambda value, label=label: self.slider_changed(value, label))

        return label, slider

    def create_V_slider(self, label_text, initial_value):
        label = QLabel(label_text)
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 250)  # Hue values range from 0 to 359 in HSV
        slider.setValue(initial_value)
        slider.valueChanged.connect(lambda value, label=label: self.slider_changed(value, label))
        return label, slider

    # Update all sliders
    def slider_changed(self, value, label):
        hex_colors = tuple(self.color_update(slider.value()) for slider in self.sliders)
        hex_colors = hex_colors + (self.value_slider[1].value(), self.saturation_slider[1].value())
        print(hex_colors)
        settings.storeColors(hex_colors)
        self.main_window.change_stylesheet("color")

    # Update the colors, with all HSV - components
    def color_update(self, hue):
        print(hue)
        # Update the color variable based on the slider value and convert to hex
        color = QColor()
        value = self.value_slider[1].value()
        saturation = self.saturation_slider[1].value()
        color.setHsv(hue, saturation, value) #self.saturation_slider.value(), self.value_slider.value())
        hex_color = color.name()
        return hex_color

    def hsv_to_hex(self, hsv_color):
        color = QColor()
        color.setHsv(hsv_color[0], hsv_color[1], hsv_color[2])
        return color.name()

    def hex_to_hsv(self, hex_color):
        color = QColor(hex_color)
        return color.hue(), color.saturation(), color.value()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Colifast_ALARM()
    main_window.show()
    app.exec_()


