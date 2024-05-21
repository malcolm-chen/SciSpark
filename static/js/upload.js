// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawDisChart);

/* var curUser = document.getElementById('Profile').textContent; */
var curUser = '';
var coverImg = '';
var bookTitle = '';
var pageImg = [];
var curPage = 1;
var disciplines = {};
let videoStream;

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
        step1();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function step1(){
    document.querySelector('.uploadStep').innerHTML = `<p1>Step 1</p1>
    </br>
    <p2>Upload a cover image of your book</p2>`;
    document.getElementById('workPlace').innerHTML = `<div class="uploadContent">
    <img id='camera' src="../static/files/imgs/camera.png" onclick="shootCover()">
    </div>`
}

function closeCamera(content) {
    var cameraPreview;
    if (content == 'cover'){
        cameraPreview = document.getElementById('camera-preview');
    }
    else if (content == 'page'){
        cameraPreview = document.getElementById('camera-preview-page');
    }

    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach(track => track.stop());
        cameraPreview.srcObject = null;
    }
}

async function showCamera(content){
    var cameraPreview;
    if (content == 'cover'){
        cameraPreview = document.getElementById('camera-preview');
    }
    else if (content == 'page'){
        cameraPreview = document.getElementById('camera-preview-page');
    }

    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        cameraPreview.srcObject = videoStream;
    } catch (error) {
        console.error('Error accessing the camera:', error);
    }
}

function shootCover(){
    document.querySelector('.uploadContent').innerHTML = `<video id="camera-preview" autoplay></video>
    <button class="capture-btn" onclick="captureCoverImg()">Capture</button>`;

    showCamera('cover');
}

function captureCoverImg(){
    const cameraPreview = document.getElementById('camera-preview');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = cameraPreview.videoWidth;
    canvas.height = cameraPreview.videoHeight;
    context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);
    
    closeCamera('cover');

    document.querySelector('.uploadContent').innerHTML = `<img id="captured-image" src=${canvas.toDataURL('image/png')} alt="Captured Image"></img>
    <button id="retake-btn" onclick="shootCover()">retake</button> 
    <div class='cameraBtns'>                                                         
        <input id="uploadTitle" placeholder="Name this book"/>                                   
        <button class="confirm-btn" onclick="confirmCover()">confirm</button>
    </div>`;
    
}

function confirmCover(){
    bookTitle = document.getElementById('uploadTitle').value;
    coverImg = document.getElementById('captured-image').src;
    fetch('/api/uploadCover', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            img: coverImg,
            title: bookTitle,
            username: curUser
        }),
    })
    .then(response => response.json())
    .then(data => {
        step2();
    })
    .catch((error) => {
        console.error('Error save cover:', error);
    });
}

function step2(){
    document.querySelector('.uploadStep').innerHTML = `<p1>Step 2</p1>
    </br>
    <p2>Take a picture of each page of </p2><p3>${bookTitle}</p3>`;
    document.getElementById('workPlace').innerHTML = `<div class="uploadContent">
    <img id='pageCamera' src="../static/files/imgs/camera.png" onclick="shootPage()">
    </div>`
}

function shootPage(){
    document.querySelector('.uploadContent').innerHTML = `<video id="camera-preview-page" autoplay></video>
    <button class="capture-btn" onclick="capturePageImg()">Capture</button>`;
    showCamera('page');
}

async function capturePageImg(){
    const cameraPreview = document.getElementById('camera-preview-page');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = cameraPreview.videoWidth;
    canvas.height = cameraPreview.videoHeight;
    context.drawImage(cameraPreview, 0, 0, canvas.width, canvas.height);
    
    closeCamera('page');

    document.querySelector('.uploadStep').innerHTML = `<p1>Step 2</p1>
    </br>
    <p2>Modify the story text if needed</p2>`;

    var curText = '';
    const { createWorker } = Tesseract;
    (async () => {
        const worker = await createWorker('eng');
        const { data: { text } } = await worker.recognize(canvas.toDataURL('image/png'));
        curText = text;
        console.log(text);
        if (curPage > 1){
            document.querySelector('.uploadContent').innerHTML = `<img id="captured-image" src=${canvas.toDataURL('image/png')} alt="Captured Image"></img>
            <button id="retake-btn" onclick="shootPage()">retake</button> 
            <div class='modifyUpload'>                                                         
                <textarea id="ocrText">${curText}</textarea>                                  
            </div>
            <button id="prev-btn" onclick="savePrev('${canvas.toDataURL('image/png')}')"> Previous Page</button>
            <button id="save-btn" onclick="saveContinue('${canvas.toDataURL('image/png')}')">Save and Continue</button>
            <button id="end-upload-btn" onclick="finishUpload('${canvas.toDataURL('image/png')}')">finish uploading</button>`;  
        }
        else{
            document.querySelector('.uploadContent').innerHTML = `<img id="captured-image" src=${canvas.toDataURL('image/png')} alt="Captured Image"></img>
            <button id="retake-btn" onclick="shootPage()">retake</button> 
            <div class='modifyUpload'>                                                         
                <textarea id="ocrText">${curText}</textarea>                                  
            </div>
            <button id="save-btn" onclick="saveContinue('${canvas.toDataURL('image/png')}')">Save and Continue</button>
            <button id="end-upload-btn" onclick="finishUpload('${canvas.toDataURL('image/png')}')">finish uploading</button>`;  
        }
    })();
}

