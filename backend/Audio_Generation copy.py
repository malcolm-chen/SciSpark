import json
from Text_Process import split_sentence
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import sys

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="default")
polly = session.client("polly")

def audio_gen(title, text, para, sen):
    try:
    # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = "./static/files/books/" + title + "/audio/p" + str(para) + "s" + str(sen) + ".mp3"

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def story_audio(title):
    story = load_json('./static/files/books/' + title + '/' + title + '.json')
    for i, para in enumerate(story):
        sen = split_sentence(para)
        for j, s in enumerate(sen):
            audio_gen(title, s, i, j)

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()

def save_sen_split(title):
    story_sen = []
    story = load_json('./static/files/books/' + title + '/' + title + '.json')
    for i, para in enumerate(story):
        sen = split_sentence(para)
        story_sen.append(sen)
    save_json('./static/files/books/' + title + '/' + title + '_sentence_split.json', story_sen)

# save_sen_split('The Little Snowplow')
story_audio("Why Do Sunflowers Love the Sun?")
