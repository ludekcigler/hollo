var logChangeViewForm = 
{
    init: function ()
    {
        $('#view_selection #change_view_view_type').bind('change', null, logChangeViewForm.changeView)
            .trigger('change');

    },

    changeView: function (aEvent)
    {
        var viewType = $(this).val();
        var viewSelection = $('#view_selection');

        function toggleFormVisibility(aHidden, aVisible) 
        {
            for (var i = 0; i < aHidden.length; ++i) 
            {
                viewSelection.find('#' + aHidden[i]).css('display', 'none');
                viewSelection.find('label[@for=' + aHidden[i] + ']').css('display', 'none');
            }

            for (var i = 0; i < aVisible.length; ++i) 
            {
                viewSelection.find('#' + aVisible[i]).css('display', 'inline');
                viewSelection.find('label[@for=' + aVisible[i] + ']').css('display', 'inline');
            }
        }

        switch (viewType) {
            case "weekly":
                toggleFormVisibility(/* hide */ ['change_view_month'], /* show */ ['change_view_week', 'change_view_year']);
                break;
            case "monthly":
                toggleFormVisibility(['change_view_week'], ['change_view_month', 'change_view_year']);
                break;
            case "yearly":
                toggleFormVisibility(['change_view_week', 'change_view_month'], ['change_view_year']);
                break;
            default:
                toggleFormVisibility(['change_view_week', 'change_view_month', 'change_view_year'], []);
                break;
        }
    }
}

$(document).ready(function() {
    logChangeViewForm.init();
});
