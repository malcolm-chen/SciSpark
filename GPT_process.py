import openai
import json
import re
import os
from retry import retry
from sentence_transformers import SentenceTransformer, util
from Text_Process import split_para
from Keyword_Matching import keyword_matching
from Audio_Generation import audio_gen
from openai import OpenAI

client = OpenAI(
    api_key = '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'
)
# OpenAI.api_key = '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'

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
    response = client.chat.completions.create(
        model= MODEL,
        messages=[{"role": "user", "content": each_input}],
        max_tokens=128,
        stop=stop,
    )
    return (response.choices[0].message.content).lower()

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
def conversation(message, stop=None):
    response = client.chat.completions.create(
        model = MODEL,
        messages = message,
        max_tokens = 256,
        stop = stop,
    )
    return (response.choices[0].message.content).lower()

def prompting_kg_matching(story):
  Instruction1 = f"""\
    I need you to match a story section with a piece of scientific knowledge.
    I will provide you with a short section of a story delimited by triple quotes, and a list of scientific knowledge.
    Please follow these steps:
    1. Read through the list of scientific knowledge provided.
    2. Read through the story section.
    3. Rank the knowledge list according to each knowledge's relevancy with the story narrative.
    If the story narrative, or a word or phrase in the story text is closely connected with a piece of knowledge, the piece of knowledge should rank higher.
    4. Return the most relevant piece of knowledge from the Scientific Knowledge List.

    [Scientific Knowledge List]:
    1. Pushes and pulls can have different strengths and directions.
    2. Pushing or pulling on an object can change the speed or direction of its motion and can start or stop it.
    3. When objects touch or collide, they push on one another and can change motion.
    4. A bigger push or pull makes things speed up or slow down more quickly.
    5. A situation that people want to change or create can be approached as a problem to be solved through engineering. Such problems may have many acceptable solutions.
    6. Sunlight warms Earth’s surface.
    7. All animals need food in order to live and grow. They obtain their food from plants or from other animals. Plants need water and light to live and grow.
    8. Weather is the combination of sunlight, wind, snow or rain, and temperature in a particular region at a particular time. People measure these conditions to describe and record the weather and to notice patterns over time.
    9. Plants and animals can change their environment.
    10. Things that people do to live comfortably can affect the world around them. But they can make choices that reduce their impacts on the land, water, air, and other living things.
    11. Living things need water, air, and resources from the land, and they live in places that have the things they need. Humans use natural resources for everything they do.
    12. Some kinds of severe weather are more likely than others in a given region. Weather scientists forecast severe weather so that the communities can prepare for and respond to these events.
    13. Asking questions, making observations, and gathering information are helpful in thinking about problems.
    14. Designs can be conveyed through sketches, drawings, or physical models. These representations are useful in communicating ideas for a problem’s solutions to other people.
    15. Sound can make matter vibrate, and vibrating matter can make sound.
    16. Objects can be seen if light is available to illuminate them or if they give off their own light.
    17. Some materials allow light to pass through them, others allow only some light through and others block all the light and create a dark shadow on any surface beyond them, where the light cannot reach. Mirrors can be used to redirect a light beam. (Boundary: The idea that light travels from place to place is developed through experiences with light sources, mirrors, and shadows, but no attempt is made to discuss the speed of light.)
    18. People also use a variety of devices to communicate (send and receive information) over long distances.
    19. All organisms have external parts. Different animals use their body parts in different ways to see, hear, grasp objects, protect themselves, move from place to place, and seek, find, and take in food, water and air. Plants also have different parts (roots, stems, leaves, flowers, fruits) that help them survive and grow.
    20. Adult plants and animals can have young. In many kinds of animals, parents and the offspring themselves engage in behaviors that help the offspring to survive.
    21. Animals have body parts that capture and convey different kinds of information needed for growth and survival. Animals respond to these inputs with behaviors that help them survive. Plants also respond to some external inputs.
    22. Young animals are very much, but not exactly like, their parents. Plants also are very much, but not exactly, like their parents.
    23. Individuals of the same kind of plant or animal are recognizable as similar but can also vary in many ways.
    24. Patterns of the motion of the sun, moon, and stars in the sky can be observed, described, and predicted.
    25. Seasonal patterns of sunrise and sunset can be observed, described, and predicted.
    26. Different kinds of matter exist and many of them can be either solid or liquid, depending on temperature. Matter can be described and classified by its observable properties.
    27. Different properties are suited to different purposes.
    28. A great variety of objects can be built up from a small set of pieces.
    29. Heating or cooling a substance may cause changes that can be observed. Sometimes these changes are reversible, and sometimes they are not.
    30. Plants depend on water and light to grow.
    31. Plants depend on animals for pollination or to move their seeds around.
    32. There are many different kinds of living things in any area, and they exist in different places on land and in water.
    33. Some events happen very quickly; others occur very slowly, over a time period much longer than one can observe.
    34. Wind and water can change the shape of the land.
    35. Maps show where things are located. One can map the shapes and kinds of land and water in any area.
    36. Water is found in the ocean, rivers, lakes, and ponds. Water exists as solid ice and in liquid form.
    37. Because there is always more than one possible solution to a problem, it is useful to compare and test designs.
    38. A situation that people want to change or create can be approached as a problem to be solved through engineering.
    39. Before beginning to design a solution, it is important to clearly understand the problem.

    For example,
    <Story narrative>:
    The little snowplow braced himself and PULLED.

    <Response>:
    Pushes and pulls can have different strengths and directions.

    <Story narrative>:
    '''
    {story}
    '''
    <Response>:
    """
  return Instruction1

