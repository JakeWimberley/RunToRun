// depends on the presence of a div w/ id="threadToEventModal"
// with CSS making it modal (or at the minimum, hidden on load)
// containing fieldset w/ id="threadToEventFields"
// the fieldset should be part of a form otherwise defined in the div
function populateFormThreadToEvent(whenStr,threadId) {
	$.get('/async/eventsAtTime', { when: whenStr, threadId: threadId }, function(eventData) {
		// obj returned maps event pk -> [title, timerange, owner, should-be-checked]
		$('#threadToEventFields').empty().append($("<legend>Matching datetime " + whenStr + "</legend>"));
		var listOfMatchingEvents = '';
		$.each(eventData, function(pk,info) {
			if (listOfMatchingEvents.length > 0) listOfMatchingEvents = listOfMatchingEvents.concat(',');
			listOfMatchingEvents = listOfMatchingEvents + pk;
			var title = info[0];
			var owner = info[1];
			var bCheck = info[2];
			if (bCheck) {
				$('#threadToEventFields').append($("<input>")
				.attr({
					type: "checkbox",
					class: "relationSelection",
					name: "newRelations",
					value: pk,
					id: "selection" + pk,
					checked: "checked",
				}));
				$('#threadToEventFields').append($("<label>"+title+"</label>").attr("for","selection"+pk));
				$('#threadToEventFields').append($("<br>"));
			} else {
				$('#threadToEventFields').append($("<input>")
				.attr({
					type: "checkbox",
					class: "relationSelection",
					name: "newRelations",
					value: pk,
					id: "selection" + pk,
				}));
				$('#threadToEventFields').append($("<label>"+title+"</label>").attr("for","selection"+pk));
				$('#threadToEventFields').append($("<br>"));
			}
		});
		$('#threadToEventFields').append($("<input>")
		.attr({
			type: "hidden",
			name: "threadId",
			value: threadId,
		}));
		$('#threadToEventFields').append($("<input>")
		.attr({
			type: "hidden",
			name: "allMatchingEvents",
			value: listOfMatchingEvents,
		}));
		//$(".relationSelection").checkboxradio({ icon: false });
	});
	$("#threadToEventModal").show();
}
