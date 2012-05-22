define (
    'ptah', ['handlebars'],

    function (handlebars) {
        "use strict";

        var console = window.console

        var ptah = {
            guid: function() {
                var S4 = function() {
                    return (((1+Math.random())*0x10000)|0)
                        .toString(16).substring(1)}
                return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4())
            }

            , utc: function() {
                var d = new Date()
                var localTime = d.getTime()
                var localOffset = d.getTimezoneOffset() * 60000
                d.setTime(localTime + localOffset)
                return d
            }

            , gen_url: function(path) {
                var host = window.ptah_host || '//' + window.location.host
                if (host[host.length-1] === '/')
                    host = host.substr(host.length-1, 1)

                return host + path
            }

            , get_options: function(el, prefix, opts) {
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

            , init: function(modules) {
                ptah.modules = modules
                curl({paths:ptah.modules}, ['jquery','ptah-date-format'],
                     function($) {
                         $(function() {
                             $('[ptah]').each(function(index, el) {
                                 var dom = $(el)
                                 var name = dom.attr('ptah')
                                 if (ptah.modules[name])
                                     curl({paths:ptah.modules}, [name]).then(
                                         function(factory) {
                                             new factory(
                                                 null,dom,ptah.get_options(el))
                                         })
                                 else
                                     console.log("Module is not found:", name)
                             })
                             window.ptah = ptah
                         })
                     })
            }
        }

        /* Simple JavaScript Inheritance
         * By John Resig http://ejohn.org/
         * MIT Licensed.*/
        var initializing = false
        var fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

        // The base Object implementation (does nothing)
        ptah.Object = function(){}
        ptah.Object.prototype = {
            __name__: 'ptah.Object',
            __cleanup__: [],
            __initializers__: []

            , toString: function() {
                return this.__name__
            }

            , destroy: function() {
                for (var i=0; i<this.__cleanup__.length; i++) {
                    var item = this.__cleanup__[i]
                    if (typeof(item) === 'function')
                        item.call(this)
                    else if (item.remove && item.remove.call)
                        item.remove()
                }
                this.__cleanup__ = []
            }
            , add_cleanup_item: function(item) {
                this.__cleanup__.push(item)
            }
            , remove_cleanup_item: function(item) {
                var idx = this.__cleanup__.indexOf(item)
                while (idx != -1) {
                    this.__cleanup__.splice(idx)
                    idx = this.__cleanup__.indexOf(item)
                }
            }
        }

        // Create a new Object that inherits from this class
        ptah.Object.extend = function(prop) {
            var _super = this.prototype

            // Instantiate a base class (but only create the instance,
            // don't run the init constructor)
            initializing = true
            var prototype = new this()
            initializing = false

            // Copy the properties over onto the new prototype
            for (var name in prop) {
                // Check if we're overwriting an existing function
                prototype[name] = typeof prop[name] == "function" &&
                    typeof _super[name] == "function"&&fnTest.test(prop[name])?
                    (function(name, fn){
                        return function() {
                            var tmp = this._super

                            //Add a new ._super() method that is the same method
                            //but on the super-class
                            this._super = _super[name]

                            //The method only need to be bound temporarily,so we
                            //remove it when we're done executing
                            var ret = fn.apply(this, arguments)
                            this._super = tmp

                            return ret
                        }
                    })(name, prop[name]):
                prop[name]
            }

            // The dummy class constructor
            function Object() {
                if (!initializing) {
                    this.__cleanup__ = []

                    // All construction is actually done in the init method
                    if (this.__init__ && this.__init__.apply)
                        this.__init__.apply(this, arguments)

                    if (this.init && this.init.apply)
                        this.init.apply(this)

                    // run initializers
                    for (var i=0; i<this.__initializers__.length; i++) {
                        this.__initializers__[i](this)
                    }
                }
            }

            // Populate our constructed prototype object
            Object.prototype = prototype

            // Enforce the constructor to be what we expect
            Object.prototype.constructor = Object

            // And make this class extendable
            Object.extend = ptah.Object.extend

            // Copy initializers
            Object.prototype.__initializers__ =
                this.prototype.__initializers__.slice(0)

            for (var p in prototype) {
                if (ptah.initializers[p] && (typeof prototype[p]!=="function"))
                    try {
                        ptah.initializers[p](
                            Object, Object.prototype, prototype[p])
                    } catch(e) {console.log(e)}
            }
            return Object
        }

        ptah.initializers = {}

        ptah.EventChannel = function(prefix) {
            this.prefix = prefix || 'on_'
            this.handlers = []
            this.subscriptions = {}
        }

        ptah.EventChannel.prototype = {
            toString: function() {return 'ptah.EventChannel'},

            publish: function(topic) {
                var args = Array.prototype.slice.call( arguments, 1 ),
                    topicSubscriptions,
                    subscription,
                    length,
                    i = 0,
                    ret;

                // send to handlers
                for (var idx = 0; idx < this.handlers.length; idx++) {
                    var name = this.handlers[idx].prefix + topic
                    var context = this.handlers[idx].context

                    if (context[name] && context[name].apply)
                        context[name].apply(context, args)
                }

                // individual subscribers
                if (!this.subscriptions[topic]) {
                    return true
                }

                topicSubscriptions = this.subscriptions[topic].slice()

                for ( ; i < topicSubscriptions.length; i++) {
                    subscription = topicSubscriptions[i];
                    ret = subscription.callback.apply(subscription.context,args)
                    if (ret === false)
                        break
                }
                return ret !== false
            },

            has: function(topic) {
                return !!this.subscriptions[topic]
            },

            subscribe: function(topic, context, callback, priority) {
                if (typeof(topic) === 'object') {
                    var prefix = this.prefix
                    if (typeof(context) == 'string')
                        prefix = context

                    this.handlers[this.handlers.length] = {
                        context: topic, prefix: prefix}
                    return topic
                }

                if (arguments.length === 3 && typeof callback === "number") {
                    priority = callback
                    callback = context
                    context = null
                }
                if (arguments.length === 2) {
                    callback = context
                    context = null
                }
                priority = priority || 10

                var topicIndex = 0,
                    topics = topic.split( /\s/ ),
                    topicLength = topics.length,
                    added;
                for ( ; topicIndex < topicLength; topicIndex++) {
                    topic = topics[topicIndex]
                    added = false
                    if (!this.subscriptions[topic])
                        this.subscriptions[topic] = []

                    var i = this.subscriptions[topic].length - 1
                    var subscriptionInfo = {
                        callback: callback,
                        context: context,
                        priority: priority
                    }

                    for (; i >= 0; i--)
                        if (this.subscriptions[topic][i].priority <= priority) {
                            this.subscriptions[topic].splice(
                                i+1, 0, subscriptionInfo)
                            added = true
                            break
                        }

                    if (!added)
                        this.subscriptions[topic].unshift(subscriptionInfo)
                }
                return callback
            },

            unsubscribe: function(topic, callback) {
                if (typeof(topic) === 'object') {
                    for (var i = 0; i < this.handlers.length; i++)
                        if (this.handlers[i].context === topic) {
                            this.handlers.splice(i, 1)
                            i--
                        }
                    return
                }

                if (!this.subscriptions[topic])
                    return

                var length = this.subscriptions[topic].length

                for (var i = 0; i < length; i++)
                    if (this.subscriptions[topic][i].callback === callback) {
                        this.subscriptions[topic].splice(i, 1)
                        break
                    }
            }
        }

        ptah.ActionChannel = function(dom, options) {
            this.dom = dom
            this.events = options.events
            this.scope = options.scope
            this.prefix = options.prefix || 'action_'

            if (dom) {
                dom.undelegate('[data-action]', 'click')
                dom.delegate('[data-action]', 'click', this, this.__dispatch__)
                dom.delegate('[event-click]', 'click', this, this.__dispatch__)
            }
        }

        ptah.ActionChannel.prototype = {
            toString: function() {return 'ptah.ActionChannel'}

            , __dispatch__: function(ev) {
                if (ev && ev.preventDefault) {
                    ev.preventDefault()
                    ev.stopPropagation()
                }

                var that = ev.data

                var params = ptah.get_options(this)
                var options = ptah.get_options(ev.target, null, params)
                var action = params.action

                if (that.events && that.events.has(action))
                    that.events.publish(action, options)

                var name = that.prefix+action
                var handler = that.scope[name]
                if (handler && handler.call) {
                    try {
                        handler.call(that.scope, options, ev, ev.target)
                    } catch (e) {
                        console.log("Action:", action, e)
                    }
                }
            }
        }

        ptah.View = ptah.Object.extend({
            __name__: 'ptah.View'

            , __init__: function(parent, dom, options) {
                this.__parent__ = parent
                this.__container__ = dom
                this.__uuid__ = ptah.guid()
                this.__views__ = []

                if (typeof(options) === 'undefined')
                    options = {}

                if (options.__id__)
                    this.__id__ = options.__id__

                if (this.__id__)
                    dom.append('<div id="'+this.__id__+
                               '" data-uuid="'+this.__uuid__+'"></div>')
                else
                    dom.append('<div data-uuid="'+this.__uuid__+'"></div>')
                this.__dom__ = $('[data-uuid="'+this.__uuid__+'"]', dom)

                this.options = options
                this.events = new ptah.EventChannel('on_')
                this.events.subscribe(this)
                this.actions = new ptah.ActionChannel(this.__dom__,{scope:this})

                if (this.__parent__)
                    this.__parent__.add_subview(this)
            }

            , destroy: function() {
                this.reset()
                if (this.__parent__)
                    this.__parent__.remove_subview(this)
                this.__dom__.remove()
                this._super()
            }

            , add_subview: function(view) {
                for (var i=0; i < this.__views__.length; i++)
                    if (this.__views__[i] === view)
                        return

                this.__views__.push(view)
                this.events.publish('subview_added', view)
            }

            , remove_subview: function(view) {
                var i = 0
                while (i < this.__views__.length) {
                    if (this.__views__[i] === view) {
                        this.__views__.splice(i, 1)
                        this.events.publish('subview_removed', view)
                    } else {
                        i++
                    }
                }
            }

            , reset: function() {
                while (this.__views__.length) {
                    var view = this.__views__[0]
                    view.destroy()
                    this.remove_subview(view)
                }

                this.__views__ = []
                this.__dom__.empty()
            }

            , hide: function() {
                this.__dom__.hide()
            }

            , show: function() {
                this.__dom__.show()
            }

            , resize: function() {}
        })

        ptah.ViewContainer = ptah.View.extend({
            __name__: 'ptah.ViewContainer',
            view: null,
            view_name: null

            , __init__: function(parent, dom, options) {
                this._super(parent, dom, options)

                if (!this.__workspace__)
                    this.__workspace__ = this.__dom__
            }

            , reset: function() {
                this._super()
                this.view = null
            }

            , activate: function(name, options) {
                if (typeof(name) === 'undefined')
                    return

                if (this.view && this.view_name === name) {
                    this.view.show(options)
                    return
                }

                for (var i=0; i < this.__views__.length; i++)
                    if (this.__views__[i].__view_name__ === name) {
                        if (this.view)
                            this.view.hide()
                        this.view = this.__views__[i]
                        this.view.show(options)
                        this.view_name = name
                        this.resize()
                        this.events.publish('activated', name)
                        return
                    }

                var that = this
                curl([name]).then(
                    function(factory) {
                        if (that.view)
                            that.view.hide()

                        var comp = new factory(that, that.__workspace__)
                        comp.__view_name__ = name
                        that.view = comp
                        that.view.show(options)
                        that.view_name = name
                        that.events.publish('activated', name)
                        setTimeout(function(){that.resize()}, 50)
                    }
                )
            }
        })

        // 'connect' initializer
        // example: {'connect': 'protocol-name'}
        ptah.initializers.connect = function(ctor, proto, name) {
            proto.__initializers__.push(
                function(inst) {
                    inst.connect = new ptah.Connector(name, inst)
                    ptah.connection.register(name, inst.connect)

                    inst.add_cleanup_item(
                        function() {ptah.connection.unregister(inst.connect)})
                }
            )
            proto.send = function(tp, payload) {
                ptah.connection.send(name, tp, payload)
            }
        }

        // 'protocol' initializer, define protocol ptah.protocols['...']
        // example: {'protocol': 'protocol-name'}
        ptah.initializers.protocol = function(ctor, proto, name) {
            if (ptah.Protocol.registry[name]) {
                throw Error("Protocol is registeres " + name)
            }

            ptah.Protocol.registry[name] = proto
            console.log('Protocol has been registered:', name)

            if (!ptah.protocols[name]) {
                console.log("Creating '"+name+"' protocol.")
                ptah.protocols[name] = new ctor()
            }
        }

        ptah.Protocol = ptah.Object.extend({
            __name__: 'ptah.Protocol'

            , __init__: function() {
                this.events = new ptah.EventChannel('on_')
                this.connect = new ptah.Connector(this.protocol, this)
                this.io = this.connect.io

                this.connect.register()
            }

            , send: function(tp, payload) {
                ptah.connection.send(this.protocol, tp, payload)
            }

            , subscribe: function(topic, context, callback, priority) {
                this.events.subscribe(topic, context, callback, priority)
            }

            , unsubscribe: function(topic, callback) {
                this.events.unsubscribe(topic, callback)
            }

            , on_connect: function() {}
            , on_disconnect: function() {}
        })

        ptah.protocols = {}
        ptah.Protocol.registry = {}

        ptah.Connection = function(options) {
            this.conn = null
            this.components = []
        }

        ptah.Connection.prototype = {
            reconnect_count: 5,
            reconnect_time: 200,

            connect: function(url, transports) {
                this.url = url
                this.transports = transports
                var that = this
                var conn = new ptah.sockjs(this.url, transports)

                conn.onopen = function() {
                    that.conn = conn
                    console.log('[ptah.conn] Connected.')

                    // notify components
                    for (var i=0; i<that.components.length; i++)
                        that.components[i].component.on_connect()

                    that.reconnect_time=ptah.Connection.prototype.reconnect_time
                }

                conn.onclose = function(ev) {
                    for (var i=0; i<that.components.length; i++)
                        that.components[i].component.on_disconnect()

                    if (ev.code != 1000) {
                        that.conn = null;
                        that.reconnect_time = that.reconnect_time*2
                        console.log('Disconnected.')
                        if (that.reconnect_time > 10000)
                            that.reconnect_time = 10000

                        setTimeout(
                            function() {that.connect(that.url, transports)},
                            that.reconnect_time)
                    }
                }

                conn.onmessage = function(msg) {
                    var found = false
                    var data = msg.data
                    var item

                    for (var i=0; i<that.components.length; i++) {
                        item = that.components[i]
                        if (item.name === data['protocol']) {
                            found = true
                            item.component.__dispatch_io__(
                                data['type'], data['payload'], msg)
                        }
                    }

                    if (!found)
                        console.log("Unknown protocol:", data['protocol'])
                }
            },

            send: function(component, type, payload) {
                if (!this.conn)
                    return

                if (typeof(payload) == 'undefined')
                    payload = {}

                var json_text = JSON.stringify(
                    {protocol: component,
                     type: type,
                     payload: payload
                    },
                    null, 2);

                this.conn.send(json_text)
            },

            register: function(name, component) {
                this.components.push({name:name, component:component})
                if (this.conn)
                    component.on_connect()
            },

            unregister: function(component) {
                var i = 0
                while (i < this.components.length) {
                    if (this.components[i].component === component) {
                        if (this.conn)
                            this.components[i].component.on_disconnect()
                        this.components.splice(i, 1)
                    } else {
                        i++
                    }
                }
            },

            toString: function() {
                return "ptah.Connection<"+this.url+">"
            }
        }
        ptah.connection = new ptah.Connection()

        ptah.connect = function(transports) {
            curl({paths: ptah_amd_modules || {}}, ['sockjs'],
                 function(sockjs) {
                     ptah.sockjs = sockjs
                     ptah.connection.connect(
                         ptah.gen_url('/_ptah_connection'), transports)
                 })
        }

        ptah.Connector = function(name, instance){
            this.name = name
            this.io = new ptah.EventChannel('msg_')
            this.parent = instance
        }
        ptah.Connector.prototype = {
            register: function() {
                ptah.connection.register(this.name, this)
            },
            unregister: function() {
                ptah.connection.unregister(this)
            },
            __dispatch_io__: function(type, payload, msg) {
                var hid = 'msg_'+type
                var has_handler = false

                if (this.parent[hid])
                    try {
                        has_handler = true
                        this.parent[hid](payload, msg)
                    } catch(e) {
                        console.log(
                            "Exception in handler:", this.parent[hid], e)
                    }

                // distach to event channel
                if (this.io.has(type)) {
                    has_handler = true
                    this.io.publish(type, payload, msg)
                }

                if (this.parent.on_message) {
                    has_handler = true
                    this.parent.on_message(type, payload, msg)
                } else if (!has_handler) {
                    console.log("Unknown message: "+this.name+':'+type)
                }
            }

            , send: function(tp, payload) {
                ptah.connection.send(this.name, tp, payload)
            }

            , on_connect: function() {
                if (this.parent.on_connect)
                    try {
                        this.parent.on_connect()
                    } catch(e) {
                        console.log('on_connect excetion', this.parent, e)
                    }
            }

            , on_disconnect: function() {
                if (this.parent.on_disconnect)
                    try {
                        this.parent.on_disconnect()
                    } catch(e) {
                        console.log('on_disconnect excetion', this.parent, e)
                    }
            }
        }

        ptah.Templates = function (name, templates, categories) {
            this.name = name
            this.templates = templates
            if (categories) {
                for (var n in categories)
                    this[n] = categories[n]
            }
        }

        ptah.get_templates = function(name, category) {
            var bundle = ptah.Templates.bundles[name]
            if (!bundle)
                throw Error("Can't find templates bundle: "+name)

            if (category) {
                if (!bundle[category])
                    throw Error("Can't find templates category: "+category)
                return bundle[category]
            }
            return bundle
        }

        ptah.Templates.bundles = {}

        ptah.Templates.prototype = {
            get: function(name) {
                var that = this
                var render = function(context, partial, indent) {
                    return that.render(name, context, partial, indent)
                }
                return render
            },

            get_raw: function(name) {
                return this.templates[name]
            },

            render: function(name, context, partials) {
                if (typeof(context) === 'undefined')
                    context = {}

                if (typeof(partials) === 'undefined')
                    partials = this.templates

                if (!this.templates[name]) {
                    console.log("Can't find template:", name)
                    return ''
                } else {
                    try {
                        return this.templates[name](
                            context, {partials: partials})
                    } catch(e) {
                        console.log(e)
                    }
                }
                return ''
            }
        }

        ptah.language = 'en'

        ptah.i18n = function(bundle, context, fn, options) {
            var text = fn.call(context, context, options)

            if (bundle.__i18n__ &&
                bundle.__i18n__[text] &&
                bundle.__i18n__[text][ptah.language])
                return bundle.__i18n__[text][ptah.language]

            return text
        }

        return ptah
    }
)
