
hollo.workout.weekly = {
    //Returns all rows in weekly view that correspond to the same day as the input row
        highlight_day: function () {
            var dayClass = hollo.utils.get_day_class(this);
            $(this).parents('tbody').find('tr.' + dayClass).addClass('highlighted');
        },

        unhighlight_day: function () {
            var dayClass = hollo.utils.get_day_class(this);
            $(this).parents('tbody').find('tr.' + dayClass).removeClass('highlighted');
        }
}

$(document).ready(function(event) {
    var dayRows = $('#weeklyView tbody tr');
    $('#weeklyView tbody tr').click(hollo.workout.select_day);
    $('#weeklyView tbody tr').hover(hollo.workout.weekly.highlight_day, hollo.workout.weekly.unhighlight_day);
    hollo.workout.select_view('weekly');
});
