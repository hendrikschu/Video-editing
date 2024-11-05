import sys
import cv2
import numpy as np
import pyautogui
import os
from screeninfo import get_monitors
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QComboBox, QStatusBar
from PyQt5.QtCore import QThread, pyqtSignal

class ScreenRecorder(QThread):
    frame_captured = pyqtSignal(np.ndarray)

    def __init__(self, target_frame, output_file):
        super().__init__()
        self.target_frame = target_frame
        self.output_file = output_file
        self.recording = False
        self.video_writer = None

    def run(self):
        self.recording = True
        print("Recording started.")
        screen_width, screen_height = pyautogui.size()
        self.video_writer = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (screen_width, screen_height))

        while self.recording:
            img = pyautogui.screenshot(region=self.target_frame)
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            self.video_writer.write(frame)
            self.frame_captured.emit(frame)

    def stop(self):
        self.recording = False
        self.wait()
        if self.video_writer:
            self.video_writer.release()
        print(f"Recording stopped. Video saved to {self.output_file}")

class RecorderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.recorder = None

    def init_ui(self):
        self.setWindowTitle('Screen Recorder')
        self.layout = QVBoxLayout()

        self.label = QLabel('Select Target Frame:')
        self.layout.addWidget(self.label)

        self.combo_box = QComboBox()
        self.populate_combo_box()
        self.layout.addWidget(self.combo_box)

        self.start_button = QPushButton('Start Recording')
        self.start_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Recording')
        self.stop_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_button)

        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)

        self.setLayout(self.layout)

    def populate_combo_box(self):
        self.combo_box.addItem('Full Screen')
        monitors = get_monitors()
        for i, monitor in enumerate(monitors):
            self.combo_box.addItem(f'Screen {i + 1}')

    def start_recording(self):
        target_frame = self.get_target_frame()
        output_file = os.path.join(os.path.dirname(__file__), 'screen_recording.mp4')
        self.recorder = ScreenRecorder(target_frame, output_file)
        self.recorder.frame_captured.connect(self.process_frame)
        self.recorder.start()
        self.status_bar.showMessage("Recording started.")

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.status_bar.showMessage(f"Recording stopped. Video saved to {self.recorder.output_file}")
            print(f"Recording stopped. Video saved to {self.recorder.output_file}")

    def get_target_frame(self):
        selected_text = self.combo_box.currentText()
        if selected_text == 'Full Screen':
            screen_width, screen_height = pyautogui.size()
            return (0, 0, screen_width, screen_height)
        else:
            screen_index = int(selected_text.split(' ')[1]) - 1
            monitor = get_monitors()[screen_index]
            return (monitor.x, monitor.y, monitor.width, monitor.height)

    def process_frame(self, frame):
        # Here you can process the frame, e.g., save it to a file or display it
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = RecorderDialog()
    dialog.show()
    sys.exit(app.exec_())