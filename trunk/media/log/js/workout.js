/*
 * General functions for the workout view
 */

var workoutInfoSignals = Array();
workoutEvents = Object();

function get_server_root() {
    var re = /^(http[s]*:\/\/[^\/]+)\/.*$/;
    return document.location.href.match(re)[1];
}

function get_day_class(elem) {
    var classes = elem.className.split(' ');
    var day_re = new RegExp('^\s*[a-zA-Z]+_[0-9]{4}\/[0-9]{2}\/[0-9]{2}$');
    for (var i in classes) {
        if (day_re.test(classes[i])) {
            return classes[i];
        } 
    }
    return '';
}

function assign_workout_info_signals() {
    var editWorkoutLinks = getElementsByTagAndClassName('a', 'editWorkout', $('workoutSummary'));
    var sig;

    for (var i in editWorkoutLinks) {
        sig = connect(editWorkoutLinks[i], 'onclick', workoutEvents, 'show_edit_workout_form');
        workoutInfoSignals.push(sig);
    }

    var removeWorkoutLinks = getElementsByTagAndClassName('a', 'removeWorkout', $('workoutSummary'));
    for (var i in removeWorkoutLinks) {
        sig = connect(removeWorkoutLinks[i], 'onclick', workoutEvents, 'remove_workout');
        workoutInfoSignals.push(sig);
    }

    var addWorkoutLinks = getElementsByTagAndClassName('a', 'addWorkout', $('workoutSummary'));
    for (var i in addWorkoutLinks) {
        sig = connect(addWorkoutLinks[i], 'onclick', workoutEvents, 'show_add_workout_form');
        workoutInfoSignals.push(sig);
    }
}

function remove_workout_info_signals() {
    for (var i in workoutInfoSignals) {
        disconnect(workoutInfoSignals[i]);
    }
}

function request_day_info(day) {
    var d = doSimpleXMLHttpRequest(get_server_root() + '/denik/ajax/workout/info/' + day + '/?sid=' + Math.random());
    d.addCallbacks(workoutEvents.display_workout_info, workoutEvents.display_workout_info_error);
}

function insert_workout_edit_form() {
   if (!$('workoutEditFormWindow')) {
       insertSiblingNodesAfter('body', DIV({'id': 'workoutEditFormWindow'}));
   }
}


function WorkoutEditForm(element, innerHTML) {
    this.elem = element;
    this.elem.innerHTML = innerHTML;
    var viewportDimensions = getViewportDimensions();
    setStyle(this.elem, {'width': 0.6*viewportDimensions.w + 'px', 'height': 0.8*viewportDimensions.h + 'px'});
    setElementPosition(this.elem, {'x': 0.2*viewportDimensions.w, 'y': 0.1*viewportDimensions.h});

    this.signals = Array();
    var sig = connect('workoutEditFormClose', 'onclick', this, 'close_form');
    this.signals.push(sig);

    var removeWorkoutItemButtons = getElementsByTagAndClassName(null, 'removeWorkoutItem', this.elem);

    for (var button in removeWorkoutItemButtons) {
        var sig = connect(removeWorkoutItemButtons[button], 'onclick', this, 'remove_workout_item');
        this.signals.push(sig);
    }
    
    var sig = connect($('addWorkoutItem'), 'onclick', this, 'add_workout_item');
    this.signals.push(sig);
    var sig = connect($('workoutSubmit'), 'onclick', this, 'save_workout');
    this.signals.push(sig);
}

WorkoutEditForm.prototype.remove_workout_item = function (evt) {
    evt.preventDefault(); 
    var parentRow = getFirstParentByTagAndClassName(evt.src(), 'tr', null);
    removeElement(parentRow);
    disconnectAll(evt.src());

    var formRows = getElementsByTagAndClassName('tr', null, this.elem);
    for (var row in formRows) {
        var workoutType = getFirstElementByTagAndClassName(null, 'workoutType', formRows[row]);
        var workoutDesc = getFirstElementByTagAndClassName(null, 'workoutDesc', formRows[row]);
        var workoutKm = getFirstElementByTagAndClassName(null, 'workoutKm', formRows[row]);

        workoutType.name = "workout_type_" + row;
        workoutDesc.name = "workout_desc_" + row;
        workoutKm.name = "workout_km_" + row;
    }

    $('numWorkoutItems').value = Number($('numWorkoutItems').value) - 1;
}

