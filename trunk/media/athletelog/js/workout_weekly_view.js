athletelog.ui.workout_weekly_view = {
    init: function () {
        athletelog.ui.workout_weekly_view.on_view_loaded();
    },

    highlight_day: function (aEvent) {
        var dayClass = athletelog.utils.get_day_class(this);
        $(this).parents('tbody').find('tr.' + dayClass).addClass('highlighted');
    },

    unhighlight_day: function () {
        var dayClass = athletelog.utils.get_day_class(this);
        $(this).parents('tbody').find('tr.' + dayClass).removeClass('highlighted');
    },

    change_week: function (aYear, aWeek, aDay) {
        athletelog.ui.workout.day = aDay;
        var athlete_id = athletelog.utils.get_athlete_id();
        var summary_url = athletelog.utils.get_server_root() + '/log/snippets/workout/' + 
                                 athlete_id + '/weekly_summary/' + aYear + '/' + aWeek + '/'
        var summary_callback = null;

        if (aDay) {
            summary_url = athletelog.utils.get_server_root() + '/log/snippets/workout/' + athlete_id  + '/day/' + aDay.formatDate("Y/m/d/")
            summary_callback = function (aResponse) { athletelog.ui.workout.display_info(aResponse, aDay); };
        }

        athletelog.events.trigger("ajax-request-start");
        var changed_elements = [{elem: '.main_view', 
                                 url: athletelog.utils.get_server_root() + '/log/snippets/workout/' + 
                                 athlete_id + '/week/' + aYear + '/' + aWeek + '/',
                                 callback: function (aResponse) { 
                                    athletelog.ui.workout_weekly_view.on_view_loaded(aResponse, aYear, aWeek);
                                 }},

                                {elem: '.summary .content',
                                 url: summary_url,
                                 callback: summary_callback}];

        athletelog.utils.load_to_elements(changed_elements);
    },

    on_view_loaded: function (aResponse, aYear, aWeek) {
        
        var dayRows = $('#weekly_view tbody tr');
        dayRows.click(athletelog.ui.workout.select_day);
        dayRows.hover(athletelog.ui.workout_weekly_view.highlight_day,
                                    athletelog.ui.workout_weekly_view.unhighlight_day);

        $('#workout_view .pager_menu a').click(function (aEvent) {
            week_match = athletelog.utils.get_class_match(this, /^week_(\d{4})_(\d{1,2})$/); 
            if (!week_match) return;

            athletelog.ui.workout_weekly_view.change_week(week_match[1], week_match[2]);
            aEvent.preventDefault();
        });

        if (aYear && aWeek) {
            var first_day = athletelog.utils.get_first_day_of_week(aYear, aWeek);
            document.title = aWeek + '. týden ' + aYear + ' | Tréninky';

            $('#change_view_week').val(aWeek);
            $('#change_view_month').val(first_day.formatDate("n"));
            $('#change_view_year').val(aYear);
            $('#change_view_view_type').val('weekly').trigger('change');

            athletelog.ui.workout.week = aWeek;
            athletelog.ui.workout.month = parseInt(first_day.formatDate("n"));
            athletelog.ui.workout.year = aYear;
            athletelog.ui.workout.view_type = 'weekly';
        }
    }
};
