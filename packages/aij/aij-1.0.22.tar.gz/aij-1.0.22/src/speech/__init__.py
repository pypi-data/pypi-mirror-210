import os
from pathlib import Path
import openai

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep


def main():
    """This method extract the audio from a video
    The transcriptions API takes as input the audio file you want to transcribe and the desired output file format 
    for the transcription of the audio. They currently support multiple input and output file formats.
    """

    # find all the videos in the data directory using the glob module
    videos = [str(video) for video in Path('data').glob('*.mp4')]

    # transcribe each video
    for video in videos:
        #  ffmpeg data conversion from mp4 to wav
        audio = video.replace('.mp4', '.wav')
        if not os.path.exists(audio):
            os.system(
                f"ffmpeg -i {video} -vn -acodec pcm_s16le -ar 16000 -ac 1 {video.replace('.mp4', '.wav')}")

        # Transcriptions
        # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
        # The transcriptions API takes as input the audio file you want to transcribe and the desired output file format for
        # the transcription of the audio. We currently support multiple input and output file formats.
        audio_file = open(video.replace('.mp4', '.wav'), "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

        print(
            transcript
        )

        # Translations
        # The translations API takes as input the audio file in any of the supported languages and transcribes,
        # if necessary, the audio into english. This differs from our /Transcriptions endpoint since
        # the output is not in the original input language and is instead translated to english text.
        
        transcript = openai.Audio.translate("whisper-1", audio_file)

        print(
            transcript
        )



if __name__ == '__main__':
    main()
