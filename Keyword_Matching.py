import json, openai
from retry import retry
from sentence_transformers import SentenceTransformer, util
from Text_Process import split_para, split_sentence
import os
from dotenv import load_dotenv
    
load_dotenv()

openai.api_key =  os.environ.get("OPENAI_API_KEY")

MODEL = "gpt-4"

@retry(
    (
        openai.APIError,
        openai.RateLimitError,
        openai.Timeout,
        # openai.ServiceUnavailableError,
        openai.APIConnectionError,
    ),
    tries=50,
    delay=2,
    backoff=2,
    max_delay=20,
)
def evaluate(each_input, stop=None):
    response = openai.chat.completions.create(
        model= MODEL,
        messages=[{"role": "user", "content": each_input}],
        max_tokens=128,
        stop=stop,
    )
    return (response.choices[0].message.content).lower()


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

knowledge_dict = load_json("./NGSS_DCI.json")
knowledge_list = [kg for kg in knowledge_dict.keys()]
sim_dict = load_json('./Similarity_Dict.json')
sim_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def prompting_explanation(word, knowledge):
  Instruction = f"""\
    I need you to provide a short sentence of explanation of a concept for prschoolers aged 3 to 8. 
    I will provide you the concept and the scientific knowldge it related to.
    The explanation should be clear, short and easy to understand.

    For example,
    <Concept>: pull

    <Knowledge>: Pushes and pulls can have different strengths and directions.
    
    <Response>: Pull means to use your hands or strength to bring something closer to you.
    
    <Concept>: {word}

    <Knowledge>: {knowledge}

    <Response>:
    """
  return Instruction

def get_similarity(word, knowledge):
  #Compute embedding for both lists
  embedding_1= sim_model.encode(word, convert_to_tensor=True)
  embedding_2 = sim_model.encode(knowledge, convert_to_tensor=True)
  return util.pytorch_cos_sim(embedding_1, embedding_2)[0].numpy()[0]

def calculate_similarity(word):
    if word.lower() in sim_dict:
        return float(sim_dict[word.lower()]['similarity']), sim_dict[word.lower()]['knowledge']
    else:
        max_sim = -1
        machted_kg = ''
        for knowledge in knowledge_dict:
            similarity = get_similarity(word, knowledge)
            if similarity > max_sim:
                max_sim = similarity
                machted_kg = knowledge
        sim_dict[str(word.lower())] = {
            "similarity": str(max_sim),
            "knowledge": machted_kg
        }
        return max_sim, machted_kg

def knowledge_matching(word):
    sim = 0
    kg = ''
    for knowledge in knowledge_list:
        cur_sim = get_similarity(word, knowledge)
        if cur_sim > sim:
            sim = cur_sim
            kg = knowledge
    return sim, kg

def keyword_matching(user, title, isLibrary):
    if (isLibrary):
        story_content = load_json('./static/files/books/' + title + '/' + title + '.json')
        sen_split = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    else:
        story_content = load_json('./static/files/' + user + '/' + title + '/' + title + '.json')
        sen_split = load_json('./static/files/' + user + '/' + title + '/' + title + '_sentence_split.json')
    
    all_knowldge = {}
    gen_result = {}
    for i, para in enumerate(story_content):
        text_tokens = []
        best_sim = 0.27
        keyword = ''
        best_kg = ''
        for sen in sen_split[i]:
            split_sen = split_para(sen)
            for token in split_sen:
                if token['stopword']:
                    continue
                similarity, knowledge = calculate_similarity(token['word'].lower())
                if similarity > best_sim:
                    best_sim = similarity
                    best_kg = knowledge
                    keyword = token['word']
            text_tokens.append(split_sen)
        # print(keyword, best_kg, best_sim)
        if (best_kg != '') and (best_kg not in all_knowldge) or (best_kg in all_knowldge and best_sim > all_knowldge[best_kg]['sim']):
            all_knowldge[best_kg] = {
                'sim': best_sim,
                'sec_id': i,
                'keyword': keyword
            }
        gen_result[i] = {
            'section': text_tokens,
            'section_text': sen_split[i],
            'knowledge': '',
            'keyword': '',
            'use': 0,
            'explanation': ''
        }

    for kg, value in all_knowldge.items():
        gen_result[value['sec_id']]['keyword'] = value['keyword']
        gen_result[value['sec_id']]['knowledge'] = kg
        gen_result[value['sec_id']]['use'] = 1
        gen_result[value['sec_id']]['explanation'] = evaluate(prompting_explanation(value['keyword'], kg))
        match_flag = False
        for i, sen in enumerate(gen_result[value['sec_id']]['section']):
            if (match_flag):
                break
            for j, token in enumerate(sen):
                if token['word'] == value['keyword']:
                    gen_result[value['sec_id']]['section'][i][j]['keyword'] = 1
                    match_flag = True
                    break
    
    '''for key, value in gen_result.items():
        if value['use'] == 0:
            gen_result[key]['section'] = story_content[int(key)]'''

    save_json('./Similarity_Dict.json', sim_dict)
    if (isLibrary):
        save_json('./static/files/books/' + title + '/' + title + ' Gen.json', gen_result)  
    else:
        save_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json', gen_result)  
    return gen_result

def save_split_sentence(title):
    story_content = load_json('./static/files/books/' + title + '/' + title + '.json')
    sentences = []
    for para in story_content:
        sen = split_sentence(para)
        sentences.append(sen)
    save_json('./static/files/books/' + title + '/' + title + '_sentence_split.json', sentences)

# save_split_sentence("The Little Snowplow")
# keyword_matching('user', "Why Do Sunflowers Love the Sun", True)
