athletelog.ui.competition_form = {
    init: function () {
        $('#competition_event').bind('change', athletelog.ui.competition_form.toggleEventInfo, false);
        athletelog.ui.competition_form.toggleEventInfo();
    },

    toggleEventInfo: function () {
        var eventName = $('#competition_event').val();
        if (TrackEventInfo[eventName] && TrackEventInfo[eventName].has_additional_info)
            $('p.event_info').css('display', '');
        else
            $('p.event_info').css('display', 'none');
    },

    submit: function (aEvent, aAction) {
        data = {}
        $('#competition_form input').add('#competition_form select')
                    .map(function (aIndex, aElem) {
                            data[aElem.name] = aElem.value;
                        });

        athletelog.events.trigger("ajax-request-start");
        $.post(
            athletelog.utils.get_server_root() + '/log/api/competition/' + athletelog.utils.get_athlete_id() + '/' + aAction + '/',
            data,
            athletelog.ui.competition_form.on_submit_response,
            'json');

        aEvent.preventDefault();
    },

    on_submit_response: function (aResponse) {
        athletelog.events.trigger("ajax-request-stop");
        if (aResponse.response == 'ok') {
            athletelog.ui.workout.reload();
        } else if (aResponse.response == 'failed') {
            $('#competition_form').addClass('error');
            $('#competition_form p').removeClass('error');

            for (var i = 0; i < aResponse.errors.length; ++i) {
                $('#' + aResponse.errors[i]).parents('p').addClass('error');
            }
        }
    }
};

