athletelog.ui.workout_weekly_view = {
    highlight_day: function (aEvent) {
        var dayClass = athletelog.utils.get_day_class(this);
        $(this).parents('tbody').find('tr.' + dayClass).addClass('highlighted');
    },

    unhighlight_day: function () {
        var dayClass = athletelog.utils.get_day_class(this);
        $(this).parents('tbody').find('tr.' + dayClass).removeClass('highlighted');
    }
}

$(document).ready(function(event) {
    var dayRows = $('#weekly_view tbody tr');
    $('#weekly_view tbody tr').click(athletelog.ui.workout.select_day);
    $('#weekly_view tbody tr').hover(athletelog.ui.workout_weekly_view.highlight_day,
                                    athletelog.ui.workout_weekly_view.unhighlight_day);

});
