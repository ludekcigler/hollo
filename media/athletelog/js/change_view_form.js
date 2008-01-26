athletelog.ui.change_view_form = 
{
    init: function ()
    {
        $('#view_selection #change_view_view_type').bind('change', null, athletelog.ui.change_view_form.change_view)
            .trigger('change');

    },

    change_view: function (aEvent)
    {
        var view_type = $(this).val();
        var view_selection = $('#view_selection');

        function toggle_form_visibility(aHidden, aVisible) 
        {
            for (var i = 0; i < aHidden.length; ++i) 
            {
                view_selection.find('#' + aHidden[i]).css('display', 'none');
                view_selection.find('label[@for=' + aHidden[i] + ']').css('display', 'none');
            }

            for (var i = 0; i < aVisible.length; ++i) 
            {
                view_selection.find('#' + aVisible[i]).css('display', 'inline');
                view_selection.find('label[@for=' + aVisible[i] + ']').css('display', 'inline');
            }
        }

        switch (view_type) {
            case "weekly":
                toggle_form_visibility(/* hide */ ['change_view_month'], /* show */ ['change_view_week', 'change_view_year']);
                break;
            case "monthly":
                toggle_form_visibility(['change_view_week'], ['change_view_month', 'change_view_year']);
                break;
            case "yearly":
                toggle_form_visibility(['change_view_week', 'change_view_month'], ['change_view_year']);
                break;
            default:
                toggle_form_visibility(['change_view_week', 'change_view_month', 'change_view_year'], []);
                break;
        }
    }
};

$(document).ready(function() {
    athletelog.ui.change_view_form.init();
});
