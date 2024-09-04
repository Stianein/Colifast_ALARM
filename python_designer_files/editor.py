####### MODULE NAME: Editor #####
##### Author: Stian Ingebrigtsen

# Editor for making/editing method files for the software

import sys
import ast
import os
import settings
from collections import deque
from resource_path import resource_path



from PyQt5.QtWidgets import (
    QInputDialog, QApplication, QMainWindow, QListWidget, QDockWidget, QListWidgetItem, 
    QSplitter, QPushButton, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt5.Qsci import (
    QsciScintilla, QsciLexerPython, QsciScintillaBase
)
from PyQt5.QtCore import (
    Qt, pyqtSlot, pyqtSignal, QSize, QTimer
)
from PyQt5.QtGui import (
    QIcon, QColor, QFont, QColor
)


# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_directory = os.path.dirname(current_file_directory)


app = QApplication(sys.argv)

# Function to extract function names from Python code (Method files .CFAST) RENAME TO PARSE FUNCTION INFO
def parse_function_info(code, path):
    functions_info = []
    tree = ast.parse(code)
    function_content = []

    # Use ast to find python functions in code, and extract name, code and line number of the function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_code = ast.unparse(node)
            functions_info.append((func_name, func_code, node.lineno, node.end_lineno))
    
    # Get the part of the code where functions are stored line number at start and at the end
    try:
        start_of_functions = functions_info[0][2]
        end_of_functions = functions_info[-1][3]
    except:
        start_of_functions = None
        end_of_functions = None
    
    # Process the info gotten from the ast parser, to include preceeding comments to the function content.
    with open(path, 'r', newline='') as file:
        # Make a buffer to store a few (5) lines before the function
        buffer_size = 5
        buffer = deque(maxlen=buffer_size)
        # Loop through the functions fetched by ast
        for index, (func_name, func_code, start, stop) in enumerate(functions_info):
            file.seek(0)  # Reset file pointer to the beginning of the file
            collected_code = []
            for line_number, line in enumerate(file, start=1):
                # If the line number is between the lines where the functions are
                if start <= line_number <= stop:
                    # If at the beginning of the function check for preceeding comments, in buffer
                    if line_number == start:
                        for elem in list(buffer):
                            if elem.rstrip().startswith("#"):
                                collected_code.append(elem)
                    collected_code.append(line)
                buffer.append(line)
            # Update the variable, func_code value to include the found comments
            functions_info[index] = (func_name, "".join(collected_code), start, stop)
        
        # Sort functions in alfabetic order
        sorted_functions_info = sorted(functions_info, key=lambda x: x[0])
        functions_content = []
        functions_name = []
        for name,func,_,_ in sorted_functions_info:
            functions_content.append(func) 
            functions_name.append(name)

    return functions_content, functions_name, start_of_functions, end_of_functions

# Class for handling the text interpreter QSciScintilla
class CodeEditor(QsciScintilla):
    def __init__(self, locked_mode,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bool for locking and unlocking edit mode
        self.locked_mode = locked_mode
        # Set the lexer for Python syntax highlighting
        lexer = QsciLexerPython(self)
        self.setLexer(lexer)
        # self.SendScintilla(QsciScintilla.SCI_SETFIRSTVISIBLELINE, 0)
        self.set_read_only(True)
        
        self.current_position = -1
        self.general_indicator = 1
        self.first_instance_indicator = 2

        # Set syntax colors for text - colifast colors
        blue = QColor(30, 28, 119)
        lightBlue = QColor(80, 230, 230)
        orange = QColor(237, 125, 49)
        margin_blue = QColor('#66899b')
        self.green = QColor(0, 250, 154)
        self.dark_green = QColor(0, 100, 10)
        
        # Configure styling for different code elements
        font = QFont('DejaVu Sans mono')
        # font.setPointSize(10)
        lexer.setDefaultFont(font)
        lexer.setPaper(QColor('white'))
        # Set KeyWords color
        lexer.setColor(lightBlue, QsciLexerPython.Keyword)
        # Set Comment color
        lexer.setColor(blue, QsciLexerPython.Comment)
        # Set Quoted strings color
        lexer.setColor(orange, QsciLexerPython.DoubleQuotedString)
        lexer.setColor(orange, QsciLexerPython.SingleQuotedString)
        # Enable line numbers in the margin
        self.setMarginLineNumbers(1, True)
        # Set the width of the margin for line numbers
        self.setMarginWidth(1, 35)
        # Set the margin background color for the line number margin
        self.setMarginsBackgroundColor(margin_blue)
        
    def set_text(self, text):
        self.setText("")
        self.setText(text)
    
    # Send the view to the start of a given line number    
    def line_no_at_start_of_function(self, line_no):
        self.SendScintilla(QsciScintilla.SCI_SETFIRSTVISIBLELINE, line_no)
        
    # Set the text to read only
    def set_read_only(self, read_only):
        self.setReadOnly(read_only)
        
    # Funciton to warn for locked mode when a key is hit inside the editor whilest in read only mode
    def keyPressEvent(self, event):
        if not self.isReadOnly():
            super().keyPressEvent(event)
        else:
            self.locked_mode()
   
    # Clear highlighted text from a search
    def clear_occurrences(self, indicator):
        self.SendScintilla(QsciScintillaBase.SCI_SETINDICATORCURRENT, indicator)
        self.SendScintilla(QsciScintillaBase.SCI_INDICATORCLEARRANGE, 0, self.length())

    # Find next instance of the search term
    def find_next(self, search_term):
        self.clear_occurrences(2)
        lines = self.text().split('\n')
        total_lines = len(lines)

        # Determine the starting index for reversed enumeration
        start_index = self.current_position if self.current_position >= 0 else total_lines - 1

        # Loop through all text after match with serach term
        i = start_index
        for _ in range(total_lines):
            line = lines[i]
            # Make the search case insensitive by making everything lower case
            position = line.lower().find(search_term.lower())
            # If match - mark term
            if position != -1:
                self.mark_occurrence(i, position, search_term)
                self.SendScintilla(QsciScintilla.SCI_GOTOLINE, i)
                self.current_position = (i + 1) % total_lines  # Use modular arithmetic - so after last match searching loops to start 
                return True

            i = (i + 1) % total_lines  # Move to the next line

        self.current_position = -1
        return False    


    # Find previous instance of the search term
    def find_previous(self, search_term):
        self.clear_occurrences(2)
        lines = self.text().split('\n')
        total_lines = len(lines)

        # Determine the starting index for reversed enumeration
        start_index = self.current_position if self.current_position >= 0 else total_lines - 1
        
        # Loop through all text after match with serach term
        i = start_index
        for _ in range(total_lines):
            line = lines[i]
            # Make the search case insensitive by making everything lower case
            position = line.lower().find(search_term.lower())
            # If match - mark term
            if position != -1:
                self.mark_occurrence(i, position, search_term)
                print("Found instance at line:", i + 1)
                self.SendScintilla(QsciScintilla.SCI_GOTOLINE, i)
                self.current_position = (i - 1) % total_lines  # Use modular arithmetic - so after last match searching loops to end 
                return True

            i = (i - 1) % total_lines  # Move to the previous line

        self.current_position = -1
        return False



    def mark_occurrence(self, line_number, position, search_term):
        # General occurrence marking
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETSTYLE, self.general_indicator, QsciScintilla.INDIC_ROUNDBOX)
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETFORE, self.general_indicator, self.green)
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETALPHA, self.general_indicator, 100)
        self.SendScintilla(QsciScintillaBase.SCI_INDICATORFILLRANGE, self.positionFromLineIndex(line_number, position), len(search_term))

        # First instance marking
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETSTYLE, self.first_instance_indicator, QsciScintilla.INDIC_ROUNDBOX)
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETFORE, self.first_instance_indicator, self.dark_green)
        self.SendScintilla(QsciScintillaBase.SCI_INDICSETALPHA, self.first_instance_indicator, 100)
        self.SendScintilla(QsciScintillaBase.SCI_INDICATORFILLRANGE, self.positionFromLineIndex(line_number, position), len(search_term))

            
    # Marks all instances of a search term
    def text_marker(self, search_term, indicator=1):
        self.clear_occurrences(indicator)

        # Start searching from the beginning
        position = 0
        i = 0
        lines = self.text().split('\n')
        instance_found = False
        for line in lines:
            position = line.lower().find(search_term.lower())
            if position != -1:
                instance_found = True
                # Highlight the background of the found text
                self.SendScintilla(QsciScintillaBase.SCI_INDICSETSTYLE, indicator, QsciScintilla.INDIC_ROUNDBOX)
                self.SendScintilla(QsciScintillaBase.SCI_INDICSETFORE, indicator, self.green)
                self.SendScintilla(QsciScintillaBase.SCI_INDICSETALPHA, indicator, 100)  # Set transparency
                self.SendScintilla(QsciScintillaBase.SCI_INDICATORFILLRANGE, self.positionFromLineIndex(i, position), len(search_term))
            i += 1  # Move to the next line after the found text
        return instance_found
    

