const tabItems = document.querySelectorAll('.tab-item');
const tabContents = document.querySelectorAll('.tab-content-item');

function selectItem(e) {
    removeBorder();
    removeShow();
    this.classList.add('tab-border');

    const tabContentItem = document.querySelector(`#${this.id}-content`);
    tabContentItem.classList.add('show');
}

function removeBorder() {
    tabItems.forEach(item => item.classList.remove('tab-border'));
}

function removeShow() {
    tabContents.forEach(content => content.classList.remove('show'))
}

function userLogOut() {
    localStorage.removeItem('access_token');
}

tabItems.forEach(item => item.addEventListener('click', (selectItem)));

document.addEventListener('DOMContentLoaded', userLogOut)
