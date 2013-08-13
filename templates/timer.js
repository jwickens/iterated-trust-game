{% if context.game_state == "transfer" or context.game_state == "return" or context.game_state == 'transition' or context.group == 'fake' %}
{% if context.game_state != 'restart' and context.game_state != 'expired' %}
{% if context.time_limit > 0 %}
	var left = {{ context.time_limit }} - 5,
	    speed = 1000 * left,
	    rect = paper.rect(0, 0, 300, 25).attr({stroke:'none'}),
	    counter = paper.text(20, 35, '0:'+left.toString()),
	    label = {"fill": 'white', "font-size": 20},
	    count;
	rect.attr({ fill:'#DF151A', stroke:'black' } );
	rect.animate({ x: 0, width: 0 }, speed );
	counter.attr(label);
	clearTimeout(count_timeout);
	count = function () {
		if (left > 0) {
			left -= 1;
			var seconds = left;
			var minutes = 0;
			while (seconds > 60) { 
				seconds -= 60;
				minutes += 1;
			}
			counter.attr({text:minutes.toString()+":"+seconds.toString()});
			count_timeout = window.setTimeout(count, 1000);
		}
	};
	count();
{% endif %}
{% endif %}
{% endif %}

