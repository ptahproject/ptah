define (
    'ptah', ['jquery'],

    function (jquery) {
        "use strict";

        var ptah = {
            consts: {},

            log: function(){
                if (window.console && console.log && console.log.apply) {
                    console.log.apply(console, arguments)
                }
            },

            guid: function() {
                var S4 = function() {
                    return (((1+Math.random())*0x10000)|0)
                        .toString(16).substring(1);
                };
                return (S4()+S4()+"-"+S4()+"-"+S4()+
                        "-"+S4()+"-"+S4()+S4()+S4())
            },

            utc: function() {
                var d = new Date();
                var localTime = d.getTime();
                var localOffset = d.getTimezoneOffset() * 60000;
                d.setTime(localTime + localOffset);
                return d;
            },

            gen_url: function(path) {
                var host = window.ptah_host || '//' + window.location.host
                if (host[host.length-1] === '/')
                    host = host.substr(host.length-1, 1)

                return host + path
            },

            get_logger: function(name) {
                var logger = function(name) {
                    this.name = name;
                }

                logger.prototype = {
                    _log: function(args) {
                        if (window.console && console.log && console.log.apply)
                            console.log.apply(console, args)
                    },

                    info: function() {
                        var args = Array.prototype.slice.call(arguments);
                        args.unshift('[INFO] ['+this.name+']')
                        this._log(args);
                    }
                }

                return new logger(name);
            }

            , get_options: function(el, opts) {
                var options = opts || {}
                for (var idx=0; idx < el.attributes.length; idx++) {
                    var item = el.attributes[idx]
                    if (item.name.substr(0, 5) === 'data-')
                        options[item.name.substr(5)] = item.value
                }
                return options
            }

            , scan_and_create:  function(context, parent) {
                parent = parent || null

                jquery('[ptah]', context).each(function(index, el) {
                    var container = jquery(el)
                    if (!container.attr('ptah-object')) {
                        var name = container.attr('ptah')
                        container.attr('ptah-object', '1')

                        curl([name]).then(
                            function(factory) {
                                new factory(
                                    parent, container, ptah.get_options(el))
                            }
                        )
                    }
                })
            }
        }
        ptah.logger = ptah.get_logger('ptah');

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
                if (ptah.initializers[p] && (typeof prototype[p] !== "function"))
                    try {
                        ptah.initializers[p](
                            Object, Object.prototype, prototype[p])
                    } catch(e) {ptah.logger.info(e)}
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

                    for (; i >= 0; i--) {
                        if (this.subscriptions[topic][i].priority <= priority) {
                            this.subscriptions[topic].splice(i+1, 0, subscriptionInfo);
                            added = true
                            break
                        }
                    }

                    if (!added)
                        this.subscriptions[topic].unshift(subscriptionInfo)
                }
                return callback
            },

            unsubscribe: function(topic, callback) {
                if (typeof(topic) === 'object') {
                    for (var i = 0; i < this.handlers.length; i++) {
                        if (this.handlers[i].context === topic) {
                            this.handlers.splice(i, 1)
                            i--
                        }
                    }
                    return
                }

                if (!this.subscriptions[topic])
                    return

                var length = this.subscriptions[topic].length

                for (var i = 0; i < length; i++) {
                    if (this.subscriptions[topic][i].callback === callback) {
                        this.subscriptions[topic].splice(i, 1)
                        break
                    }
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
                var options = ptah.get_options(ev.target, params)

                if (that.events && that.events.has(params.action))
                    that.events.publish(params.action, options)

                var name = that.prefix+params.action
                var handler = that.scope[name]
                if (handler && handler.call) {
                    try {
                        handler.call(that.scope, options, ev, ev.target)
                    } catch (e) {
                        ptah.logger.info("Action:", params.action, e)
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

                if (options && options.__id__)
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
                this.actions = new ptah.ActionChannel(this.__dom__, {scope:this})
            }

            , destroy: function() {
                this.__dom__.remove()
                this._super()
            }

            , hide: function() {
                this.__dom__.hide()
            }

            , show: function() {
                this.__dom__.show()
            }
        })

        ptah.ViewContainer = ptah.View.extend({
            __name__: 'ptah.ViewContainer',
            view: null,
            view_name: null

            , __init__: function(parent, dom, options) {
                this.__views__ = {}

                this._super(parent, dom, options)

                if (!this.__workspace__)
                    this.__workspace__ = this.__dom__
            }

            , resize: function() {}

            , destroy: function() {
                for (var key in this.__views__) {
                    this.__views__[key].destroy()
                }
                this.view = null
                this.view_name = null
                this.__views__ = {}
                this.__workspace__.empty()

                this._super()
            }

            , activate: function(name, options) {
                if (typeof(name) === 'undefined')
                    return

                if (this.view && this.view_name === name) {
                    this.view.show(options)
                    return
                }

                this.view_name = name

                if (this.__views__[name]) {
                    if (this.view)
                        this.view.hide()
                    this.view = this.__views__[name]
                    this.view.show(options)
                    this.resize()
                    this.events.publish('activated', name)
                } else {
                    var that = this
                    curl([name]).then(
                        function(factory) {
                            if (that.view)
                                that.view.hide()

                            var comp = new factory(that, that.__workspace__)
                            comp.__dom__.attr("data-container", name)
                            that.__views__[name] = comp
                            that.view = comp
                            that.view.show(options)
                            that.events.publish('activated', name)
                            setTimeout(function(){that.resize()}, 200)
                        })
                }
            }
        })

        // 'connect' initializer
        // example: {'connect': 'protocol-name'}
        ptah.initializers.connect = function(ctor, proto, name) {
            proto.__initializers__.push(
                function(inst) {
                    inst.connect = new ptah.Connector(name, inst)
                    ptah.connection.register(inst.connect)

                    inst.add_cleanup_item(
                        function() {
                            ptah.connection.unregister(inst.connect)})
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
            ptah.logger.info('Protocol has been registered:', name)

            if (!ptah.protocols[name]) {
                ptah.logger.info("Creating '"+name+"' protocol.")
                ptah.protocols[name] = new ctor()
            }
        }

        ptah.Protocol = ptah.Object.extend({
            __name__: 'ptah.Protocol'

            , __init__: function() {
                this.events = new ptah.EventChannel('on_')
                this.connect = new ptah.Connector(this.protocol, this)
                this.io = this.connect.io

                ptah.connection.register(this.connect)
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
        })

        ptah.protocols = {}
        ptah.Protocol.registry = {}

        ptah.Connection = function(options) {
            this.conn = null
            this.components = []
            this.logger = ptah.get_logger('ptah.connection')
        }

        ptah.Connection.prototype = {
            reconnect_count: 5,
            reconnect_time: 200,

            connect: function(url) {
                this.url = url
                var that = this
                var conn = new ptah.sockjs(this.url, this.transports)

                conn.onopen = function() {
                    that.conn = conn
                    that.logger.info('Connected.')

                    // notify components
                    for (var name in that.components) {
                        var component = that.components[name]
                        if (component.on_connect)
                            try {
                                component.on_connect.call(component)
                            } catch(e) {
                                that.logger.info('Exception in ',that.handler,e)
                            }
                    }
                    that.reconnect_time=ptah.Connection.prototype.reconnect_time

                    // scan for components
                    ptah.scan_and_create()
                }

                conn.onclose = function(ev) {
                    for (var name in that.components) {
                        var component = that.components[name]
                        if (component.on_disconnect)
                            component.on_disconnect.call(component)
                    }
                    that.components = []

                    if (ev.code != 1000) {
                        that.conn = null;
                        that.logger.info('Disconnected.')
                        that.reconnect_time = that.reconnect_time*2
                        if (that.reconnect_time > 10000)
                            that.reconnect_time = 10000

                        setTimeout(
                            function() {that.connect(that.url)},
                            that.reconnect_time)
                    }
                }

                conn.onmessage = function(msg) {
                    var found = false
                    var data = msg.data
                    var component

                    for (var i=0; i<that.components.length; i++) {
                        component = that.components[i]
                        if (component.__ptah_name__ === data['protocol']) {
                            found = true
                            try {
                                component.__dispatch_io__(
                                    data['type'], data['payload'], msg)
                            } catch(e) {
                                that.logger.info(
                                    "Exception in component:",
                                    data['component'], e)
                            }
                        }
                    }

                    if (!found)
                        that.logger.info("Unknown component:",data['component'])
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

            register: function(component) {
                this.components.push(component)
                if (this.conn && component.on_connect)
                    component.on_connect()
            },

            unregister: function(component) {
                for (var i=0; i < this.components.length; i++)
                    if (this.components[i] === component)
                        delete this.components[i]
            },

            toString: function() {
                return "ptah.Connection<"+this.url+">"
            }
        }
        ptah.connection = new ptah.Connection()

        ptah.connect = function() {
            curl({paths: ptah_amd_modules || {}}, ['sockjs'],
                 function(sockjs) {
                     ptah.sockjs = sockjs
                     ptah.connection.connect(ptah.gen_url('/_ptah_connection'))
                 })
        }

        ptah.Connector = function(name, instance){
            this.name = name
            this.instance = instance
            this.io = new ptah.EventChannel('msg_')
            this.__ptah_name__ = name
        }
        ptah.Connector.prototype = {
            __dispatch_io__: function(type, payload, msg) {
                var hid = 'msg_'+type
                var handler = this[hid]
                var has_handler = false

                if (this.instance[hid])
                    try {
                        has_handler = true
                        this.instance[hid](payload, msg)
                    } catch(e) {
                        ptah.logger.info("Exception in handler:", handler, e)
                    }

                // distach to event channel
                if (this.io.has(type)) {
                    has_handler = true
                    this.io.publish(type, payload, msg)
                }

                if (this.instance.on_message) {
                    has_handler = true
                    this.instance.on_message(type, payload, msg)
                } else if (!has_handler) {
                    ptah.logger.info("Unknown message: "+this.name+':'+type)
                }
            }

            , send: function(tp, payload) {
                ptah.connection.send(this.name, tp, payload)
            }

            , on_connect: function() {
                if (this.instance && this.instance.on_connect)
                    this.instance.on_connect()
            }

            , on_disconnect: function() {
                if (this.instance && this.instance.on_disconnect)
                    this.instance.on_disconnect()
            }
        }

        ptah.Templates = function (name, templates) {
            this.name = name
            this.templates = templates
            this.logger = ptah.get_logger(name)
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
                    this.logger.info("Can't find template:", name)
                    return ''
                } else {
                    try {
                        return this.templates[name](
                            context, {partials: partials})
                    } catch(e) {
                        ptah.logger.info(e)
                    }
                }
                return ''
            }
        }

        return ptah
    }
)
