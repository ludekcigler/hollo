
function StarPicker () {
    var mNumStars;
    var mColorClass;
    var mRootElem;
    var mPickerElems;
    var mHighlightRootElem;
    var mHighlightElems;
    var mSelectedIndex = -1;
    var mListeners = new Array();

    var mThis = this;

    // Creates star picker element for given 
    this.createElement = function (aNumStars, aColorClass) {
        mNumStars = aNumStars;

        mRootElem = document.createElement('span');
        $(mRootElem).addClass('star_picker');
        $(mRootElem).addClass(aColorClass);
        mHighlightRootElem = document.createElement('span');
        $(mHighlightRootElem).addClass('star_picker_highlight');
        mPickerElems = new Array();
        mHighlightElems = new Array();

        for (var i = 0; i < aNumStars; ++i)
        {
            var pickerElem = document.createElement('span');
            $(pickerElem).addClass('star_picker_element');
            mPickerElems.push(pickerElem);
            $(mRootElem).append(pickerElem);

            var highlightElem = document.createElement('span');
            $(highlightElem).addClass('star_picker_highlight_element')
                .bind('mouseover', this.onHighlightElement, false)
                .bind('mouseout', this.onUnhighlightElements, false)
                .bind('click', this.onSelectElement, false);
            mHighlightElems.push(highlightElem);
            $(mHighlightRootElem).append(highlightElem);
        }
        $(mRootElem).append(mHighlightRootElem);
        return mRootElem;
    }

    this.selectIndex = function (aIndex) {
        aIndex = Math.max(0, Math.min(aIndex, mNumStars - 1));
        _addClassUpToIndex(aIndex, mPickerElems, 'selected');

        for (var i = 0; i < mListeners.length; ++i)
        {
            if (mListeners[i].onSelect)
            {
                mListeners[i].onSelect(mThis, aIndex);
            }
        }
    }

    this.onHighlightElement = function (aEvent)
    {
        var highlightedIndex = -1; 
        for (var i = 0; i < mHighlightElems.length; ++i) {
            if (this == mHighlightElems[i]) {
                highlightedIndex = i;
                break;
            }
        }
        if (highlightedIndex < 0)
            return;

        _addClassUpToIndex(highlightedIndex, mHighlightElems, 'highlighted');

        for (var i = 0; i < mListeners.length; ++i)
        {
            if (mListeners[i].onHighlight)
                mListeners[i].onHighlight(mThis, highlightedIndex);
        }
    };

    this.onUnhighlightElements = function ()
    {
        _removeClassFromElems(mHighlightElems, 'highlighted');
    };

    this.onSelectElement = function (aEvent)
    {
        var selectedIndex = -1; 
        for (var i = 0; i < mHighlightElems.length; ++i) {
            if (this == mHighlightElems[i]) {
                selectedIndex = i;
                break;
            }
        }
        if (selectedIndex < 0)
            return;

        mThis.selectIndex(selectedIndex);
    };

    this.addListener = function (aListener)
    {
        mListeners.push(aListener);
    };

    this.removeListener = function (aListener)
    {
        for (var i = 0; i < mListeners.length; ++i)
        {
            if (mListeners[i] == aListener)
            {
                mListeners.splice(i, 1);
                return;
            }
        }
    };

    // Adds a given class to all elements in the array aElems up to
    // aElem, and removes the class from the rest
    function _addClassUpToIndex(aIndex, aElems, aClass)
    {
        var i = 0;
        var highestAddedIndex = -1;
        for (i = 0; i < Math.min(aIndex + 1, mNumStars); ++i)
        {
            $(aElems[i]).addClass(aClass);
        }

        for (i = aIndex + 1; i < mNumStars; ++i)
        {
            $(aElems[i]).removeClass(aClass);
        }
    }

    function _removeClassFromElems (aElems, aClass)
    {
        for (var i = 0; i < mNumStars; ++i)
        {
            $(aElems[i]).removeClass(aClass);
        }
    }
};

var selectListener = 
{
    onSelect : function (aPicker, aIndex)
    {
        $('#selected_item').html('' + aIndex);
    }
};

$(document).ready(function () {
    var starPicker = new StarPicker();
    starPicker.addListener(selectListener);
    $('#picker').empty().append(starPicker.createElement(5, 'yellow'));
    starPicker.selectIndex(0);
})
