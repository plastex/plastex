$(document).ready(function() {
	showmore_update = function(showmore_level) {
		$.cookie('showmore_level', showmore_level, { expires : 10 });
		console.log('update', showmore_level);
		switch(showmore_level) {
			case 0:
			 $("svg#showmore-minus").hide();
			 $("figure").hide();
			 $("svg#showmore-plus").show();
			 $("div.content > p").each(
					 function(){
						 $(this).hide();
					 });
			 $("div.proof_wrapper").each(
					 function(){
						 $(this).hide();
					 });
			 $("footer").hide();
			 break;
			case 1:
			 $("svg#showmore-minus").show();
			 $("figure").show();
			 $("svg#showmore-plus").show();
			 $("div.content > p").each(
					 function(){
						 $(this).show();
					 });
			 $("div.proof_content").each(
					 function(){
						 $(this).hide();
					 });
			 $("svg.expand-proof").show();
			 $("footer").show();
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
			 $("svg.expand-proof").hide();
		}
	};

	cookie_level = function(){
      var showmore_level = parseInt($.cookie('showmore_level'));
	  if (isNaN(showmore_level)) {
		  return 1;
	  } else {
		  return showmore_level;
	  }
	};
	showmore_update(cookie_level());

	$("svg#showmore-minus").click(
			function() {
                var showmore_level = cookie_level();
				console.log('click ', showmore_level);
				if (showmore_level > 0) {
					showmore_level -= 1;
					showmore_update(showmore_level);
				}
			})

	$("svg#showmore-plus").click(
			function() {
                var showmore_level = cookie_level();
				console.log('click ', showmore_level);
				if (showmore_level < 2) {
					showmore_level += 1;
					showmore_update(showmore_level);
				}
			})
})
