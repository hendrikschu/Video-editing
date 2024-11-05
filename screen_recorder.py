import sys
import cv2
import numpy as np
import pyautogui
import os
import time
from screeninfo import get_monitors
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QComboBox, QStatusBar, QCheckBox, QLCDNumber, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon

CURSOR = cv2.imread('cursor.png', cv2.IMREAD_UNCHANGED)

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
        self.cursor_img = CURSOR

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

                # Overlay the cursor image on the frame
                if 0 <= cursor_x < frame.shape[1] and 0 <= cursor_y < frame.shape[0]:
                    cursor_h, cursor_w = self.cursor_img.shape[:2]
                    if cursor_x + cursor_w <= frame.shape[1] and cursor_y + cursor_h <= frame.shape[0]:
                        alpha_s = self.cursor_img[:, :, 3] / 255.0
                        alpha_l = 1.0 - alpha_s

                        for c in range(0, 3):
                            frame[cursor_y:cursor_y+cursor_h, cursor_x:cursor_x+cursor_w, c] = (alpha_s * self.cursor_img[:, :, c] +
                                 alpha_l * frame[cursor_y:cursor_y+cursor_h, cursor_x:cursor_x+cursor_w, c])

            self.frames.append(frame)
            self.frame_captured.emit(frame)

            # Ensure consistent frame capture interval
            elapsed_time = time.time() - current_time
            time.sleep(max(0, self.frame_interval - elapsed_time))

    def stop(self):
        self.recording = False
        self.wait()

class SaveThread(QThread):
    save_finished = pyqtSignal(str)

    def __init__(self, frames, output_file, actual_frame_rate):
        super().__init__()
        self.frames = frames
        self.output_file = output_file
        self.actual_frame_rate = actual_frame_rate

    def run(self):
        screen_width, screen_height = pyautogui.size()
        video_writer = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'mp4v'), self.actual_frame_rate, (screen_width, screen_height))
        for frame in self.frames:
            video_writer.write(frame)
        video_writer.release()
        self.save_finished.emit(self.output_file)

class RecorderDialog(QDialog):
    def __init__(self):
        super().__init__(None, Qt.WindowCloseButtonHint)
        self.init_ui()
        self.recorder = None
        self.save_thread = None
        self.cursor_img = CURSOR

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

        self.waiting_label = QLabel("Saving")
        self.waiting_label.hide()
        self.layout.addWidget(self.waiting_label)

        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)

        self.setLayout(self.layout)

        self.waiting_timer = QTimer()
        self.waiting_timer.timeout.connect(self.update_waiting_label)
        self.waiting_dots = 0

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
            self.status_bar.showMessage("Saving video...")
            self.waiting_label.show()
            self.waiting_timer.start(500)

            # Calculate the actual frame rate based on the recording duration
            actual_duration = time.time() - self.recorder.start_time
            actual_frame_rate = len(self.recorder.frames) / actual_duration

            # Start the save thread
            self.save_thread = SaveThread(self.recorder.frames, self.recorder.output_file, actual_frame_rate)
            self.save_thread.save_finished.connect(self.on_save_finished)
            self.save_thread.start()

    def on_save_finished(self, output_file):
        self.waiting_timer.stop()
        self.waiting_label.hide()
        self.status_bar.showMessage(f"Recording stopped. Video saved to {output_file}")
        print(f"Recording stopped. Video saved to {output_file}")

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
        # Get the current mouse position
        mouse_x, mouse_y = pyautogui.position()
        
        # Draw the cursor on the frame using self.cursor_img
        draw_cursor(frame, mouse_x, mouse_y, self.cursor_img)
        
        # Here you can process the frame, e.g., save it to a file or display it
        pass

    def update_timer(self, elapsed_time):
        minutes, seconds = divmod(elapsed_time, 60)
        milliseconds = (elapsed_time - int(elapsed_time)) * 1000
        self.timer_display.display(f"{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}")

    def update_waiting_label(self):
        self.waiting_dots = (self.waiting_dots + 1) % 4
        self.waiting_label.setText("Saving" + "." * self.waiting_dots)

def draw_cursor(frame, mouse_x, mouse_y, cursor_img):
    # Get the dimensions of the cursor image
    cursor_height, cursor_width = cursor_img.shape[:2]
    
    # Calculate the position to overlay the cursor image
    top_left_x = mouse_x - cursor_width // 2
    top_left_y = mouse_y - cursor_height // 2
    
    # Ensure the overlay is within the frame boundaries
    if top_left_x < 0:
        top_left_x = 0
    if top_left_y < 0:
        top_left_y = 0
    if top_left_x + cursor_width > frame.shape[1]:
        cursor_width = frame.shape[1] - top_left_x
    if top_left_y + cursor_height > frame.shape[0]:
        cursor_height = frame.shape[0] - top_left_y
    
    # Overlay the cursor image on the frame
    overlay = frame[top_left_y:top_left_y + cursor_height, top_left_x:top_left_x + cursor_width]
    cursor_img_resized = cv2.resize(cursor_img, (cursor_width, cursor_height))
    
    if cursor_img_resized.shape[2] == 4:  # Check if the image has an alpha channel
        mask = cursor_img_resized[:, :, 3]
    else:
        # Create a mask based on a color key (e.g., white background)
        mask = cv2.inRange(cursor_img_resized, (255, 255, 255), (255, 255, 255))
    
    mask_inv = cv2.bitwise_not(mask)
    img_bg = cv2.bitwise_and(overlay, overlay, mask=mask_inv)
    img_fg = cv2.bitwise_and(cursor_img_resized, cursor_img_resized, mask=mask)
    dst = cv2.add(img_bg, img_fg)
    frame[top_left_y:top_left_y + cursor_height, top_left_x:top_left_x + cursor_width] = dst

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = RecorderDialog()
    dialog.show()
    sys.exit(app.exec_())