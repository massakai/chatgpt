"""ChatGPTと音声でやりとりするプログラム"""
import re

from google.cloud import texttospeech

from chatgpt.chat import Chat
from chatgpt.speaker import Speaker
from chatgpt.transcript import Transcriptionist, MicrophoneStream

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


def main():
    language_code = "ja-JP"
    transcriptionist = Transcriptionist(language_code, RATE)

    chat = Chat()

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    speaker = Speaker(voice)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    print("user: ", end="", flush=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        transcript_generator = transcriptionist.transcribe(audio_generator)

        for transcript in transcript_generator:
            print(transcript)

            if re.search(r"\b(終了|停止|終わり)\b", transcript, re.I):
                print("Exiting..")
                break

            print(f"assistant: ", end="", flush=True)
            reply = chat.send(transcript)
            print(reply)
            speaker.say(reply, audio_config)
            print("user: ", end="", flush=True)


if __name__ == "__main__":
    main()
