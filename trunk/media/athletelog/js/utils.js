// Miscellaneous utility functions for the Log application

var hollo = Object();
hollo.utils = {

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
    get_day_class: function (elem) {
        var classes = elem.className.split(' ');
        var day_re = new RegExp('^\s*[a-zA-Z]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$');
        for (var i in classes) {
            if (day_re.test(classes[i])) {
                return classes[i];
            } 
        }
        return '';
    },

    show_edit_form: function (responseText, code, response) {
        // Insert the div for workout form
        if ($('#editFormWindow').length == 0) {
            var d = document.createElement('div');
            d.id = 'editFormWindow';
            $('body')[0].appendChild(d);
        }
        
        var w = $('#editFormWindow');
        w.css('width', 0.7 * window.innerWidth);
        w.css('height', 0.7 * window.innerHeight);
        w.css('top', 0.15 * window.innerHeight);
        w.css('left', 0.15 * window.innerWidth);
        w.css('display', 'block');
        
        w.html(responseText);
    }
}
