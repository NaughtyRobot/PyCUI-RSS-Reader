import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

API_KEY = ''
APP_PATH = Path(__file__).resolve().parent.parent

def api_key_ok() -> bool:
    """ Checks for the presence of an API key environment variable

    Returns:
        True if the key is found, otherwise False
    """
    global API_KEY
    load_dotenv(override=True)
    API_KEY = os.getenv('GOOGLE-API-KEY')
    return True if API_KEY else False

def ask_gemini(text:str) -> str:
    """
    Passes the supplie markdown text to Gemini API and asks for a summarised version in return.

    Args:
        text: str - The article text to be summarised.
    Returns:
        A string containing the article summary is everything went well, otherwise a JSON object describing the problem.
    """
    
    client = genai.Client(api_key = API_KEY)
    model = 'gemini-2.5-flash-lite'
    prompt = 'Please read the following article and return a short summary (no more than three paragraphs) in Markdown format:'
    try:
        response = client.models.generate_content(
            model = model,
            config = types.GenerateContentConfig(system_instruction = prompt),
            contents = text
        )
        return response.text
    except Exception as e:
        return e

def save_api_key(key: str) -> bool:
    """ Saves the supplied API key in .env for later reuse """
    filename = Path(APP_PATH / '.env')
    if filename.exists(): os.unlink(filename)
    try:
        with open (filename, 'w') as f:
            f.write(f"GOOGLE-API-KEY={key}\n")
    except OSError:
        return False
