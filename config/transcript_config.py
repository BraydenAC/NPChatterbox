import logging
from pathlib import Path

#Define the level of the each logging tier
TRANSCRIPT = 25
MODE = 16
SYSTEM = 14

def add_logging_level(level_name: str, level_num: int, method_name: str | None = None):
    """
    Comprehensively adds a new logging level to the `logging` module.
    """
    if hasattr(logging, level_name):
        raise AttributeError(f'{level_name} already defined in logging module')
    if hasattr(logging, method_name or level_name.lower()):
        raise AttributeError(f'{method_name or level_name.lower()} already defined')

    # Add the level
    logging.addLevelName(level_num, level_name)

    # Create the method on the Logger class: logger.transcript(), logger.mode(), etc.
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    # Create the method on the module: logging.transcript(), logging.mode(), etc.
    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    method_name = method_name or level_name.lower()

    logging.getLoggerClass().method_name = log_for_level
    setattr(logging, method_name, log_to_root)
    setattr(logging, level_name, level_num)

#Custom logging levels
#TRANSCRIPT logs lines spoken by players or npcs.  
# Timestamp, Player_Name: "Hey there!"
add_logging_level("TRANSCRIPT", TRANSCRIPT, "transcript")
#MODE logs the changing between settings in an npc.  
# Timestamp, NPC_ID: rumorsharing > shopkeep
add_logging_level("MODE", MODE, "mode")
#SYSTEM logs the back-end actions relevant to the conversation.  Not recorded in normal transcript, the equivalent to DEBUG.
# Timestamp: Player_Name gives NPC_ID 5 coins
add_logging_level("SYSTEM", SYSTEM, "system")

#Create logging folder if it doesn't exist
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,  # lowest level we care about
    format='%(asctime)s | %(levelname)-10s | %(name)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.handlers.RotatingFileHandler(
            "logs/app.log", maxBytes=10_000_000, backupCount=5, encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

# import logging
# import time
# import os
# from appdirs import user_log_dir

# # Time format for filenames
# t = time.localtime()
# current_time = time.strftime("%H-%M-%S", t)

# # Directory setup
# BASE_DIR = user_log_dir("ConversationInferenceTree")
# os.makedirs(BASE_DIR, exist_ok=True)

# # File paths (use f-strings for actual variable substitution)
# LOG_FILE = os.path.join(BASE_DIR, f'log_{current_time}.log')
# PROGRESS_FILE = os.path.join(BASE_DIR, f'progress_{current_time}.log')

# # Logger for general debug/info
# logger = logging.getLogger('main_logger')
# logger.setLevel(logging.DEBUG)

# file_handler = logging.FileHandler(LOG_FILE)
# file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# logger.addHandler(file_handler)

# # Logger for progress (separate file)
# log_progress = logging.getLogger('progress_logger')
# log_progress.setLevel(logging.INFO)

# progress_handler = logging.FileHandler(PROGRESS_FILE)
# progress_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
# log_progress.addHandler(progress_handler)