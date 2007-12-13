var WorkoutTypeInfo =
{
    {% for t in workout_types %}
    '{{ t.abbr }}': {
                     'name': '{{ t.name }}',
                     'num_type': '{{ t.num_type }}'
                    }
        {% if forloop.last %}
        {% else %}
                    ,
        {% endif %}
    {% endfor %}
};
