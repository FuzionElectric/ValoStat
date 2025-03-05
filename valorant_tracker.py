from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QTabWidget, QTextEdit, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import json
import os
import requests
import logging
import time
import ctypes

# ==========================================================
# Logging Setup - Logs all actions and errors for debugging
# ==========================================================
logging.basicConfig(
    filename="logs/tracker_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def debug_log(message):
    """Logs a debug message to the console and file."""
    print("[DEBUG]:", message)
    logging.debug(message)

# ==========================================================
# API Key Handling - Loads the Riot API Key from config file
# ==========================================================
CONFIG_FILE = "config/tracker_config.json"
def load_api_key():
    """Loads API key from configuration file, ensuring it's valid."""
    if not os.path.exists(CONFIG_FILE):
        debug_log("Config file not found. Please update tracker_config.json.")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        api_key = config.get("api_key", "").strip()
        return api_key if api_key and "RGAPI-" in api_key else None

RIOT_API_KEY = load_api_key()

# ==========================================================
# Match Tracker - Fetches real-time match data via API
# ==========================================================
class MatchTracker(QThread):
    match_data_signal = pyqtSignal(str)  # Signal to update the UI

    def run(self):
        """Runs the tracking thread to continuously fetch match status."""
        while True:
            match_status = self.fetch_match_status()
            self.match_data_signal.emit(match_status)
            time.sleep(5)  # Updates every 5 seconds

    def fetch_match_status(self):
        """Fetches current match status from Riot's API."""
        url = "https://americas.api.riotgames.com/valorant/v1/matches"
        headers = {"X-Riot-Token": RIOT_API_KEY}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return "Match Active - Data Retrieved!"
            else:
                return "No Active Match Found."
        except Exception as e:
            debug_log(f"API Error: {e}")
            return "Error fetching data."

# ==========================================================
# Main GUI - Displays match data and logs
# ==========================================================
class ValorantTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Valorant Tracker - Enterprise Edition")
        self.setGeometry(100, 100, 1000, 650)
        self.initUI()
        self.start_tracking()

    def initUI(self):
        """Initializes the user interface layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_status_tab(), "Live Match")
        self.tabs.addTab(self.create_logs_tab(), "Logs")
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

    def create_status_tab(self):
        """Creates the Live Match status tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        self.match_status_label = QLabel("Waiting for match data...")
        self.match_status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.match_status_label)
        tab.setLayout(layout)
        return tab

    def create_logs_tab(self):
        """Creates the Logs tab to display debug information."""
        tab = QWidget()
        layout = QVBoxLayout()
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        tab.setLayout(layout)
        return tab

    def start_tracking(self):
        """Starts the background tracking process."""
        self.tracker_thread = MatchTracker()
        self.tracker_thread.match_data_signal.connect(self.update_match_status)
        self.tracker_thread.start()

    def update_match_status(self, status):
        """Updates the UI with the latest match status."""
        self.match_status_label.setText(status)

# ==========================================================
# Application Entry Point - Launches the GUI
# ==========================================================
def launch_gui():
    app = QApplication(sys.argv)
    window = ValorantTrackerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_gui()
