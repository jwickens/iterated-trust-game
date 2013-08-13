{% extends 'diagram_base.js' %}
{% block drawing %}
	try {
		paper.remove();
	}
	catch (error) {}
	$("#drawing{{ context.pk }}").html('<h1>{{ context.self_msg }}</h1><h2>{{ context.instructions }}</h2>');
{% endblock %}
