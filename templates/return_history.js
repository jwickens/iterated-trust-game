$('#history{{ context.treatment.id }} li: first').append('{{ context.actions|safe }}');
$('#getHistory').html('/trustgame/json/loadhistory/{{ context.treatment.id }}/{{ context.game_id }}/{{ context.turn_num }}');
