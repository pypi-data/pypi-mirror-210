import threading
import time
from datetime import datetime
import os
import ffmpeg

class VideoThread(threading.Thread):
    """Creates a new thread that handles the creation of video recordings for browser sessions.
    """
    def __init__(self, driver):
        """Receives a webdriver to create an additional thread where screenshots are taken during test execution.
           These screenshots are converted to an mp4 file when the webdriver is killed or after the moonrise test execution has completed.
        """
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.driver = driver
        self.video_folder = None
        self.start()

    def run(self):
        while not self.stop_event.is_set():
            try:
                timestamp = str(datetime.now()).replace(" ", "_").replace(":", "_")
                self.driver.save_screenshot(f"{self.video_folder}/{timestamp}.png")
                time.sleep(0.05)
            except Exception:
                self.stop()

    def stop(self):
        self.stop_event.set()

    def create_video_from_pngs(self, output_file):

        # Get a list of PNG files in the folder
        png_files = [file for file in os.listdir(self.video_folder) if file.endswith('.png')]

        # Sort the files in ascending order based on their names
        png_files.sort()

        # Set up the FFmpeg input file list
        input_file_list = os.path.join(self.video_folder, 'input.txt')
        with open(input_file_list, 'w') as f:
            for i, png_file in enumerate(png_files):
                file_path = os.path.join(self.video_folder, png_file)
                f.write(f"file '{file_path}'\nduration 0.1\n")
        
        ffmpeg.input(input_file_list, format='concat', safe=0).output(
            output_file,
            r=10,  # Set framerate to 10 frames per second (adjust as needed)
            start_number=0  # Set the start number of the input files
        ).overwrite_output().run()
