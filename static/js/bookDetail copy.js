const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

const bookTitle = urlParams.get('title');
document.getElementById('BookTitle').innerHTML = bookTitle;


let currentImageIndex = 1;
let currentSentence = 0;
var totalPages;
var genData;
var curUser = '';
var sections = [];
var gptData = {};
var isDataGen = false;
var isAudioPlaying = false;
var isKeyWord = false;
var synthesis = window.speechSynthesis;

function getUser(){
    fetch('/api/user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        curUser = data.username;
        document.getElementById('Profile').innerHTML = data.username;
        fetchGenData();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function fetchGenData(){
    console.log({ 
        username: curUser,
        title: bookTitle 
    });
    fetch('/api/gen', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: curUser,
            title: bookTitle 
        }),
    })
    .then(response => response.json())
    .then(data => {
        genData = data.generation;
        gptData = data.answerProgress;
        totalPages = Object.keys(genData).length;
        isDataGen = true;
        if (isDataGen){
            textAudio();
            showImage();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function render_caption(textData){
    let paragraph = document.createElement("div");
    const caption = document.getElementById('Caption');
    paragraph.className = "paragraph";
    paragraph.innerHTML = "";
    if(typeof textData === 'string'){
        paragraph.innerHTML += textData;
    }
    else{
        textData.forEach(function (e) {
            if (e.keyword == 0){
                paragraph.innerHTML += `<div id="s${e.id}" class="sentence">${e.word}</div>`
            }
            else{
                paragraph.innerHTML += `<div id="s${e.id}" class="sentence_key" >${e.word}</div>`
                isKeyWord = true;
            }
        })
        if (isKeyWord){
            console.log(gptData[(currentImageIndex-1).toString()]);
            if(!gptData[(currentImageIndex-1).toString()].answer){
                genConv();
            }
            else{
                review();
            }
        }
    }
    if(caption.childNodes.length == 0){
        caption.appendChild(paragraph);
    }
    else{
        caption.replaceChild(paragraph, caption.childNodes[0]);
    }
}

function genConv(){
    const container = document.querySelector('.container');
    let knowledge = document.createElement("div");
    knowledge.className = 'Knowledge';
    knowledge.innerHTML = `<div class="keyWord">
                            <div id="bubble">
                                <p1 id="Word">${gptData[(currentImageIndex-1).toString()].keyword}</p1>
                                </br>
                                <p2 id="Exp">${gptData[(currentImageIndex-1).toString()].explanation}</p2>
                            </div>
                            <div class="tail"></div>
                         </div>`;
    if(container.children.length == 1){
        container.appendChild(knowledge);
    }

    /*const voiceInputBtn = document.getElementById('voiceInputBtn');
    const textinput = document.getElementById('textInput');
    voiceInputBtn.addEventListener('click', startVoiceInput);*/

    fetch('/api/conv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: (currentImageIndex-1).toString(),
            title: bookTitle
         })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        let chatHistory = document.createElement("div");
        chatHistory.className = 'chatHistory';
        chatHistory.innerHTML = ``;
        knowledge.appendChild(chatHistory)

        let chatBox = document.createElement("div");
        chatBox.className = 'chatBox';
        chatBox.innerHTML = `<div class="topContent">
                                <img id='penguin' src='../static/files/imgs/penguin.png' />
                                <div id='chatContent'>
                                </div>
                            </div>`
        knowledge.appendChild(chatBox);
        document.getElementById('chatContent').innerHTML = data;
        document.querySelector('.chatBox').innerHTML += `<div class='inputBlock'>
                                <button id="voiceInputBtn" onclick="startVoiceInput()">
                                    <img src='../static/files/imgs/voiceInput.png'>Answer here!
                                </button>
                                <textarea id="textInput"></textarea>
                              </div>`
        knowledge.innerHTML += `<div class='submitBlock'>
                              <button id="submitBtn" onclick="submitText()">
                                <span>Send my answer!</span>
                              </button>
                          </div>`;
        /*console.log(chatBox.innerHTML);*/
        /*document.getElementById('response').innerHTML = data.response;*/
    })
    .catch(error => console.error('Error:', error));
}

function playAudio(audioSrc) {
    audioPlayer.src = audioSrc;
    audioPlayer.play();
    audioPlayer.addEventListener('ended', playNextSentence);
}

function playNextSentence() {
    if (currentSentence < sections[currentImageIndex-1].length -1 && !isKeyWord) {
        currentSentence++;
        playAudio(sections[currentImageIndex-1][currentSentence].audio);
        render_caption(sections[currentImageIndex-1][currentSentence].text);
    } else {
        audioPlayer.removeEventListener('ended', playNextSentence);
    }
}

function updateProgressBar() {
    const progressBar = document.querySelector('.progress');
    const progressPercentage = (currentImageIndex / (totalPages - 1)) * 100;
    progressBar.style.width = `${progressPercentage}%`;
    document.getElementById('curPage').innerHTML = `Page ${currentImageIndex} of ${totalPages}`;
}

function showImage() {
    isKeyWord = false;
    const currentImage = document.getElementById("BookImg");
    currentImage.src = `../static/files/books/${bookTitle}/pages/page${currentImageIndex}.jpg`;
    updateProgressBar();
    currentSentence = 0;

    var utterance = new SpeechSynthesisUtterance(sections[currentImageIndex-1][currentSentence].text);
    utterance.voice = synthesis.getVoices()[0];
    synthesis.speak(utterance);

    /*const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.removeEventListener('ended', playNextSentence);
    audioPlayer.pause();
    audioPlayer.currentTime = 0;

    playAudio(sections[currentImageIndex-1][currentSentence].audio);*/
    render_caption(sections[currentImageIndex-1][currentSentence].text);
}

