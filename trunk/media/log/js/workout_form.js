const WORKOUT_FORM_MAX_RATING = 5;

function WorkoutFormStarPickerListener (aFormField) {
    var mFormField = aFormField;

    this.onSelect = function (aPicker, aIndex) {
        $(mFormField).val(aIndex + 1);    
    };
};

var workoutForm = {
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
        $('.workout_items .type select').bind('change', workoutForm.changeNumDataLabel, false).trigger('change');

        $(window).bind('unload', workoutForm.finalize, false);
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
    }


};

$(document).ready(function () {
    workoutForm.init();
});
