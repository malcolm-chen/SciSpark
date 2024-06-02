from pathlib import Path
import openai


from dotenv import load_dotenv
    
load_dotenv()
    
openai.api_key =  = os.environ.get("OPENAI_API_KEY")




speech_file_path = Path(__file__).parent / "speech.mp3"
response = openai.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)