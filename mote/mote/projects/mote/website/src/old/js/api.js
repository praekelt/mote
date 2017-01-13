/* Class that performs multiple API calls in one request */
function MoteAPI(api_root) {
    this.api_root = api_root;
    this._stack = new Array();

    this.push = function(url, data, selector, callback) {
        // Dictionary values must be stringified else encoding fails
        for (k in data)
            data[k] = JSON.stringify(data[k]);
        this._stack.push({
            'url': url,
            'data': data,
            'selector': selector,
            'callback': callback
        });
    };

    this.run = function() {
        var calls = new Array();
        for (var i=0; i<this._stack.length; i++) {
            var el = this._stack[i];
            var url = el['url'];
            var data = el['data'] || {};
            calls.push(url + '?' + $.param(data));
        }
        $.getJSON(
            this.api_root + 'multiplex/',
            {'api_root': this.api_root, 'calls': JSON.stringify(calls)},
            this.callback(this)
        );
    };

    this.callback = function(sender) {
        // jQuery getJSON overwrites "this", hence this trickery
        return function(data) {
            for (var i=0; i<data.results.length; i++) {
                var result = data.results[i];
                var el = sender._stack[i];
                var selector = el['selector'] || null;
                var callback = el['callback'] || null;
                if (selector)
                    $(selector).html(result.rendered);
                if (callback)
                    callback(result);
            }
       }
    };

}
