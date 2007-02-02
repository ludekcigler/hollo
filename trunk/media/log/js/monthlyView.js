var monthlyViewEvents = Object();

monthlyViewEvents.init = function (evt) {
    var dayCells = getElementsByTagAndClassName('td', null, 
                        getFirstElementByTagAndClassName('tbody', null, 'monthlyView'));
    for (var i in dayCells) {
        var c = get_day_class(dayCells[i]);
        if (c != '') {
            connect(dayCells[i], 'onclick', workoutEvents, 'select_day');
        }
    }
    switch_view_selection_form('monthly');
}

connect(window, 'onload', monthlyViewEvents, 'init');
