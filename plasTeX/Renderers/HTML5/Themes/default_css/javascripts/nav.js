$(document).ready(function() {
    $(".mobile").click(function() {
        $("nav").toggleClass("active")
    }), $("nav ul li ul").each(function() {
        $(this).before('<span class="arrow"></span>')
    }), $("nav ul li").click(function() {
        $(this).children("ul").toggleClass("active"), $(this).children(".arrow").toggleClass("rotate")
    })
});
