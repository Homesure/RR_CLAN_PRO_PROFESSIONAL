console.log("RR CLAN PRO Professional MVP loaded");

document.addEventListener("DOMContentLoaded", function () {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.display = "none";
        }, 4500);
    });
});
