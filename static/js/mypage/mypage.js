const editBtn = document.getElementById("edit-btn");
const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");

const displayItems = document.querySelectorAll(".display-value");
const editItems = document.querySelectorAll(".edit-item");

const withdrawArea = document.getElementById("withdraw-area");

const imageInput = document.getElementById("profile-image");
const profileArea = document.querySelector(".profile-area");
const profileWrapper = document.querySelector(".profile-image-wrapper");
const profileImageEdit = document.getElementById("profile-image-edit");

const profileMessage = document.getElementById("profile_message");
const profileMessageCount = document.getElementById("profile_message_count");

let preview = document.getElementById("profile-preview");
let defaultIcon = document.getElementById("profile-default");


//==========================
// 元の値を保存
//==========================

const originalValues = {};

editItems.forEach(item => {

    if (item.id) {
        originalValues[item.id] = item.value;
    }
});


//==========================
// 元のプロフィール画像状態
//==========================

const originalProfileImage = preview
    ? preview.src
    : "";

const originalHasProfileImage = !!preview;


//==========================
// 編集開始
//==========================

if (editBtn) {

    editBtn.addEventListener("click", () => {

        //================================
        // スクロール位置を一番上へ
        //================================

        const scrollArea = document.querySelector(".mypage-scroll");

        if (scrollArea) {
            scrollArea.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        }

        //================================
        // 表示用項目を非表示
        //================================

        displayItems.forEach(item => {
            item.classList.add("hidden");
        });

        //================================
        // 編集項目を表示
        //================================

        editItems.forEach(item => {
            item.classList.remove("hidden");
        });

        //================================
        // 設定・本登録エリアを非表示
        //================================

        if (withdrawArea) {
            withdrawArea.classList.add("hidden");
        }

        //================================
        // ボタン切り替え
        //================================

        editBtn.classList.add("hidden");

        if (saveBtn) {
            saveBtn.classList.remove("hidden");
        }

        if (cancelBtn) {
            cancelBtn.classList.remove("hidden");
        }

        //================================
        // 画像変更表示
        //================================

        if (profileImageEdit) {
            profileImageEdit.classList.remove("hidden");
        }

        //================================
        // 自己紹介文字数
        //================================

        if (profileMessageCount) {

            profileMessageCount.classList.remove("hidden");

            updateProfileMessageCount();
        }
    });
}


//==========================
// キャンセル
//==========================

if (cancelBtn) {

    cancelBtn.addEventListener("click", () => {

        //================================
        // 入力値を元に戻す
        //================================

        editItems.forEach(item => {

            if (
                item.id &&
                originalValues[item.id] !== undefined
            ) {
                item.value = originalValues[item.id];
            }

            item.classList.add("hidden");
        });


        //================================
        // 表示項目を戻す
        //================================

        displayItems.forEach(item => {
            item.classList.remove("hidden");
        });


        //================================
        // ファイル選択を解除
        //================================

        if (imageInput) {
            imageInput.value = "";
        }


        //================================
        // Object URLを解放
        //================================

        revokeObjectUrl();


        //================================
        // プロフィール画像を元に戻す
        //================================

        restoreProfileImage();


        //================================
        // 設定エリアを表示
        //================================

        if (withdrawArea) {
            withdrawArea.classList.remove("hidden");
        }


        //================================
        // ボタンを戻す
        //================================

        if (editBtn) {
            editBtn.classList.remove("hidden");
        }

        if (saveBtn) {
            saveBtn.classList.add("hidden");
        }

        cancelBtn.classList.add("hidden");


        //================================
        // 画像変更表示を非表示
        //================================

        if (profileImageEdit) {
            profileImageEdit.classList.add("hidden");
        }


        //================================
        // 文字数カウントを非表示
        //================================

        if (profileMessageCount) {
            profileMessageCount.classList.add("hidden");
        }
    });
}


