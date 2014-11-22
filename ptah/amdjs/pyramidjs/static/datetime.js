define('pyramid:datetime', ['handlebars', 'moment'],
function(handlebars, moment) {
    function utc() {
        var d = new Date()
        var localTime = d.getTime()
        var localOffset = d.getTimezoneOffset() * 60000
        d.setTime(localTime + localOffset)
        return d
    }

    // datetime format
    var formats = {'short': 'M/D/YY h:mm A',
                   'medium': 'MMM D, YYY h:mm:ss a',
                   'full': 'MMMM, D, YYYY h:mm:ss a Z'}
    if (typeof(datetime_short) != 'undefined')
        formats['short'] = datetime_short
    if (typeof(datetime_medium) != 'undefined')
        formats['medium'] = datetime_medium
    if (typeof(datetime_full) != 'undefined')
        formats['full'] = datetime_full

    // handlebars dateTime formatters
    handlebars.registerHelper(
        'datetime', function(text, format) {
            if (text===null || typeof(text) === 'undefined')
                text = this

            text = String.trim(text)

            // create date
            var date = new Date(text)
            if (isNaN(date.getTime())) {
                console.log("Can't parse datetime value:", text)
                return text
            }

            // covnert to local time
            var localTime = date.getTime()
            var localOffset = date.getTimezoneOffset() * 60000
            date = new Date(localTime - localOffset)

            format = formats[format]
            if (!format)
                format = formats['short']

            // print date
            return moment(date).format(format)
        }
    )
})