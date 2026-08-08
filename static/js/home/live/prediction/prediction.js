/* =========================================================
 * 曲選択モーダル
 * ========================================================= */

function openSongModal(){
    document.getElementById("song-modal").style.display = "block";
}

function closeSongModal(){
    document.getElementById("song-modal").style.display = "none";
}

function resetSongModal(){
    document.getElementById("song-search").value = "";
    document.getElementById("is-medley").checked = false;

    document.querySelectorAll('input[name="song"]').forEach(item => {
        item.checked = false;
    });

    document.querySelectorAll(".song-select").forEach(item => {
        item.style.display = "";
    });

    const songList = document.querySelector(".song-list");

    if(songList){
        songList.scrollTop = 0;
    }
}


/* =========================================================
 * Sortable
 * ========================================================= */

let sortable = null;

function initSortable(){

    const setlistArea =
        document.getElementById("setlist-area");

    if(!setlistArea){
        return;
    }

    if(sortable){
        sortable.destroy();
    }

    sortable = new Sortable(
        setlistArea,
        {
            animation:150,
            handle:".drag-handle",
            draggable:".setlist-item",
            onEnd:function(){
                updateOrder();
            }
        }
    );
}


/* =========================================================
 * 曲追加
 * ========================================================= */

function addSong(){

    const noSetlist =
        document.querySelector(".no-setlist");

    if(noSetlist){
        noSetlist.remove();
    }

    const isMedley =
        document.getElementById("is-medley").checked;

    const selectedSongs =
        document.querySelectorAll(
            'input[name="song"]:checked'
        );

    const setlistArea =
        document.getElementById("setlist-area");

    if(selectedSongs.length === 0){
        alert("曲を選択してください。");
        return;
    }

    /* 今回追加するメドレー番号 */
    let medleyOrder = null;

    if(isMedley){

        let maxMedleyOrder = 0;

        document.querySelectorAll(".setlist-item")
        .forEach(item => {

            const order =
                Number(item.dataset.medleyOrder);

            if(order > maxMedleyOrder){
                maxMedleyOrder = order;
            }
        });

        medleyOrder = maxMedleyOrder + 1;
    }

    selectedSongs.forEach(song => {

        const order =
            document.querySelectorAll(
                ".setlist-item"
            ).length + 1;

        const songName =
            song.parentElement.dataset.songName;

        const medleyBadge =
            isMedley
                ? `<span class="medley-badge">
                       メドレー${medleyOrder}
                   </span>`
                : "";

        const item =
            document.createElement("div");

        item.className = "setlist-item";

        item.dataset.songId = song.value;
        item.dataset.isMedley = isMedley;
        item.dataset.medleyOrder =
            isMedley ? medleyOrder : "";

        item.innerHTML = `
            <div class="song-order">
                ${order}
            </div>

            <div class="song-name">
                ${songName}
                ${medleyBadge}
            </div>

            <button class="delete-btn"
                    type="button"
                    onclick="deleteSong(this)">
                ×
            </button>

            <div class="drag-handle">
                ☰
            </div>
        `;

        setlistArea.appendChild(item);
    });

    updateOrder();
    initSortable();

    resetSongModal();
    closeSongModal();
}


/* =========================================================
 * 並び順更新
 * ========================================================= */

function updateOrder(){

    const items =
        document.querySelectorAll(
            ".setlist-item"
        );

    items.forEach((item,index) => {

        item.querySelector(".song-order")
            .textContent = index + 1;
    });

    if(items.length === 0){

        document.getElementById(
            "setlist-area"
        ).innerHTML = `
            <div class="no-setlist">
                セットリストが登録されていません
            </div>
        `;
    }
}


/* =========================================================
 * 保存用データ取得
 * ========================================================= */

function getSetlistOrder(){

    const order = [];

    document.querySelectorAll(
        ".setlist-item"
    ).forEach((item,index) => {

        order.push({
            song_id: item.dataset.songId,
            song_order: index + 1,
            is_medley:
                item.dataset.isMedley === "true",
            medley_order:
                item.dataset.isMedley === "true"
                    ? Number(item.dataset.medleyOrder)
                    : null
        });
    });

    return order;
}


/* =========================================================
 * 曲削除
 * ========================================================= */

function deleteSong(button){

    const item =
        button.closest(".setlist-item");

    if(!item){
        return;
    }

    item.remove();

    updateOrder();
    initSortable();
}


/* =========================================================
 * 曲検索
 * ========================================================= */

function searchSong(){

    const keyword =
        document.getElementById("song-search")
        .value
        .toLowerCase();

    document.querySelectorAll(".song-select")
    .forEach(item => {

        const name =
            item.textContent.toLowerCase();

        item.style.display =
            name.includes(keyword)
                ? ""
                : "none";
    });
}


/* =========================================================
 * 予測セトリ保存
 * ========================================================= */

async function savePrediction(){

    const songs =
        getSetlistOrder();

    if(songs.length === 0){
        alert("予測する曲を追加してください。");
        return;
    }

    if(!confirm("予測セトリを保存しますか？")){
        return;
    }

    try{

        const response =
            await fetch(
                `/home/live/prediction/new/${liveId}/save`,
                {
                    method:"POST",
                    headers:{
                        "Content-Type":"application/json"
                    },
                    body:JSON.stringify(songs)
                }
            );

        const result =
            await response.json();

        if(result.success){

            alert(result.message);

        }else{

            alert(
                result.message ||
                "保存に失敗しました。"
            );
        }

    }catch(error){

        console.error(error);

        alert(
            "保存中にエラーが発生しました。"
        );
    }
}


