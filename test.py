from pathlib import Path
import openai

openai.api_key = "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"

speech_file_path = Path(__file__).parent / "speech.mp3"
response = openai.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)