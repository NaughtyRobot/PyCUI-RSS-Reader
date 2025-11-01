""" Saves and loads state in files 'feed.json' and 'bookmarks.json' """

import json
from pathlib import Path

APP_PATH = Path(__file__).resolve().parent.parent

def load_json(filename: str) -> dict:
    """ Opens and reads a JSON file as specified in 'filename'

    Returns: 
           A dict object containing the file content if successful or an empty dict if not
    """
   
    path = Path(APP_PATH / filename)

    # If the file doesn't exist, just return an empty dict
    if not path.exists():
        return {}

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Return empty dict instead of False if anything goes wrong
        return {}

def save_json(feed: dict, filename: str) -> bool:
    """ Opens and saves a JSON file containing a dict specified in dict

    Returns:
           True if successful or False
    """
    
    try:
        with open (Path(APP_PATH / filename), 'w') as f:
            json.dump(feed, f, indent = 2)
            return True
    except (json.JSONDecodeError, OSError):
            return False
