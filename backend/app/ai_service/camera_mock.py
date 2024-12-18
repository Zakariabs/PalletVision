import os
import time

class CameraMock:
    def __init__(self, images_dir, interval=5):
        """
        images_dir: Directory containing images named image_1.png, image_2.png, etc.
        interval: Time in seconds between each "capture".
        """
        self.images_dir = images_dir
        self.interval = interval
        # List and sort the image files by their numeric suffix if possible
        self.image_files = self._get_ordered_image_list()

    def _get_ordered_image_list(self):
        # Assuming files named image_1.png, image_2.png, etc.
        files = [f for f in os.listdir(self.images_dir) if f.startswith("image_")]
        # Extract the numeric part and sort
        def extract_num(name):
            # name like image_1.png
            base = os.path.splitext(name)[0]  # image_1
            _, num = base.split("_")          # ["image","1"]
            return int(num)

        files.sort(key=extract_num)
        return files

    def run_continuous_capture(self, callback):
        """
        Continuously capture an image every 'interval' seconds and run callback(image_path).
        Loops through the images repeatedly.
        """
        index = 0
        while True:
            if not self.image_files:
                time.sleep(self.interval)
                continue
            image_name = self.image_files[index]
            image_path = os.path.join(self.images_dir, image_name)
            callback(image_path)

            index = (index + 1) % len(self.image_files)
            time.sleep(self.interval)
