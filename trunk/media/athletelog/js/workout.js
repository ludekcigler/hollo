/*
 * General functions for the workout view
 */

athletelog.ui.workout = {

    select_day: function (aEvent) {
        var day = athletelog.utils.get_day_class(this).match(/(\d{4})-(\d{2})-(\d{2})/);
        var d = new Date(day[2] + "/" + day[3] + "/" + day[1]);
        if (!day) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        if (!athletelog.ui.workout.summary_content)
            athletelog.ui.workout.summary_content = $('#workout_summary .content').html();


        athletelog.events.trigger("ajax-request-start");
        $('#workout_summary .content').load(
            athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id  + '/day/' + day[1] + '/' + day[2] + '/' + day[3] + '/',
            function (aResponse) { athletelog.ui.workout.display_info(aResponse, d); });

        aEvent.preventDefault();
    },

    display_info: function (aResponse, aDay) {
        $('#workout_summary .workout_info_jump_back').click(athletelog.ui.workout.restore_summary);
        $('#workout_summary .add_workout').click(athletelog.ui.workout.load_add_form);
        $('#workout_summary .edit_workout').click(athletelog.ui.workout.load_edit_form);
        $('#workout_summary .add_competition').click(athletelog.ui.competition.load_add_form);
        $('#workout_summary .edit_competition').click(athletelog.ui.competition.load_edit_form);
        athletelog.events.trigger("ajax-request-stop");

        athletelog.ui.workout.day = aDay;
    },

    restore_summary: function (aEvent) {
        $('#workout_summary .content').html(athletelog.ui.workout.summary_content);
        athletelog.ui.workout.summary_content = null;
        aEvent.preventDefault();
    },

    load_add_form: function (aEvent) {
        var day = this.id.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        if (!athletelog.ui.main_view)
            athletelog.ui.main_view = $('.main_view').clone(true);

        athletelog.ui.progress_display.show();
        athletelog.events.trigger("ajax-request-start");
        $('.main_view').load(
            athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id + '/add/' + day[1] + '/' + day[2] + '/' + day[3] + '/',
            function (aEvent) { athletelog.ui.workout.display_form(aEvent, 'add')});

        aEvent.preventDefault();
    },

    load_edit_form: function (aEvent) {
        var day = this.id.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }
        var workout_id = this.id.match(/_(\d+)$/);
        if (!workout_id) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        if (!athletelog.ui.main_view)
            athletelog.ui.main_view = $('.main_view').clone(true);

        athletelog.ui.progress_display.show();
        $('.main_view').load(
            athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id + '/edit/' + day[1] + '/' + day[2] + '/' + day[3] + '/' + workout_id[1] + '/',
            function (aEvent) { athletelog.ui.workout.display_form(aEvent, 'edit')});

        aEvent.preventDefault();
    },

    display_form: function (aEvent, aAction) {
        athletelog.events.trigger("ajax-request-stop");
        athletelog.ui.workout_form.init();
        $('#workout_form .cancel').click(athletelog.ui.workout.hide_form);
        $('#workout_form .ok').click(function (aEvent) { athletelog.ui.workout_form.submit(aEvent, aAction); });
        $('#workout_form').corner('6px');
    },

    hide_form: function (aEvent) {
        $('.main_view').replaceWith(athletelog.ui.main_view);
        athletelog.ui.main_view = null;
        aEvent.preventDefault();
    },

    change_view: function (aEvent) {
        var view_type = $('#change_view_view_type').val();
        var year = $('#change_view_year').val();

        athletelog.ui.workout.day = null;
        if (view_type == 'weekly') {
            var week = $('#change_view_week').val();
            athletelog.ui.workout_weekly_view.change_week(year, week);
        } else if (view_type == 'monthly') {
            var month = $('#change_view_month').val();
            athletelog.ui.workout_monthly_view.change_month(year, month);
        }

        aEvent.preventDefault();
    },

    reload: function () {
        if (athletelog.ui.workout.view_type == 'weekly') {
            athletelog.ui.workout_weekly_view.change_week(athletelog.ui.workout.year, athletelog.ui.workout.week, athletelog.ui.workout.day);
        } else if (athletelog.ui.workout.view_type == 'monthly') {
            athletelog.ui.workout_monthly_view.change_month(athletelog.ui.workout.year, athletelog.ui.workout.month, athletelog.ui.workout.day);
        }
    },

    summary_content: null,

    day: null,
    week: null,
    month: null,
    year: null,
    view_type: 'weekly'
};

$(document).ready(function () {
    $('#change_view_submit').click(athletelog.ui.workout.change_view);
    athletelog.ui.workout.week = $('#change_view_week').val();
    athletelog.ui.workout.month = $('#change_view_month').val();
    athletelog.ui.workout.year = $('#change_view_year').val();
    athletelog.ui.workout.view_type = $('#change_view_view_type').val();
    athletelog.ui.workout_weekly_view.init();
});
