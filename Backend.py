from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import json
import base64
import os
import threading
from urllib.parse import unquote
from PIL import Image
from io import BytesIO
from GPT_process import knowledge_keyword_gen, conv_gen, chat_gen, save_knowledge, get_book_discipline
from Text_Process import split_sentence
from Keyword_Matching import keyword_matching

app = Flask(__name__, static_folder = './static')
app.secret_key = 'storytelling'

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

# Sample user data (replace with your actual user authentication mechanism)
users = [
    {'username': 'user1', 'password': 'pass1'},
    {'username': 'user2', 'password': 'pass2'},
    {'username': 'user3', 'password': 'pass3'},
    {'username': 'user4', 'password': 'pass4'},
    {'username': 'user5', 'password': 'pass5'},
    {'username': 'user6', 'password': 'pass6'},
    {'username': 'user7', 'password': 'pass7'},
    {'username': 'user8', 'password': 'pass8'},
    {'username': 'Emma', 'password': 'emma'},
]

'''
current_user = {
    'username': '',
    'password': ''
}
'''

LibraryBooks = [
    "the little snowplow",
    "newton and me",
    "sami's beach rescue",
    "why do sunflowers love the sun",
    "how to catch the wind"
]

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not os.path.isdir('./static/files/' + username):
        os.makedirs('./static/files/' + username)
    if not os.path.exists('./static/files/' + username + '/dashboardData.json'):
        stat = {
            "reading": "", 
            "bookStat": {},
            "scienceStat": {
                "Discipline": {}, 
                "subDisc": {}
            }, 
            "readingRecord": {
                "date":{
                    "year": "",
                    "month": "",
                    "day": ""
                },
                "todayBook": [],
                "totalBook":[],
                "todayRead": 0, "todayTime": 0, "totalRead": 0, "totalTime": 0
            }, 
            "weekTime": {"Sun": 0, "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0}, 
            "upload": []
        }
        save_json('./static/files/' + username + '/dashboardData.json', stat)
    session['username'] = username
    session['password'] = password
    # Check if the provided username and password are valid
    if any(user['username'] == username and user['password'] == password for user in users):
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/library')
def library():
    if 'username' in session:
        return render_template('library.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/bookDetail')
def bookDetail():
    if 'username' in session:
        return render_template('bookDetail.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/customize')
def customize():
    if 'username' in session:
        return render_template('customize.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/upload')
def upload():
    if 'username' in session:
        return render_template('upload.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/custBookDetail')
def custBookDetail():
    if 'username' in session:
        return render_template('custBookDetail.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/api/user', methods=['POST'])
def user():
    if 'username' in session:
        return jsonify({'username': session['username'], 'password': session['password']})

@app.route('/api/gen', methods=['POST'])
def generation1():
    data = request.json
    user = data.get('username')
    title = unquote(data.get('title'))
    print(title)
    isLibrary = True
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False
    print(title, isLibrary)
    gpt_gen = knowledge_keyword_gen(user, title, isLibrary)
    if not os.path.exists('./static/files/' + user + '/' + title):
        os.makedirs('./static/files/' + user + '/' + title)
    if not os.path.exists('./static/files/' + user + '/' + title + '/conversation'):
        os.makedirs('./static/files/' + user + '/' + title + '/conversation')
    if not os.path.exists('./static/files/' + user + '/' + title + '/progress'):
        os.makedirs('./static/files/' + user + '/' + title + '/progress') 
    if not os.path.exists('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json'):
        if isLibrary:
            save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', load_json('./static/files/books/' + title + '/' + title + '_knowledge_dict.json'))
        else:
            save_knowledge(user, title, isLibrary)
    knowledge_dict = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    dashboard_data = load_json('./static/files/' + user + '/dashboardData.json')
    
    dashboard_data['reading'] = title
    save_json('./static/files/' + user + '/dashboardData.json', dashboard_data)

    return jsonify({
        'generation': gpt_gen,
        'answerProgress': knowledge_dict
    })

@app.route('/api/conv', methods=['POST'])
def generation2():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    if title.lower() in LibraryBooks:
        isLibrary = True
    else:
        isLibrary = False
    return jsonify(conv_gen(id, title, user, isLibrary))

@app.route('/api/chat', methods=['POST'])
def generation3():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    response = data.get('response')
    answerProgress = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    answerProgress[id]['answer'] = True
    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', answerProgress)
    return jsonify(chat_gen(id, title, user, response))

@app.route('/api/continue', methods=['POST'])
def save_progress():
    data = request.json
    user = data.get('username')
    id = str(data.get('id'))
    title = unquote(data.get('title'))
    html = data.get('html')
    isUpdate = data.get('dash_stat_flag')
    isEnd = data.get('end_flag')
    save_json('./static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json', html)
    dash_stat = load_json('./static/files/' + user + '/dashboardData.json')
    knowledge_dict = load_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json')
    if knowledge_dict[id]['dash'] == False:
        knowledge_dict[id]['dash'] = True
        if title not in dash_stat["bookStat"]:
            if title.lower() in LibraryBooks:
                src = '../static/files/books/' + title + '/cover.jpg'
            else:
                src = '../static/files/' + user + '/' + title + 'cover.jpg'
            dash_stat["bookStat"][title] = {
                'coverSrc': src,
                'count': len(knowledge_dict),
                'records': {}
            }
        dash_stat["bookStat"][title]['records'][id] = {
            "concept": knowledge_dict[id]['keyword'],
            "knowledge": knowledge_dict[id]['knowledge'],
            "topic": knowledge_dict[id]['topic'],
            "progress": isEnd
        }
        if knowledge_dict[id]['discipline'] not in dash_stat["scienceStat"]['Discipline']:
            dash_stat["scienceStat"]['Discipline'][knowledge_dict[id]['discipline']] = 1
        else:
            dash_stat["scienceStat"]['Discipline'][knowledge_dict[id]['discipline']] += 1
        if knowledge_dict[id]['sub-disc'] not in dash_stat["scienceStat"]['subDisc']:
            dash_stat["scienceStat"]['subDisc'][knowledge_dict[id]['sub-disc']] = 1
        else:
            dash_stat["scienceStat"]['subDisc'][knowledge_dict[id]['sub-disc']] += 1
    else:
        dash_stat["bookStat"][title]['records'][id]['progress'] = isEnd
    
    save_json('./static/files/' + user + '/dashboardData.json', dash_stat)
    save_json('./static/files/' + user + '/' + title + '/' + title + '_knowledge_dict.json', knowledge_dict)
    return jsonify("success")

@app.route('/api/review', methods=['POST'])
def send_html():
    data = request.json
    user = data.get('username')
    id = data.get('id')
    title = unquote(data.get('title'))
    if os.path.exists('./static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json'):
        return jsonify(load_json('./static/files/' + user + '/' + title + '/progress/sec_' + str(id) + '.json'))
    else:
        return jsonify('knowledge not saved')

@app.route('/api/stat', methods=['POST'])
def send_stat():
    data = request.json
    user = data.get('username')
    return jsonify(load_json('./static/files/' + user + '/dashboardData.json'))

@app.route('/api/uploadHistory', methods=['POST'])
def upload_history():
    data = request.json
    user = data.get('username')
    return jsonify(load_json('./static/files/' + user + '/dashboardData.json')['upload'])

@app.route('/api/uploadCover', methods=['POST'])
def upload_cover():
    data = request.json
    user = data.get('username')
    cover = data.get('img')
    title = unquote(data.get('title'))

    _, encoded_data = cover.split(',', 1)
    image_data = base64.b64decode(encoded_data)

    image = Image.open(BytesIO(image_data))
    image = image.convert('RGB')

    if not os.path.isdir('./static/files/' + user + '/' + title):
        os.mkdir('./static/files/' + user + '/' + title)
    image.save('./static/files/' + user + '/' + title + '/cover.jpg')

    '''save_json('./static/files/' + user + '/dashboardData.json', load_json('./static/files/' + user + '/dashboardData.json')['upload'].append(
        {
            "title": title,
            "cover": './static/files/' + user + '/' + title + '/cover.jpg',
            "finished": False
        }
    ))'''
    return jsonify("success")

@app.route('/api/uploadPage', methods=['POST'])
def upload_page():
    data = request.json
    user = data.get('username')
    pages = data.get('pageData')
    title = unquote(data.get('title'))
    if not os.path.isdir('./static/files/' + user + '/' + title + '/conversation'):
        os.mkdir('./static/files/' + user + '/' + title + '/conversation')
    if not os.path.isdir('./static/files/' + user + '/' + title + '/progress'):
        os.mkdir('./static/files/' + user + '/' + title + '/progress')
    if not os.path.isdir('./static/files/' + user + '/' + title + '/audio'):
        os.mkdir('./static/files/' + user + '/' + title + '/audio')
    if not os.path.isdir('./static/files/' + user + '/' + title + '/pages'):
        os.mkdir('./static/files/' + user + '/' + title + '/pages')
    
    paragraphs = []
    sentences = []
    for i, page in enumerate(pages[1:]):
        para = page['text']
        sen = split_sentence(para)
        sentences.append(sen)
        paragraphs.append(para)
       
        _, encoded_data = page['img'].split(',', 1)
        image_data = base64.b64decode(encoded_data)

        image = Image.open(BytesIO(image_data))
        image = image.convert('RGB')
        image.save('./static/files/' + user + '/' + title + '/pages/page' + str(i + 1) + '.jpg')

    save_json('./static/files/' + user + '/' + title + '/' + title + '.json', paragraphs)
    save_json('./static/files/' + user + '/' + title + '/' + title + '_sentence_split.json', sentences)

    # 1. match knowledge
    gen_result = keyword_matching(user, title, False)
    
    # 2. calculate knowledge stat
    save_knowledge(user, title, False)
    disciplines = get_book_discipline(user, title, False)

    # 3. update dashboard data
    dashboard_data = load_json('./static/files/' + user + '/dashboardData.json')
    
    dashboard_data['upload'].append({
            "title": title,
            "cover": './static/files/' + user + '/' + title + '/cover.jpg',
            "tags": disciplines
        })
    save_json('./static/files/' + user + '/dashboardData.json', dashboard_data)

    return jsonify(disciplines)


@app.route('/api/timer', methods=['POST'])
def update_time():
    data = request.json
    print(data)
    user = data.get('username')
    duration = data.get('duration')
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    title = data.get('title')
    dashboard_stat = load_json('./static/files/' + user + '/dashboardData.json')
    new_day_flag = 0
    if year != dashboard_stat['readingRecord']['date']['year']:
        dashboard_stat['readingRecord']['date']['year'] = year
        new_day_flag = 1
    if month != dashboard_stat['readingRecord']['date']['month']:
        dashboard_stat['readingRecord']['date']['month'] = month
        new_day_flag = 1
    if day != dashboard_stat['readingRecord']['date']['day']:
        dashboard_stat['readingRecord']['date']['day'] = day
        new_day_flag = 1
    if new_day_flag == 0:
        dashboard_stat['readingRecord']['todayTime'] += duration
        if title not in dashboard_stat['readingRecord']['todayBook']:
            dashboard_stat['readingRecord']['todayBook'].append(title)
    elif new_day_flag == 1:
        dashboard_stat['readingRecord']['todayTime'] = int(duration)
        dashboard_stat['readingRecord']['todayBook'] = [title]
    dashboard_stat['readingRecord']['totalTime'] += int(duration)
    if title not in dashboard_stat['readingRecord']['totalBook']:
        dashboard_stat['readingRecord']['totalBook'].append(title)
    dashboard_stat['readingRecord']['todayRead'] = len(dashboard_stat['readingRecord']['todayBook'])
    dashboard_stat['readingRecord']['totalRead'] = len(dashboard_stat['readingRecord']['totalBook'])
    save_json('./static/files/' + user + '/dashboardData.json', dashboard_stat)
    return jsonify('success')

if __name__ == '__main__':    
    app.run(debug=True)
