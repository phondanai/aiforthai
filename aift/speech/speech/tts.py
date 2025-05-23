import requests
import time
import wave
from aift.setting.setting import get_api_key, PACKAGE_NAME
import sys
import time
import os
import requests
from pythainlp import sent_tokenize
from pythainlp.corpus.common import thai_words
from pythainlp.util import Trie

def convert(text:str, path:str, speaker:int=0, phrase_break:int=0, audiovisual:int=0):
    api_key = get_api_key()
    headers = {'Apikey':api_key, 'X-lib':PACKAGE_NAME}
    url = 'https://api.aiforthai.in.th/vaja9/synth_audiovisual'
    data = {'speaker': speaker, 'phrase_break':phrase_break, 'audiovisual':audiovisual}

    if len(text) <= 300:
        data['input_text'] = text
        time.sleep(1)
        response = requests.post(url, json=data, headers=headers)
        time.sleep(2)
        resp = requests.get(response.json()['wav_url'], headers=headers)
        if resp.status_code == 200:
            with open(path, 'wb') as f:
                f.write(resp.content)

            return f'{path}'
        else:
            return resp.reason

    else:
        if os.path.isfile(path):
            os.remove(path)
        sents = sent_tokenize(text.replace('\n', ' '))
        process_sents = []

        for line in sents:
            if len(line) <= 300:
                process_sents.append(line)
            else:
                process_sents += split_line(line)

        for line in process_sents:
            call_vaja(line.strip(), url, headers, data)
            join_wav(path)

        return f'{path}'

def call_vaja(text, url, headers, data):
    time.sleep(1)
    data['input_text'] = text
    status_code = 0
    while (status_code != 200):
        response = requests.post(url, json=data, headers=headers)
        status_code = response.status_code

    time.sleep(2)
    status_code = 0
    while (status_code != 200):
        resp = requests.get(response.json()['wav_url'], headers=headers)
        status_code=resp.status_code
        if status_code != 200:
            time.sleep(1)
        else:
            with open('./tts_file_for_merge.wav', 'wb') as file:
                file.write(resp.content)

def join_wav(path):
    if not os.path.isfile(path):
        os.rename('./tts_file_for_merge.wav', path)
    else:
        with wave.open(path, 'rb') as sound1, wave.open("./tts_file_for_merge.wav", 'rb') as sound2:

            # Read frames
            frames1 = sound1.readframes(sound1.getnframes())
            frames2 = sound2.readframes(sound2.getnframes())

        # Write the combined frames back to the original file
        with wave.open(path, 'wb') as output:
            output.setparams(sound1.getparams()) 
            output.writeframes(frames1 + frames2)  # Concatenate audio frames

        # Remove the temporary file
        os.remove('./tts_file_for_merge.wav')

def split_line(text, max_char=300):
    process_sents = []
    s = 0
    while s < len(text):
        process_sents.append(text[s:s+max_char])
        s += max_char

    return process_sents