# Main class
class Editor(QMainWindow):
    def __init__(self, main, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.main = main
        # Create a widget for the custom header
        header_widget = QWidget()
        header_widget.setMaximumSize(QSize(16777215, 30))
        self.header_layout = QHBoxLayout(header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0) 

        # Title
        title_label = QLabel("Editor")
        # title_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        # PadLock button for opening file for editing
        self.padlock_button = QPushButton()
        self.locked_padlock_button = QIcon(resource_path(os.path.join(parent_directory, "icons\\lock.svg")))  # Replace with your padlock icon path
        self.open_padlock_button = QIcon(resource_path(os.path.join(parent_directory, "icons\\unlock.svg")))  # Replace with your padlock icon path
        self.padlock_button.setFlat(True)
        self.is_modified = False
        self.padlock_button.setIcon(self.locked_padlock_button)
        self.padlock_button.setToolTip("Unlock editing")
        self.padlock_button.setFixedSize(22, 22)
        self.padlock_button.clicked.connect(lambda: self.toggle_editing(self.padlock_button))

        # Add widgets to the layout
        self.header_layout.addWidget(title_label)
        self.header_layout.addStretch(1)  # Stretch pushes icon to the right of the window
        self.header_layout.addWidget(self.padlock_button)
        # self.header_layout.setSizeConstraint(QLayout.SetFixedSize)

        # Set the custom header as the central widget
        # self.setCentralWidget(header_widget)

        # Variables
        self.variable_editor = CodeEditor(self.locked_mode)
        # Main Code editor
        self.editor = CodeEditor(self.locked_mode)
        # Function Editor
        self.function_editor = CodeEditor(self.locked_mode)
        # Function list
        self.function_list = QListWidget()
        
        self.load_text(settings.getMethod())
        
        # instantiate widget for interacting with the search functionality
        self.editors = [self.variable_editor, self.function_editor, self.editor]
        search_save_widget = SearchWidget(self.editors, self.function_list, self.header_layout, self)

        # Create a container widget for the buttons
        button_container = QWidget()
        button_container.setObjectName("button_container")

        # Save button
        self.save_file_btn = QPushButton('Save File', button_container)
        self.save_file_btn.clicked.connect(self.save_file)
        # Save As button
        save_as_button = QPushButton("Save As", button_container)
        save_as_button.clicked.connect(self.save_as)
        
        func_container = QWidget()
        func_container.setObjectName("func_container")
        # Adding a function
        self.add_funcBtn = QPushButton("Add new function", func_container)
        self.add_funcBtn.clicked.connect(self.add_list_item)
        # Removing a function
        self.remove_funcBtn = QPushButton("Remove function", func_container)
        self.remove_funcBtn.clicked.connect(self.remove_list_item)

        func_layout = QHBoxLayout(func_container)
        func_layout.addWidget(self.add_funcBtn)
        func_layout.addWidget(self.remove_funcBtn)

        # Create a layout for the search and save components
        save_layout = QHBoxLayout(button_container)
        # Add the buttonsto the widget
        save_layout.addWidget(self.save_file_btn)
        save_layout.addWidget(save_as_button)
        
        # Variables for Blinking padlock icon if text is in readOnly mode/ locked mode
        self.blink_timer = None
        self.selected_item = None
        
        for editor in self.editors:
            editor.cursorPositionChanged.connect(self.locked_mode)
            editor.textChanged.connect(self.modified)
            
        self.function_list.itemClicked.connect(self.on_itemClicked)
        self.function_list.itemClicked.connect(lambda: search_save_widget.search_text())
        self.function_list.itemActivated.connect(self.on_itemClicked)

        function_dock = QDockWidget("Function List and Editor", self)
        function_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # Splitting window in the different editors
        self.function_splitter = QSplitter(Qt.Vertical)
        self.function_splitter.addWidget(self.function_list)
        self.function_splitter.addWidget(func_container)
        self.function_splitter.addWidget(self.function_editor)
        self.function_splitter.addWidget(button_container)
        # Set initial stretch factor for function editor and list to 1/3 of the total space
        self.function_splitter.setStretchFactor(0, 1)
        self.function_splitter.setStretchFactor(1, 2)

        function_dock.setWidget(self.function_splitter)
        self.addDockWidget(Qt.RightDockWidgetArea, function_dock)
       
        var_dock = QDockWidget("Main editor and Variables", self)
        var_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        # Create a QWidget to hold the splitter
        container = QWidget()

        # Create a QVBoxLayout for the container
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)  # No margins

        # Create and set up the QSplitter
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self.variable_editor)
        main_splitter.addWidget(self.editor)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)

       # Set the QWidget with the QSplitter as the central widget of the QDockWidget
        var_dock.setWidget(main_splitter)
        

        # Create a QSplitter for function and variable editors
        horisontal_splitter = QSplitter(Qt.Horizontal)
        horisontal_splitter.addWidget(var_dock)
        horisontal_splitter.addWidget(function_dock)
        horisontal_splitter.setStretchFactor(0, 2)
        horisontal_splitter.setStretchFactor(1, 1)
        # Add the QSplitter to the container
        container_layout.addWidget(horisontal_splitter)
 
        # Optionally, set the background color of the container
        # container.setStyleSheet("background-color: #92C5DE;")
        
        layout = QVBoxLayout()

        # Add the custom header to the layout
        layout.addWidget(header_widget)

        # Add the QDockWidget to the layout
        layout.addWidget(container)

        # Create a QWidget to hold the layout
        main_widget = QWidget()
        main_widget.setLayout(layout)

        # Set the central widget of your QMainWindow
        self.setCentralWidget(main_widget)

    # Toggle modified file variable
    def modified(self):
        self.is_modified == True
        # self.save_file_btn.setStyleSheet("background-color: white;")

    # Function to load the text of the provided file path
    def load_text(self, file_path):
        # Path with file
        self.path = file_path
        try:
            if self.path:
                # Open the file
                with open(file_path, 'r', newline='') as file:
                    code = file.read()
        
            else: 
                code = ""
        

            # Extract the different parts of the code based on the functions
            try:
                self.all_functions_content, func_name, start_of_functions, end_of_functions = parse_function_info(code, file_path)
                code_with_variables = self.extract_lines_from_code(code, 0, start_of_functions - 3)
                main_code = self.extract_lines_from_code(code, end_of_functions, -1).lstrip()
            # Show syntax error in file 
            except SyntaxError as e:
                func_name = []
                self.all_functions_content = []
                code_with_variables = ""
                main_code = code

                # Extract the line number where the error occurred
                error_line_number = e.lineno
                print(f"SyntaxError on line {error_line_number}: {e.msg}")

            # If the file does not follow the patterns of a Colifast method file, load all text into the main editor window
            except:
                func_name = []
                self.all_functions_content = []
                code_with_variables = ""
                main_code = code
                
            # Clear the function list and content of the function editor if it has content
            if self.function_list != None:
                self.function_list.clear()
                self.function_editor.set_text("")

            # Set text for other editors
            self.variable_editor.set_text(code_with_variables.lstrip().rstrip())
            self.editor.set_text(main_code.lstrip().rstrip())
            func_code_string = "".join(self.all_functions_content)
            self.function_editor.set_text(func_code_string.lstrip().rstrip())

            # Populate the function list
            if func_name:
                for elem in func_name:
                    self.function_list.addItem(elem)
            else:
                try:
                    self.highlight_line(error_line_number)
                    self.editor.SendScintilla(QsciScintilla.SCI_SETFIRSTVISIBLELINE, error_line_number-1)
                    from Colifast_ALARM_manager import ErrorDialog
                    error_message = f"You have some invalid syntax in your code, at line {error_line_number}"
                    dialog = ErrorDialog(error_message)
                    dialog.exec_()
                except:
                    pass
        except:
            from Colifast_ALARM_manager import ErrorDialog
            error_message = f"The stored method file, {file_path}, could not be found"
            dialog = ErrorDialog(error_message)  
            dialog.exec_()



    # Highlight a specific line number
    def highlight_line(self, line_number):
        print("inside highlighter")
        # Set the indicator style
        self.editor.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, 0, QsciScintilla.INDIC_ROUNDBOX)

        # Set the indicator color
        self.editor.SendScintilla(QsciScintilla.SCI_INDICSETFORE, 0, QColor(0, 250, 154))

        # Set transparency (optional)
        self.editor.SendScintilla(QsciScintilla.SCI_INDICSETALPHA, 0, 100)

        # Calculate the position of the first character in the line
        position = self.editor.positionFromLineIndex(line_number - 1, 0)

        # Get the length of the line
        line_length = len(self.editor.text(line_number - 1))


        self.editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, position, line_length)

            
        
    # Function that fetch the specific content of a clicked function in the function list
    @pyqtSlot(QListWidgetItem)
    def on_itemClicked(self, clicked_item):  # Rename the parameter
        search_string = "def " + clicked_item.text()      
        print(search_string)
        # Find the position of the search string in the text
        start_position = self.function_editor.text().find(search_string)

        # Find the position of the search string in the text
        # start_position = self.function_editor.findFirst(search_string, False, False, False, False)

        if start_position != -1:
            # Scroll to the found position
            self.line_number = self.function_editor.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start_position)
            print(self.line_number)

            # self.function_editor.SendScintilla(QsciScintilla.SCI_GOTOLINE, line_number)
            self.function_editor.SendScintilla(QsciScintilla.SCI_SETFIRSTVISIBLELINE, self.line_number-1)

                
    # add function to the program
    def add_list_item(self):
        if not self.editor.isReadOnly():
            print("implement add list item")
            
            text, ok = QInputDialog.getText(self, 'Enter Text', 'Enter the text for the new item:')
            if ok and text:
                new_item = QListWidgetItem(text)
                self.function_list.addItem(new_item)
                new_function = f"\n\n# Describe your function here\ndef {text}():"
                self.function_editor.insert(new_function)
                self.on_itemClicked(new_item)
                self.function_editor.SendScintilla(QsciScintilla.SCI_GOTOLINE, self.function_editor.length())
        else:
            self.locked_mode()
    
    # remove function to the program
    def remove_list_item(self):
        if not self.editor.isReadOnly():
            print("implement remove list item")
            try:
                start_of_function = self.line_number - 1
            except:
                print("Choose a list item, to remove")
                return False   
            try:
                search_string = "def " + self.get_next_item()
                # Find the position of the search string in the text
                start_position_next_item = self.function_editor.text().find(search_string)
                end_of_function = self.function_editor.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start_position_next_item) - 2
            except:
                end_of_function = self.function_editor.length()
                print(end_of_function)

            print("start: ", start_of_function, "end: ", end_of_function)
            
            self.function_editor.SendScintilla(QsciScintilla.SCI_GOTOLINE, start_of_function)

            # current_line = self.function_editor.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, self.function_editor.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS))
            # print("current", current_line)
            lines_to_delete = end_of_function - start_of_function
            i = 0
            while i <lines_to_delete:
                self.function_editor.SendScintilla(QsciScintilla.SCI_LINEDELETE)
                i += 1
          
            current_row = self.function_list.currentRow()
            if current_row >= 0:
                current_item = self.function_list.takeItem(current_row)
                del current_item
             
            self.function_editor.SendScintilla(QsciScintilla.SCI_GOTOLINE, self.line_number)
            self.function_editor.set_text(self.function_editor.text().rstrip())

        else:
            self.locked_mode()

    def get_next_item(self):
        current_row = self.function_list.currentRow()
        if current_row != -1 and current_row < self.function_list.count() - 1:
            next_item = self.function_list.item(current_row + 1)
            print("Next Item:", next_item.text())
            return next_item.text()
        else:
            print("No next item.")
            return False


    # Save file, fetch text from editors and loop through all functions 
    def save_file(self, file_path=None):
        if not file_path:
            file_path = self.path
        
        if not self.editor.isReadOnly():
            # Combine the content of all editors into the complete code
            complete_code = ""
            for editor in self.editors:
                complete_code = complete_code + editor.text() + "\n\n\n\n"
                # if editor == self.editor:
                #     print(editor.text())

            # print("\n\nsavefunc start\n\n", complete_code, "\n\n stop savefunc\n\n")
            with open(file_path, 'w', newline='') as file:
                file.write(complete_code)    

            self.is_modified = False
            # self.save_file_btn.setStyleSheet("")

        else:
            self.locked_mode()

    # Save file as
    def save_as(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog  # Use the native dialog for better integration

        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setDirectory(os.path.dirname(settings.getMethod()))  # Set the initial directory
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Text Files (*.CFAST);;All Files (*)")

        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            self.save_file(selected_file)
            print(selected_file)
            settings.storeMethod(selected_file)

            # self.load_text(selected_file)
            # self.main.methodDropDown()
            self.main.methodSelector.addItem(selected_file)
            self.main.methodSelector.setCurrentText(settings.getMethod())
            # self.main.method_file_changer(0)
            print(settings.getMethod())

        

    def extract_lines_from_code(self, code, start, stop):
        # Split the file content into lines
        lines = code.split('\n')
        # for line in lines:
        #     print(line)
        # Extract lines between start_of_functions and end_of_functions
        selected_lines = lines[start:stop]
        # print("selected: ", selected_lines)

        # Join the selected lines back into a string
        return '\n'.join(selected_lines)


    def toggle_read_only(self):
        # Toggle between read-only and editable states
        read_only = not self.editor.isReadOnly()
        self.editor.set_read_only(read_only)
        
    def toggle_editing(self, button):
        # toggle editability
        locked = self.editor.isReadOnly()
        for editor in self.editors:
            editor.set_read_only(not locked)
        # change icon            
        if locked:
            self.current_blink_count = 2500
            # time.sleep(0.5)
            button.setIcon(self.open_padlock_button)
            self.padlock_button.setToolTip("Lock editing")
            # self.is_modified = True
        else:
            button.setIcon(self.locked_padlock_button)
            self.padlock_button.setToolTip("Unlock editing")
            
    def locked_mode(self):
        # print("Locked mode called")
        if not self.editor.isReadOnly():
            # print("Editor is not read-only")
            return
        if self.blink_timer is not None and self.blink_timer.isActive():
            # print("Blink timer is active")
            return
        # print("Starting blink timer")
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.icon_blink)
        self.blink_interval = 150  # Blink every 150 milliseconds
        self.blink_duration = 2450  # Blink for 2450 milliseconds
        self.blink_count = self.blink_duration // self.blink_interval
        self.current_blink_count = 0

        self.blink_timer.start(self.blink_interval)

    def icon_blink(self):
        # print("Icon blink called")
        # Toggle the button icon on and off
        current_icon = self.padlock_button.icon()
        self.padlock_button.setIcon(self.locked_padlock_button if current_icon.isNull() else QIcon())

        self.current_blink_count += 1
        if self.current_blink_count >= self.blink_count:
            # print("Stopping blink timer")
            self.blink_timer.stop()
            if not self.editor.isReadOnly():
                self.padlock_button.setIcon(self.open_padlock_button)
            else:
                self.padlock_button.setIcon(self.locked_padlock_button)
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.new_window()
            
    def new_window(self):
        if not hasattr(self, 'wind') or not self.wind.isVisible():
            if hasattr(self, 'free_LqHwindow'):
                self.free_editor.setParent(None)  # Remove from current parent
            else:
                self.free_editor = Editor()
                
            self.wind = QMainWindow()
            self.wind.setCentralWidget(self.free_editor)
            self.wind.show()
        else:
            self.wind.hide()  # hide the window if it's already visible


