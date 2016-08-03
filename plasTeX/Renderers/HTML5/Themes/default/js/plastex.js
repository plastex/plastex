$.fn.toggleText = function(t1, t2){
  if (this.text() == t1) this.text(t2);
  else                   this.text(t1);
  return this;
};

$(document).ready(function() {
     var icon = function($icon, $class, $id) {
		 if ($id) {
			 $id = ' id="'+$id+'"';
		 } else {
			 $id = '';
		 }

		 return '<svg'+ $id + ' class="icon icon-' + $icon + ' ' + $class +'"><use xlink:href="symbol-defs.svg#icon-'+$icon+'"></use></svg>'
	 };

     $("#toc-toggle").click(function() {
         $("nav.toc").toggleClass("active")
     });

    $("nav.toc").on("click", "svg.expand-toc",
            function() {
				$(this).siblings("ul").slideToggle('fast');

				if ($(this).attr('class') == 'icon icon-cross expand-toc') {
                  $(this).replaceWith(icon('plus', 'expand-toc'));
				} else {
                  $(this).replaceWith(icon('cross', 'expand-toc'));
				};

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

    $("li.quizz-right").click(
           function() {
               $(this).toggleClass('active-right')
               $(this).children("svg").toggle()
               $(this).siblings().each(function() {
                 $(this).removeClass('active-right');
                 $(this).removeClass('active-wrong');
                 $(this).children("svg").hide()
               });
           })

    $("li.quizz-wrong").click(
           function() {
               $(this).toggleClass('active-wrong')
               $(this).children("svg").toggle()
               $(this).siblings().each(function() {
                 $(this).removeClass('active-right');
                 $(this).removeClass('active-wrong');
                 $(this).children("svg").hide()
               });
           })

    $("button.modal").click(
        function() {
          $(this).next("div.modal-container").css('display', 'flex');
        })
    $("button.closebtn").click(
        function() {
          $(this).parent().parent().parent().hide();
        })
  });

