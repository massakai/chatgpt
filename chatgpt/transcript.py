import queue
import re
from typing import Generator

import pyaudio
from google.cloud import speech
from google.api_core.exceptions import OutOfRange


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


class Transcriptionist:
    def __init__(self, language_code: str, rate: int):
        self._client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=rate,
            language_code=language_code,
        )

        self._streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

    def transcribe(self, audio_data) -> Generator[str, None, None]:
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_data
        )

        while True:
            responses = self._client.streaming_recognize(self._streaming_config, requests)
            # FIXME 5分以上経過するとAPIの仕様でエラーになる
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                if not result.is_final:
                    continue

                yield result.alternatives[0].transcript


def main():
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms

    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    transcriptionist = Transcriptionist("ja-JP", RATE)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        transcript_generator = transcriptionist.transcribe(audio_generator)

        for transcript in transcript_generator:
            print(transcript)

            if re.search(r"\b(終了|停止|終わり)\b", transcript, re.I):
                print("Exiting..")
                break


if __name__ == "__main__":
    main()
