from PyQt5.QtGui import (
    QPainter, QPixmap, QMouseEvent, QPalette, QCursor,
    QTextCharFormat, QIcon, QColor, QFont, QBrush, QTransform
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QPoint, QCoreApplication,
    QThread, pyqtSignal, QEvent, QDate, QSize, QTimer
)
from PyQt5.QtWidgets import (
    QLineEdit, QGroupBox, QGraphicsProxyWidget, QGraphicsLinearLayout,
    QHBoxLayout, QVBoxLayout, QLabel, QButtonGroup, QRadioButton,
    QPushButton, QGraphicsPixmapItem, QGraphicsView, QGraphicsScene,
    QMainWindow, QFrame, QMessageBox, QToolButton, QDockWidget, QGraphicsItem,
    QWidget, QApplication, QSizePolicy, QDialog, QFileDialog, QCheckBox, QTabWidget
)
import sys
from components.adu.adu import adu
import os
import time
from python_designer_files.ADUadv import Ui_Form as ADU_window
from resource_path import resource_path

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_directory = os.path.dirname(current_file_directory)


app = QApplication(sys.argv)

# Class for graphics interfaces for implementing mouse releases in the graphics, back to main app
class CustomGraphicsView(QGraphicsView):
    def __init__(self, instance, *args, **kwargs):
        super(CustomGraphicsView, self).__init__(*args, **kwargs)
        self.instance = instance
           
    def mouseReleaseEvent(self, event):
        # Handle mouse release event here
        self.instance.handleMouseRelease(event)
        # Propagate the event to the aduadv class 
        super().mouseReleaseEvent(event)
        
    def mousePressEvent(self, event):
        # Handle mouse release event here
        if event.button() == Qt.LeftButton:
            # Example: Check if there's an item at the release position
            item = self.itemAt(event.pos())
            # If pixmap item - 
            if item and isinstance(item, QGraphicsPixmapItem):
                self.instance.handleMousePress(event)
            # If Graphics View item - 
            elif item and isinstance(item, QGraphicsItem):
                super().mousePressEvent(event)
                self.instance.handleMousePress(event)
            else:
                # Propagate the event to the aduadv class 
                self.instance.handleMousePress(event)
        
    def mouseMoveEvent(self, event):
        # Propagate the event to the aduadv class 
        self.instance.handleMouseMove(event)
        super().mouseMoveEvent(event)
        