class MyLineEdit(QLineEdit):
    escapePressed = pyqtSignal()
    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            self.escapePressed.emit()
        elif event.key() == Qt.Key_Return:
            self.returnPressed.emit()   
        else:
            super().keyPressEvent(event) 

class SearchWidget(QWidget):
    def __init__(self, editors, function_list, header_layout, editor):
        super().__init__()

        self.editors = editors

        self.function_list = function_list
        self.main_editor = editor
        self.header_layout = header_layout
        # Add a search input field
        self.forward = True
        self.search_input = MyLineEdit(self)
        self.search_input.escapePressed.connect(self.clear_occurrences_in_editors)
        self.search_input.returnPressed.connect(self.return_press_for_search)

        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.search_text)
        # self.search_input.keyPressEvent(self.esc)
        self.search_term = ""
        self.nextBtn = QPushButton()
        self.nextBtn.setIcon(QIcon(resource_path(os.path.join(parent_directory, "icons\\chevron-right.svg"))))
        self.nextBtn.setFixedSize(22, 22)
        self.nextBtn.clicked.connect(self.next_button)

        self.previousBtn = QPushButton()
        self.previousBtn.setIcon(QIcon(resource_path(os.path.join(parent_directory, "icons\\chevron-left.svg"))))
        self.previousBtn.setFixedSize(22, 22)
        self.previousBtn.clicked.connect(self.previous_button)

        self.header_layout.addWidget(self.search_input)
        self.header_layout.addWidget(self.previousBtn)
        self.header_layout.addWidget(self.nextBtn)
        self.header_layout.setAlignment(Qt.AlignRight)
        
    #     # Variable to store the active editor
    #     self.active_editor = None

    #     # Connect editor signals
    #     for editor in self.editors:
    #         editor.mousePressEvent = lambda event: self.set_active_editor(editor)

    # def set_active_editor(self, editor):
    #     # Update the active editor variable
    #     self.active_editor = editor
    #     print(f"Active editor: {self.active_editor.objectName()}")
        

    def return_press_for_search(self):
        if self.forward: 
            self.next_button()
        else: 
            self.previous_button()
    
    def clear_occurrences_in_editors(self):
        for editor in self.editors:
            editor.clear_occurrences(1)
            
    def find_next_in_all_editors(self):
        for editor in self.editors:
            # if editor == self.active_editor:
            editor.find_next(self.search_term)
    
    def find_previous_in_all_editors(self):
        for editor in self.editors:
            # if editor == self.active_editor:
            editor.find_previous(self.search_term)      

           
    def search_text(self):
        # Get the search term from the input field
        self.search_term = self.search_input.text()
        if self.search_term is None or self.search_term == "":
            print("search term is not set")
        else:
            # Clear any previous selections or highlights in all editors
            for editor in self.editors:
                # Prepare variables for search, and clear previous selections
                editor.SendScintilla(QsciScintilla.SCI_CLEARSELECTIONS)
                editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, editor.length())
                # pass
                editor.text_marker(self.search_term)
                
    def next_button(self):
        self.forward = True
        self.find_next_in_all_editors()
        # self.previousBtn.setStyleSheet("")
        # self.nextBtn.setStyleSheet("background-color: #d4d4d4;")
        self.search_input.setFocus()
        
    
    def previous_button(self):
        self.forward = False
        self.find_previous_in_all_editors()
        # self.nextBtn.setStyleSheet("")
        # self.previousBtn.setStyleSheet("background-color: #d4d4d4;")
        self.search_input.setFocus()

            

if __name__ == '__main__':
    window = Editor()
    window.show()
    sys.exit(app.exec_())


# License for Lexilla, Scintilla, and SciTE

# Copyright 1998-2021 by Neil Hodgson <neilh@scintilla.org>

# All Rights Reserved