WorkoutEditForm.prototype.add_workout_item = function (evt) {
    var formRow = getFirstElementByTagAndClassName('tr', null, 
                                getFirstElementByTagAndClassName('tbody', null, this.elem)).cloneNode(true);


    var num_rows = getElementsByTagAndClassName('tr', null,
                                getFirstElementByTagAndClassName('tbody', null, this.elem)).length;

    appendChildNodes(getFirstElementByTagAndClassName('tbody', null, this.elem), formRow);
    var workoutType = getFirstElementByTagAndClassName(null, 'workoutType', formRow);
    var workoutDesc = getFirstElementByTagAndClassName(null, 'workoutDesc', formRow);
    var workoutKm = getFirstElementByTagAndClassName(null, 'workoutKm', formRow);

    workoutType.name = "workout_type_" + num_rows;
    workoutDesc.name = "workout_desc_" + num_rows;
    workoutKm.name = "workout_km_" + num_rows;

    workoutType.selectedIndex = 0;
    workoutDesc.value = '';
    workoutKm.value = '';

    var sig = connect(getFirstElementByTagAndClassName('a', 'removeWorkoutItem', formRow), 
                        'onclick', this, 'remove_workout_item');
    this.signals.push(sig)

    $('numWorkoutItems').value = Number($('numWorkoutItems').value) + 1;
    
    evt.preventDefault();
}

WorkoutEditForm.prototype.save_workout = function (evt) {
    
}

WorkoutEditForm.prototype.close_form = function (evt) {
    for (var i in this.signals) {
        disconnect(this.signals[i]);
    }
    removeElement(this.elem);
    evt.preventDefault();
}
    


workoutEvents.select_day = function (event) {
    var dayElem = event.src();
    var day = get_day_class(dayElem).replace('day_', '');
    request_day_info(day);
}

workoutEvents.display_workout_info = function (response) {
    remove_workout_info_signals();
    $('workoutSummary').innerHTML = response.responseText;
    assign_workout_info_signals();
}

workoutEvents.display_workout_info_error = function (response) {
    logDebug('displayWorkoutInfo error ' + response.number);
}

workoutEvents.show_edit_workout_form = function(evt) {
    var dayMatch = evt.src().id.match('^[^_]+_([^_]+)_([^_]+)$');
    var day = dayMatch[1];
    var workoutId = dayMatch[2];

    // Request the edit form...
    var d = doSimpleXMLHttpRequest(get_server_root() + '/denik/ajax/workout/edit_form/' + day + '/' + workoutId + '/?sid=' + Math.random());
    d.addCallback(workoutEvents.display_workout_edit_form);
    evt.preventDefault();
}

workoutEvents.remove_workout = function(evt) {
    var dayMatch = evt.src().id.match('^[^_]+_([^_]+)_([^_]+)$');
    var day = dayMatch[1];
    var workoutId = dayMatch[2];
    logDebug('Remove workout');
    //evt.preventDefault();
}

workoutEvents.show_add_workout_form = function(evt) {
    var dayMatch = evt.src().id.match('^[^_]+_([^_]+)$');
    var day = dayMatch[1];

    var d = doSimpleXMLHttpRequest(get_server_root() + '/denik/ajax/workout/add_form/' + day + '/?sid=' + Math.random());
    d.addCallback(workoutEvents.display_workout_edit_form);

    evt.preventDefault();
}

workoutEvents.display_workout_edit_form = function(response) {
    // Add div with the form inside..
    insert_workout_edit_form();
    var editForm = new WorkoutEditForm($('workoutEditFormWindow'), response.responseText);
}


// Change workout view
workoutEvents.change_view = function(evt) {
    evt.preventDefault();
    if ($('viewType').value == "weekly") {
            // Weekly view
        document.location.href = get_server_root() + '/denik/week/' +
                                  numberFormatter("0000")($('year').value) + '/' +
                                  numberFormatter("00")($('week').value) + '/';
    } else if ($('viewType').value == "monthly") {
        // Monthly view
        document.location.href = get_server_root() + '/denik/month/' +
                                  numberFormatter("0000")($('year').value) + '/' +
                                  numberFormatter("00")($('month').value) + '/';
    }
    evt.preventDefault();
}

// Switch between weekly/monthly view in the viewSelection form
workoutEvents.switch_view_selection = function (evt) {
    switch_view_selection_form($('viewType').value);
}

function switch_view_selection_form(viewType) {
    if (viewType == "weekly") {
        setStyle($('week'), {'display': 'inline'});
        setStyle(get_label_for_form_item('week', 'viewSelection'), {'display': 'inline'});
        setStyle($('month'), {'display': 'none'});
        setStyle(get_label_for_form_item('month', 'viewSelection'), {'display': 'none'});
    } else {
        setStyle($('month'), {'display': 'inline'});
        setStyle(get_label_for_form_item('month', 'viewSelection'), {'display': 'inline'});
        setStyle($('week'), {'display': 'none'});
        setStyle(get_label_for_form_item('week', 'viewSelection'), {'display': 'none'});
    }
    $('viewType').value = viewType;
}

function get_label_for_form_item(formItemId, formId) {
    var labels = getElementsByTagAndClassName('label', null, formId);
    for (var i in labels) {
        if (labels[i].htmlFor && labels[i].htmlFor == formItemId) {
            return labels[i];
        }
    }
    return null;
}

workoutEvents.init = function(evt) {
    connect('viewSelectionSubmit', 'onclick', workoutEvents, 'change_view');
    connect('viewType', 'onchange', workoutEvents, 'switch_view_selection');
}

connect(window, 'onload', workoutEvents, 'init');
