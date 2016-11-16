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


    $("div.proof_content p:last").append('<span class="qed">□</span>')

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
                proof.show()
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


    $("button.modal").click(
        function() {
          $(this).next("div.modal-container").css('display', 'flex');
        })
    $("button.closebtn").click(
        function() {
          $(this).parent().parent().parent().hide();
        })
});
