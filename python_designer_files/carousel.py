# from pdf2image import convert_from_path

# from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPixmap, QTransform, QPainter
# from PyQt5.QtCore import QUrl

# import sys
# import os
# import datetime



### Code for making images of PDFs But this is now done automatically whenever a report is made. ###


# def fetch_and_convert_pdfs(base_directory, output_folder="pages", dpi=150):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     # Collect already-generated images from the output folder
#     existing_images = set(os.listdir(output_folder))
#     image_paths = [os.path.join(output_folder, img) for img in existing_images if img.endswith(".png")]

#     # Traverse the directory structure for PDFs
#     for root, _, files in os.walk(base_directory):
#         for file in files:
#             if file.endswith(".pdf"):
#                 pdf_path = os.path.join(root, file)
#                 pdf_base_name = os.path.basename(pdf_path).replace('.pdf', '')

#                 # Check if images for this PDF already exist
#                 page = convert_from_path(pdf_path, dpi=dpi)
#                 image_name = f"{pdf_base_name}.png"
#                 if image_name not in existing_images:  # Process only if the image isn't already there
#                     image_path = os.path.join(output_folder, image_name)
#                     page[0].save(image_path, "PNG")
#                     image_paths.append(image_path)



### File with class for generating a carousel view of the Colifast ALARM reports 


from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTransform
import datetime
import os
import sys



### It would be nice if the images shown in the carousel were connected to the date of the calendar, 
### so that the switching of date, and rolling of the carousel was coupled, and the front most report 
### shown was allways the date marked in the calendar.


class CarouselViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Graphics view and scene setup
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Adjust the size policy to expand to fill the parent widget
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize attributes
        self.current_index = 0
        self.scale = 0.4
        self.items = []
        self.image_paths = []
        self.load_images_around_date()

    def update_scene(self):
        self.scene.clear()
        self.scale = 0.4
        self.items = []
        self.populate_scene()

    def populate_scene(self):
        if not self.image_paths:
            print("No images found!")
            return

        for path in self.image_paths:
            pixmap = QPixmap(path)
            item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(item)
            self.items.append(item)
        
        self.update_positions()


    def update_positions(self):
        """Update the positions of the items with perspective and highlight effects."""
        center_x = self.width() / 2
        center_y = self.height() / 2

        max_angle = 45  # Maximum rotation angle for the furthest images
        max_offset = 300  # Maximum horizontal offset for the furthest images

        for i, item in enumerate(self.items):
            offset = i - self.current_index

            # Calculate scale for each item
            if offset == 0:
                scale = self.scale  # Use the scale from the wheelEvent for the front item
                item.setZValue(10)
                item.setScale(scale)
                transform = QTransform()
                item.setTransform(transform)
                item.setPos(center_x - item.pixmap().width() * scale / 2, center_y - item.pixmap().height() * scale / 2)
            else:
                scale = max(0.1, self.scale - 0.2 * abs(offset))  # Scale decreases for items further away
                rotation_angle = max_angle * offset / len(self.items)  # Proportional angle
                horizontal_offset = max_offset * offset / len(self.items)  # Proportional offset
                transform = QTransform().rotate(rotation_angle, Qt.YAxis)
                item.setTransform(transform)

                item.setZValue(5 - abs(offset))  # Lower Z-value for non-central items
                item.setScale(scale)

                # Offset the item horizontally and vertically
                item.setPos(center_x + horizontal_offset - item.pixmap().width() * scale / 2,
                            center_y - item.pixmap().height() * scale / 2)
                

    def load_images_around_date(self, selected_date_str="2024-11-04", n=10):
        """
        Loads n images around the selected date from the given image folder.
        
        :param selected_date_str: The selected date as a string in the format 'YYYY-MM-DD'.
        :param n: The number of images to load around the selected date.
        :updates the list of images variable of the class, self.image_paths
        """
        
        image_folder = "C:\\Colifast\\Reports\\report_images"

        # Parse the selected date
        selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d")
        
        # List to hold the image paths
        image_paths = []
        
        # List to store (date, path) tuples
        image_dates = []
        
        # Walk through the directory and collect all image file paths and their dates
        for dirpath, dirnames, filenames in os.walk(image_folder):
            for filename in filenames:
                if filename.endswith(".png"):
                    # Extract date from the filename
                    date_str = filename.replace(".png", "")
                    try:
                        # Parse the image date
                        image_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        # Store the image date and its full path
                        image_dates.append((image_date, os.path.join(dirpath, filename)))
                    except ValueError:
                        continue  # Skip files with invalid date formats
        
        # Sort images by their date
        image_dates.sort(key=lambda x: x[0])

        # Find the closest image to the selected date
        closest_index = 0
        closest_diff = abs(image_dates[0][0] - selected_date)
        
        for i, (image_date, _) in enumerate(image_dates):
            diff = abs(image_date - selected_date)
            if diff < closest_diff:
                closest_diff = diff
                closest_index = i
        
        # Now we have the closest image, let's fetch n images surrounding it
        start_index = max(0, closest_index - n // 2)
        end_index = min(len(image_dates), start_index + n)
        
        # Extract the image paths for the selected range
        for i in range(start_index, end_index):
            image_paths.append(image_dates[i][1])

        self.image_paths = image_paths

    # Enable scrolling up and down the report, and zooming - scroll while holding shift.
    def wheelEvent(self, event):
        """Enable zoom only for the central item when Shift is held, otherwise allow default scrolling."""
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ShiftModifier:  # Check if the Shift key is pressed
            if len(self.items) > 0:
                # Define zoom factor
                factor = 1.2
                central_item = self.items[self.current_index]

                # Get the current scale of the central item
                current_scale = central_item.scale()

                # Zoom in: Only zoom out (scale < 1.0)
                if event.angleDelta().y() > 0 and current_scale > 0.1:  # Zoom out limit (can't zoom further out)
                    new_scale = current_scale / factor

                # Zoom out: If zooming in, stay below 1.0
                elif event.angleDelta().y() < 0 and current_scale < 1.0:  # Zoom in limit (can't scale up beyond 1.0)
                    new_scale = current_scale * factor
                else:
                    return  # No scaling to apply

                # Apply the new scale
                central_item.setScale(new_scale)

                # Update the positions of the items with the new scale
                self.scale = new_scale
                central_item.setScale(new_scale)
                self.update_positions()
        else:
            # Forward the event for default behavior (e.g., scrolling the window)
            super(CarouselViewer, self).wheelEvent(event)

    # arrow press are flipping through the reports
    def keyPressEvent(self, event):
        """Handle left and right arrow keys for navigation."""
        if event.key() == Qt.Key_Left:
            self.current_index = (self.current_index - 1 + len(self.items)) % len(self.items)
            self.update_positions()
        elif event.key() == Qt.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.items)
            self.update_positions()
        elif event.key() == Qt.Key_Space:  # Optionally toggle zoom on the central item
            central_item = self.items[self.current_index]
            if central_item.scale() > 1.0:
                central_item.setScale(1.0)
            else:
                central_item.setScale(2.5)

    # Enable dragging to adjust where to display of the report, for use in conjunction with the zooming
    def mousePressEvent(self, event):
        """Handle mouse press to start dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move during dragging."""
        if self.is_dragging:
            delta = event.pos() - self.last_pos
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Ensure scrollbar appears
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pos = event.pos()  # Update last position for the next move

    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            

### Part of code to make it possible to usa as a stand alone.        ###
### In SW this is done form the main GUI - Colifast_ALARM_manager.py ###

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create an instance of CarouselViewer
        self.viewer = CarouselViewer()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.viewer)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set main window title and populate the scene with images
        self.setWindowTitle("Carousel Viewer")
        self.viewer.populate_scene()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Specify the base directory containing reports
    base_directory = "C:\\Colifast\\Reports"

    # Un comment the upper code, and this "fetch_and_convert_pdfs", for this to work, in case images of reports must be made. 
    # - this is now done when ever a report is generated

    # fetch_and_convert_pdfs(base_directory, output_folder=os.path.join(base_directory, "report_images"))

    window = MainWindow()
    window.viewer.load_images_around_date()
    window.show()

    sys.exit(app.exec_())
