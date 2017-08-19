function check_answer(challenge_id){
	given_answer = $('#'+challenge_id+' input[name="answer"]').val();
	

	$.ajax(
		{ 	url:"/check_answer",
			method: "POST",
			data: { 
					"challenge_id": challenge_id,
					"answer": given_answer
				  },
			dataType: "json",

			success:(function(response){

				if ( response['correct'] == 1){
					var new_score = response['new_score'];
					$.notify('Correct!', 'success');
					$('#score').text( '[' + String(new_score) + ']' );

					correct_challenge(challenge_id);
				}
				if ( response['correct'] == 0){
					$.notify('Incorrect!', 'error');
				}
				if ( response['correct'] == -1){
				$.notify('You have already solved this challenge!', 'warn');
				}
	})});

	return false;
}


function correct_challenge(challenge_id){

	$('#'+ challenge_id ).children().first().next().slideUp();
	$('#'+ challenge_id ).children().first().css({
		'border-bottom': '1px solid lightgreen',
		'color': 'lightgreen',
		// 'opacity' : '0.3',
	});
}

$(document).ready(function(){
	$('#trainings img').each(function(){

		if ($(this).attr('src') != ""){ 
			name = $(this).attr('alt')

			$(this).parent().html($(this).parent().html() + "<p><span>" + name + "</span></p>") 
			$(this).attr('alt','') 
		}
	});


	$('.challenge_title').hover(function(){

		if ( $(this).css('color') == 'rgb(144, 238, 144)' ){
			$(this).find('.create_writeup').toggle();
		}
	});
	
	$('.edit_icon').attr('width','15px');


	$('.challenge_title').mouseenter(function(){
		$(this).find('.delete_icon').show();
		$(this).find('.edit_icon').show();
	});
	$('.challenge_title').mouseleave(function(){
		$(this).find('.delete_icon').hide();
		$(this).find('.edit_icon').hide();
	});

	$('tr').mouseenter(function(){
		$(this).find('.delete_icon').show();
		$(this).find('.edit_icon').show();
	});
	$('tr').mouseleave(function(){
		$(this).find('.delete_icon').hide();
		$(this).find('.edit_icon').hide();
	});


	$('.training_block').mouseenter(function(){
		$(this).find('.delete_icon').show();
		$(this).find('.edit_icon').show();
	});
	$('.training_block').mouseleave(function(){
		$(this).find('.delete_icon').hide();
		$(this).find('.edit_icon').hide();
	});



	$('.confirm').click(function() {
	    return window.confirm("Are you sure you would like to delete this? This cannot be undone!");
	});
})
