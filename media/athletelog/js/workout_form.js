var WORKOUT_FORM_MAX_RATING = 5;

function WorkoutFormStarPickerListener (aFormField) {
    var mFormField = aFormField;

    this.onSelect = function (aPicker, aIndex) {
        $(mFormField).val(aIndex + 1);    
    };
};

athletelog.ui.workout_form = {
    satisfactionPicker: null,
    difficultyPicker: null,

    init: function () {
        var satisfaction = parseInt($('#workout_rating_satisfaction').val());
        $('#workout_rating_satisfaction').remove();

        var satField = document.createElement('input');
        satField.setAttribute('type', 'hidden');
        satField.setAttribute('id', 'workout_rating_satisfaction');
        satField.setAttribute('name', 'rating_satisfaction');
        
        this.satisfactionPicker = new StarPicker();
        this.satisfactionPicker.addListener(new WorkoutFormStarPickerListener(satField));
        var satPickerElem = this.satisfactionPicker.createElement(WORKOUT_FORM_MAX_RATING, "yellow");

        $('tr.satisfaction td:last-child').append(satField);
        $('tr.satisfaction td:last-child').append(satPickerElem);
        
        this.satisfactionPicker.selectIndex(satisfaction - 1);

        // Difficulty
        var difficulty = parseInt($('#workout_rating_difficulty').val());
        $('#workout_rating_difficulty').remove();

        var difField = document.createElement('input');
        difField.setAttribute('type', 'hidden');
        difField.setAttribute('id', 'workout_rating_difficulty');
        difField.setAttribute('name', 'rating_difficulty');
        
        this.difficultyPicker = new StarPicker();
        this.difficultyPicker.addListener(new WorkoutFormStarPickerListener(difField));
        var difPickerElem = this.difficultyPicker.createElement(WORKOUT_FORM_MAX_RATING, "red");

        $('tr.difficulty td:last-child').append(difField);
        $('tr.difficulty td:last-child').append(difPickerElem);
        
        this.difficultyPicker.selectIndex(difficulty - 1);

        // Bind change events for workout types
        $('.workout_items .type select').bind('change', athletelog.ui.workout_form.changeNumDataLabel, false).trigger('change');

        $(window).bind('unload', athletelog.ui.workout_form.finalize, false);

        $('input.remove_workout_item').click(athletelog.ui.workout_form.removeWorkoutItem);
        $('#add_workout_item').click(athletelog.ui.workout_form.addWorkoutItem);
    },

    finalize: function () {
    },

    changeNumDataLabel: function () {
        var numType = null;
        if (WorkoutTypeInfo[$(this).val()])
            numType = WorkoutTypeInfo[$(this).val()].num_type;
        else
            return;

        var labelElem = $(this).parent().parent().children('.num_data').children('label');
        
        var labelText = '';
        if (numType == 'DISTANCE')
            labelText = 'km';
        else if (numType == 'WEIGHT')
            labelText = 'kg';
        else if (numType == 'TIME')
            labelText = 'min';
        else if (numType == 'COUNT')
            labelText = 'počet';
        else
            labelText = '';

        labelElem.text(labelText);
    },

    removeWorkoutItem: function (aEvent) {
        aEvent.preventDefault();
        var workoutItemCount = parseInt($('#workout_num_workout_items').val());
        if (workoutItemCount <= 1)
            return; // Do not remove the last item

        var removedItem = parseInt($(this).attr('name').match(/^[^0-9]*([0-9]+)$/)[1]);

        $(this).parents('tr').remove();

        var changedProperties = ['type', 'desc', 'num_data'];
        for (var i = removedItem + 1; i < workoutItemCount; ++i) {
            for (var j = 0; j < changedProperties.length; ++j) {
                $('#workout_item_' + i + '_' + changedProperties[j])
                    .attr('id', 'workout_item_' + (i - 1) + '_' + changedProperties[j])
                    .attr('name', 'workout_item_' + (i - 1) + '_' + changedProperties[j])
                    .prev('label')
                        .attr('for', 'workout_item_' + (i - 1) + '_' + changedProperties[j]);
            }
        }

        // Change names on all remove buttons
        $('input.remove_workout_item').map(function (aButton) {
            if (!$(aButton).attr('name'))
                return;

            var val = $(aButton).attr('name').match(/^[^0-9]*([0-9]+)$/)[1];
            if (val > removedItem) {
                $(aButton).attr('name', 'submit_remove_workout_item_' + (val - 1));
            }
        });

        $('#workout_num_workout_items').val(workoutItemCount - 1);
    },

    addWorkoutItem: function (aEvent) {
        aEvent.preventDefault();
        var workoutItemCount = parseInt($('#workout_num_workout_items').val());
        var itemRow = $($('.workout_items tbody tr')[0]).clone(true);

        // Rename the input fields
        var changedProperties = ['type', 'desc', 'num_data'];
        for (var i = 0; i < changedProperties.length; ++i) {
            $(itemRow).children().filter('td.' + changedProperties[i]).removeClass('error').children()
             .filter('#workout_item_0_' + changedProperties[i])
                .attr('id', 'workout_item_' + workoutItemCount + '_' + changedProperties[i])
                .attr('name', 'workout_item_' + workoutItemCount + '_' + changedProperties[i])
                .val('')
                .prev('label')
                    .attr('for', 'workout_item_' + workoutItemCount + '_' + changedProperties[i]);
        }

        // Rename the remove button
        $(itemRow).children('.remove_workout_item')
            .attr('name', 'submit_remove_workout_item_' + workoutItemCount)
            .attr('value', '--');

        $('.workout_items tbody').append(itemRow);

        $('#workout_num_workout_items').val(workoutItemCount + 1);
    },

    submit: function (aEvent, aAction) {
        data = {}
        $('#workout_form input').add('#workout_form select')
                    .map(function (aIndex, aElem) {
                            data[aElem.name] = aElem.value;
                        });

        athletelog.events.trigger("ajax-request-start");
        $.post(
            athletelog.utils.get_server_root() + '/log/api/workout/' + athletelog.utils.get_athlete_id() + '/' + aAction + '/',
            data,
            athletelog.ui.workout_form.on_submit_response,
            'json');

        aEvent.preventDefault();
    },

    on_submit_response: function (aResponse) {
        athletelog.events.trigger("ajax-request-stop");
        if (aResponse.response == 'ok') {
            athletelog.ui.workout.reload();
        } else if (aResponse.response == 'failed') {
            $('#workout_form').addClass('error');
            $('#workout_form td').removeClass('error');

            for (var i = 0; i < aResponse.errors.length; ++i) {
                $('#' + aResponse.errors[i]).parents('td').addClass('error');
            }
        }
    }
};

$(document).ready(function () {
    athletelog.ui.workout_form.init();
});
