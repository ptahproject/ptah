define (
    'ptah-ws', ['ptah', 'sockjs'],

    function (ptah, sockjs) {
        "use strict";

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
                var conn = new sockjs(this.url, this.transports)

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
            ptah.connection.connect(ptah.gen_url('/_ptah_connection'))
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
        return ptah
    }
)
