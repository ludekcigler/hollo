athletelog.ui.athlete_selection = {
    init: function () {
        $('#athlete_selection_link').click(function (aEvent) { athletelog.ui.athlete_selection.toggle_selection(aEvent); });
    },

    toggle_selection: function (aEvent) {
        $('#athlete_selection_other_athletes').toggle();
        $('#athlete_selection_link').toggleClass('selected');
        aEvent.preventDefault();
    }
};

$(document).ready(function () {
    athletelog.ui.athlete_selection.init();
});
