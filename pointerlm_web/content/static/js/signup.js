const form = document.getElementById('form');

const requiredElements = [
    document.getElementById('username-input'),
    document.getElementById('email-input'),
    document.getElementById('password-input'),
    document.getElementById('repeat-password-input')
];
const errorMessage = document.getElementById('error-message');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let errors = [];

    for (let element of requiredElements) {
        if (!element.value) {
            errors.push(element.placeholder + " is required");
            element.parentElement.classList.add('incorrect');
        } else {
            element.parentElement.classList.remove('incorrect');
        }
    }

    const emailInput = document.getElementById('email-input');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailInput.value && !emailRegex.test(emailInput.value)) {
        errors.push("Email is invalid");
        emailInput.parentElement.classList.add('incorrect');
    }

    const password = document.getElementById('password-input').value;
    const repeatPassword = document.getElementById('repeat-password-input').value;
    if (password !== repeatPassword) {
        errors.push("Passwords do not match");
        document.getElementById('repeat-password-input').parentElement.classList.add('incorrect');
    }
    if (password.length < 6 || password.length > 20) {
        errors.push("Passwords should be from 6 to 20 characters");
        document.getElementById('password-input').parentElement.classList.add('incorrect');
        document.getElementById('repeat-password-input').parentElement.classList.add('incorrect');
    }

    if (errors.length > 0) {
        errorMessage.innerText = errors.join('. ');
        return;
    }

    try {
        const result = await fetch(`http://127.0.0.1:8000/user/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "username": requiredElements[0].value,
                "email": requiredElements[1].value,
                "password": requiredElements[2].value
            }),
        });

        if (result.ok) {
            const data = await result.json();
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '../html/chat.html';
        } else {
            const errorData = await result.json().catch(() => ({}));
            console.log('Error data:', errorData);
            errorMessage.innerText = errorData.detail || "Failed to sign up";
        }
    } catch (error) {
        errorMessage.innerText = "Network error: " + error.message;
    }
});
