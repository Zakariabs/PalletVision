document.addEventListener("DOMContentLoaded", function () {
    function initializeLogin() {
        const loginLink = document.getElementById('loginLink');
        const loginFormContainer = document.getElementById('loginFormContainer');
        const loginForm = document.getElementById('loginForm');

        console.log("loginLink:", loginLink);
        console.log("loginFormContainer:", loginFormContainer);
        console.log("loginForm:", loginForm);

        if (loginLink) {
            loginLink.addEventListener('click', function (event) {
                event.preventDefault();
                loginFormContainer.style.display = 'block';
                console.log("Login link clicked, form displayed");
            });
        }

        if (loginForm) {
            loginForm.addEventListener('submit', function (event) {
                event.preventDefault();

                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;

                console.log("Form submitted with username:", username);

                fetch('http://127.0.0.1:5000/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Login failed');
                    }
                    return response.json();
                })
                .then(data => {
                    // Store the JWT token
                    localStorage.setItem('jwtToken', data.access_token);
                    alert('Login successful');
                    loginFormContainer.style.display = 'none';
                    console.log("Login successful, token stored");
                })
                .catch(error => {
                    console.error('Error during login:', error);
                    alert('Login failed');
                });
            });
        }
    }


    const header = document.getElementById('header');
    if (header) {
        fetch('./partials/header.html')
            .then(response => response.text())
            .then(html => {
                header.innerHTML = html;
                initializeLogin();
            });
    } else {
        initializeLogin();
    }
});
