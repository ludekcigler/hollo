var WorkoutTypeInfo =
{
    {% for t in workout_types %}
    '{{ t.abbr }}': {
                     'name': '{{ t.name }}',
                     'num_type': '{{ t.num_type }}',
                    },
    {% endfor %}
};
