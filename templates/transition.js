{% extends 'diagram_base.js' %}
{% block drawing %}
	$("#drawing{{ context.pk }}").html('<h1>{{ context.self_msg }}</h1><h2>{{ context.instructions }}</h2>');
	$('#selfmsg{{ context.pk }}').html('{{ context.self_msg }}');
	var paper = new Raphael("drawing{{ context.pk }}", "100%", 50);
{% include 'timer.js' %}
{% endblock %}
