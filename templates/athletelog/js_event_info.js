var TrackEventInfo =
{
    {% for e in events %}
    '{{ e.name }}': {
                     'has_additional_info': 
                     {% if e.has_additional_info %}
                        true
                     {% else %}
                        false
                     {% endif %},
                     'result_type': '{{ t.result_type }}',
                    },
    {% endfor %}
};