def prompting_kword(story, knowledge):
  Instruction2 = f"""\
    Please identify a key word from a short story section.
    You'll be provided with a short story section enclosed in triple quotes and a piece of scientific knowledge.

    Here are the steps to follow:
    1. Read the story section provided.
    2. Review the scientific knowledge provided.
    3. From all the words in the story text, identify a word from the story text that is semantically related to the provided scientific knowledge.
    The chosen word should be suitable for educating children aged 3 to 6 about the related knowledge.
    4. Check if the identified word is from the story text. If not, repeat step 3.
    5. For the identified word, generate a short explanation of the word in one sentence. The explanation should be friendly to preschoolers aged 3 to 6. The explanation should follow this format: [key word] means [explanation]
    6. Return the identified word and explanation. If there is no word that meets the criteria, respond with 'not identified.'

    For example,
    <Story Text>:
    '''The little snowplow braced himself and PULLED.'''

    <Knowledge>:
    Pushes and pulls can have different strengths and directions.
    
    <Response>:
    PULLED
    Pull means to use your hands or strength to bring something closer to you.
    
    <Story Text>:
    '''
    {story}
    '''

    <Knowledge>: {knowledge}

    <Response>:
    """
  return Instruction2

def prompt_conv(title, story, keyword, knowledge, statements):
    Instruction4 = f"""\
Now you are a conversational agent interacting with a child aged 3-6, like a teacher, by asking questions and providing responsive feedback to the child. 
You and the child will take turns having a conversation, with each turn generating one question.
During the conversation, ask a series of questions n child-friendly language.
The total question number should be no more than five.
If the child demonstrate great understanding of the knowledge, you should ask less questions.

There will be a concept word in the story text, and the concept word is associated with a piece of external science knowledge.
The generated questions should be based on the concept word in the story text and associated with external science knowledge.
The generated questions should contain the associated external science knowledge to enrich the child's science knowledge.
The generated question series should follow the Science and Engineering Practices of preschoolers.
The generated question series should be based on the story text, concept word, knowledge, and practices I provide.

When the child responds, provide your response to them.
Your response should include: a judgment of whether the child's answer is correct or incorrect, a friendly, encouraging feedback based on the child's answer, an explanation of the answer to the previous question, and finally transit to the next question if the conversation does not end.
If the child’s answer is incorrect, use scaffold to inspire their thinking.
Keep your response concise, each part should preferably not exceed 100 characters.

For the first question you generate which the conversation starts, please follow this json format:
    {{
        "greeting": [Greet the child and starts the conversation.],
        "question": [The first question.]
    }}

The format of your response should follow this json format:
    {{
        "judgement": [Judgement of the child's answer: correct/incorrect/partially correct.],
        "feedback": [Your feedback to the child's answer, it should be encouraging regardless of the correctness of the child's answer, such as 'Good job!', 'You are absolutely right', 'That's ok!', etc.],
        "explanation": [An explanation of the previous question with the related knowledge according to the child's answer],
        "transition": [A transition to a new question or closing the conversation, such as 'Here's a new question:', 'Let's move on reading!', etc.],
        "question": [The new question.]
        "end": [true/false]
    }}
If the conversation comes to an end and you are providing the last feedback without asking a new question to the child, leave the 'question' part empty and the 'end' part should be 'true'.
Please note that when the texts of 'feedback', 'explanation', 'transition' and 'question' are combined, it should become a smooth reply.

<Story Title>: {title}
    <Story Text>:
    '''
    {story}
    '''

    <Concept Word>:{keyword}
    <Knowledge>:{knowledge}
    <Science and Engineering Practices>:{statements}

    Now, start the conversation:
    """

    Instruction3 = f"""\
    Now you are a conversational agent interacting with a preschooler. You and the child will take turns having a conversation, with each turn generating a question. 
    In total, the conversation consists of a series of questions (no more than five questions) in child-friendly language.

    There will be a concept word in the story text, and the concept word is associated with the external science knowledge.
    The feedback contains your response to the child's answer and a new question.
    The generated questions should be based on the concept word in the story text and associated with external science knowledge.
    The generated questions should contain the associated external science knowledge to enrich the preschooler's science knowledge.
    The generated questions in the series should follow the Science and Engineering Practices of preschoolers.
    The generated question series should be based on the story text, concept word, knowledge, and practices I provide.  

    For the first question you generate which the conversation starts, please follow this json format:
    {{
        "greeting": [Greet the child and starts the conversation.],
        "question": [The first question.]
    }}

    After generating one question, do not automatically generate the child's response, because I will provide the child's response. 
    When the child responds, provide your response to them.
    Your response should consist a judgment of whether the child's answer is correct or incorrect, then give a friendly feedback based on the child's answer, an explanation of the answer to the previous question, and finally transit to the next question if the conversation does not end.
    The format of your response should follow this json format:
    {{ 
        "judgement": [Judgement of the child's answer: correct/incorrect/partially correct.],
        "feedback": [Your feedback to the child's answer, it should be encouraging regardless of the correctness of the child's answer, such as 'Good job!', 'You are absolutely right', 'That's ok!', etc.],
        "explanation": [An explanation of the previous question with the related knowledge according to the child's answer],
        "transition": [A transition to a new question or closing the conversation, such as 'Here's a new question:', 'Let's move on reading!', etc.],
        "question": [The new question.]
        "end": [true/false]
    }}    
    
    If the conversation comes to an end and you are providing the last feedback without asking a new question to the child, leave the 'question' part empty and the 'end' part should be 'true'.
    Please note that when the texts of 'feedback', 'explanation', 'transition' and 'question' are combined, it should become a smooth reply.
    Keep your response concise, each part should preferably not exceed 100 characters. 

    <Story Title>: {title}
    <Story Text>:
    '''
    {story}
    '''

    <Concept Word>:{keyword}
    <Knowledge>:{knowledge}
    <Science and Engineering Practices>:{statements}

    Now, start the conversation:
    """
    return Instruction4

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
statements_dict = load_json("./NGSS_statements.json")

