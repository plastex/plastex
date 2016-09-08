$(document).ready(function() {
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
})