/* =========================================================
 * 予測セトリ削除
 * ========================================================= */

async function deletePrediction(predictionId){

    if(!confirm(
        "このライブの予測セトリを削除しますか？\n\n" +
        "削除した予測は元に戻せません。"
    )){
        return;
    }

    try{

        const response =
            await fetch(
                `/home/live/prediction/${predictionId}/delete`,
                {
                    method:"POST"
                }
            );

        const result =
            await response.json();

        if(result.success){

            alert(result.message);
            window.location.reload();

        }else{

            alert(
                result.message ||
                "削除に失敗しました。"
            );
        }

    }catch(error){

        console.error(error);

        alert(
            "削除中にエラーが発生しました。"
        );
    }
}


/* =========================================================
 * セトリ予測シェア
 * ========================================================= */

let shareText = "";


/* シェアポップアップを閉じる */

function closeShareModal(){

    document.getElementById(
        "share-modal"
    ).style.display = "none";
}


/* シェア開始 */

async function sharePrediction(
    liveName,
    predictionId
){

    const modal =
        document.getElementById("share-modal");

    const image =
        document.getElementById("share-image");

    const text =
        document.getElementById("share-text");

    /* 投稿文 */
    shareText =
        `水瀬いのり「${liveName}」のセトリを予測中！\n\n` +
        `#水瀬いのり #いのりまち`;

    text.value = shareText;

    /* ポップアップ表示 */
    modal.style.display = "block";

    /* 画像を初期化 */
    image.removeAttribute("src");
    image.alt = "セトリ画像を生成しています";

    shareImageBlob = null;

    try{

        /* セトリ情報取得 */
        const response =
            await fetch(
                `/home/live/prediction/${predictionId}/share`
            );

        if(!response.ok){
            throw new Error(
                `APIエラー: HTTP ${response.status}`
            );
        }

        const result =
            await response.json();

        if(!result.success){
            throw new Error(
                result.message ||
                "セトリ情報の取得に失敗しました。"
            );
        }

        /* 画像生成 */
        const imageData =
            createPredictionImage(
                result.prediction,
                result.songs
            );

        if(!imageData){
            throw new Error(
                "画像データを生成できませんでした。"
            );
        }

        /* 画面に表示 */
        image.src = imageData;
        image.alt = "セトリ予測";

    }catch(error){

        console.error(
            "シェア画像生成エラー:",
            error
        );

        alert(
            "セトリ画像の生成に失敗しました。\n\n" +
            error.message
        );

        closeShareModal();
    }
}


/* =========================================================
 * セトリ画像生成
 * ========================================================= */

function createPredictionImage(
    prediction,
    songs
){

    const canvas =
        document.createElement("canvas");

    const ctx =
        canvas.getContext("2d");

    if(!ctx){
        throw new Error(
            "Canvasを取得できませんでした。"
        );
    }

    const width = 800;
    const padding = 50;
    const rowHeight = 58;
    const titleHeight = 130;
    const footerHeight = 60;

    const height =
        titleHeight +
        songs.length * rowHeight +
        footerHeight;

    canvas.width = width;
    canvas.height = height;

    /* 背景 */
    ctx.fillStyle = "#ffffff";

    ctx.fillRect(
        0,
        0,
        width,
        height
    );

    /* ライブ名 */
    ctx.fillStyle = "#333333";
    ctx.font = "bold 32px sans-serif";

    ctx.fillText(
        prediction.live_name || "",
        padding,
        55
    );

    /* ツアー名 */
    ctx.fillStyle = "#777777";
    ctx.font = "20px sans-serif";

    ctx.fillText(
        prediction.tour_name || "",
        padding,
        90
    );

    /* セトリ */
    let y = titleHeight;

    songs.forEach((song,index) => {

        /* 曲番号 */
        ctx.fillStyle = "#888888";
        ctx.font = "20px sans-serif";

        ctx.fillText(
            `${index + 1}.`,
            padding,
            y
        );

        /* 曲名 */
        ctx.fillStyle = "#333333";
        ctx.font = "bold 20px sans-serif";

        let songName =
            song.song_name || "";

        if(song.is_medley){

            songName +=
                `  メドレー${song.medley_order}`;
        }

        ctx.fillText(
            songName,
            padding + 50,
            y
        );

        /* 区切り線 */
        ctx.strokeStyle = "#eeeeee";

        ctx.beginPath();

        ctx.moveTo(
            padding,
            y + 18
        );

        ctx.lineTo(
            width - padding,
            y + 18
        );

        ctx.stroke();

        y += rowHeight;
    });

    /* フッター */
    ctx.fillStyle = "#999999";
    ctx.font = "16px sans-serif";

    ctx.fillText(
        "セトリ予測",
        padding,
        height - 20
    );

    return canvas.toDataURL(
        "image/png"
    );
}


/* =========================================================
 * 投稿文コピー
 * ========================================================= */

async function copyShareText(){

    try{

        await navigator.clipboard.writeText(
            shareText
        );

        alert(
            "投稿文をコピーしました。"
        );

    }catch(error){

        console.error(error);

        const textarea =
            document.getElementById(
                "share-text"
            );

        textarea.removeAttribute(
            "readonly"
        );

        textarea.select();

        document.execCommand("copy");

        textarea.setAttribute(
            "readonly",
            ""
        );

        alert(
            "投稿文をコピーしました。"
        );
    }
}


/* =========================================================
 * ページ表示時
 * ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){
        initSortable();
    }
);