import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QFrame, QGraphicsEllipseItem, 
    QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout, 
    QSpacerItem, QSizePolicy, QDateEdit
)
from PyQt5.QtGui import QColor, QBrush, QFont, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QTimer, QSize, QDate
import datetime
import settings

class TimeSelectorWidget(QWidget):
    def __init__(self, mode):
        super(TimeSelectorWidget, self).__init__()
        self.mode = mode
        self.resize(340, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        layout = QVBoxLayout()
        self.setLayout(layout)

        vertical_spacer = QSpacerItem(100, 5, QSizePolicy.Fixed, QSizePolicy.Minimum)
        # date_layout = QHBoxLayout()
        # layout.addLayout(date_layout)
        # layout.addItem(vertical_spacer)
        top_layout = QHBoxLayout()
        layout.addLayout(top_layout)
        # top_layout.addItem(vertical_spacer)
        layout.addItem(vertical_spacer)


        if self.mode == "dark_mode":
            self.background = "#2d2d2d"
            self.foreground = "#404040"
            self.btn_press = "#2d2d2d"
            self.contrast = "#00bcd4"
            self.color = "#fff"
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
        rounded_time = (current_time - datetime.timedelta(minutes=current_time.minute % 5)) + datetime.timedelta(minutes=5)

        rounded_hour = str(rounded_time.hour)
        rounded_minute = str(rounded_time.minute)
        
        # Add Date Picker
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedWidth(120)
        self.date_edit.setFixedHeight(40)
        self.date_edit.setFont(QFont("Arial", 16))
        top_layout.addWidget(self.date_edit)
        
        # # Add space
        horisontal_spacer = QSpacerItem(50, 45, QSizePolicy.Fixed, QSizePolicy.Minimum)
        top_layout.addItem(horisontal_spacer)
        
        # Create Hour Button
        self.hour_button = QPushButton(rounded_hour)
        self.hour_button.setFixedWidth(60)
        self.hour_button.setFixedHeight(45)
        self.hour_button.setFont(QFont("Arial", 16))
        self.hour_button.clicked.connect(self.show_hour_selector)
        top_layout.addWidget(self.hour_button)

        # Colon
        colon_label = QLabel(":")
        colon_label.setAlignment(Qt.AlignCenter)
        colon_label.setFont(QFont("Arial", 20))
        top_layout.addWidget(colon_label)

        # Create Minute Button
        self.minutes_button = QPushButton(rounded_minute)
        self.minutes_button.setFixedWidth(60)
        self.minutes_button.setFixedHeight(45)
        self.minutes_button.setFont(QFont("Arial", 16))
        self.minutes_button.clicked.connect(self.show_minute_selector)
        top_layout.addWidget(self.minutes_button)

        # Add space
        # top_layout.addItem(horisontal_spacer)

        # Graphics View
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene)
        self.view.setSceneRect(-250, -250, 500, 500)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.view)

        self.buttons_hours = []
        self.buttons_minutes = []

        self.show_hour_selector()
        self.drag_start_pos = None
        self.drag_current_pos = None

    def draw_watch_face(self):
        watch_face = QGraphicsEllipseItem(-125, -125, 250, 250)
        brush = QBrush(QColor(self.foreground))
        watch_face.setBrush(brush)
        watch_face.setPen(QPen(Qt.transparent))
        self.scene.addItem(watch_face)
        return watch_face

    def show_hour_selector(self):
        self.scene.clear()
        outer_circle_minutes = self.draw_watch_face()
        self.scene.addItem(outer_circle_minutes)

        for i in range(1, 13):
            button = QPushButton(str((12 - i)))
            button.setFixedSize(30, 30)
            angle = ((i + 3) % 12 / 12) * 360
            line = QLineF(0, 0, 104, 0)
            line.setAngle(angle)
            button_pos = line.p2()
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            button.setFlat(True)
            button.setStyleSheet(self.styling)
            button.clicked.connect(self.handle_hour_button_click)
            self.scene.addWidget(button)
            self.buttons_hours.append(button)

        for i in range(12):
            button = QPushButton(str(23 - i))
            button.setFixedSize(30, 30)
            angle = ((i + 4) % 12 / 12) * 360
            line = QLineF(0, 0, 70, 0)
            line.setAngle(angle)
            button_pos = line.p2()
            button.setFlat(True)
            button.setStyleSheet(self.styling)
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            button.clicked.connect(self.handle_hour_button_click)
            self.scene.addWidget(button)
            self.buttons_hours.append(button)

    def show_minute_selector(self):
        self.scene.clear()
        outer_circle_minutes = self.draw_watch_face()
        self.scene.addItem(outer_circle_minutes)

        for i in range(1, 13):
            button = QPushButton(str((12 - i) * 5))
            button.setFixedSize(30, 30)
            angle = ((i + 3) % 12 / 12) * 360
            line = QLineF(0, 0, 100, 0)
            line.setAngle(angle)
            button_pos = line.p2()
            button.setGeometry(int(button_pos.x()) - 15, int(button_pos.y()) - 15, 30, 30)
            button.setFlat(True)
            button.setStyleSheet(self.styling)
            button.pressed.connect(self.handle_minute_button_click)
            self.scene.addWidget(button)
            self.buttons_minutes.append(button)

    def handle_hour_button_click(self):
        button = self.sender()
        if button:
            text = button.text()
            if len(text) == 1:
                text = "0" + button.text()
            self.hour_button.setText(text)
            QTimer.singleShot(0, self.show_minute_selector)

    def handle_minute_button_click(self):
        button = self.sender()
        if button:
            text = button.text()
            if len(text) == 1:
                text = "0" + button.text()
            self.minutes_button.setText(text)

    def return_chosen_time(self):
        hour = int(self.hour_button.text())
        minutes = int(self.minutes_button.text())
        selected_date = self.date_edit.date().toPyDate()

        # Combine the selected date and time
        chosen_time = datetime.datetime.combine(selected_date, datetime.time(hour, minutes))

        # Check if the chosen time has already passed today, and if so automatically update date til tomorrow
        if chosen_time < datetime.datetime.now():
            # If passed, set the date to tomorrow
            chosen_time = chosen_time + datetime.timedelta(days=1)
            self.date_edit.setDate(chosen_time.date())

        return chosen_time

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setFrameShape(QGraphicsView.NoFrame)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimeSelectorWidget("default_mode")  # Pass mode as argument
    window.show()
    sys.exit(app.exec_())
