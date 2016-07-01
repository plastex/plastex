$(document).ready(function() {
    $("#toc-toggle").click(function() {
        $("nav.toc").toggleClass("active")
    });

   $("button.uses").click(function() {
     $(this).siblings("div.thm_uses").slideDown()
   })
  });

