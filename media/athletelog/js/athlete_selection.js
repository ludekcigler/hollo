var athletelog = new Object();

athletelog.athlete_selection = {
    onInit: function () {
        $('#athlete_selection_link').click(function (aEvent) { athletelog.athlete_selection.toggleSelection(aEvent); });
    },

    toggleSelection: function (aEvent) {
        $('#athlete_selection_other_athletes').toggle();
        $('#athlete_selection_link').toggleClass('selected');
        aEvent.preventDefault();
    }
};

$(document).ready(function () {
    athletelog.athlete_selection.onInit();
});


