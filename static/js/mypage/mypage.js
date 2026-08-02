const editBtn = document.getElementById("edit-btn");
const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");

const displayItems = document.querySelectorAll(".display-value");
const editItems = document.querySelectorAll(".edit-item");

const withdrawArea = document.getElementById("withdraw-area");

const imageInput = document.getElementById("profile-image");
const preview = document.getElementById("profile-preview");

const profileMessage = document.getElementById("profile_message");
const profileMessageCount = document.getElementById("profile_message_count");

// 元の値を保存
const originalValues = {};

editItems.forEach(item => {
    if (item.id) {
        originalValues[item.id] = item.value;
    }
});

//==========================
// 編集開始
//==========================
editBtn.addEventListener("click", () => {

    displayItems.forEach(item => {
        item.classList.add("hidden");
    });

    editItems.forEach(item => {
        item.classList.remove("hidden");
    });

    imageInput.classList.remove("hidden");

    withdrawArea.classList.add("hidden");

    editBtn.classList.add("hidden");
    saveBtn.classList.remove("hidden");
    cancelBtn.classList.remove("hidden");

    profileMessageCount.classList.remove("hidden");
    updateProfileMessageCount();
});

//==========================
// キャンセル
//==========================
cancelBtn.addEventListener("click", () => {

    editItems.forEach(item => {

        if (item.id) {
            item.value = originalValues[item.id];
        }

        item.classList.add("hidden");
    });

    displayItems.forEach(item => {
        item.classList.remove("hidden");
    });

    imageInput.classList.add("hidden");

    withdrawArea.classList.remove("hidden");

    editBtn.classList.remove("hidden");
    saveBtn.classList.add("hidden");
    cancelBtn.classList.add("hidden");
    profileMessageCount.classList.add("hidden");
});

//==========================
// プロフィール画像
//==========================
imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    preview.src = URL.createObjectURL(file);

});

//==========================
// 自己紹介
//==========================

function updateProfileMessageCount() {
    profileMessageCount.textContent =
        `${profileMessage.value.length} / ${profileMessage.maxLength}`;
}

profileMessage.addEventListener("input", updateProfileMessageCount);