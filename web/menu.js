import("https://kit.fontawesome.com/9fa2f75402.js") /* font awesome icons */

let menuBtn = $(".menu-btn");
let menu = $(".menu");
let menuIcon = $(".menu-icon");
let menuToggle = () => {
    menu.toggleClass("menu-active");
    menuIcon.toggleClass("menu-icon-open");
    $("body").toggleClass("overflow-hidden");
}

// when clicking outside the menu to close it
$(document).click((e) => {
	if (menu.hasClass("menu-active")) {
  	    menuToggle();
    }
});

menuBtn.click((e) => {
    e.stopPropagation();
    menuToggle();
});

menu.click((e) => {
    e.stopPropagation();
});
