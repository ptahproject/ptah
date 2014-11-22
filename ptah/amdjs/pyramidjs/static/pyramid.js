define(
    'pyramid', ['backbone', 'underscore'],

    function (Backbone, _) {
        "use strict";

        var console = window.console

        var pyramid = {
            guid: function() {
                var S4 = function() {
                    return (((1+Math.random())*0x10000)|0)
                        .toString(16).substring(1)}
                return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4())
            },

            utc: function() {
                var d = new Date()
                var localTime = d.getTime()
                var localOffset = d.getTimezoneOffset() * 60000
                d.setTime(localTime + localOffset)
                return d
            },

            gen_url: function(path) {
                var host = window.AMDJS_APP_URL || '//' + window.location.host
                if (host[host.length-1] === '/')
                    host = host.substr(host.length-1, 1)

                return host + path
            },

            get_options: function(el, prefix, opts) {
                if (el.jquery)
                    el = el.get(0)

                prefix = prefix || 'data-'
                var len = prefix.length
                var options = opts || {}
                for (var idx=0; idx < el.attributes.length; idx++) {
                    var item = el.attributes[idx]
                    if (item.name.substr(0, len) === prefix)
                        options[item.name.substr(len)] = item.value
                }
                return options
            }
        }

        var viewOptions = ['parent']

        var View = pyramid.View = Backbone.View.extend({
            _optionsProps: [],

            attributes: function() {
                return {'data-uuid': pyramid.guid()}
            },

            delegateEvents: function(events) {
                if (!events)
                    events = _.result(this, 'events')
                if (!events)
                    events = {}

                events['click [on-click]'] = '_onClick'

                Backbone.View.prototype.delegateEvents.call(this, events)
            },

            setElement: function(element, delegate) {
                Backbone.View.prototype.setElement.call(this, element, delegate)

                if (!this.$el.parent().length)
                    this.$el.appendTo('body')

                return this
            },

            _configure: function(options) {
                Backbone.View.prototype._configure.call(this, options)

                _.extend(
                    this, _.pick(options, viewOptions))
                _.extend(
                    this, _.pick(options, this._optionsProps))
                _.extend(
                    this, _.pick(options, this.constructor.prototype._optionsProps))

                // attach handlers
                _.extend(
                    this, _.pick(options, _.functions(options)))
            },

            _onClick: function(ev) {
                if (ev && ev.preventDefault) {
                    ev.preventDefault()
                    ev.stopPropagation()
                }

                var options = pyramid.get_options(ev.target)

                options.event = ev
                options.target = ev.target

                var name = ev.target.attributes.getNamedItem('on-click').value

                var handler = this[name]
                if (handler && handler.call) {
                    try {
                        handler.call(this, options, ev)
                    } catch (e) {
                        console.log("on-click:", name, e)
                    }
                }
            }
        })

        return pyramid
    }
)
