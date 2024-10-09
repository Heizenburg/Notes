import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import argparse
import threading

# Set up logging
logging.basicConfig(filename='file_monitor.log', level=logging.INFO)

# Open the log file and print its contents
with open('file_monitor.log', 'r') as file:
    print(file.read())

# Define constants
SOURCE_FOLDER = r'R:\RawData\Massmart Data'
PARAMETERS = [
    {'target_dir': r'R:\RawData\Masscash\\Wholesale\ToUpload', 'keyword': 'MassCashWholesale'},
    {'target_dir': r'R:\RawData\Masscash\Retail\ToUpload',     'keyword': 'MassCashRetail'},
    {'target_dir': r'R:\RawData\Makro Updated\\ToUpload',      'keyword': 'Makro'},
    {'target_dir': r'R:\RawData\Game\ToUpload',                'keyword': 'MassDiscounters'},
    {'target_dir': r'R:\RawData\KitKat\ToUpload',              'keyword': 'KitKat'},
    {'target_dir': r'R:\RawData\Massbuild\ToUpload',           'keyword': 'Massbuild'}
]
EXCLUDED_KEYWORDS = ['ExportSummary', 'Stock', 'test']
MAX_ALLOWED_TIME_LAPSE = 60 * 5  # Five minutes

class FileHandler(FileSystemEventHandler):
    def __init__(self, source_dir, parameters):
        self.source_dir = source_dir
        self.parameters = parameters

    def on_created(self, event):
        for params in self.parameters:
            if params['keyword'] in event.src_path:
                move_files_based_on_keyword(self.source_dir, params['target_dir'], params['keyword'])

def move_files_based_on_keyword(source_dir, target_dir, keyword):
    try:
        # Get a list of files in the source directory that match the keyword and are not excluded
        files_to_move = [file for file in os.listdir(source_dir) 
                        if keyword in file 
                        and file.endswith('.txt') 
                        and not any(excluded_keyword.lower() in file.lower() for excluded_keyword in EXCLUDED_KEYWORDS)
                        ]

        if not files_to_move:
            logging.info(f"No files with the keyword '{keyword}' found in {source_dir}. Skipping move operation.")
            return

        # Move each file to the target directory if it doesn't already exist
        for file in files_to_move:
            source = os.path.join(source_dir, file)
            destination = os.path.join(target_dir, file)
            if not os.path.exists(destination):
                shutil.move(source, destination)
                logging.info(f"Moved {file} to {destination}")
            else:
                logging.info(f"Skipping {file} as it already exists in {target_dir}")

    except Exception as e:
        logging.error(f"Error moving files: {str(e)}")

def monitor_files(source_folder, parameters, max_inactive_time):
    try:
        for params in parameters:
            move_files_based_on_keyword(source_folder, params['target_dir'], params['keyword'])

        # Create a file handler and observer to monitor the source folder
        event_handler = FileHandler(source_folder, parameters)
        observer = Observer()
        observer.schedule(event_handler, source_folder, recursive=True)
        observer.start()

        logging.info(f"Monitoring {source_folder} for new files...")
        start_time = time.time()
        while True:
            if time.time() - start_time >= max_inactive_time:
                logging.info(f"No new files detected for the past {int(max_inactive_time / 60)} minutes. Terminating script.")
                observer.stop()
                break

            time.sleep(10)
    except Exception as e:
        logging.error(f"Error monitoring files: {str(e)}")
    finally:
        observer.join()

def tail_log_file():
    with open('file_monitor.log', 'r') as file:
        file.seek(0, 2)  # Move to the end of the file
        while True:
            line = file.readline()
            if line:
                print(line.strip())

# Start a separate thread to tail the log file
log_tail_thread = threading.Thread(target=tail_log_file)
log_tail_thread.daemon = True  # Set as daemon thread to exit with main thread
log_tail_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_folder', type=str, default=SOURCE_FOLDER)
    parser.add_argument('--parameters', type=str, default=PARAMETERS)
    parser.add_argument('--time', type=int, default=MAX_ALLOWED_TIME_LAPSE)
    args = parser.parse_args()

    # Start monitoring in a separate thread
    monitoring_thread = threading.Thread(target=monitor_files, args=(args.source_folder, args.parameters, args.time))
    monitoring_thread.start()

"""
---------------- USAGE ------------------------
1) In the terminal, run the following command:
> cd notebooks/massmart/ && python massmart_placement.py
2) If you want to add parameters, run the following command:
> python massmart_placement.py --source_folder R:\RawData\Massmart Data --parameters "[{'target_dir': r'R:\RawData\Masscash\\Wholesale\ToUpload', 'keyword': 'MassCashWholesale'}]" --time 60
-----------------------------------------------
"""
