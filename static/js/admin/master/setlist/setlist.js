function addSong(){
    const noSetlist = document.querySelector(".no-setlist");

    if (noSetlist) {
        noSetlist.remove();
    }

    const selectedSongs = document.querySelectorAll(
        'input[name="song"]:checked'
    );

    const setlistArea = document.getElementById(
        "setlist-area"
    );

    selectedSongs.forEach((song, index)=>{
        const label = song.parentElement;
        const songName = label.textContent.trim();
        const item = document.createElement("div");
        item.className = "setlist-item";
        item.innerHTML = `
            <div class="song-order">
                ${order}
            </div>

            <div class="song-name">
                ${songName}
            </div>

            <div class="drag-handle">
                ☰
            </div>
        `;
        setlistArea.appendChild(item);
    });
    closeSongModal();
}

const sortable = new Sortable(
    document.getElementById("setlist-area"),
    {
        animation:150,
        handle:".drag-handle",
        onEnd:function(){
            updateOrder();
        }
    }
);

const order=[];
document.querySelectorAll(".setlist-item").forEach((item,index)=>{
    order.push({
        song_id:item.dataset.songId,
        song_order:index+1
    });
});

function updateOrder(){
    document.querySelectorAll(".setlist-item").forEach((item,index)=>{
        item.querySelector(".song-order").textContent=index+1;
    });
}