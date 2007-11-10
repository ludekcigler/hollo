var competitionForm = {
    init: function () {
        $('#competition_event').bind('change', competitionForm.toggleEventInfo, false);
        competitionForm.toggleEventInfo();
    },

    toggleEventInfo: function () {
        var eventName = $('#competition_event').val();
        if (TrackEventInfo[eventName] && TrackEventInfo[eventName].has_additional_info)
            $('p.event_info').css('display', '');
        else
            $('p.event_info').css('display', 'none');
    }
}

$(document).ready(function() {
    competitionForm.init();
})
