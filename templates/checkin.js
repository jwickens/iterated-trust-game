checkinURL = '/trustgame/json/checkin/{{ context.pk }}/{{ context.game_state }}';
checkin = function () {
	$.ajax({ url: checkinURL, type: 'GET', success: callback });
	timeout = window.setTimeout(checkin, 5000);
};
checkin();
$.getScript('/trustgame/json/loadscreen/{{ context.pk }}/');
