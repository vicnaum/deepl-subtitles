# Original Author: Rasmus Toivanen (@R4ZZ3)
# Original code:
# https://huggingface.co/spaces/RASMUS/Whisper-youtube-crosslingual-subtitles
# Modified by: @vicnaum
# Modified code: removed whisper and youtube, and left just DeepL translation from file

import requests
import json
import pysrt
import pandas as pd

# Put your DeepL API key here
headers = {'Authorization': 'DeepL-Auth-Key 12345678-1234-1234-1234-1234567890ab:fx'}

DeepL_language_codes_for_translation = {
"Bulgarian": "BG",
"Czech": "CS",
"Danish": "DA",
"German": "DE",
"Greek": "EL",
"English": "EN",
"Spanish": "ES",
"Estonian": "ET",
"Finnish": "FI",
"French": "FR",
"Hungarian": "HU",
"Indonesian": "ID",
"Italian": "IT",
"Japanese": "JA",
"Lithuanian": "LT",
"Latvian": "LV",
"Dutch": "NL",
"Polish": "PL",
"Portuguese": "PT",
"Romanian": "RO",
"Russian": "RU",
"Slovak": "SK",
"Slovenian": "SL",
"Swedish": "SV",
"Turkish": "TR",
"Ukrainian": "UK",
"Chinese": "ZH"
}

def parse_srt(srt_path):
    try:    
        df = pd.DataFrame(columns = ['start','end','text'])
        subs = pysrt.open(srt_path)

        objects = []
        for sub in subs:
            start_hours = str(str(sub.start.hours) + "00")[0:2] if len(str(sub.start.hours)) == 2 else str("0" + str(sub.start.hours) + "00")[0:2]
            end_hours = str(str(sub.end.hours) + "00")[0:2] if len(str(sub.end.hours)) == 2 else str("0" + str(sub.end.hours) + "00")[0:2]
            
            start_minutes = str(str(sub.start.minutes) + "00")[0:2] if len(str(sub.start.minutes)) == 2 else str("0" + str(sub.start.minutes) + "00")[0:2]
            end_minutes = str(str(sub.end.minutes) + "00")[0:2] if len(str(sub.end.minutes)) == 2 else str("0" + str(sub.end.minutes) + "00")[0:2]
            
            start_seconds = str(str(sub.start.seconds) + "00")[0:2] if len(str(sub.start.seconds)) == 2 else str("0" + str(sub.start.seconds) + "00")[0:2]
            end_seconds = str(str(sub.end.seconds) + "00")[0:2] if len(str(sub.end.seconds)) == 2 else str("0" + str(sub.end.seconds) + "00")[0:2]
            
            start_millis = str(str(sub.start.milliseconds) + "000")[0:3]
            end_millis = str(str(sub.end.milliseconds) + "000")[0:3]
            objects.append([sub.text, f'{start_hours}:{start_minutes}:{start_seconds}.{start_millis}', f'{end_hours}:{end_minutes}:{end_seconds}.{end_millis}'])

        for object in objects:
            srt_to_df = {
            'start': [object[1]],
            'end': [object[2]], 
            'text': [object[0]] 
            }
    
            df = pd.concat([df, pd.DataFrame(srt_to_df)])
    except Exception as e:
        print("Error creating srt df")
    return df
    
def translate_transcriptions(df, selected_translation_lang_2):
    if selected_translation_lang_2 is None:
        selected_translation_lang_2 = 'English'
    df.reset_index(inplace=True)
    
    print("start_translation")
    translations = []

    text_combined = ""
    for i, sentence in enumerate(df['text']):
        if i == 0:
            text_combined = sentence
        else:
            text_combined = text_combined + '\n' + sentence

    data = {'text': text_combined,
    'tag_spitting': 'xml',
    'target_lang': DeepL_language_codes_for_translation.get(selected_translation_lang_2)
           }
    try:
        usage = requests.get('https://api-free.deepl.com/v2/usage', headers=headers)
        usage = json.loads(usage.text)
        deepL_character_usage = str(usage['character_count'])
        try:
            print('Usage is at: ' + deepL_character_usage + 'characters')
        except Exception as e:
            print(e)
        
        if int(deepL_character_usage) <= 490000:
            print("STILL CHARACTERS LEFT")
            response = requests.post('https://api-free.deepl.com/v2/translate', headers=headers, data=data)
    
            # Print the response from the server
            translated_sentences = json.loads(response.text)
            translated_sentences = translated_sentences['translations'][0]['text'].split('\n')
            df['translation'] = translated_sentences

        else:
            df['translation'] = df['text']    

    except Exception as e:
        print("EXCEPTION WITH DEEPL API")
        print(e)
        df['translation'] = df['text']
        
    print("translations done")

    print("Starting SRT-file creation")
    print(df.head())
    df.reset_index(inplace=True)
    with open('subtitles.vtt','w', encoding="utf-8") as file:
        print("Starting WEBVTT-file creation")
    
        for i in range(len(df)):
            if i == 0:
                file.write('WEBVTT')
                file.write('\n')

            else:
                file.write(str(i+1))
                file.write('\n')
                start = df.iloc[i]['start']
               
            
                file.write(f"{start.strip()}")
                
                stop = df.iloc[i]['end']
                
                
                file.write(' --> ')
                file.write(f"{stop}")
                file.write('\n')
                file.writelines(df.iloc[i]['translation'])
                if int(i) != len(df)-1:
                    file.write('\n\n')

    print("WEBVTT DONE") 

    with open('subtitles.srt','w', encoding="utf-8") as file:
        print("Starting SRT-file creation")
    
        for i in range(len(df)):
            file.write(str(i+1))
            file.write('\n')
            start = df.iloc[i]['start']
           
        
            file.write(f"{start.strip()}")
            
            stop = df.iloc[i]['end']
            
            
            file.write(' --> ')
            file.write(f"{stop}")
            file.write('\n')
            file.writelines(df.iloc[i]['translation'])
            if int(i) != len(df)-1:
                file.write('\n\n')
        
    print("SRT DONE") 
    subtitle_files = ['subtitles.vtt','subtitles.srt']

    return df, subtitle_files

usage = requests.get('https://api-free.deepl.com/v2/usage', headers=headers)
usage = json.loads(usage.text)
deepL_character_usage = str(usage['character_count'])
print("Character usage:", deepL_character_usage)

# Put your SRT file in the same folder as this script and change the name below
df = parse_srt("subs.srt")
print(df)

# Change the language to the language you want to translate to
translate_transcriptions(df, "English")