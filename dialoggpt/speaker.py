import tempfile
import types
from pathlib import Path
from typing import Generator

from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play


class Speaker:
    def __init__(self, voice: texttospeech.VoiceSelectionParams):
        self._client = texttospeech.TextToSpeechClient()
        self._voice = voice

    def create_speech_file(self, text: str, audio_config: texttospeech.AudioConfig, output_path: Path):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        response = self._client.synthesize_speech(
            input=synthesis_input, voice=self._voice, audio_config=audio_config
        )

        with open(output_path, "wb") as out:
            out.write(response.audio_content)

    @staticmethod
    def play_file(path: Path, format: str):
        sound = AudioSegment.from_file(path, format=format)
        play(sound)

    def say(self, text_or_generator: str | Generator[str, None, None], audio_config: texttospeech.AudioConfig):
        if audio_config.audio_encoding == texttospeech.AudioEncoding.LINEAR16:
            audio_format = "wav"
        elif audio_config.audio_encoding == texttospeech.AudioEncoding.MP3:
            audio_format = "mp3"
        else:
            raise ValueError(f"Unsupported audio encoding: ${audio_config.audio_encoding}")

        if isinstance(text_or_generator, types.GeneratorType):
            for text in text_or_generator:
                self._say(text, audio_config, audio_format)
        else:
            text = text_or_generator
            self._say(text, audio_config, audio_format)

    def _say(self, text: str, audio_config: texttospeech.AudioConfig, audio_format: str):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        response = self._client.synthesize_speech(
            input=synthesis_input, voice=self._voice, audio_config=audio_config
        )

        with tempfile.TemporaryFile() as wf:
            wf.write(response.audio_content)

            wf.seek(0)

            sound = AudioSegment.from_file(wf, format=audio_format)
            play(sound)


def main():
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
    speaker = Speaker(voice)

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16)
    speaker.say("こんにちは、世界！", audio_config)


if __name__ == "__main__":
    main()
