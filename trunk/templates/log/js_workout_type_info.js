var WorkoutTypeInfo = {
    {% for type in workout_types %}
        '{{ type.abbr }}': {'name': '{{ type.name }}',
                            'num_type': '{{ type.num_type }}'
                           },
    {% endfor %}
}
