$.fn.toggleText = function(t1, t2){
  if (this.text() == t1) this.text(t2);
  else                   this.text(t1);
  return this;
};

$(document).ready(function() {
     $("#toc-toggle").click(function() {
         $("nav.toc").toggleClass("active")
     });

    $("span.expand-toc").click(
            function() {
                $(this).toggleClass('fa-close').toggleClass('fa-plus');
                $(this).siblings("ul").slideToggle('fast')
            })

    $("button.uses").click(
           function() {
               $(this).siblings("div.thm_uses").slideToggle()
           })
    
    $("div.proof_heading").click(
           function() {
               $(this).children('span.expand-proof').toggleClass('fa-close').toggleClass('fa-plus');
               $(this).siblings("div.proof_content").slideToggle()
           })
  });

