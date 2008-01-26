var athletelog = new Object();

athletelog.events = {
    
    /**
     * Registers a callback with an event
     */
    register_listener: function (aListener, aEvent) {
        if (athletelog.events._event_store[aEvent]) {
            if (athletelog.events._event_store[aEvent].indexOf(aListener) == -1)
                athletelog.events._event_store[aEvent].push(aListener);
        } else {
            athletelog.events._event_store[aEvent] = [aListener];
        }
    },

    /**
     * Unregisters previously registered listener with a given event
     * If no event is given, removes the listener from all events
     */
    unregister_listener: function (aListener, aEvent) {
        if (aEvent) {
            if (athletelog.events._event_store[aEvent]) {
                var idx = athletelog.events._event_store[aEvent].indexOf(aListener);
                athletelog.events._event_store[aEvent].splice(idx);
            }
        } else {
            for (evt in athletelog.events._event_store) {
                var idx = athletelog.events._event_store[evt].indexOf(aListener);
                athletelog.events._event_store[evt].splice(idx);
            }
        }
    },

    /**
     * Triggers an event aEvent, second argument is the element that triggered the event
     */
    trigger: function (aEvent, aElement, aArgs) {
        if (athletelog.events._event_store[aEvent]) {
            var s = athletelog.events._event_store[aEvent];
            for (var i = 0; i < s.length; ++i) {
                s[i](aElement, aArgs);
            }
        }
    },

    _event_store: {}
};

athletelog.utils = {
    
    // Format number n to a fixed length.
    // Example: number_format(20, '0000') -> '0020'
    number_format: function(n, zeros) {
        var s = zeros + n;
        return s.substr(s.length - zeros.length);
    },

    // Return server root address (eg. http://www.example.com/)
    get_server_root: function() {
        var re = /^(http[s]*:\/\/[^\/]+)\/.*$/;
        return document.location.href.match(re)[1];
    },

    // Return class which specifies day for a given element elem
    // i.e. 'day_2007-01-20'
    get_day_class: function (aElem) {
        var classes = aElem.className.split(' ');
        var day_re = new RegExp('^\s*[a-zA-Z]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$');
        for (var i = 0; i < classes.length; ++i) {
            if (day_re.test(classes[i])) {
                return classes[i];
            } 
        }
        return '';
    },

    get_athlete_id: function () {
        var classes = document.getElementById('athlete_selection').className.split(' ');
        var day_re = new RegExp('^athlete_(.*)$');
        for (var i = 0; i < classes.length; ++i) {
            m = classes[i].match(day_re);
            if (m) {
                return m[1];
            } 
        }
        return '';
    },

    get_class_match: function (aElem, aRegex) {
        var classes = aElem.className.split(' ');
        for (var i = 0; i < classes.length; ++i) {
            m = classes[i].match(aRegex);
            if (m) {
                return m;
            } 
        }
        return null;
    },

    /**
     * Loads content to set of elements, and calls a callback at the end
     *
     * @param aElements     Array of (element, URL, callback) to load from
     * @param aCallback     Callback function to call after the whole sequence loads
     * @param aArgs         Arguments to the callback function
     */
    load_to_elements: function (aElems, aCallback) {
        if (!aElems || aElems.length == 0) {
            athletelog.events.trigger("ajax-request-stop");
            if (aCallback) aCallback();
        } else {
            var elem = aElems[0].elem;
            var url = aElems[0].url;
            var callback = aElems[0].callback;
            
            aElems = aElems.splice(1, aElems.length);

            $(elem).load(
                url,
                function (aResponse) {
                    if (callback) callback(aResponse);

                    athletelog.utils.load_to_elements(aElems, aCallback)
                });
        }
    },

    get_first_day_of_week: function (aYear, aWeek) {
        var day = 1;
        var d = new Date("1/" + day + "/" + aYear);
        var week = parseInt(d.formatDate("W"));

        while (week != aWeek) {
            day += 7;
            
            d = new Date("1/" + day + "/" + aYear);
            week = parseInt(d.formatDate("W"));
        }

        day = Math.max(1, day - parseInt(d.formatDate("N")) + 1);
        return new Date("1/" + day + "/" + aYear);
    },

};

athletelog.ui = new Object();

athletelog.ui.progress_display = {
    show: function () {
        var progress_display = document.getElementById('progress_display');

        if (!progress_display) {
            $('body').append('<div id="progress_display">Loading...</div>');
        } else {
            $(progress_display).show();
        }
    },

    hide: function () {
        var progress_display = $('#progress_display');
        progress_display.hide();
    }
};

athletelog.events.register_listener(function () { athletelog.ui.progress_display.show(); }, "ajax-request-start");
athletelog.events.register_listener(function () { athletelog.ui.progress_display.hide(); }, "ajax-request-stop");

athletelog.ui.main_view = null;

$(document).ready(function () {
    $('#view_selection').corner('6px');
    $('#main_menu li a').corner('5px top');
});
