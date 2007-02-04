/*
 * General functions for the workout view
 */

hollo.workout = {

    select_day: function (evt) {
        var day = hollo.utils.get_day_class(this).match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }

        $('#workoutSummary').load(
            hollo.utils.get_server_root() + '/log/ajax/workout/info/' + day[1] + '/' + day[2] + '/' + day[3] + '/',
            {'sid': Math.random()},
            hollo.workout.display_info)
    },

    display_info: function (responseText, code, response) {
        hollo.workout.assign_info_signals();
    },

    // Assigns signals to buttons on the workout info view
    assign_info_signals: function () {
        $('#workoutSummary a.editWorkout').click(hollo.workout.show_edit_form);
        $('#workoutSummary a.removeWorkout').click(hollo.workout.remove);
        $('#workoutSummary a.addWorkout').click(hollo.workout.show_add_form);
    },

    show_edit_form: function(evt) {
        var dayMatch = this.id.match(/^[^_]+_(\d{4})-(\d{2})-(\d{2})_([^_]+)$/);

        $.get(hollo.utils.get_server_root() + '/log/ajax/workout/edit_form/' + dayMatch[1] + '/' + dayMatch[2] + '/' + dayMatch[3] + '/' + dayMatch[4] + '/', 
              {'sid': Math.random()},
              hollo.workout.show_form_callback);

        evt.preventDefault();
    },

    show_add_form: function(evt) {
        var dayMatch = this.id.match(/^[^_]+_(\d{4})-(\d{2})-(\d{2})$/);

        $.get(hollo.utils.get_server_root() + '/log/ajax/workout/add_form/' + dayMatch[1] + '/' + dayMatch[2] + '/' + dayMatch[3] + '/',
              {'sid': Math.random()},
              hollo.workout.show_form_callback);

        evt.preventDefault();
    },

    show_form_callback: function (responseText, code, response) {
        // Insert the div for workout form
        if ($('#workoutEditFormWindow').length == 0) {
            var d = document.createElement('div');
            d.id = 'workoutEditFormWindow';
            $('body')[0].appendChild(d);
        }
        
        var w = $('#workoutEditFormWindow');
        w.css('width', 0.7 * window.innerWidth);
        w.css('height', 0.7 * window.innerHeight);
        w.css('top', 0.15 * window.innerHeight);
        w.css('left', 0.15 * window.innerWidth);
        w.css('display', 'block');
        
        w.html(responseText);

        hollo.workout.assign_form_signals();
    },

    remove: function(evt) {
        var dayMatch = evt.currentTarget.id.match('^[^_]+_([^_]+)_([^_]+)$');
        var day = dayMatch[1];
        var workoutId = dayMatch[2];
        evt.preventDefault();
    },

    // Change workout view
    change_view: function(evt) {
        if ($('#viewType')[0].value == "weekly") {
            // Weekly view
            document.location.href = hollo.utils.get_server_root() + '/log/week/' +
                                  hollo.utils.number_format($('#year')[0].value, "0000") + '/' +
                                  hollo.utils.number_format($('#week')[0].value, "00") + '/';
        } else if ($('#viewType')[0].value == "monthly") {
            // Monthly view
            document.location.href = hollo.utils.get_server_root() + '/log/month/' +
                                  hollo.utils.number_format($('#year')[0].value, "0000") + '/' +
                                  hollo.utils.number_format($('#month')[0].value, "00") + '/';
        }
        evt.preventDefault();
    },

    select_view: function (viewType) {
        if (viewType == "weekly") {
            $('#viewSelection #month').css('display', 'none');
            $('#viewSelection label[@for=month]').css('display', 'none');
            $('#viewSelection #week').css('display', 'inline');
            $('#viewSelection label[@for=week]').css('display', 'inline');
        } else {
            $('#viewSelection #week').css('display', 'none');
            $('#viewSelection label[@for=week]').css('display', 'none');
            $('#viewSelection #month').css('display', 'inline');
            $('#viewSelection label[@for=month]').css('display', 'inline');
        }
        $('#viewType')[0].value = viewType;
    },

    assign_form_signals: function () {
        $('#workoutEditFormWindow .removeWorkoutItem').click(hollo.workout.remove_item);
        $('#workoutEditFormWindow #addWorkoutItem').click(hollo.workout.add_item);
        $('#workoutEditFormWindow #workoutEditFormClose').click(hollo.workout.close_form);
    },

    remove_item: function (evt) {
        if ($('#numWorkoutItems')[0].value > 1) {
            $(this).unbind();
            $(this).parents('tr').remove();
            $('#numWorkoutItems')[0].value = $('#workoutEdit table tbody tr').length;
        }
        evt.preventDefault();
    },

    add_item: function (evt) {
        var row = $('#workoutEditFormWindow table tbody tr')[0].cloneNode(true);
        $('#workoutEditFormWindow table tbody').append(row);
        $(row).find('.removeWorkoutItem').click(hollo.workout.remove_item);
        
        $('#numWorkoutItems')[0].value = $('#workoutEdit table tbody tr').length;
        evt.preventDefault();
    },

    close_form: function (evt) {
        $('#workoutEditFormWindow .removeWorkoutItem').unbind();
        $('#workoutEditFormWindow #addWorkoutItem').unbind();
        $('#workoutEditFormWindow #workoutEditFormClose').unbind();
        $('#workoutEditFormWindow').remove();
        evt.preventDefault();
    }
}

$(document).ready(function () {
    $('#viewSelectionSubmit').click(hollo.workout.change_view);
    $('#viewType').change(function () { hollo.workout.select_view(this.value); });
});
