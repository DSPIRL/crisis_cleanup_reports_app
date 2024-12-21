import sys

from PyQt6.QtHelp import QCompressedHelpInfo

from reports import csv_cleanup, weekly_report
from pathlib import Path
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QTableWidget, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget, QFileDialog
)


class CrisisCleanupReports(QDialog):
    def __init__(self, parent=None):
        super(CrisisCleanupReports, self).__init__(parent)

        # Setup group boxes
        self.top_left_group_box = self.GroupBoxTopLeft()
        self.top_right_group_box = self.GroupBoxTopRight()
        # self.bottom_group_box = self.GroupBoxBottom()  # Bottom group box

        self.original_palette = QApplication.palette()

        # Main layout
        main_layout = QGridLayout()
        main_layout.addWidget(self.top_left_group_box, 1, 0)
        main_layout.addWidget(self.top_right_group_box, 1, 1)
        # main_layout.addWidget(self.bottom_group_box, 2, 0, 2, 2)  # Bottom group box

        main_layout.setRowStretch(1, 1)
        # main_layout.setRowStretch(2, 1)  # Bottom group box
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        self.setLayout(main_layout)

        self.setWindowTitle("Crisis Cleanup Reports")
        self.setFixedSize(600, 400)

        # Connect the drop-down list signal to update the right view
        self.top_left_group_box.combo_box_report_type.currentTextChanged.connect(
            self.update_top_right_view
        )

        # Explicitly initialize the top-right view with the default value (empty string)
        self.update_top_right_view(self.top_left_group_box.combo_box_report_type.currentText())


    def update_top_right_view(self, selected_text):
        """
        Dynamically update the content of GroupBoxTopRight based on the selected report type.
        """
        # if not selected_text.strip():
        #     self.top_right_group_box.clear_view()
        #     return

        self.top_right_group_box.update_view(selected_text)


    class GroupBoxTopLeft(QGroupBox):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setTitle("Select a job type:")
            self.top_left_layout = QVBoxLayout()
            self.setLayout(self.top_left_layout)

            self.combo_box_report_type = QComboBox()
            self.combo_box_report_type.addItems(["", "CSV Cleanup", "Weekly Report"])

            self.combo_box_report_type.setCurrentText("")

            # Add widgets to the layout
            label_box_report_type = QLabel("Job type:")
            self.top_left_layout.addWidget(label_box_report_type)
            self.top_left_layout.addWidget(self.combo_box_report_type)
            self.top_left_layout.addStretch(1)

        def get_selected_job(self):
            return self.combo_box_report_type.currentText()

    class GroupBoxTopRight(QGroupBox):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setTitle("Select file(s) to run job on:")
            self.top_right_layout = QVBoxLayout()
            self.setLayout(self.top_right_layout)

            # Store the selected file path
            self.selected_file = None


        def update_view(self, selected_text):
            # Clear the previous view and reset file selection states
            self.clear_view()

            if selected_text == "CSV Cleanup":
                # Single file case (CSV Cleanup job)
                self.select_file_button = QPushButton("Select File")
                self.select_file_button.clicked.connect(lambda: self.select_csv_file("single"))
                self.top_right_layout.addWidget(self.select_file_button)

                # Display and remove file button
                self.file_info_layout = QHBoxLayout()
                self.file_display_label = QLabel("")  # For displaying only one file
                self.remove_file_button = QPushButton("Remove File")
                self.csv_help_text = QLabel("Select a CSV file exported from the Crisis Cleanup app. Running this\n"
                                            "job will export a CSV in the current directory that this program is\n"
                                            "located in.")
                self.remove_file_button.clicked.connect(lambda: self.remove_file("single"))
                self.remove_file_button.setEnabled(False)  # Initially disabled

                self.file_info_layout.addWidget(self.file_display_label)
                self.file_info_layout.addWidget(self.remove_file_button)
                self.top_right_layout.addLayout(self.file_info_layout)
                self.top_right_layout.addStretch(1)
                self.top_right_layout.addWidget(self.csv_help_text)

                # Add the new bottom button here (common to both CSV Cleanup and Weekly Report)
                self.run_report_button = QPushButton("Run Report")  # Add your custom name here
                self.run_report_button.clicked.connect(lambda: self.run_csv_cleanup())
                self.top_right_layout.addWidget(self.run_report_button)

            elif selected_text == "Weekly Report":
                # Two files (Weekly Report job)

                # First file (Old Report)
                self.select_first_file_button = QPushButton("Select Old Report")
                self.select_first_file_button.clicked.connect(lambda: self.select_csv_file("old"))
                self.top_right_layout.addWidget(self.select_first_file_button)

                self.file_one_info_layout = QHBoxLayout()
                self.file_one_display_label = QLabel("")  # Old file label
                self.weekly_report_help_text = QLabel("Select the old and new reports generated by the CSV Cleanup\n"
                                                      "job. This job will generate a New Cases and Closed Cases\n"
                                                      "report in the directory that this program is located in.")
                self.remove_file_one_button = QPushButton("Remove File")
                self.remove_file_one_button.clicked.connect(lambda: self.remove_file("old"))
                self.remove_file_one_button.setEnabled(False)
                self.file_one_info_layout.addWidget(self.file_one_display_label)
                self.file_one_info_layout.addWidget(self.remove_file_one_button)
                self.top_right_layout.addLayout(self.file_one_info_layout)

                # Second file (New Report)
                self.select_second_file_button = QPushButton("Select New Report")
                self.select_second_file_button.clicked.connect(lambda: self.select_csv_file("new"))
                self.top_right_layout.addWidget(self.select_second_file_button)

                self.file_two_info_layout = QHBoxLayout()
                self.file_two_display_label = QLabel("")  # New file label
                self.remove_file_two_button = QPushButton("Remove File")
                self.remove_file_two_button.clicked.connect(lambda: self.remove_file("new"))
                self.remove_file_two_button.setEnabled(False)
                self.file_two_info_layout.addWidget(self.file_two_display_label)
                self.file_two_info_layout.addWidget(self.remove_file_two_button)
                self.top_right_layout.addLayout(self.file_two_info_layout)

                self.top_right_layout.addStretch(1)

                self.top_right_layout.addWidget(self.weekly_report_help_text)
                # Add Run Report button
                self.run_report_button = QPushButton("Run Report")
                # Connect the button to the run_report_action method for Weekly Report
                self.run_report_button.clicked.connect(lambda: self.run_weekly_report())
                self.top_right_layout.addWidget(self.run_report_button)

            elif selected_text == "":

                self.info_layout= QHBoxLayout()
                self.help_text = QLabel("Select a job type from the drop-down list above.")

                self.top_right_layout.addStretch(1)
                self.top_right_layout.addLayout(self.info_layout)
                self.top_right_layout.addWidget(self.help_text)


        def run_weekly_report(self):
            # Check if both file types (old and new) are selected
            if self.old_report_file and self.new_report_file:
                weekly_report.generate_weekly_report(self.old_report_file, self.new_report_file)
            else:
                return


        def run_csv_cleanup(self):
            # Check if a file was selected
            if self.selected_file:
                csv_cleanup.generate_csv_cleanup(self.selected_file)
            else:
                return


        def clear_view(self):
            """
            Clears all widgets in the top-right group box and resets file state.
            """
            # Clear the layout widgets
            while self.top_right_layout.count():
                widget = self.top_right_layout.takeAt(0).widget()
                if widget:
                    widget.setParent(None)

            # Reset file selection states for all file types
            self.selected_file = None
            self.old_report_file = None
            self.new_report_file = None

            # Reset button and label attributes
            if hasattr(self, 'remove_file_button'):
                self.remove_file_button.deleteLater()  # Properly delete the button widget
                del self.remove_file_button  # Remove the reference from the object
            if hasattr(self, 'remove_file_one_button'):
                self.remove_file_one_button.deleteLater()
                del self.remove_file_one_button
            if hasattr(self, 'remove_file_two_button'):
                self.remove_file_two_button.deleteLater()
                del self.remove_file_two_button

            # Reset display labels if they exist
            if hasattr(self, 'file_display_label'):
                self.file_display_label.deleteLater()
                del self.file_display_label
            if hasattr(self, 'file_one_display_label'):
                self.file_one_display_label.deleteLater()
                del self.file_one_display_label
            if hasattr(self, 'file_two_display_label'):
                self.file_two_display_label.deleteLater()
                del self.file_two_display_label

            # Reset other GUI elements like help text or buttons, if needed
            if hasattr(self, 'csv_help_text'):
                self.csv_help_text.deleteLater()
                del self.csv_help_text
            if hasattr(self, 'weekly_report_help_text'):
                self.weekly_report_help_text.deleteLater()
                del self.weekly_report_help_text
            if hasattr(self, 'run_report_button'):
                self.run_report_button.deleteLater()
                del self.run_report_button


        def select_csv_file(self, file_type):
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("CSV Files (*.csv)")
            if file_dialog.exec():  # Trigger the file dialog
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    selected_file = selected_files[0]
                    file_display_name = Path(selected_file).name
                    # Handle based on file type
                    if file_type == "single":
                        self.selected_file = selected_file
                        self.file_display_label.setText(f"Selected: {file_display_name}")
                        self.remove_file_button.setEnabled(True)
                        self.select_file_button.setEnabled(False)
                        return file_display_name
                    elif file_type == "old":
                        self.old_report_file = selected_file
                        self.file_one_display_label.setText(f"Selected: {file_display_name}")
                        self.remove_file_one_button.setEnabled(True)
                        self.select_first_file_button.setEnabled(False)
                        return file_display_name
                    elif file_type == "new":
                        self.new_report_file = selected_file
                        self.file_two_display_label.setText(f"Selected: {file_display_name}")
                        self.remove_file_two_button.setEnabled(True)
                        self.select_second_file_button.setEnabled(False)
                        return file_display_name


        def remove_file(self, file_type):
            if file_type == "single":
                self.selected_file = None
                self.file_display_label.setText("")
                self.remove_file_button.setEnabled(False)
                self.select_file_button.setEnabled(True)
            elif file_type == "old":
                self.old_report_file = None
                self.file_one_display_label.setText("")
                self.remove_file_one_button.setEnabled(False)
                self.select_first_file_button.setEnabled(True)
            elif file_type == "new":
                self.new_report_file = None
                self.file_two_display_label.setText("")
                self.remove_file_two_button.setEnabled(False)
                self.select_second_file_button.setEnabled(True)


    class GroupBoxBottom(QGroupBox):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setTitle("Info and Results:")

            # Create a tab widget for the bottom area
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            self.tab_widget = QTabWidget()
            self.tab_widget.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Ignored
            )

            # Tab 1: Table
            tab1 = QWidget()
            table_widget = QTableWidget(10, 10)  # Create table (10x10)

            tab1hbox = QHBoxLayout()
            tab1hbox.setContentsMargins(5, 5, 5, 5)
            tab1hbox.addWidget(table_widget)
            tab1.setLayout(tab1hbox)

            # Tab 2: Text Edit
            tab2 = QWidget()
            text_edit = QTextEdit()

            tab2hbox = QHBoxLayout()
            tab2hbox.setContentsMargins(5, 5, 5, 5)
            tab2hbox.addWidget(text_edit)
            tab2.setLayout(tab2hbox)

            # Add tabs
            self.tab_widget.addTab(tab1, "&Table")
            self.tab_widget.addTab(tab2, "Text &Edit")

            # Add the tab widget to the bottom group box layout
            self.layout.addWidget(self.tab_widget)

            # Add a timer for potential updates (if needed)
            self.timer = QTimer(self)
            self.timer.start(1000)


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create QApplication instance
    main_window = CrisisCleanupReports()  # Create an instance of the main window
    main_window.show()  # Show the main application window
    sys.exit(app.exec())  # Run the application loop
