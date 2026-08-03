function openSongModal(){
    document.getElementById("song-modal").style.display = "block";
}

function closeSongModal(){
    document.getElementById("song-modal").style.display = "none";
}

function resetSongModal(){

    document.getElementById("album-search").value = "";
    document.getElementById("song-search").value = "";

    document.getElementById("is-medley").checked = false;

    document.querySelectorAll('input[name="song"]').forEach(item=>{
        item.checked = false;
    });

    document.querySelectorAll(".song-select").forEach(item=>{
        item.style.display = "";
    });

    document.querySelectorAll(".album-name").forEach(item=>{
        item.style.display = "";
    });

    document.querySelector(".song-list").scrollTop = 0;
}

function addSong(){

    const noSetlist = document.querySelector(".no-setlist");

    if(noSetlist){
        noSetlist.remove();
    }

    const isMedley = document.getElementById("is-medley").checked;

    const selectedSongs = document.querySelectorAll(
        'input[name="song"]:checked'
    );

    const setlistArea = document.getElementById("setlist-area");

    selectedSongs.forEach(song=>{

        const order =
            document.querySelectorAll(".setlist-item").length + 1;

        const songName =
            song.parentElement.textContent.trim();

        const medleyBadge =
            isMedley
                ? '<span class="medley-badge">メドレー</span>'
                : '';

        const item = document.createElement("div");

        item.className = "setlist-item";
        item.dataset.songId = song.value;
        item.dataset.isMedley = isMedley;

        item.innerHTML = `
            <div class="song-order">
                ${order}
            </div>

            <div class="song-name">
                ${songName}
                ${medleyBadge}
            </div>

            <button class="delete-btn" onclick="deleteSong(this)" style="display:none;">
                ×
            </button>

            <div class="drag-handle" style="display:none;">
                ☰
            </div>
        `;

        setlistArea.appendChild(item);

        const editMode =
            document.getElementById("save-area").style.display === "block";

        if(editMode){

            item.querySelector(".delete-btn")
                .style.display="block";

            item.querySelector(".drag-handle")
                .style.display="block";
        }
    });

    resetSongModal();

    closeSongModal();

}

let sortable = null;

function editSetlist(){

    document.getElementById("edit-btn")
        .style.display="none";

    document.getElementById("cancel-area")
        .style.display="block";

    document.getElementById("save-area")
        .style.display="block";

    document.getElementById("add-area")
        .style.display="block";


    document.querySelectorAll(".drag-handle")
        .forEach(item=>{
            item.style.display="block";
        });


    document.querySelectorAll(".delete-btn")
        .forEach(item=>{
            item.style.display="block";
        });

    if(sortable){
        sortable.destroy();
    }

    sortable = new Sortable(
        document.getElementById("setlist-area"),
        {
            animation:150,
            handle:".drag-handle",
            onEnd:function(){
                updateOrder();
            }
        }
    );
}

function updateOrder(){

    const items=document.querySelectorAll(".setlist-item");

    items.forEach((item,index)=>{
        item.querySelector(".song-order").textContent=index+1;
    });

    if(items.length===0){
        document.getElementById("setlist-area").innerHTML=
        `
        <div class="no-setlist">
            セットリストが登録されていません
        </div>
        `;
    }
}

function getSetlistOrder(){

    const order = [];

    document.querySelectorAll(".setlist-item").forEach((item,index)=>{

        order.push({
            song_id:item.dataset.songId,
            song_order:index + 1,
            is_medley:item.dataset.isMedley === "true"
        });

    });

    return order;

}

async function saveSetlist(){

    const response = await fetch(
        `/admin/master/setlist/LIVE/${liveId}/save`,
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(getSetlistOrder())
        }
    );

    const result = await response.json();

    if(result.success){

        alert(result.message);

        if(sortable){
            sortable.destroy();
            sortable=null;
        }

        document.getElementById("edit-btn")
            .style.display="block";

        document.getElementById("cancel-area")
            .style.display="none";

        document.getElementById("save-area")
            .style.display="none";

        document.getElementById("add-area")
            .style.display="none";


        document.querySelectorAll(".drag-handle")
            .forEach(item=>{
                item.style.display="none";
            });


        document.querySelectorAll(".delete-btn")
            .forEach(item=>{
                item.style.display="none";
            });
    }
}

function deleteSong(button){

    const item = button.closest(".setlist-item");

    item.remove();

    updateOrder();

    document.getElementById("save-area")
        .style.display="block";

}

function cancelEdit(){

    if(confirm("変更内容を破棄しますか？")){

        location.reload();

    }

}