def is_format(input_string):
    pattern = re.compile(r'^\d+\.\s.*$')
    return bool(pattern.match(input_string))

def evaluate_knowledge(input):
    if is_format(input):
        input = input.split('. ')[1]
    if input.lower() in knowledge_list:
        return input.lower()
    else:
        return 'not matched'

def capitalize_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    capitalized_sentences = [sentence.capitalize() for sentence in sentences]
    
    capitalized_text = ' '.join(capitalized_sentences)
    
    return capitalized_text

def evaluate_kword(section, input):
    if input.lower() in section.lower():
        return input.lower()
    else:
        return 'not identified'

def get_similarity(word, knowledge):
  sim_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
  #Compute embedding for both lists
  embedding_1= sim_model.encode(word, convert_to_tensor=True)
  embedding_2 = sim_model.encode(knowledge, convert_to_tensor=True)
  return util.pytorch_cos_sim(embedding_1, embedding_2)[0].numpy()[0]

def knowledge_matching(input):
    output = {}
    for i, section in enumerate(input):
        each_output = evaluate(prompting_kg_matching(section)).split('\n')[0]
        knowledge = evaluate_knowledge(each_output)
        if i not in output:
            output[i] = {
                'section': section,
                'knowledge': knowledge,
                'keyword': '',
                'use': 0,
                'explanation': ''
            }
    return output

