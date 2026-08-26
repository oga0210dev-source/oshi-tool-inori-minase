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

                /* 並び順を変更した */
                markFormChanged();
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

    /* 曲を追加した */
    markFormChanged();

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

    /* 曲を削除した */
    markFormChanged();
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

            /*
             * 保存成功したので
             * 未保存変更を解除
             */
            markFormSaved();

            alert(result.message);

            window.location.href =
                "/home/live/prediction";

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
 * ページ表示時
 * ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function(){
        initSortable();
    }
);


/* =========================================================
 * Xでシェア
 * ========================================================= */

async function sharePrediction(predictionId){

    const shareUrl =
        `${window.location.origin}/home/live/prediction/share/${predictionId}`;

    const responseText =
        `水瀬いのり「セトリ予測」のセトリを予測中！\n\n` +
        `${shareUrl}\n\n` +
        `#水瀬いのり #いのりまち`;

    const encodedText =
        encodeURIComponent(responseText);

    const xWebUrl =
        `https://x.com/intent/post?text=${encodedText}`;

    /*
     * Xアプリを起動
     */
    window.location.href =
        `twitter://post?message=${encodedText}`;

    /*
     * Xアプリが起動しなかった場合は
     * Web版Xへフォールバック
     */
    setTimeout(function(){

        window.open(
            xWebUrl,
            "_blank",
            "noopener,noreferrer"
        );

    }, 1000);
}