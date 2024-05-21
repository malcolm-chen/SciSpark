// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(setStat);

var curUser = document.getElementById('Profile').textContent;
var statDict = {};

function getTag(dis){
    var topics = [
        "Motion and Stability", "Biological Evolution", "Earth’s Systems", "Engineering Design", "Energy", "Earth’s Place in the Universe"
    ]
    return topics.indexOf(dis) + 1
}

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
        getStat();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function getStat(){
    fetch('/api/stat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: curUser
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        statDict = data;
        setStat();
    })
    .catch((error) => {
        console.error('Error get stats:', error);
    });
}

function setStat(){
    /* Set reading book */
    var bookTitle = statDict.reading;
    document.getElementById('nowReading').innerHTML =  `<p1>Now reading:</p1>
                                                        <p2>${bookTitle}</p2>
                                                        <img id="nowBookImg" src='../static/files/books/${encodeURIComponent(bookTitle).replace(/'/g, '%27')}/cover.jpg'>`

    /* Set Book Reading Data */
    setBookData(statDict.bookStat);


    /* Set Record Data */
    var record = statDict.readingRecord;
    document.getElementById('todayRead').innerHTML = record['todayRead'];
    document.getElementById('todayTime').innerHTML = record['todayTime'];
    document.getElementById('totalRead').innerHTML = record['totalRead'];
    document.getElementById('totalTime').innerHTML = record['totalTime'];

    /* Set week Data */
    drawScienceData(statDict.scienceStat);
    drawWeekData(statDict.weekTime);
}

function setBookData(bookDict){
    const table = document.getElementById('statTable')
    let table_id = 0;
    for(var key in bookDict){
        table_id += 1;
        if(document.getElementById(`header_${table_id}`)){
            continue;
        }
        var pathParts = bookDict[key].coverSrc.split('/')
            var encodedPathParts = pathParts.map(function(part) {
                return encodeURIComponent(part).replace(/'/g, '%27');
            });
        var bookcoverSrc = encodedPathParts.join("/");
        var curLen = Object.keys(bookDict[key].records).length;
        table.innerHTML += `
        <div class="tableHeader" id='header_${table_id}'>
            <div class="header-cell">
                <div class="coverTitle">
                    <img src='${bookcoverSrc}'>
                    <p1>${key}</p1>
                </div>
                <div class="conceptInst">${bookDict[key].count} keywords in total</div>
                <div class="progressCircle">
                    <p>${Math.round(100*curLen/bookDict[key].count)} %</p>
                    <svg class="progress-circle" width="100%" height="100%">
                        <circle cx="50%" cy="50%" r="40"></circle>
                        <circle cx="50%" cy="50%" r="40" class="progress-bar"></circle>
                    </svg>
                </div>
            </div>
            <button class="expand-btn" onclick="toggleTable('${table_id}')"></button>
        </div>
        <div class="table-content" id="tableContent_${table_id}" style="display: none;">
        </div>
        `
        var content = document.getElementById(`tableContent_${table_id}`);
        setProgress(100*curLen/bookDict[key].count);
        /*setProgress(70);*/
        for(var detail in bookDict[key].records){
            var progressDot = '';
            var progressFlag = 0;
            if(detail.progress == 'true'){
                progressDot = 'green-dot';
                progressFlag = 1;
            }
            else{
                progressDot = 'yellow-dot';
            }
            
            bookRec = document.createElement('div');
            bookRec.className = 'bookRec';
            bookRec.innerHTML = `
            <div class="bookKg">
                <span class="dot ${progressDot}"></span>
                <p1>${bookDict[key].records[detail].concept}</p1>
                <p2>${bookDict[key].records[detail].knowledge}</p2>
                <div class='tagSpace'>
                    <div class='tag${getTag(bookDict[key].records[detail].topic)}'>#${bookDict[key].records[detail].topic}</div>
                </div>
            </div>`
            content.appendChild(bookRec);
        }
    }
}

function toggleTable(id) {
    var content = document.getElementById(`tableContent_${id}`);
    var btn = document.querySelector(".expand-btn");
    btn.classList.toggle('up');
    if (content.style.display === "none") {
      content.style.display = "block";
    } else {
      content.style.display = "none";
    }
}

function setProgress(percent) {
    var progressBar = document.querySelector('.progress-bar');
    var radius = parseInt(progressBar.getAttribute('r'));
    var circumference = 2 * Math.PI * radius;
    var offset = circumference - percent / 100 * circumference;
    if (percent >= 50) offset = 100-percent; 
    progressBar.style.strokeDasharray = `${percent / 100 * circumference} ${circumference}`;
    progressBar.style.strokeDashoffset = offset;
}

function drawScienceData(scienceDict){
    var dataArray1 = [['Category', 'Value']];
    for (var category in scienceDict["Discipline"]) {
        dataArray1.push([category, scienceDict["Discipline"][category]]);
    }
    var data1 = google.visualization.arrayToDataTable(dataArray1);

    var options = {
        title: 'Disciplines learning record',
        titleTextStyle: {
            fontSize: 18,  
            bold: true,    
            italic: false, 
            textAlign: 'center' 
        },
        colors: ['#acb4d3', '#ffb289', '#89c8ff', '#fff583'],
        backgroundColor: { fill: 'transparent' },
    };

    var chart = new google.visualization.PieChart(document.getElementById('pieChart'));
    chart.draw(data1, options);

    var dataArray2 = [['Category', '# Knowledge learned', { role: 'style' }]];
    var colors = ['#FFBE82', '#A2FDB1', '#FFED8F', '#88EDFB', '#8A9DFF'];
    var i = 0;
    for (var category in scienceDict["subDisc"]) {
        dataArray2.push([category, scienceDict["subDisc"][category], colors[i]]);
        i += 1;
    }
    var data2 = google.visualization.arrayToDataTable(dataArray2);

    var options = {
        title: 'Most learned sub-disciplines',
        titleTextStyle: {
            fontSize: 18,  
            bold: true,    
            italic: false, 
            textAlign: 'center' 
        },
        backgroundColor: { fill: '#F7ECDB' },
        height: 250,
        legend: 'none', 
    };

    var chart = new google.visualization.BarChart(document.getElementById('barChart'));
    chart.draw(data2, options);
}

function drawWeekData(weekDict){
    var columndataArray = [
        ['Days', 'Reading Time'],
        ['Sunday', weekDict['Sun']],
        ['Monday', weekDict['Mon']],
        ['Tuesday', weekDict['Tue']],
        ['Wednesday', weekDict['Wed']],
        ['Thursday', weekDict['Thu']],
        ['Friday', weekDict['Fri']],
        ['Saturday', weekDict['Sat']]
    ];
    console.log(columndataArray)

    var columnData = google.visualization.arrayToDataTable(columndataArray);

    // Set chart options
    var options = {
      vAxis: {title: 'Reading time (minutes)'},
      width: 600,
      height: 380,
      backgroundColor: { fill: 'transparent' },
      series: {
            0: { color: '#5D997E' },
        },
        vAxis: {
            gridlines: { color: 'lightgrey', count: 7 }, 
        },
        hAxis: {
            gridlines: { color: 'lightgrey' }, 
        },
    };

    // Instantiate and draw the chart
    var chart = new google.visualization.ColumnChart(document.getElementById('columnChart'));
    chart.draw(columnData, options);
}

/* getUser(); */
getStat();