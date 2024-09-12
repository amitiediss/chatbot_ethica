import openai
import boto3
import pyaudio
import whisper
import os

# Load environment variables (assuming you're using .env)
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up AWS Polly client using environment variables for credentials
polly = boto3.client('polly', 
                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                     region_name='us-east-1')  # Specify your AWS region

# Initialize Whisper model
model = whisper.load_model("base")

# PyAudio setup
audio = pyaudio.PyAudio()

# Function to record audio
def record_audio(duration=5):
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    print("Recording...")
    frames = []
    for i in range(0, int(44100 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    return b''.join(frames)

# Function to transcribe audio using Whisper
def transcribe_audio(audio_data):
    with open("temp.wav", "wb") as f:
        f.write(audio_data)
    result = model.transcribe("temp.wav")
    return result['text']

# Function to get ChatGPT response
def get_chatgpt_response(prompt):
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # Using the latest model
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Function to convert text to speech using AWS Polly
def speak_text(text):
    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")
    with open("output.mp3", "wb") as f:
        f.write(response['AudioStream'].read())
    # Play the audio file (using your preferred method)
    os.system("start output.mp3")  # This works for Windows. Use 'afplay' for macOS or 'mpg321' for Linux.

# Main chatbot loop
def chatbot_loop():
    while True:
        print("Press Enter to record your message...")
        input()  # Wait for the user to press Enter
        audio_data = record_audio()  # Record audio
        transcription = transcribe_audio(audio_data)  # Transcribe the audio
        print(f"Transcription: {transcription}")
        
        response = get_chatgpt_response(transcription)  # Get response from ChatGPT
        print(f"ChatGPT Response: {response}")
        
        speak_text(response)  # Speak the response with AWS Polly

if __name__ == "__main__":
    chatbot_loop()  # Start the chatbot loop
