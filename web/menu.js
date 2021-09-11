function toggle_menu(){
    var button = document.getElementById("menu-button");

    // true if we want to open the menu, false if we want to close it
    var open = button.getAttribute("state") == "open";

    if(open === true){
        $(".menu-container").css("animation", "openMenu .3s");
        $(".menu-container").css("display", "flex");
        $("body").css("overflow", "hidden");
        button.setAttribute("state", "close");
    }
    else{
        $(".menu-container").css("animation", "closeMenu .3s");
        setTimeout(function(){
            $(".menu-container").css("display", "none");
        }, 300);
        $("body").css("overflow", "");
        button.setAttribute("state", "open");
    }
}

// Dropdown section
var dropdownVar = true;
function dropdown(element){
    dropdownVar = !dropdownVar;
    if(dropdownVar === true){
        $(element).css("animation", "dropdownAnimationUp .2s");
        setTimeout(function(){
            $(element).css("display", "none");
        }, 0);
        $(element).prev().removeClass("arrowDown");
    }
    else {
        $(element).css("display", "block")
        $(element).prev().toggleClass("arrowDown");
        $(element).css("animation", "dropdownAnimationDown .2s");
    }
}

$(document).mousedown(function(e){
    var container = $(".menu-container");
    // If the target of the click isn't the container
    if(openMenu === true && !container.is(e.target) && container.has(e.target).length === 0){
        navMenu();
    }
});