/*
 * General functions for competition handling
 */

hollo.competition = {
    
    show_add_form: function (evt) {
        var dayMatch = this.id.match(/^[^_]+_(\d{4})-(\d{2})-(\d{2})$/);

        $.get(hollo.utils.get_server_root() + '/log/ajax/competition/add_form/' + dayMatch[1] + '/' + dayMatch[2] + '/' + dayMatch[3] + '/',
              {'sid': Math.random()},
              hollo.competition.show_form_callback);

        evt.preventDefault();
    },

    show_form_callback: function (responseText, code, response) {
        hollo.utils.show_edit_form(responseText, code, response);
        hollo.competition.assign_form_signals();
    },

    assign_form_signals: function() {
        $('#editFormWindow').jqDrag('.jqDrag').jqResize('.jqResize');
        $('#editFormWindow #competitionEditFormClose').click(hollo.competition.close_form);
    },

    close_form: function (evt) {
        $('#editFormWindow #competitionEditFormClose').unbind();
        $('#editFormWindow').remove();
    },

    select_view: function (viewType) {
        if (viewType == "monthly") {
            $('#viewSelection #month').css('display', 'inline');
            $('#viewSelection label[@for=month]').css('display', 'inline');
        } else {
            $('#viewSelection #month').css('display', 'none');
            $('#viewSelection label[@for=month]').css('display', 'none');
        }
        $('#viewType')[0].value = viewType;
    },

    change_view: function(evt) {
        if ($('#viewType')[0].value == "monthly") {
            // Monthly view
            document.location.href = hollo.utils.get_server_root() + '/log/competition/month/' +
                                  hollo.utils.number_format($('#year')[0].value, "0000") + '/' +
                                  hollo.utils.number_format($('#month')[0].value, "00") + '/';
        } else if ($('#viewType')[0].value == "yearly") {
            // Yearly view
            document.location.href = hollo.utils.get_server_root() + '/log/competition/year/' +
                                  hollo.utils.number_format($('#year')[0].value, "0000") + '/';
        }
        evt.preventDefault();
    }
};
        
