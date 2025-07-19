"""
Video processing for screen recording
"""

import cv2
import numpy as np
import pyautogui
import threading
import time
from typing import Optional, Tuple
from src.config import config
from src.utils import setup_logging, generate_timestamp

logger = setup_logging(level=config.log_level)

class VideoRecorder:
    """
    Screen video recorder implementation
    """
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.screen_thread = None
        self.screen_size = pyautogui.size()
        logger.info(f"Screen size detected: {self.screen_size}")

    def start_recording(self, output_filename: Optional[str] = None, region: Optional[Tuple[int, int, int, int]] = None):
        """Start screen recording"""
        if not output_filename:
            timestamp = generate_timestamp()
            output_filename = f"screen_recording_{timestamp}"

        self.recording = True

        if region:
            x, y, width, height = region
            video_size = (width, height)
        else:
            x, y = 0, 0
            width, height = self.screen_size
            video_size = self.screen_size

        fourcc = cv2.VideoWriter_fourcc(*config.video.codec)
        video_filename = f"{output_filename}.{config.video.extension}"
        self.video_writer = cv2.VideoWriter(video_filename, fourcc, config.video.fps, video_size)

        logger.info(f"Starting screen recording to {video_filename}")
        logger.info(f"Region: {'Full screen' if not region else f'{region}'}")

        self.screen_thread = threading.Thread(target=self._record_screen, args=(region,))
        self.screen_thread.start()

        return output_filename

    def _record_screen(self, region: Optional[Tuple[int, int, int, int]]):
        """Screen recording thread function"""
        try:
            while self.recording:
                if region:
                    x, y, width, height = region
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                else:
                    screenshot = pyautogui.screenshot()

                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                self.video_writer.write(frame)
                time.sleep(1/config.video.fps)

        except Exception as e:
            logger.error(f"Screen recording error: {e}")

    def stop_recording(self) -> bool:
        """Stop screen recording"""
        if not self.recording:
            logger.warning("No recording in progress")
            return False

        logger.info("Stopping screen recording...")
        self.recording = False

        if self.screen_thread:
            self.screen_thread.join()

        if self.video_writer:
            self.video_writer.release()

        logger.info("✅ Screen recording stopped successfully")
        return True

    def get_screen_region_interactively(self) -> Tuple[int, int, int, int]:
        """Get screen region from user input"""
        print("\nTo select a region:")
        print("1. Position your mouse at the top-left corner")
        print("2. Note the coordinates")

        try:
            x = int(input("Enter X coordinate: "))
            y = int(input("Enter Y coordinate: "))
            width = int(input("Enter width: "))
            height = int(input("Enter height: "))
            return (x, y, width, height)
        except ValueError:
            logger.error("Invalid input for screen region")
            return None

if __name__ == "__main__":
    recorder = VideoRecorder()
    output_file = recorder.start_recording()
    try:
        import time
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        recorder.stop_recording()
        logger.info(f"Video recorded: {output_file}.{config.video.extension}")
