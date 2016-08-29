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

     $(".close-toc").click(function() {
         $("nav.toc").removeClass("active")
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
               var expand_icon = $(this).children('svg.expand-proof');
							 if (expand_icon.attr('class') == 'icon icon-cross expand-proof') {
												 expand_icon.replaceWith(icon('plus', 'expand-proof'));
							 } else {
												 expand_icon.replaceWith(icon('cross', 'expand-proof'));
							 };

               $(this).siblings("div.proof_content").slideToggle()
           })

		$("a.proof").click(
				function() {
					var ref= $(this).attr('href').split('#')[1];
					var proof = $('#'+ref)
					proof.children('.proof_content').each(
							function() { 
								var proof_content = $(this)
								proof_content.show().addClass('hilite')
								setTimeout(function(){
									proof_content.removeClass('hilite')
									}, 1000);
							})
          var expand_icon = proof.find('svg.expand-proof');
					expand_icon.replaceWith(icon('cross', 'expand-proof'));
					
				})

    $("li.quizz-qright").click(
           function() {
               $(this).toggleClass('active-qright')
               $(this).children("svg").toggle()
               $(this).siblings().each(function() {
                 $(this).removeClass('active-qright');
                 $(this).removeClass('active-qwrong');
                 $(this).children("svg").hide()
               });
           })

    $("li.quizz-qwrong").click(
           function() {
               $(this).toggleClass('active-qwrong')
               $(this).children("svg").toggle()
               $(this).siblings().each(function() {
                 $(this).removeClass('active-qright');
                 $(this).removeClass('active-qwrong');
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

		var showmore_level = 1;

		showmore_update = function() {
			switch(showmore_level) {
				case 0:
				 $("svg#showmore-minus").hide();
				 $("svg#showmore-plus").show();
				 $("div.content > p").each(
						 function(){
							 $(this).hide();
						 });
				 $("div.proof_wrapper").each(
						 function(){
							 $(this).hide();
						 });
				 break;
				case 1:
				 $("svg#showmore-minus").show();
				 $("svg#showmore-plus").show();
				 $("div.content > p").each(
						 function(){
							 $(this).show();
						 });
				 $("div.proof_content").each(
						 function(){
							 $(this).hide();
						 });
				 break;
				case 2:
				 $("svg#showmore-minus").show();
				 $("svg#showmore-plus").hide();
				 $("div.content > p").each(
						 function(){
							 $(this).show();
						 });
				 $("div.proof_content").each(
						 function(){
							 $(this).show();
						 });
			}
		};

		$("svg#showmore-minus").click(
				function() {
					if (showmore_level > 0) {
						showmore_level -= 1;
						showmore_update();
					}
				})

		$("svg#showmore-plus").click(
				function() {
					if (showmore_level < 2) {
						showmore_level += 1;
						showmore_update();
					}
				})

		$("div.proof_content p:last-child").append('<span class="qed">□</span>')
  });

