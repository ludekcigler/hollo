/*
 * General functions for competition handling
 */

athletelog.ui.competition = {
    load_add_form: function (aEvent) {
        var day = this.id.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        athletelog.events.trigger("ajax-request-start");
        if (!athletelog.ui.main_view)
            athletelog.ui.main_view = $('.main_view').clone(true);

        $('.main_view').load(
            athletelog.utils.get_server_root() + '/log/snippets/competition/' + athlete_id + '/add/' + day[1] + '/' + day[2] + '/' + day[3] + '/',
            function (aEvent) { athletelog.ui.competition.display_form(aEvent, 'add')});

        aEvent.preventDefault();
    },

    load_edit_form: function (aEvent) {
        var day = this.id.match(/(\d{4})-(\d{2})-(\d{2})/);
        if (!day) { return; }
        var competition_id = this.id.match(/_(\d+)$/);
        if (!competition_id) { return; }

        var athlete_id = athletelog.utils.get_athlete_id();

        if (!athletelog.ui.main_view)
            athletelog.ui.main_view = $('.main_view').clone(true);

        athletelog.events.trigger("ajax-request-start");
        $('.main_view').load(
            athletelog.utils.get_server_root() + '/log/snippets/competition/' + athlete_id + '/edit/' + day[1] + '/' + day[2] + '/' + day[3] + '/' + competition_id[1] + '/',
            function (aEvent) { athletelog.ui.competition.display_form(aEvent, 'edit')});

        aEvent.preventDefault();
    },

    display_form: function (aEvent, aAction) {
        athletelog.events.trigger("ajax-request-stop");
        athletelog.ui.competition_form.init();
        $('#competition_form .cancel').click(athletelog.ui.competition.hide_form);
        $('#competition_form .ok').click(function (aEvent) { athletelog.ui.competition_form.submit(aEvent, aAction); });
        $('#competition_form').corner('6px');
    },

    hide_form: function (aEvent) {
        $('.main_view').replaceWith(athletelog.ui.main_view);
        athletelog.ui.main_view = null;
        aEvent.preventDefault();
    }
};

