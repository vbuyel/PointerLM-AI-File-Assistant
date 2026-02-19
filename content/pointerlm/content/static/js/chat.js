const chatHeader = document.querySelector(".app-header");
const helloHeader = chatHeader.querySelector(".hello-header");

const chatContainer = document.querySelector(".chat-container");
const promptForm = document.querySelector(".prompt-form");

const promptInput = promptForm.querySelector(".prompt-input");
const fileInput = promptForm.querySelector(".file-input");

const fileUploadWrapper = promptForm.querySelector(".file-upload-wrapper");
const stopResponseBtn = document.querySelector("#stop-response-btn");
const themeToggle = document.querySelector("#theme-toggle-btn");


let controller, typingInterval;
const API_URL = `https://vbuyel.github.io/`;
// const API_URL = `http://127.0.0.1:8000/`;

const userData = { message: "", file: null };

const createMsgElement = (content, ...classes) => {
    const div = document.createElement("div");
    div.classList.add("message", ...classes);
    div.innerHTML = content;
    return div;
}

const typingEffect = (responseText, messageElement, modelMsgDiv) => {
    messageElement.textContent = "";

    const htmlContent = marked.parse(responseText);

    const words = responseText.split(" ");
    let wordIndex = 0;

    typingInterval = setInterval(() => {
        if (wordIndex < words.length) {
            messageElement.textContent += (wordIndex === 0 ? "" : " ") + words[wordIndex];
            modelMsgDiv.classList.remove("loading");
        } else {
            clearInterval(typingInterval);
            messageElement.innerHTML = htmlContent;
        }
        wordIndex++;
    }, 40);
}

const generateResponse = async (modelMsgDiv) => {
    const messageElement = modelMsgDiv.querySelector(".message-input");
    controller = new AbortController();

    try {
        const formData = new FormData();
        formData.append("text", userData.message);
        if (userData.file && userData.file instanceof File) {
            formData.append("file", userData.file);
        }

        const token = localStorage.getItem('access_token');
        stopResponseBtn.classList.add("active");
        fileUploadWrapper.classList.add("nonactive");

        const response = await fetch(API_URL + `response/generate`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData,
            signal: controller.signal
        });

        if (!response.ok) {
            stopResponseBtn.classList.remove("active");
            fileUploadWrapper.classList.remove("nonactive");

            const error = await response.json();
            throw new Error(`Server error: ${response.status} - ${error}`);
        }

        const responseText = await response.json();
        if (!responseText.current_user) {
            localStorage.removeItem('access_token');
            checkAuth();
        }
        typingEffect(responseText.response, messageElement, modelMsgDiv);

        userData.file = null;
        stopResponseBtn.classList.remove("active");
        fileUploadWrapper.classList.remove("nonactive");
        fileUploadWrapper.classList.remove("active");
    } catch (error) {
        console.error(error);

        if (error.message == "Fetch is aborted") {
            messageElement.textContent = "Response generation stopped.";
        } else {
            messageElement.textContent = error.message;
        }
        modelMsgDiv.classList.remove("loading");

        userData.file = null;
        stopResponseBtn.classList.remove("active");
        fileUploadWrapper.classList.remove("nonactive");
        fileUploadWrapper.classList.remove("active");
    }
}

const handleFormSubmit = (e) => {
    e.preventDefault();
    userData.message = promptInput.value.trim();
    if (!userData.message) {
        return;
    }
    promptInput.value = "";

    if (!helloHeader.classList.contains("nonactive")) {
        helloHeader.classList.add("nonactive");
    }

    const userMsgHTML = `
        <p class="message-input"></p>
        ${userData.file ? `<p class="file-attachment"><span class="material-symbols-outlined">description</span>${userData.file.name}</p>` : ""}
    `;

    const userMsgDiv = createMsgElement(userMsgHTML, "user-message");

    userMsgDiv.querySelector(".message-input").textContent = userData.message;
    chatContainer.appendChild(userMsgDiv);

    setTimeout(() => {
        const modelMsgHTML = `<img src="../../static/img/logo.png" class="logo">\n<p class="message-input">Just a sec...</p>`;
        const modelMsgDiv = createMsgElement(modelMsgHTML, "model-message", "loading");
        chatContainer.appendChild(modelMsgDiv);

        generateResponse(modelMsgDiv);
    }, 600);
}

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) {
        return;
    }

    console.log("File selected:", file.name, "Size:", file.size, "Type:", file.type);
    userData.file = file;

    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = (e) => {
        fileInput.value = "";
        fileUploadWrapper.querySelector("img").src = e.target.result;
        fileUploadWrapper.classList.add("active");
    }

    reader.onerror = (error) => {
        console.error("FileReader error:", error);
        alert("Failed to read file");
        userData.file = null;
    }
});

document.querySelector("#cancel-file-btn").addEventListener("click", () => {
    fileUploadWrapper.classList.remove("active");
    userData.file = null;
    fileInput.value = "";
});

stopResponseBtn.addEventListener("click", () => {
    fileUploadWrapper.classList.remove("active");
    userData.file = null;
    fileInput.value = "";

    controller?.abort();
    clearInterval(typingInterval);
});

document.querySelector("#new-chat-btn").addEventListener("click", async () => {
    response = await fetch(API_URL + `response/clear_chat`, {
        method: "GET",
    });

    if (!response.ok) {
        const modelMsgHTML = `<img src="../../static/img/logo.png" class="logo">\n<p class="message-input">Just a sec...</p>`;
        const modelMsgDiv = createMsgElement(modelMsgHTML, "model-message", "loading");
        chatContainer.appendChild(modelMsgDiv);

        const messageElement = modelMsgDiv.querySelector(".message-input");
        typingEffect("Chat can not be deleted. Try refresh the page.", messageElement, modelMsgDiv);
        return;
    }

    chatContainer.innerHTML = "";
    helloHeader.classList.remove("nonactive");
});

themeToggle.addEventListener("click", () => {
    const isLightTheme = document.body.classList.toggle("light-theme");
    themeToggle.textContent = isLightTheme ? "dark_mode" : "light_mode";
});

promptForm.addEventListener("submit", handleFormSubmit);
promptForm.querySelector("#add-file-btn").addEventListener("click", () => fileInput.click());
