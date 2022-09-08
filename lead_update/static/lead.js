function fillValues(lead_id) {
	alert("Hello " + lead_id);
}

function statusChange() {
	var status_dropdown = document.getElementById("status");
	var dq_reason_dropdown = document.getElementById("dq_reason");
	var opp_number_text = document.getElementById("opp_number");
	
	if(status_dropdown.value == "Disqualified") {
		dq_reason_dropdown.disabled = false;
	} else {
		dq_reason_dropdown.disabled = true;
	}
	
	if(status_dropdown.value == "Opportunity") {
		opp_number_text.disabled = false;
	} else {
		opp_number_text.disabled = true;
	}
}
function save() {
	
	jQuery('#save_button').prop('disabled', true).html('Saving');
	
	post_body = {
		lead_id: 		jQuery('#lead_id').val(),
		status:  		jQuery('#status').val(),
		opp_number: 	jQuery('#opp_number').val(),
		dq_reason: 		jQuery('#dq_reason').val(),
		dsr: 			jQuery('#dsr').val(),
		presales: 		jQuery('#presales').val(),
		notes: 			jQuery('#notes').val()
		};
		
	j = JSON.stringify(post_body);
	
	jQuery.post({
		url: '/lead/' + post_body.lead_id,
		contentType: "application/json; charset=utf-8",
		data: j
	}).done(save_confirm);		
} 

function save_confirm(data) {	
	console.log(data);
	if(data.API == 'OK') {
		jQuery('#save_button').prop('disabled', false).css("background-color","#52ba68").html('Saved');
	} else {
		jQuery('#save_button').prop('disabled', false).css("background-color","#d64d40").html('Failed (did not save)');
	}
}

function save_reset() {
	jQuery('#save_button').prop('disabled', false).css("background-color","#8cc4d3").html('Save');
}