function NextPage() {
    if (document.querySelector('.Knowledge') != null){
        save_knowledge_state(true);
    }
    currentImageIndex = currentImageIndex < totalPages ? currentImageIndex + 1: currentImageIndex;
    showImage();
}

function PrevPage() {
    if (document.querySelector('.Knowledge') != null){
        save_knowledge_state(true);
    }
    currentImageIndex = currentImageIndex > 1 ? currentImageIndex - 1 : currentImageIndex;
    showImage();
}

function textAudio(){
    sections = [];
    let i = 0;
    for (let key in genData){
        var sentences = [];
        let j = 0;
        for (let sen in genData[key]['section_text']){
            sentences.push({
                "text": genData[key]['section_text'][sen],
                "audio": `../static/files/books/${bookTitle}/audio/p${i}s${j}.mp3`
            })
            j += 1;
        }
        sections.push(sentences)
        i += 1;
    }
    console.log(sections);
}

function startVoiceInput() {
    const textInput = document.getElementById('textInput');
    textInput.style.visibility = 'visible';
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.style.visibility = 'visible';
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.lang = 'en-US';

      recognition.onresult = function(event) {
        const result = event.results[0][0].transcript;
        textInput.value = result;
        textInput.removeAttribute('readonly');
      };

      recognition.start();
    } else {
      alert('Sorry, your browser does not support speech recognition!');
    }
}

function submitText() {
    const textInput = document.getElementById('textInput');
    if(textInput.value == ''){
        alert("You need to answer this question first!");
        return;
    }
    gptData[(currentImageIndex-1).toString()].answer = true;
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: (currentImageIndex-1).toString(),
            title: bookTitle,
            response: textInput.value,
            answerProgress: gptData
         })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById('chatContent').innerHTML = data.feedback;
        document.getElementById('textInput').value = '';
        addStar(data);
        if(data.end){
            document.querySelector('.inputBlock').remove();
            document.querySelector('.submitBlock').remove();
            document.querySelector('.Knowledge').innerHTML += `<div id='continueBlock'>
                                        <button id="continue" onclick="continueRead()">Continue reading!</button>
                                    </div>`;
            save_knowledge_state(false);
        }
    })
    .catch(error => console.error('Error:', error));
}

function addStar(response){
    const history = document.querySelector('.chatHistory');
    if(response.judgement == 'correct'){
        history.innerHTML += `<div class='starBlock'>
                                <img class='star' id="img${response.q_id}" onclick='showKnowledge(kd${response.q_id})' src='../static/files/imgs/star${response.q_id}.png'>
                                <div class="knowledgeDetail" id="kd${response.q_id}">
                                    <p1>Question ${response.q_id}</p1> </br>
                                    <p2>Knowledge: ${response.knowledge}</p2> </br>
                                    <button class="closeButton" id="close${response.q_id}" onclick='hideKnowledge(kd${response.q_id})'>Close</button>
                                </div>
                            </div>`;
    }
    else{
        history.innerHTML += `<div class='starBlock'>
                                <img class='prob' id="img${response.q_id}" onclick='showKnowledge(kd${response.q_id})' src='../static/files/imgs/question.png'>
                                <div class="knowledgeDetail" id="kd${response.q_id}">
                                    <p1>Question ${response.q_id}</p1> </br>
                                    <p2>Knowledge ${response.knowledge}</p2>
                                    <button id="learned" onclick='changeStar(img${response.q_id}, ${response.q_id})'>Now I get it!</button> </br>
                                    <button class="closeButton" id="close${response.q_id}" onclick='hideKnowledge(kd${response.q_id})'>Close</button>
                                </div>
                            </div>`;
    }
}

function showKnowledge(kdId){
    kdId.style.display = 'block';
}

function hideKnowledge(kdId){
    kdId.style.display = 'none';
}

function changeStar(imgId, qId){
    imgId.src = `../static/files/imgs/star${qId}.png`;
    document.getElementById('learned').remove();
    save_knowledge_state(false);
}

function save_knowledge_state(isClear){
    const knowledge = document.querySelector('.Knowledge');
    fetch('/api/continue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: currentImageIndex-1,
            title: bookTitle,
            html: knowledge.innerHTML,
            answerProgress: gptData
         })
    })
    .then(response => response.json())
    .then(data => {
        if (isClear){
            document.querySelector('.container').removeChild(document.querySelector('.Knowledge'));
        }
    })
    .catch(error => console.error('Error:', error));
}

function continueRead( ){
    gptData[(currentImageIndex-1).toString()].answer = true;
    save_knowledge_state(true);

    audioPlayer.addEventListener('ended', playNextSentence);
    isKeyWord = false;
}

function review(){
    console.log('review previous progress');
    fetch('/api/review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: currentImageIndex-1,
            title: bookTitle
         })
    })
    .then(response => response.json())
    .then(data => {
        let knowledge = document.createElement("div");
        knowledge.className = 'Knowledge';
        knowledge.innerHTML = data;
        const container = document.querySelector('.container');
        if(container.children.length == 1){
            container.appendChild(knowledge);
        }
    })
    .catch(error => console.error('Error:', error));
}

getUser();