def keyword_identifying(title, input):
    all_knowldge = {}
    sen_split = load_json('./static/files/books/' + title + '/' + title + '_sentence_split.json')
    id = 0
    for key, value in input.items():
        section = value['section']
        knowledge = value['knowledge']
        each_output = evaluate(prompting_kword(section, knowledge)).split('\n')
        candidate_word = each_output[0]
        exp = each_output[1]
        key_word = evaluate_kword(section, candidate_word)
        sim = get_similarity(key_word, knowledge)
        if (knowledge not in all_knowldge) or (knowledge in all_knowldge and all_knowldge[knowledge]['sim'] < sim):
          if key_word != 'not identified':
            all_knowldge[knowledge] = {
                'sim': sim,
                'section': id,
                'keyword': key_word
            }
        input[id]['section'] = sen_split[id]
        input[id]['explanation'] = exp
        id += 1

    for kg, value in all_knowldge.items():
        input[value['section']]['keyword'] = value['keyword']
        keyword_list = value['keyword'].split(' ')
        split_word = []
        match_flag = 0
        for sen in input[value['section']]['section']:
            split_sen = split_para(sen)
            for i in range(len(split_sen) - len(keyword_list) + 1):
                if all(split_sen[i + j]['word'].lower() == keyword_list[j] for j in range(len(keyword_list))) and match_flag == 0:
                    for j in range(len(keyword_list)):
                        split_sen[i + j]['keyword'] = 1
                    match_flag = 1
                    input[value['section']]['use'] = 1
            split_word.append(split_sen)         
        input[value['section']]['section'] = split_word
       
    return input

# Deprecated
'''def knowledge_keyword_gen(user, title, isLibrary):
    if os.path.exists('./static/files/books/' + title + '/' + title + ' Gen_test.json'):
        identified_words = load_json('./static/files/books/' + title + '/' + title + ' Gen_test.json')
    else:
      story_content = load_json('./static/files/books/' + title + '/' + title + '.json')
      knowledge_match = knowledge_matching(story_content)
      identified_words = keyword_identifying(title, knowledge_match)
      save_json('./static/files/books/' + title + '/' + title + ' Gen.json', identified_words)  
    return identified_words'''

def knowledge_keyword_gen(user, title, isLibrary):
    if isLibrary:
        return load_json('./static/files/books/' + title + '/' + title + ' Gen.json')

    if os.path.exists('./static/files/' + user + '/' + title + '/' + title + ' Gen.json'):
        return load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')
    else:
      knowledge_gen = keyword_matching(user, title, isLibrary)
      save_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json', knowledge_gen)  
    return knowledge_gen

def conv_gen(id, title, user, isLibrary):
    if os.path.exists("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json"):
        return json.loads(load_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json")[1]['content'])
    if isLibrary:
        sec_dict = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/books/' + title + '/' + title + '.json')[int(id)]
    else:
        sec_dict = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')[str(id)]
        section = load_json('./static/files/' + user + '/' + title + '/' + title + '.json')[int(id)]
    chatHistory = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')

    keyword = sec_dict['keyword']
    knowledge = sec_dict['knowledge'].lower()
    linked_statements = knowledge_dict[knowledge]["Statements"]
    statements = ''
    for sts_id in linked_statements:
        char = sts_id.split('-')
        if statements != '':
            statements += '\n'
        statements += statements_dict[char[0]][char[1]][char[2]][char[3]]
    input = prompt_conv(title, section, keyword, knowledge, statements)
    first_conv = evaluate(input)
    start_index = first_conv.find('{')
    end_index = first_conv.rfind('}') + 1
    first_conv = first_conv[start_index:end_index]
    first_conv_dict = json.loads(first_conv)
    first_conv_dict['greeting'] = capitalize_sentences(first_conv_dict['greeting'])
    first_conv_dict['question'] = capitalize_sentences(first_conv_dict['question'])
    messages = [
        {"role": "system", "content": input},
        {"role": "assistant", "content": first_conv}
    ]

    chatHistory[id]['conversation'].append({
        'question': first_conv_dict['question'],
        'answer': '',
        'correct': '',
        'explanation': ''
    })

    if not os.path.exists("./static/files/" + user + "/" + title + "/conv_audio"):
        os.makedirs("./static/files/" + user + "/" + title + "/conv_audio")
    audio_gen(first_conv_dict['greeting'] + first_conv_dict['question'], "./static/files/" + user + "/" + title + "/conv_audio/sec_" + str(id) + "_q_1.mp3")

    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', chatHistory)
    save_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)
    return first_conv_dict
    

