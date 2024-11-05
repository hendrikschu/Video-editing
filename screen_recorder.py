import sys
import cv2
import numpy as np
import pyautogui
import os
import time
from screeninfo import get_monitors
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QComboBox, QStatusBar, QCheckBox, QLCDNumber, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon

class ScreenRecorder(QThread):
    frame_captured = pyqtSignal(np.ndarray)
    recording_time = pyqtSignal(float)

    def __init__(self, target_frame, output_file, show_cursor, frame_rate=60.0):
        super().__init__()
        self.target_frame = target_frame
        self.output_file = output_file
        self.show_cursor = show_cursor
        self.recording = False
        self.video_writer = None
        self.frame_rate = frame_rate
        self.frame_interval = 1.0 / frame_rate
        self.frames = []
        self.start_time = None

    def run(self):
        self.recording = True
        self.start_time = time.time()
        print("Recording started.")
        screen_width, screen_height = pyautogui.size()

        while self.recording:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            self.recording_time.emit(elapsed_time)

            img = pyautogui.screenshot(region=self.target_frame)
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            if self.show_cursor:
                cursor_x, cursor_y = pyautogui.position()
                cursor_x -= self.target_frame[0]
                cursor_y -= self.target_frame[1]
                cursor_img = pyautogui.screenshot(region=(cursor_x, cursor_y, 16, 16))
                cursor_img = cv2.cvtColor(np.array(cursor_img), cv2.COLOR_BGR2RGB)

                # Ensure the cursor image is within the bounds of the frame
                if 0 <= cursor_x < frame.shape[1] - 16 and 0 <= cursor_y < frame.shape[0] - 16:
                    frame[cursor_y:cursor_y+16, cursor_x:cursor_x+16] = cursor_img

            self.frames.append(frame)
            self.frame_captured.emit(frame)

            # Ensure consistent frame capture interval
            elapsed_time = time.time() - current_time
            time.sleep(max(0, self.frame_interval - elapsed_time))

    def stop(self):
        self.recording = False
        self.wait()
        if self.frames:
            # Calculate the actual frame rate based on the recording duration
            actual_duration = time.time() - self.start_time
            actual_frame_rate = len(self.frames) / actual_duration

            # Write frames to the video file with the adjusted frame rate
            screen_width, screen_height = pyautogui.size()
            self.video_writer = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'mp4v'), actual_frame_rate, (screen_width, screen_height))
            for frame in self.frames:
                self.video_writer.write(frame)
            self.video_writer.release()
        print(f"Recording stopped. Video saved to {self.output_file}")

class RecorderDialog(QDialog):
    def __init__(self):
        super().__init__(None, Qt.WindowCloseButtonHint)
        self.init_ui()
        self.recorder = None

    def init_ui(self):
        self.setWindowTitle('Screen Recorder')
        self.setWindowIcon(QIcon('icon.ico'))  # Add a generic icon (ensure 'icon.png' is in the same directory)
        self.layout = QVBoxLayout()

        self.label = QLabel('Select Target Frame:')
        self.layout.addWidget(self.label)

        self.combo_box = QComboBox()
        self.populate_combo_box()
        self.layout.addWidget(self.combo_box)

        self.cursor_checkbox = QCheckBox('Show Mouse Cursor')
        self.layout.addWidget(self.cursor_checkbox)

        self.start_button = QPushButton('Start Recording')
        self.start_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Recording')
        self.stop_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_button)

        self.timer_display = QLCDNumber()
        self.timer_display.setDigitCount(8)
        self.timer_display.setSegmentStyle(QLCDNumber.Flat)
        self.timer_display.display("00:00.000")
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(QLabel("Recording Time:"))
        timer_layout.addWidget(self.timer_display)
        self.layout.addLayout(timer_layout)

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
        show_cursor = self.cursor_checkbox.isChecked()
        self.recorder = ScreenRecorder(target_frame, output_file, show_cursor)
        self.recorder.frame_captured.connect(self.process_frame)
        self.recorder.recording_time.connect(self.update_timer)
        self.recorder.start()
        self.start_button.setEnabled(False)
        self.status_bar.showMessage("Recording started.")

    def stop_recording(self):
        if self.recorder:
            self.recorder.stop()
            self.start_button.setEnabled(True)
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

    def update_timer(self, elapsed_time):
        minutes, seconds = divmod(elapsed_time, 60)
        milliseconds = (elapsed_time - int(elapsed_time)) * 1000
        self.timer_display.display(f"{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = RecorderDialog()
    dialog.show()
    sys.exit(app.exec_())