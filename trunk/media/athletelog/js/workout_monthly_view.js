hollo.workout.monthly = {
    highlight_day: function () {
        $(this).addClass('highlighted');
    },

    unhighlight_day: function () {
        $(this).removeClass('highlighted');
    }
}

$(document).ready(function () {
    $('#monthlyView tbody td:not(.empty)').click(hollo.workout.select_day).hover(hollo.workout.monthly.highlight_day, hollo.workout.monthly.unhighlight_day);

    hollo.workout.select_view('monthly');
});

