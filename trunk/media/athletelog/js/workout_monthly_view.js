athletelog.ui.workout_monthly_view = {
    highlight_day: function () {
        $(this).addClass('highlighted');
    },

    unhighlight_day: function () {
        $(this).removeClass('highlighted');
    }
}

$(document).ready(function () {
    $('#monthly_view tbody td:not(.empty)').click(athletelog.ui.workout.select_day)
        .hover(athletelog.ui.workout_monthly_view.highlight_day,
                athletelog.ui.workout_monthly_view.unhighlight_day);
});

