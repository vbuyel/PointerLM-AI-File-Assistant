function checkAuth() {
    const token = localStorage.getItem('access_token');
    const notLoggedIn = document.querySelector('.not-loggedin');
    const loggedIn = document.querySelector('.loggedin');

    if (token) {
        notLoggedIn.classList.remove('active');
        loggedIn.classList.add('active');
    } else {
        notLoggedIn.classList.add('active');
        loggedIn.classList.remove('active');
    }
}

document.addEventListener('DOMContentLoaded', checkAuth);
