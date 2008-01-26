athletelog.ui.workout_monthly_view = {
    init: function () {
        athletelog.ui.workout_monthly_view.on_view_loaded();
    },

    highlight_day: function () {
        $(this).addClass('highlighted');
    },

    unhighlight_day: function () {
        $(this).removeClass('highlighted');
    },

    change_month: function (aYear, aMonth, aDay) {
        athletelog.ui.workout.day = aDay;
        var athlete_id = athletelog.utils.get_athlete_id();
        
        var summary_url = athletelog.utils.get_server_root() + '/log/snippets/workout/' + 
                                 athlete_id + '/monthly_summary/' + aYear + '/' + aMonth + '/';
        var summary_callback = null;

        if (aDay) {
            summary_url = athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id  + '/day/' + aDay.formatDate("Y/m/d/")
            summary_callback = function (aResponse) { athletelog.ui.workout.display_info(aResponse, aDay); };
        }

        athletelog.events.trigger("ajax-request-start");
        var changed_elements = [{elem: '.main_view', 
                                 url: athletelog.utils.get_server_root() + '/log/snippets/workout/' + 
                                 athlete_id + '/month/' + aYear + '/' + aMonth + '/',
                                 callback: function (aResponse) { 
                                    athletelog.ui.workout_monthly_view.on_view_loaded(aResponse, aYear, aMonth);
                                 }},

                                {elem: '.summary .content',
                                 url: summary_url,
                                 callback: summary_callback}];

        athletelog.utils.load_to_elements(changed_elements);
    },

    on_view_loaded: function (aResponse, aYear, aMonth) {
        $('#monthly_view tbody td:not(.empty)').click(athletelog.ui.workout.select_day)
            .hover(athletelog.ui.workout_monthly_view.highlight_day,
                athletelog.ui.workout_monthly_view.unhighlight_day);

        $('#workout_view .pager_menu a').click(function (aEvent) {
            month_match = athletelog.utils.get_class_match(this, /^month_(\d{4})_(\d{1,2})$/); 
            if (!month_match) return;

            athletelog.ui.workout_monthly_view.change_month(month_match[1], month_match[2]);
            aEvent.preventDefault();
        });

        $('#workout_view tbody th a').click(function (aEvent) {
            week_match = athletelog.utils.get_class_match(this, /^week_(\d{4})_(\d{1,2})$/); 
            if (!week_match) return;

            athletelog.ui.workout_weekly_view.change_week(week_match[1], week_match[2]);
            aEvent.preventDefault();
        });

        if (aYear && aMonth) {
            var d = new Date(aMonth + "/1/" + aYear);
            document.title = d.formatDate("F Y") + ' | Tréninky';

            $('#change_view_week').val(d.formatDate("W"));
            $('#change_view_month').val(aMonth);
            $('#change_view_year').val(aYear);
            $('#change_view_view_type').val('monthly').trigger('change');

            athletelog.ui.workout.week = d.formatDate("W");
            athletelog.ui.workout.month = aMonth;
            athletelog.ui.workout.year = aYear;
            athletelog.ui.workout.view_type = 'monthly';
        }
    }
};

