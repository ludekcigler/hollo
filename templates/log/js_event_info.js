var TrackEventInfo = {
    {% for event in events %}
        '{{ event.name }}': {'has_additional_info': 
            {% if event.has_additional_info %}
                true
            {% else %}
                false
            {% endif %}
            },
    {% endfor %}
}
