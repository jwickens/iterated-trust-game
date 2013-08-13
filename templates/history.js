$('#history{{ context.treatment.id }}').prepend('<li>{{ context.actions|safe }}</li>');
$('#getHistory').html('/trustgame/json/loadhistory/{{ context.treatment.id }}/{{ context.game_id }}/{{ context.turn_num }}');
