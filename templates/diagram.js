{% extends 'diagram_base.js' %}
{% block drawing %}
	try {
		paper.remove();
	}
	catch (error) {}	
	var paper = new Raphael("drawing{{ context.pk }}", "100%", "100%"),
	    glow,
	    p0 = paper.Participant("{{ context.shape0 }}",	500,	446,	"{{ context.color0 }}" ,  "{{ context.label0|safe }}"),
	    p1 = paper.Participant("{{ context.shape1 }}",	100,	446,	"{{ context.color1 }}" ,  "{{ context.label1|safe }}"),
	    p2 = paper.Participant("{{ context.shape2 }}",	300,	100,	"{{ context.color2 }}" ,  "{{ context.label2|safe }}"),
	    label = {"fill": 'white', "font-size": 20},
	    t0 = paper.text(p0.x ,p0.y , p0.state),
	    t1 = paper.text(p1.x ,p1.y , p1.state),
	    t2 = paper.text(p2.x ,p2.y , p2.state),
	    texts = paper.set(),
	    glowattr = {'color': 'yellow', 'width': 15};
	p{{ context.game_id }}.shape.glow({'color':'yellow'});	
{% if context.condition.info_condition == "global" or context.game_id != 2 %}
	var ar1 = paper.arrows(p0.x-70, p0.y,	p1.x+70, p1.y, p0, p1, 	{{ context.s01 }},	{{ context.s10 }},	{{ context.r01 }},	{{ context.r10 }});
{% endif %}
{% if context.condition.info_condition == "global" or context.game_id != 0 %}
	var ar2 = paper.arrows(p1.x+30, p1.y-80, p2.x-50, p2.y+50, p1, p2, 	{{ context.s12 }},	{{ context.s21 }},	{{ context.r12 }},	{{ context.r21 }});
{% endif %}
{% if context.condition.info_condition == "global" or context.game_id != 1 %}
	var ar3 = paper.arrows(p2.x+50, p2.y+50, p0.x-30, p0.y-80, p2, p0,	{{ context.s20 }},	{{ context.s02 }},	{{ context.r20 }},	{{ context.r02 }});
{% endif %}
	texts.push(t0, t1, t2);
	texts.attr(label);
	paper.setStart();
{% if context.last_transferer != None  %}
	p{{ context.last_transferer }}.transfers.glow(glowattr);
{% endif %}
{% for i in context.last_returners %}
	p{{ i }}.returns.glow(glowattr);
{% endfor %}
	glow = paper.setFinish();
	glow.toBack();
{% include 'timer.js'%}
{% endblock %}
