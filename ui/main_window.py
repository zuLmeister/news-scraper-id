# ui/main_window.py
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from scraper.worker import ScraperWorker


class NewsScraperApp(QMainWindow):
    def __init__(self):
        """
        Initialize the main window and build the user interface.
        
        Sets the window title and default geometry, creates the `worker` attribute (initialized to `None`), and constructs UI components by calling `init_ui`.
        """
        super().__init__()
        self.setWindowTitle("Indo News Scraper Pro")
        self.setGeometry(100, 100, 800, 600)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """
        Constructs and configures the main window's widgets, layouts, and signal connections.
        
        Creates and places the keyword input, minimum-year and target spin boxes (year range 2000–2030, default 2020; target range 1–1000, default 50), an output-folder display defaulting to the current working directory with a selector button, a read-only dark-themed monospaced log viewer, a progress bar, and START/STOP buttons. Connects the folder button to select_folder, the start button to start_scraping, and the stop button to stop_scraping, and initializes widget state (stop button disabled).
        """
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Input row
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Keyword:"))
        self.inp_keyword = QLineEdit()
        self.inp_keyword.setPlaceholderText("Contoh: korupsi KPK")
        form_layout.addWidget(self.inp_keyword, 3)

        self.inp_year = QSpinBox()
        self.inp_year.setRange(2000, 2030)
        self.inp_year.setValue(2020)
        self.inp_year.setPrefix("Min Tahun: ")
        form_layout.addWidget(self.inp_year)

        self.inp_target = QSpinBox()
        self.inp_target.setRange(1, 1000)
        self.inp_target.setValue(50)
        self.inp_target.setPrefix("Target: ")
        form_layout.addWidget(self.inp_target)

        layout.addLayout(form_layout)

        # Folder output
        folder_layout = QHBoxLayout()
        self.lbl_folder = QLineEdit(os.getcwd())
        self.lbl_folder.setReadOnly(True)
        btn_folder = QPushButton("Pilih Folder Output")
        btn_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.lbl_folder, 1)
        folder_layout.addWidget(btn_folder)
        layout.addLayout(folder_layout)

        # Log box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #00ff00; 
            font-family: Consolas, Monaco, monospace;
        """)
        layout.addWidget(self.log_box, 1)

        # Progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("START SCRAPING")
        self.btn_start.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 10px;")
        self.btn_start.clicked.connect(self.start_scraping)

        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 10px;")
        self.btn_stop.clicked.connect(self.stop_scraping)
        self.btn_stop.setEnabled(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)

    def select_folder(self):
        """
        Open a folder selection dialog and update the output-folder display with the chosen path.
        
        If the user selects a directory, set the `lbl_folder` widget's text to that directory path; do nothing if the dialog is cancelled.
        """
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if folder:
            self.lbl_folder.setText(folder)

    def log(self, text: str):
        """
        Append a message to the UI log box and scroll the log view to the bottom.
        
        Parameters:
            text (str): Message to append to the log display.
        """
        self.log_box.append(text)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def start_scraping(self):
        """
        Initiates a scraping run using the current UI inputs and transitions the UI into a running state.
        
        If the keyword input is empty, shows a warning and aborts. Otherwise, clears the log, resets and configures the progress bar, disables relevant inputs and the start button while enabling the stop button, constructs a ScraperWorker with the current keyword, minimum year, target count, and output directory, connects the worker's log, progress, and finished signals to the UI handlers, and starts the worker.
        """
        keyword = self.inp_keyword.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Error", "Keyword tidak boleh kosong!")
            return

        target = self.inp_target.value()
        self.progress.setMaximum(target)
        self.progress.setValue(0)
        self.log_box.clear()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.inp_keyword.setEnabled(False)

        self.worker = ScraperWorker(
            keyword=keyword,
            min_year=self.inp_year.value(),
            target_n=target,
            output_dir=self.lbl_folder.text()
        )
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def stop_scraping(self):
        """
        Request the running scraper worker to stop if one exists and is active.
        
        If a worker instance is present and currently running, this method calls its `stop()` method to request cancellation.
        """
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    def on_finished(self, filepath: str):
        """
        Restore UI controls to their idle state and notify the user when the scraping worker finishes.
        
        If `filepath` is a non-empty string, informs the user that data was saved at that path; otherwise informs the user that the process completed with no results or was cancelled.
        
        Parameters:
            filepath (str): Path to the saved output file if scraping produced a result, or an empty string when there is no output.
        """
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.inp_keyword.setEnabled(True)

        if filepath:
            QMessageBox.information(self, "Sukses!", f"Data berhasil disimpan di:\n{filepath}")
        else:
            QMessageBox.information(self, "Selesai", "Proses selesai tanpa hasil atau dibatalkan.")