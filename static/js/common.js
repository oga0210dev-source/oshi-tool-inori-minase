function showToast(message, type = "error") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast";
    toast.classList.add(type);
    toast.classList.add("show");
    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);

}

document.addEventListener("DOMContentLoaded",()=>{
    document.querySelectorAll('a[href="#"], .not-implemented').forEach(item=>{
        item.addEventListener("click",(e)=>{
            e.preventDefault();
            showToast("この機能は未実装です");
        });
    });
});