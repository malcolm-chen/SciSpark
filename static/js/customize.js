var curUser = document.getElementById('Profile').textContent;
var uploadBooks = [];

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
        showUpload();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function showUpload(){
    fetch('/api/uploadHistory', {
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
        uploadBooks = data;
        mapUploadedBook(uploadBooks);
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function mapUploadedBook(uploadBooks){
    const shelf = document.getElementById('uploadShelf');
    console.log(uploadBooks)
    if (uploadBooks.length != 0) {
        uploadBooks.map((book, index) => {
            const bookElement = document.createElement('div');
            bookElement.innerHTML = `
            <div class='FeaturedBook' key=${index}>
                <img src='../static/files/${curUser}/${book.title}/cover.jpg' alt=${book.title} />
                <br />
                <div class='ShelfBookTitle' onclick="toBookDetail('${book.title}')">${book.title}</div>
                <div id='uploadTagSpace_${index}'>
                </div>
                <br />
                <div class='ShelfReadBook'>
                    <i class="fa-solid fa-forward"></i>
                    READ THE FULL STORY
                </div>
            </div>`
            shelf.appendChild(bookElement);
            document.getElementById(`uploadTagSpace_${index}`).innerHTML = '';
            for(let dis in book.tags['sub-discipline']){
                document.getElementById(`uploadTagSpace_${index}`).innerHTML += `<div class='tag${getTag(book.tags['sub-discipline'][dis])}'>#${book.tags['sub-discipline'][dis][0]}</div>`;
            }
        });
    }
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='toUpload' id='uploadIcon' onclick="window.location.href='./upload'">
        <img src='../static/files/imgs/add.png' />
    </div>`
    shelf.appendChild(bookElement);
}

function getTag(dis){
    if(dis == "Motion and Stability") {
        return 1;
    }
    if(dis == "Biological Evolution") {
        return 2;
    }
    if(dis == "Earth’s Systems") {
        return 3;
    }
    if(dis == "Engineering Design") {
        return 4;
    }
    if(dis == "Energy") {
        return 5;
    }
    if(dis == "Earth’s Place in the Universe") {
        return 6;
    }
}

function toBookDetail(title){
    window.location.href='./custBookDetail?title=' + encodeURIComponent(title);
}

/* getUser(); */
showUpload();