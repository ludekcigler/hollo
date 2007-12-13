/*
 * General functions for the workout view
 */

athletelog.ui.workout = {

    select_day: function (aEvent) {
        var day = athletelog.utils.get_day_class(this).match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        if (!athletelog.ui.workout.summary_content)
            athletelog.ui.workout.summary_content = $('#workout_summary .content').html();


        athletelog.ui.progress_display.show();
        $('#workout_summary .content').load(
            athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id  + '/day/' + day[1] + '/' + day[2] + '/' + day[3] + '/',
            athletelog.ui.workout.display_info);

        aEvent.preventDefault();
    },

    display_info: function (responseText, code, response) {
        $('#workout_summary .workout_info_jump_back').click(athletelog.ui.workout.restore_summary);
        athletelog.ui.progress_display.hide();
    },

    restore_summary: function (aEvent) {
        $('#workout_summary .content').html(athletelog.ui.workout.summary_content);
        athletelog.ui.workout.summary_content = null;
        aEvent.preventDefault();
    },

    summary_content: null
};