//==========================
// プロフィール画像クリック
//==========================

if (profileArea) {

    profileArea.addEventListener("click", () => {

        // 編集モード以外では何もしない
        if (!editBtn || !editBtn.classList.contains("hidden")) {
            return;
        }

        if (imageInput) {
            imageInput.click();
        }
    });
}


//==========================
// プロフィール画像変更
//==========================

if (imageInput) {

    imageInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }


        //================================
        // 画像ファイル以外は拒否
        //================================

        if (!file.type.startsWith("image/")) {

            this.value = "";

            return;
        }


        //================================
        // 古いObject URLを解放
        //================================

        revokeObjectUrl();


        //================================
        // Object URL作成
        //================================

        const objectUrl = URL.createObjectURL(file);


        //================================
        // img要素が存在しない場合
        //================================

        if (!preview) {

            if (!profileWrapper) {
                return;
            }

            preview = document.createElement("img");

            preview.id = "profile-preview";
            preview.className = "profile-image";

            preview.alt = "プロフィール画像";

            profileWrapper.appendChild(preview);


            // 新しく作成した画像にもクリックイベントを設定
            preview.addEventListener("click", () => {

                if (
                    editBtn &&
                    editBtn.classList.contains("hidden") &&
                    imageInput
                ) {
                    imageInput.click();
                }
            });
        }


        //================================
        // デフォルトアイコンを非表示
        //================================

        if (defaultIcon) {
            defaultIcon.classList.add("hidden");
        }


        //================================
        // プレビュー表示
        //================================

        preview.dataset.objectUrl = objectUrl;
        preview.src = objectUrl;
        preview.classList.remove("hidden");
    });
}


//==========================
// Object URL解放
//==========================

function revokeObjectUrl() {

    if (
        preview &&
        preview.dataset.objectUrl
    ) {

        URL.revokeObjectURL(
            preview.dataset.objectUrl
        );

        delete preview.dataset.objectUrl;
    }
}


//==========================
// プロフィール画像を元に戻す
//==========================

function restoreProfileImage() {

    //================================
    // 元々画像が設定されていた場合
    //================================

    if (originalHasProfileImage) {

        // imgが存在しない場合は作成
        if (!preview) {

            if (!profileWrapper) {
                return;
            }

            preview = document.createElement("img");

            preview.id = "profile-preview";
            preview.className = "profile-image";

            preview.alt = "プロフィール画像";

            profileWrapper.appendChild(preview);


            preview.addEventListener("click", () => {

                if (
                    editBtn &&
                    editBtn.classList.contains("hidden") &&
                    imageInput
                ) {
                    imageInput.click();
                }
            });
        }

        preview.src = originalProfileImage;

        preview.classList.remove("hidden");


        if (defaultIcon) {
            defaultIcon.classList.add("hidden");
        }

        return;
    }


    //================================
    // 元々画像がなかった場合
    //================================

    if (preview) {

        preview.remove();

        preview = null;
    }


    //================================
    // デフォルトアイコンがなければ作成
    //================================

    if (!defaultIcon) {

        if (!profileWrapper) {
            return;
        }

        defaultIcon = document.createElement("div");

        defaultIcon.id = "profile-default";

        defaultIcon.className =
            "profile-default";

        defaultIcon.setAttribute(
            "aria-label",
            "プロフィール画像未設定"
        );

        defaultIcon.textContent = "👤";

        profileWrapper.appendChild(defaultIcon);
    }


    defaultIcon.classList.remove("hidden");
}


//==========================
// 自己紹介文字数
//==========================

function updateProfileMessageCount() {

    if (
        !profileMessage ||
        !profileMessageCount
    ) {
        return;
    }

    profileMessageCount.textContent =
        `${profileMessage.value.length} / ${profileMessage.maxLength}`;
}


if (profileMessage) {

    profileMessage.addEventListener(
        "input",
        updateProfileMessageCount
    );
}