## ADU class ##
class ADUadv(QWidget, ADU_window):
    instantiated = False  # flag for checking the advanced menu status
    def __init__(self, main, *args, **kwargs):
        ADUadv.instantiated = True
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.main = main
        self.blink_timer = None
        
        # Install the event filter
        self.installEventFilter(self)
        
        # Set the custom buttons' icons
        self.green_ring = QIcon(resource_path(os.path.join(parent_directory, "Images\\ring1.png")))
        self.red_ring = QIcon(resource_path(os.path.join(parent_directory, "Images\\ring_red.png")))

        self.graphics_View = CustomGraphicsView(self)     
        self.verticalLayout_6.addWidget(self.graphics_View)
        # Set a scene for the images
        self.scene = QGraphicsScene()
        self.graphics_View.setMouseTracking(True)
        self.graphics_View.setScene(self.scene)
        
        # Load the image as a QPixmap and add it to the scene
        pixmap = QPixmap(resource_path(os.path.join(parent_directory, "Images\\ADU2082.png")))
        image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(image_item)
        
        # Buttons
        self.self_adu_button.clicked.connect(self.selfTestADU)
        self.adu_load.clicked.connect(self.load_adu)
        self.reset_btn.clicked.connect(self.reset)
        self.please_load = True

        # Create button variables for the adu channels
        self.PA0_btn = QPushButton()
        self.PA1_btn = QPushButton()
        self.PA2_btn = QPushButton()
        self.K0_btn = QPushButton()
        self.K1_btn = QPushButton()
        self.K2_btn = QPushButton()
        self.K3_btn = QPushButton()
        self.K4_btn = QPushButton()
        self.K5_btn = QPushButton()
        self.K6_btn = QPushButton()
        self.K7_btn = QPushButton()
        
        ## Set tooltip ##
        # Read
        self.PA0_btn.setToolTip("GSM - Start")
        self.PA1_btn.setToolTip("ThermoSwitch")
        self.PA2_btn.setToolTip("Float Switches")
        # WRITE
        self.K0_btn.setToolTip("Peristaltic Pump")
        self.K1_btn.setToolTip("GSM, positive sample")
        self.K2_btn.setToolTip("GSM, Stop/error")
        self.K3_btn.setToolTip("UV LED")
        self.K4_btn.setToolTip("IR LED")
        self.K5_btn.setToolTip("Bacteria alarm - Red light & PLC")
        self.K6_btn.setToolTip("Turbidity alarm - PLC")
        self.K7_btn.setToolTip("Stop/Error - Yellow light & PLC")
       
        # Dictionary for holding the button elements for positioning on top of the image
        self.widget_data = {
            'PA0': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.PA0_btn,
                'position': (218, 14),  # Y-value decreased by 90
            },
            'PA1': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.PA1_btn,
                'position': (238, -6),  # Y-value decreased by 90
            },
            'PA2': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.PA2_btn,
                'position': (258, 14),  # Y-value decreased by 90
            },
            'K0': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K0_btn,
                'position': (103, 290),  # Y-value decreased by 90
            },
            'K1': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K1_btn,
                'position': (137, 270),  # Y-value decreased by 90
            },
            'K2': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K2_btn,
                'position': (175, 290),  # Y-value decreased by 90
            },
            'K3': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K3_btn,
                'position': (210, 270),  # Y-value decreased by 90
            },
            'K4': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K4_btn,
                'position': (244, 290),  # Y-value decreased by 90
            },
            'K5': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K5_btn,
                'position': (279, 270),  # Y-value decreased by 90
            },
            'K6': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K6_btn,
                'position': (317, 290),  # Y-value decreased by 90
            },
            'K7': {
                'proxy': QGraphicsProxyWidget(),
                'button': self.K7_btn,
                'position': (352, 270),  # Y-value decreased by 90
            },
        }


        # Set the overlay layout to contain the ProxyWidgets
        self.overlay_layout = QGraphicsLinearLayout()

        # Connect all buttons to its respective clicks
        for elem_name, data in self.widget_data.items():
            proxy = data['proxy']
            button = data['button']
            position = data['position']
            # Set the property of the QPushButtons
            button.setIcon(self.red_ring)
            button.setFlat(True)
            button.setStyleSheet("background-color: transparent;")
            button.setIconSize(QSize(22, 22))
            button.setObjectName(elem_name)

            # P-channels are read-only, and clicking them only reads the input and changes button according to the returned value
            if "P" in elem_name:
                relay = str(elem_name)
                button.clicked.connect(lambda checked, elem_name=elem_name, \
                                       button=button: self.setColour(str(elem_name.strip("P")), button))
            # Toggle relays when clicked 
            else:
                relay = str(elem_name)
                button.clicked.connect(self.toggleRelay) #lambda: self.toggleRelay(str(elem_name.strip("P")), button))

            # Set the widget for the proxy
            proxy.setWidget(button)
            # Append proxy to the main layout
            proxy.setPos(*position)
            self.overlay_layout.addItem(proxy)
            self.scene.addItem(proxy)

        # Initialize ADU and update buttons
        self.initialize()
        self.update_adu_relay_buttons()

    # Function for toggling relay (sender)
    def toggleRelay(self):
        button = self.sender()
        relay = button.objectName()
        # Check connection
        if self.please_load:
            self.not_connected()
        else:
            # Read status of relay first, then switch
            read_command = 'RP{}'.format(relay)
            status = adu.read(read_command)
            if status == 0:
                write_command = 'S{}'.format(relay)
                icon = self.green_ring
            elif status == 1:
                write_command = 'R{}'.format(relay)
                icon = self.red_ring
            else:
                self._not_connected_error(relay)
                

            adu.write(write_command)
            button.setIcon(icon)

    # Function for setting the color of the relay/input 
    def setColour(self, relay, button):
        # Check connection
        if self.please_load:
            self.not_connected()
        else:
            # Read status of relay and adjust the button features
            read_command = 'RP{}'.format(relay)
            status = adu.read(read_command)
            if status == 0:
                button.setIcon(self.red_ring)
                button.setFlat(True)
                button.setStyleSheet("background-color: transparent;")
                button.setIconSize(QSize(22, 22))
                return
            elif status == 1:
                button.setIcon(self.green_ring)
                button.setFlat(True)
                button.setStyleSheet("background-color: transparent;")
                button.setIconSize(QSize(22, 22))
                return
            # If no connection try to load
            else:
                self._not_connected_error(relay)


    # Initialize the button widgets
    def update_adu_relay_buttons(self):
        # Check connection
        if self.please_load:
            self.not_connected()
        else:
            # Loop through the custom buttons 
            for elem_name, data in self.widget_data.items():
                # fetch button name
                button = data['button']
                # Update the visual button status
                self.setColour(str(elem_name.strip("P")), button)

    # Testing all channels of the adu
    def selfTestADU(self):
        string = ""
        # Check connection
        if self.please_load:
            self.not_connected()
        else:  
            # Loop through all buttons for diagnosis
            for name, item in self.widget_data.items():
                name = name.strip("P")    
                button = item['button']
                command = "RP" + name
                status = adu.read(command)  
                if status == 0 or status == 1:
                    string = string + f"Relay, {name} is ok status: {status}\n"
                    button.click()
                    time.sleep(0.2)
                    button.click()
                    time.sleep(0.2)
                    self.st_adu_txt.setText(string)
                    print("ok")
                else:
                    self._not_connected_error(name)
            return
        

    # CONSIDER REMOVING THIS PART
    def man_command(self):
        # Check connection
        if self.please_load:
            self.not_connected()
        else:
            command = self.command_to_send.toPlainText()
            status = adu.read(command)
            print("MAN_COMMAND: ", status)
            print("implement this, or is it really necessary?")




    # Function to load ADU and update the relay buttons
    def load_adu(self):
        try:
            self.initialize()
            self.update_adu_relay_buttons()
            return True
        except:
            from Colifast_ALARM_manager import ErrorDialog
            error_message = f"Cannot connect to the adu"
            dialog = ErrorDialog(error_message)

    # Update the ADU status field
    def initialize(self):
        self.statusAdu.setTextMargins(5, 0, 0, 0)
        if adu.initialize():
            self.please_load = False
            self.statusAdu.setText("ADU is connected")
            self.statusAdu.setStyleSheet("color: #000;")
            return True
        else:
            self.please_load = True
            self.statusAdu.setText("ADU is not connected")
            self.statusAdu.setStyleSheet("color: #d10000;")
            return False
  
    # Reset all ports
    def reset(self):
        # Check connection
        if self.please_load:
            self.not_connected()
        else:
            adu.reset()
            self.update_adu_relay_buttons()
    
    # Check function for adu connection and relay error    
    def _not_connected_error(self, relay):
        from Colifast_ALARM_manager import ErrorDialog
        try:
            if self.load_adu():
                error_message = f"ADU is not connected"
                dialog = ErrorDialog(error_message)
                dialog.exec_()
                return False
        # If it does load, but does not connect to a relay, send relay port error
        except:
            error_message = f"Something is wrong with output {relay}"
            dialog = ErrorDialog(error_message)
            dialog.exec_()
            return
        
    # Function to signal to user that the ADU is not connected - using a blinking red font in the ADU status field
    def not_connected(self):
        # Make all buttons the red icon, when disconnected
        for elem_name, data in self.widget_data.items():
            button = data['button']
            button.setIcon(self.red_ring)

        if self.blink_timer is not None and self.blink_timer.isActive():
            return
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_text)
        self.blink_interval = 150  # Blink every 400 milliseconds
        self.blink_duration = 2450  # Blink for 4 seconds
        self.blink_count = self.blink_duration // self.blink_interval
        self.current_blink_count = 0

        self.blink_timer.start(self.blink_interval)

    # Toggle on and off the text to give a blinking apearance
    def toggle_text(self):
        current_text = self.statusAdu.text()
        if current_text:
            self.statusAdu.setText("")
        else:
            self.statusAdu.setText("ADU is not connected")
        # Limit the duration it blinks
        self.current_blink_count += 1
        if self.current_blink_count >= self.blink_count:
            self.blink_timer.stop()
            self.statusAdu.setText("ADU is not connected")


    # Enable the opening of the ADU control in a new window    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.new_window()
    # Send mouse action to the main gui
    def handleMousePress(self, event):
        self.main.handleMousePress(event)
        
    def handleMouseMove(self, event):
        self.main.handleMouseMove(event)

    def handleMouseRelease(self, event):
        self.main.handleMouseRelease(event)
            
    # resize graphics view along with window size
    def resizeEvent(self, event):
        pass
        # self.graphics_View.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
    # Function for generating an external window
    def new_window(self):
        if not hasattr(self, 'wind') or not self.wind.isVisible():
            if hasattr(self, 'free_LqHwindow'):
                self.free_aduwindow.setParent(None)  # Remove from current parent
            else:
                self.free_aduwindow = ADUadv(self.main)

            self.wind = QMainWindow()
            self.wind.setCentralWidget(self.free_aduwindow)
            self.wind.show()
        else:
            self.wind.hide()  # hide the window if it's already visible
