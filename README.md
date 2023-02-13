# deepl-subtitles
Translate Subtitles with DeepL API

This code is 99% based on Rasmus Toivanen [@R4ZZ3](https://github.com/R4ZZ3) code from:

https://huggingface.co/spaces/RASMUS/Whisper-youtube-crosslingual-subtitles

So send all kudos and respect to him!

I've just stripped away the youtube and whisper part, and left only subtitles translation with DeepL - for the case when you already have .srt file and just want to translate it.

To run it you need Python, register on DeepL for the Developer API access to get the API key, and then edit the .py file:
1. Put your DeepL API key on the top
2. Put your .srt subtitles file name on the bottom
3. Choose a languate you want to translate TO on the bottom
