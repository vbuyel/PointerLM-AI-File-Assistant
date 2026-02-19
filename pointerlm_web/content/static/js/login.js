const form = document.getElementById('form');
const requiredElements = [
    document.getElementById('email-input'),
    document.getElementById('password-input')
];
const errorMessage = document.getElementById('error-message');

form.addEventListener('submit', async (e) => {
    e.preventDefault()
    let errors = [];

    for (let element of requiredElements) {
        if (!element.value) {
            errors.push(element.placeholder + " is required");
            element.parentElement.classList.add('incorrect');
        } else {
            element.parentElement.classList.remove('incorrect');
        }
    }

    const emailInput = requiredElements[0];
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailInput.value && !emailRegex.test(emailInput.value)) {
        errors.push("Email is invalid");
        emailInput.parentElement.classList.add('incorrect');
    }

    if (errors.length > 0) {
        errorMessage.innerText = errors.join('. ');
        return;
    }

    const response = await fetch(`http://127.0.0.1:8000/user/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
            "username": requiredElements[0].value,
            "password": requiredElements[1].value
        }),
    });
    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        window.location.href = '../html/chat.html';
    } else {
        errorMessage.innerText = data.detail || "Failed to login";
    }

});
