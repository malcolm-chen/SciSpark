const isLoggedIn = false;

function handleLogin(){
    var username = document.getElementById('userName').value;
    var password = document.getElementById('passWord').value;
    console.log(username, password);
    // Send the username and password to the Flask backend for validation
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            window.location.href = '/library';
        } else {
            alert('Login failed. Please check your username and password.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}