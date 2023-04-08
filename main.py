import importlib
import socket
import telnetlib
import json


# Check if Google Translator is installed, otherwise install it
try:
    importlib.import_module('googletrans')
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "googletrans"])

from googletrans import Translator

# IP and Port to Connect
HOST = "localhost"
PORT = 4545

# Connect to the CSGO-Server
server_address = (HOST, PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)

# load all available Languages
with open("languages.json") as f:
    languages = json.load(f)

# load the Settings
with open("settings.json") as f:
    settings = json.load(f)

# Google-Translartor created
translator = Translator()


def clean_name(name):
    '''
    Function to clean the Usernames
    '''

    name = name.replace("(Terrorist)", "").replace("(Counter-Terrorist)", "").replace("*DEAD*", "").replace("*SPEC*", "").split("@")[0]
    return name


def send_to_server(text):
    '''
    Function to send a Message to the Server
    '''

    # Telnet-Connection created
    tn = telnetlib.Telnet(HOST, PORT)

    # Message sent
    tn.write(f"{text}\n".encode())

    # Telnet-Connection closed
    tn.close()


def search_language(keyword):
    '''
    Function to find a Language by its Code

    Example:If you input es, it will return Espanol
    '''

    # lade alle verfügbaren Sprachen
    with open("languages.json") as f:
        languages = json.load(f)

    for code, language in languages['language'].items():
        if keyword.lower() == language.lower():
            return code
    return None

# Endless Loop to read the CSGO-Console and searching for Messages
while True:
    data = sock.recv(1024)
    if not data:
        break
    messages = data.decode().split('\n')
    for message in messages:
        if ' :' in message and (" pkts " not in message):

            parts = message.split(' : ', 1)
            username = parts[0]
            if username.strip() not in ["hostname", "version", "udp/ip", "os", "type", "map", "players", "netcon"]:
            
                username = clean_name(username)

                message_text = parts[1].strip()
                translated_text = message_text

                if message_text.startswith("["):
                    pass

                elif message_text.startswith("tm_"):

                    lang_code = message_text.split(" ", 1)[0].replace("tm_", "")

                    message_text = message_text.replace(f"tm_{lang_code}", "")

                    result = translator.translate(message_text, dest=lang_code)
                    translated_text = result.text

                    send_to_server(f'say [{username} in {languages["language"][lang_code]}]: {translated_text}')
                    print(f'''{username} - {translated_text}''')

                elif message_text.startswith("code_"):

                    lang_to_find = message_text.replace("code_", "").split(" ", 1)[0].lower().strip()
                    message_text = message_text.replace(f"code_{lang_to_find}", "")
                    code = search_language(lang_to_find)

                    if code == None:
                        send_to_server(f'say {lang_to_find.capitalize()} is not a valid Language, check my Profile Bio for more.')
                    else:
                        send_to_server(f'say @{username} the Code for {lang_to_find.capitalize()} is {code} - try: tm_{code} Hello')

                else:
                    result = translator.translate(message_text, dest=settings["dest_language"])
                    translated_text = result.text

                    print(f'''{username} - {translated_text}''')
