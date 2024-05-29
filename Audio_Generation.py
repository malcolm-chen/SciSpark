import json
from Text_Process import split_sentence
import openai
import os
from openai import OpenAI

client = OpenAI(
    api_key = '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'
)
# OpenAI.api_key = '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'

def audio_gen(text, path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input = text
    )
    response.stream_to_file(path)


def audio_story_gen(user, title, text, para, sec, isLibrary):
    if os.path.exists("./static/files/books/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"):
        return
    if isLibrary:
        path = "./static/files/books/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"
    else:
        path = "./static/files/" + user + "/" + title + "/audio/p" + str(para) + "sec" + str(sec) + ".mp3"
    if text != '':
        audio_gen(text, path)

def audio_conv_gen(user, title, text, para, sec, path):
    audio_gen(text, path)

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()

def save_sen_split(user, title, isLibrary):
    story_sen = []
    if isLibrary:
        story = load_json('./static/files/books/' + title + '/' + title + '.json')
    else:
        story = load_json('./static/files/' + user + '/' + title + '/' + title + '.json')
    for i, para in enumerate(story):
        para_list = []
        for section in para:
            if len(section) < 120:
                para_list.append(section)
            else:
                sentences = split_sentence(section)
                if len(sentences) == 1:
                    para_list.append(sentences[0])
                else:
                    current_section = []
                    for sen in sentences:
                        if sen.strip():
                            current_section.append(sen)
                        if len(current_section) >= 2 and len(current_section[-2]) + len(current_section[-1]) <= 120:
                            current_section[-2] += current_section[-1]
                            current_section.pop()
                        if len(current_section) >= 3 and len(current_section[-3]) + len(current_section[-2]) + len(current_section[-1]) <= 120:
                            current_section[-3] += current_section[-2] + current_section[-1]
                            current_section.pop()
                            current_section.pop()
                    para_list += current_section
        story_sen.append(para_list)
    if(isLibrary):
        save_json('./static/files/books/' + title + '/' + title + '_sentence_split.json', story_sen)
    else:
        save_json('./static/files/' + user + '/' + title + '/' + title + '_sentence_split.json', story_sen)

def story_audio(user, title, isLibrary):
    if isLibrary:
        story = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    else:
        story = load_json('./static/files/' + user + '/' + title + '/' + title + '_sentence_split.json')
    for i, para in enumerate(story):
        for j, sec in enumerate(para):
            audio_story_gen(user, title, sec, i, j, isLibrary)

# save_sen_split('user', "How to Catch the Wind", True)
# story_audio('user', "How to Catch the Wind", True)


def validate_text(title):
    text1 = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    text2 = load_json('./static/files/books/' + title + '/' + title + '.json')

    all_text1 = ''
    all_text2 = ''

    for i in text1:
        for j in i:
            all_text1 += j
    for i in text2:
        for j in i:
            all_text2 += j
    print(all_text1.replace(' ', '') == all_text2.replace(' ', ''))