# conv_gen("2", 'The Little Snowplow', 'user')

def chat_gen(id, title, user, response):
    messages = load_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json")
    chatHistory = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    messages.append(
        {"role": "user", "content": response}
    )
    feedback = conversation(messages)
    start_index = feedback.find('{')
    end_index = feedback.rfind('}') + 1
    feedback = feedback[start_index:end_index]
    feedback_dict = json.loads(feedback)
    
    feedback_dict['feedback'] = capitalize_sentences(feedback_dict['feedback'])
    feedback_dict['explanation'] = capitalize_sentences(feedback_dict['explanation'])
    feedback_dict['transition'] = capitalize_sentences(feedback_dict['transition'])
    feedback_dict['question'] = capitalize_sentences(feedback_dict['question'])

    messages.append(
        {"role": "assistant", "content": feedback}
    )
    save_json("./static/files/" + user + "/" + title + "/conversation/get_conv_sec_" + id + ".json", messages)

    chatHistory[id]['conversation'][-1]['answer'] = response
    chatHistory[id]['conversation'][-1]['correct'] = feedback_dict['judgement']
    chatHistory[id]['conversation'][-1]['explanation'] = feedback_dict['explanation']

    chatHistory[id]['conversation'].append({
        'question': feedback_dict['question'],
        'answer': '',
        'correct': '',
        'explanation': ''
    })
    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', chatHistory)

    feedback_dict['q_id'] = len(chatHistory[id]['conversation'])
    print(feedback_dict)

    audio_gen(feedback_dict['feedback'] + feedback_dict['explanation'] + feedback_dict['transition'] + feedback_dict['question'], "./static/files/" + user + "/" + title + "/conv_audio/sec_" + str(id) + "_q_" + str(len(chatHistory[id]['conversation'])) + ".mp3")

    return {
        "response_dict": feedback_dict,
        "QA_pair": chatHistory[id]['conversation'][-2]
    }

def save_knowledge(user, title, isLibrary):
    if (isLibrary):
        gen_data = load_json('./static/files/books/' + title + '/' + title + ' Gen.json')
    else:
        gen_data = load_json('./static/files/' + user + '/' + title + '/' + title + ' Gen.json')
    gpt_data = {}
    for key, value in gen_data.items():
        if value['use'] == 1:
            gpt_data[key] = {
                'keyword': value['keyword'],
                'explanation': value['explanation'],
                'knowledge': value['knowledge'],
                'discipline': knowledge_dict[value['knowledge']]['Discipline'],
                'sub-disc': knowledge_dict[value['knowledge']]['SubDiscipline'],
                'topic': knowledge_dict[value['knowledge']]['Topic'],
                'answer': False,
                'dash': False,
                'conversation': []
            }
    if (isLibrary):
        save_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json', gpt_data)
    else:
        save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', gpt_data)

def get_book_discipline(user, title, isLibrary):
    if (isLibrary):
        gpt_data = load_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json')
    else:
        gpt_data = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    disc = {}
    sub_dis = {}
    for key, value in gpt_data.items():
        dis = knowledge_dict[value['knowledge']]['Discipline']
        sub = knowledge_dict[value['knowledge']]['SubDiscipline']
        if dis not in disc:
            disc[dis] = 1
        else:
            disc[dis] += 1
        if sub not in sub_dis:
            sub_dis[sub] = 1
        else:
            sub_dis[sub] += 1
    disc = sorted(disc.items(), key=lambda x:x[1])
    sub_dis = sorted(sub_dis.items(), key=lambda x:x[1])
    topic = {
        "discipline": disc,
        "sub-discipline": sub_dis
    }
    print(topic)
    return topic



# save_knowledge('user', "The Little Snowplow", True)
# get_book_discipline('user', "Why Do Sunflowers Love the Sun?", True)
# knowledge_keyword_gen('user', "Why Do Sunflowers Love the Sun", True)

def update_lib():
    lib_book = [
        "How to Catch the Wind",
        "Newton And Me",
        "The Little Snowplow",
        "Sami's Beach Rescue",
        "Why Do Sunflowers Love the Sun"
    ]
    for b in lib_book:
        save_knowledge('user', b, True)
        knowledge_keyword_gen('user', b, True)

# update_lib()
