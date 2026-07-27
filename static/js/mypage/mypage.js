const editBtn = document.getElementById("edit-btn");
const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");
const inputs = document.querySelectorAll(".edit-item");
const imageInput = document.getElementById("profile-image");
const preview = document.getElementById("profile-preview");

// 元の値を保存
const originalValues = {};

inputs.forEach(input => {
    originalValues[input.id] = input.value;
});


// 編集開始
editBtn.addEventListener("click", () => {
    inputs.forEach(input => {
        input.classList.add("editing");
        if(input.tagName === "SELECT"){
            input.disabled = false;
        }
        else{
            input.readOnly = false;
        }
    });
    editBtn.classList.add("hidden");
    saveBtn.classList.remove("hidden");
    cancelBtn.classList.remove("hidden");
    document.getElementById("profile-image").classList.remove("hidden");
});


// キャンセル
cancelBtn.addEventListener("click", () => {
    inputs.forEach(input => {
        input.value = originalValues[input.id];
        input.classList.remove("editing");
        if(input.tagName === "SELECT"){
            input.disabled = true;
        }
        else{
            input.readOnly = true;
        }
    });
    editBtn.classList.remove("hidden");
    saveBtn.classList.add("hidden");
    cancelBtn.classList.add("hidden");
    document.getElementById("profile-image").classList.add("hidden");
});


imageInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;
    preview.src = URL.createObjectURL(file);
});
