/* Class that performs multiple API calls in one request */
function MoteAPI(api_root, project_id) {
    this.api_root = api_root;
    this._stack = new Array();

    this.push = function(dotted_name, data, selector, callback) {
        this._stack.push({
            'dotted_name': dotted_name,
            'data': data,
            'selector': selector,
            'callback': callback
        });
    };

    this.run = function() {
        var calls = new Array();
        for (var i=0; i<this._stack.length; i++) {
            var el = this._stack[i];
            var dotted_name = el['dotted_name'];
            var data = el['data'] || {};
            calls.push({'id': dotted_name, 'data': data});
        }
        $.getJSON(
            this.api_root + 'multiplex/',
            {'project_id': project_id, 'calls': JSON.stringify(calls)},
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
