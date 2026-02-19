const accountData = document.querySelector(".account-data");
const historyData = accountData.querySelector(".history");
const infoData = accountData.querySelector(".info");
const userNameInfo = infoData.querySelector(".name");
const userEmailInfo = infoData.querySelector(".email");

const accountCloseBtn = document.getElementById("close-btn");
const accountExitBtn = document.getElementById("exit-btn");
const accountDeleteBtn = document.getElementById("delete-btn");
const accountDataBtn = document.querySelector(".btn-account");

const historyItems = historyData.querySelectorAll("p");

// Exit from account
accountExitBtn.addEventListener("click", () => {
    accountData.classList.remove("active");
    localStorage.removeItem('access_token');
    checkAuth();
});


// See account info
accountDataBtn.addEventListener("click", async () => {
    const token = localStorage.getItem('access_token');

    try {
        // Get user info
        const response_user = await fetch(API_URL + `user/info`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            },
        });

        if (!response_user.ok) {
            localStorage.removeItem('access_token');
            window.location.href = "../../dynamic/html/login.html"
            return;
        }
        const userData = await response_user.json();
        userNameInfo.textContent = `Username: ${userData.username}`;
        userEmailInfo.textContent = `Email: ${userData.email}`;

        // Add history
        const response_history = await fetch(API_URL + `response/history`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            },
        });

        const historyDataJson = await response_history.json();

        for (let i = 0; i < historyDataJson.history.length; i++) {
            historyItems[i].textContent = historyDataJson.history[i];
        }

        accountData.classList.add("active");
    } catch (error) {
        console.error("Error fetching user info:", error);
        localStorage.removeItem('access_token');
    }
});


accountCloseBtn.addEventListener("click", () => {
    accountData.classList.remove("active");
});


// Delete account
accountDeleteBtn.addEventListener("click", () => {
    const token = localStorage.getItem('access_token');
    localStorage.removeItem('access_token');

    const response = fetch(API_URL + `user/delete`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
    accountData.classList.remove("active");

    if (!response.ok) {
        window.location.href = "../html/login.html";
        return;
    }

    window.location.href = "../../static/html/index.html";
});

