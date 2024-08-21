import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QFrame, QGraphicsEllipseItem, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QColor, QBrush, QFont, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QTimer, QSize, QEvent, pyqtSignal

import datetime
import settings

# Class for getting a simple time selector with a watch face 
# interface for selecting hours and minutes(5 min intervals) 
class TimeSelectorWidget(QWidget):
    def __init__(self, mode):
        super(TimeSelectorWidget, self).__init__()
        ## Design & Layout ##
        # color mode as arg to style the window as the GUI
        self.mode = mode
        self.resize(320, 440)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Make the window frameless
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create top layout for the selected hours, (colon) and minutes 
        top_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        spacer = QSpacerItem(100, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)  # Add spacer
        top_layout.addItem(spacer)

        # Fetch style colors from mode variable
        if self.mode == "dark_mode":
            self.background = "#2d2d2d"
            self.foreground = "#404040"
            self.btn_press = "#2d2d2d"
            self.contrast = "#00bcd4"
            self.color = "#fff"
            print("\n\n\nDAAARK MOOODE!\n\n\n\n")


        elif self.mode == "color":
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

        # Attach the style colors to the style of the window buttons, hover, and check funciton
        self.styling = """
                QPushButton {{
                        border-radius: 15px;
                        background-color: {};
                        border: none;
                        color: {};
                    }}
                    QPushButton:hover {{
                        border-radius: 15px;
                        background-color: {};
                    }}
                    QPushButton:checked {{
                        border-radius: 15px;
                        background-color: {};
                    }}
                """.format(self.foreground, self.color, self.contrast, self.btn_press)

        # Get the current time
        current_time = datetime.datetime.now()
        # Round down to the nearest five minutes
        rounded_time = (current_time - datetime.timedelta(minutes=current_time.minute % 5))+ datetime.timedelta(minutes=5)

        # Extract hour and minute components from the rounded time
        rounded_hour = str(rounded_time.hour)
        rounded_minute = str(rounded_time.minute)
        # Create Hour Button
        self.hour_button = QPushButton(rounded_hour)
        self.hour_button.setFixedWidth(60)  # Width
        self.hour_button.setFixedHeight(45)  # Height
        self.hour_button.setFont(QFont("Arial", 16))  # Set the font for the QPushButton
        self.hour_button.clicked.connect(self.show_hour_selector)  # Connect clicked signal to show_hour_selector watch face
        top_layout.addWidget(self.hour_button)

        # Colon between the button to indicate a clock
        colon_label = QLabel(":")
        colon_label.setAlignment(Qt.AlignCenter)
        colon_label.setFont(QFont("Arial", 20))
        top_layout.addWidget(colon_label)

        # Create Minute Button
        self.minutes_button = QPushButton(rounded_minute)
        self.minutes_button.setFixedWidth(60)  # Width
        self.minutes_button.setFixedHeight(45)  # Height
        self.minutes_button.setFont(QFont("Arial", 16))  # Set the font for the QPushButton
        self.minutes_button.clicked.connect(self.show_minute_selector)  # Connect clicked signal to show_minute_selector watch face
        top_layout.addWidget(self.minutes_button)

        # Add space for design
        spacer = QSpacerItem(100, 45, QSizePolicy.Fixed, QSizePolicy.Minimum)
        top_layout.addItem(spacer)

        # Make scene and view for containing the watch face
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene) # Custom to make it frameless
        self.view.setSceneRect(-250, -250, 500, 500)  # Enlarge scene rect size
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.view)

        # List containers for the buttons; every hour, and every five minutes of the hour
        self.buttons_hours = []
        self.buttons_minutes = []

        # Initially show the hour selector watch face
        self.show_hour_selector()
        
        # Variables to track dragging
        self.drag_start_pos = None
        self.drag_current_pos = None

    # Draw filled circle of watch face
    def draw_watch_face(self):
        watch_face = QGraphicsEllipseItem(-125, -125, 250, 250)  # Circle size
        brush = QBrush(QColor(self.foreground))
        watch_face.setBrush(brush)
        watch_face.setPen(QPen(Qt.transparent))
        self.scene.addItem(watch_face)
        return watch_face

    # Create Watch Face with hours
    def show_hour_selector(self):
        # Clear existing items from the scene
        self.scene.clear()
        outer_circle_minutes = self.draw_watch_face()
        self.scene.addItem(outer_circle_minutes)

        # Create buttons for hours (outer ring 0-11)
        for i in range(1, 13):
            button = QPushButton(str((12 - i)))     # Assign button name as hour
            button.setFixedSize(30, 30)             # Button size
            angle = ((i + 3) % 12 / 12) * 360       # Angle of button
            line = QLineF(0, 0, 104, 0)             # Distance from center
            line.setAngle(angle)
            button_pos = line.p2()
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            button.setFlat(True)  # Make the button flat (no background)
            button.setStyleSheet(self.styling)
            
            # Enable mouse tracking for the widget to know which button is clicked
            button.clicked.connect(self.handle_hour_button_click)
            self.scene.addWidget(button)
            self.buttons_hours.append(button)

        # Create buttons for hours (outer ring 12-23)
        for i in range(12):
            button = QPushButton(str(23 - i))       # Assign button name as hour
            button.setFixedSize(30, 30)             # Button size
            angle = ((i + 4) % 12 / 12) * 360       # Angle of button
            line = QLineF(0, 0, 70, 0)              # Distance from center
            line.setAngle(angle)
            button_pos = line.p2()
            button.setFlat(True)  # Make the button flat (no background)
            button.setStyleSheet(self.styling)
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            
            # Enable mouse tracking for the widget to know which button is clicked
            button.clicked.connect(self.handle_hour_button_click)
            self.scene.addWidget(button)
            self.buttons_hours.append(button)

    # Create Watch Face with minutes
    def show_minute_selector(self):
        # Clear existing items from the scene and redraw watch face with minutes
        self.scene.clear()
        outer_circle_minutes = self.draw_watch_face()
        self.scene.addItem(outer_circle_minutes)

        for i in range(1, 13):
            button = QPushButton(str((12 - i)*5))   # Assign button name as minutes (5 min interval)
            button.setFixedSize(30, 30)             # Button size
            angle = ((i + 3) % 12 / 12) * 360       # Angle of button
            line = QLineF(0, 0, 100, 0)             # Distance from circle center
            line.setAngle(angle)
            button_pos = line.p2()
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            button.setFlat(True)  # Make the button flat (no background)
            button.setStyleSheet(self.styling)

            # Enable mouse tracking for the widget to know which button is clicked
            button.pressed.connect(self.handle_minute_button_click)
            self.scene.addWidget(button)
            self.buttons_minutes.append(button)

    ## Functions for handling watch face clicks ##
    # Hours
    def handle_hour_button_click(self):
        button = self.sender()
        if button:
            text = button.text()
            if len(text) == 1:
                text = "0" + button.text()
            self.hour_button.setText(text)
            QTimer.singleShot(0, self.show_minute_selector)
    # Minutes
    def handle_minute_button_click(self):
        button = self.sender()
        if button:
            text = button.text()
            if len(text) == 1:
                text = "0" + button.text()
            self.minutes_button.setText(text)

    # Function to get the time to the GUI
    def return_chosen_time(self):
        hour = int(self.hour_button.text())
        minutes = int(self.minutes_button.text())
        return hour, minutes
        
# Custom QGraphicsView class without frame
class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setFrameShape(QGraphicsView.NoFrame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeSelectorWidget()
    window.show()
    sys.exit(app.exec_())