function savePrev(imgSrc){
    pageImg[curPage] = {
        'img': imgSrc,
        'text': document.getElementById('ocrText').value
    }
    if(curPage >= 1 ){
        curPage -= 1;
    }
    console.log(pageImg);
    /*shootPage();*/
    document.querySelector('.uploadContent').innerHTML = `<img id="captured-image" src=${pageImg[curPage].img} alt="Captured Image"></img>
        <button id="retake-btn" onclick="shootPage()">retake</button> 
        <div class='modifyUpload'>                                                         
            <textarea id="ocrText">${pageImg[curPage].text}</textarea>                                  
        </div>
        <button id="prev-btn" onclick="savePrev('${pageImg[curPage].img}')"> Previous Page</button>
        <button id="save-btn" onclick="saveContinue('${pageImg[curPage].img}')">Save and Continue</button>
        <button id="end-upload-btn" onclick="finishUpload('${pageImg[curPage].img}')">finish uploading</button>`;   
}

function saveContinue(imgSrc){
    pageImg[curPage] = {
        'img': imgSrc,
        'text': document.getElementById('ocrText').value
    }
    curPage += 1;
    console.log(pageImg);
    shootPage();
}

function finishUpload(imgSrc){
    /* 1. Parse and calculate disciplines
    2. Update dashboard info ( update[ title, coverImg, tags] ) 
    3. Update local folder 
    4. switch to customize page */
    pageImg[curPage] = {
        'img': imgSrc,
        'text': document.getElementById('ocrText').value
    }
    fetch('/api/uploadPage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: bookTitle,
            username: curUser,
            pageData: pageImg
        }),
    })
    .then(response => response.json())
    .then(data => {
        /* 1. show discipline distribution
        2. switch to customize page */
        disciplines = data;
        step3(disciplines);
        /*window.location.href='./customize';*/
    })
    .catch((error) => {
        console.error('Error save pages:', error);
    });

}

function step3(disciplines){
    /* show discipline distribution */
    console.log(disciplines);
    var disc = disciplines['discipline'];
    var subdis = disciplines['sub-discipline'];
    console.log(disc)
    document.getElementById('workPlace').innerHTML = `<div id="discPieChart"></div><div id="subdisBarChart"></div>`;
    document.getElementById('workPlace').style.marginTop = 0;
    drawDisChart(disc);
    drawSubdisChart(subdis)
    document.querySelector('.uploadStep').innerHTML = `<p1>Disciplines matched!</p1>
    </br>
    <p2>The most relevant discipline of </p2><p3>${bookTitle}</p3><p2> is </p2><p4>${disc[0][0]}</p4>
    <button id="backtoCust" onclick="toCust()">Got it!</button>`;
}

function toCust(){
    window.location.href = "./customize";
}

function drawDisChart(disc){
    var dataArray1 = [['Category', 'Value']];
    for (let i=0; i < disc.length; i++) {
        dataArray1.push([disc[i][0], disc[i][1]]);
    }
    console.log(dataArray1);
    var data1 = google.visualization.arrayToDataTable(dataArray1);

    var options = {
        title: `Disciplines distribution of ${bookTitle}`,
        titleTextStyle: {
            fontSize: 18,  
            bold: true,    
            italic: false, 
            textAlign: 'center' 
        },
        colors: ['#acb4d3', '#ffb289', '#89c8ff', '#fff582'],
        backgroundColor: { fill: 'transparent' },
        width:800,
        height:400
    };

    var chart = new google.visualization.PieChart(document.getElementById('discPieChart'));
    chart.draw(data1, options);
}

function drawSubdisChart(subdis){
    var dataArray2 = [['Category', '# Sub-disciplines', { role: 'style' }]];
    var colors = ['#FFBE82', '#A2FDB1', '#FFED8F', '#88EDFB', '#8A9DFF'];
    var i = 0;
    for (var category in subdis) {
        dataArray2.push([subdis[category][0], subdis[category][1], colors[i]]);
        i += 1;
    }
    console.log(dataArray2);
    var data2 = google.visualization.arrayToDataTable(dataArray2);

    var options = {
        title: 'Most matched sub-disciplines',
        titleTextStyle: {
            fontSize: 18,  
            bold: true,    
            italic: false, 
            textAlign: 'center' 
        },
        backgroundColor: { fill: '#F7ECDB' },
        height: 250,
        width: 800,
        legend: 'none', 
    };

    var chart = new google.visualization.BarChart(document.getElementById('subdisBarChart'));
    chart.draw(data2, options);
}

getUser(); 