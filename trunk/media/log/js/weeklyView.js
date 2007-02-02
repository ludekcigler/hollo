var weeklyViewEvents = Object();

//Returns all rows in weekly view that correspond to the same day as the input row
function get_day_rows(dayRow) {
    var dayClass = get_day_class(dayRow);
    if (dayClass != '') {
        return getElementsByTagAndClassName('tr', dayClass, $('weeklyView'));
    } else {
        return Array();
    }
}

weeklyViewEvents.highlight_day = function (event) {
    var dayRows = get_day_rows(event.src());

    for (row in dayRows) {
        addElementClass(dayRows[row], 'highlighted');
    }
}

weeklyViewEvents.unhighlight_day = function (event) {
    var dayRows = get_day_rows(event.src());

    for (row in dayRows) {
        removeElementClass(dayRows[row], 'highlighted');
    }
}

weeklyViewEvents.init = function(event) {
    var dayRows = getElementsByTagAndClassName('tr', null, 
            getFirstElementByTagAndClassName('tbody', null, $('weeklyView')));

    for (row in dayRows) {
        connect(dayRows[row], 'onclick', workoutEvents, 'select_day');
        connect(dayRows[row], 'onmouseover', weeklyViewEvents, 'highlight_day');
        connect(dayRows[row], 'onmouseout', weeklyViewEvents, 'unhighlight_day');
    }
    switch_view_selection_form('weekly');
}

//Load all JavaScript after the page has loaded
connect(window, 'onload', weeklyViewEvents, 'init');
