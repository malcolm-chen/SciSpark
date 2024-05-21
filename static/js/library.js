const books1 = [
    { title: "The Little Snowplow", subDis: ['Motion and Stability', 'Engineering Design', 'Earth’s Systems'] },
    { title: "Newton And Me", subDis: ['Motion and Stability', 'Engineering Design', 'Earth’s Systems'] },
    // Add more books as needed
];

const books2 = [
    { title: `Sami\'s Beach Rescue`, subDis: ['Earth’s Systems', 'Motion and Stability', 'Biological Evolution'] },
    // Add more books as needed
];

const books3 = [
    { title: "How to Catch the Wind", subDis: ['Earth’s Systems', 'Motion and Stability'] },
    { title: "Why Do Sunflowers Love the Sun", subDis: ['Earth’s Systems', 'Energy', "Earth’s Place in the Universe"] }
    // Add more books as needed
];

const shelf1 = document.getElementById('Shelf1')
const shelf2 = document.getElementById('Shelf2')
const shelf3 = document.getElementById('Shelf3')
var curUser = '';

function getTag(dis){
    var topics = [
        "Motion and Stability", "Biological Evolution", "Earth’s Systems", "Engineering Design", "Energy", "Earth’s Place in the Universe"
    ]
    return topics.indexOf(dis) + 1
}

books1.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index} onclick="toBookDetail('${book.title}')">
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />
        <br />
        <div class='ShelfBookTitle'>${book.title}</div>
        <div class='tagSpace' id='tags_1${index}'>
        </div>
        <br />
        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            READ THE FULL STORY
        </div>
    </div>`
    shelf1.appendChild(bookElement);
    document.getElementById(`tags_1${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_1${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

books2.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index}>
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />
        <br />
        <div class='ShelfBookTitle' onclick="toBookDetail('${encodeURIComponent(book.title).replace(/'/g, '%27')}')">${book.title}</div>
        <div class='tagSpace' id='tags_2${index}'>
        </div>
        <br />
        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            READ THE FULL STORY
        </div>
    </div>`
    shelf2.appendChild(bookElement);
    document.getElementById(`tags_2${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_2${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

books3.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index}>
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />
        <br />
        <div class='ShelfBookTitle' onclick="toBookDetail('${book.title}')">${book.title}</div>
        <div class='tagSpace' id='tags_3${index}'>
        </div>
        <br />
        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            READ THE FULL STORY
        </div>
    </div>`
    shelf3.appendChild(bookElement);
    document.getElementById(`tags_3${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_3${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

function toBookDetail(title){
    window.location.href='./bookDetail?title=' + encodeURIComponent(title);
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
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

/* getUser(); */