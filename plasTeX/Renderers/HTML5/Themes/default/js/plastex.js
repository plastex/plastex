$.fn.toggleText = function(t1, t2){
  if (this.text() == t1) this.text(t2);
  else                   this.text(t1);
  return this;
};

$(document).ready(function() {
    $("#toc-toggle").click(function() {
        $("nav.toc").toggleClass("active")
    });

   $("button.uses").click(
		   function() {
			   $(this).siblings("div.thm_uses").slideToggle()
		   })

   $("button.expand-toc").click(
		   function() {
			   $(this).toggleText('x', '+');
			   $(this).siblings("ul").slideToggle('fast')
		   })
  });

