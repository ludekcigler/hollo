var athletelog = new Object();

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
    }
}

athletelog.ui = new Object();

athletelog.ui.progress_display = {
    show: function () {
        var progress_display = document.getElementById('progress_display');

        if (!progress_display) {
            $('body').append('<div id="progress_display">Načítám...</div>');
        } else {
            $(progress_display).show();
        }
    },

    hide: function () {
        var progress_display = $('#progress_display');
        progress_display.hide();
    }
}
