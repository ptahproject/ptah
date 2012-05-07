define (
    'ptah-form', ['jquery', 'ptah', 'ptah-templates', 'bootstrap'],

    function($, ptah, templates) {
        "use strict";

        ptah.Form = function(component, mtype, data, options) {
            this.id = 'win'+ptah.guid()

            this.mtype = mtype
            this.component = component

            if (typeof data === 'undefined')
                data = {}
            this.data = data

            // options
            if (typeof options === 'undefined')
                options = {}
            this.options = options

            // templates
            this.tmpl = options.tmpl
            this.formtmpl = options.form

            // workspace
            $('body').append('<div id="'+this.id+'"></div>')

            this.window = null
            this.workspace = $('#'+this.id)

            // FileReader
            this.readers = []

            // start interaction
            if (mtype) {
                component.io.subscribe(mtype, this, this.message)

                var d = {'__init__': true}
                for (var name in this.data) {
                    d[name] = this.data[name]
                }
                component.send(mtype, data)
            }

            ptah.Form.window = this
        }

        ptah.Form.window = null

        ptah.Form.prototype = {
            window: null,
            templates: templates.form

            , toString: function() {
                return 'ptah.Form<'+this.mtype+'>'
            }

            , create_window: function() {
                var that = this
                var win = this.window

                win.modal()
                win.on('hidden', function() {that.destroy()})
                win.delegate(
                    '[data-action]', 'click',
                    this, function(ev) {
                        ev.data.action.call(ev.data, ev, this, ptah.get_options(this))
                    }
                )
            }

            , destroy_window: function() {
                if (this.window)
                    this.window.modal('hide')
            }

            , destroy: function() {
                if (this.mtype)
                    this.component.io.unsubscribe(this.mtype, this.message)

                this.destroy_window()

                if (this.workspace)
                    this.workspace.remove()

                if (this.content && this.content.remove)
                    this.content.remove()

                this.window = null
                this.workspace = null
            }

            , __send: function(self, data) {
                for (var i = 0; i < self.readers.length; i++) {
                    if (self.readers[i].readyState == 1) {
                        setTimeout(function() {self.__send(self, data)}, 200)
                        return
                    }
                }
                self.component.send(self.mtype, data)
            }

            , action: function(ev, el, options) {
                if (ev && ev.preventDefault)
                    ev.preventDefault()

                var action = $(el).attr('data-action')

                if (action === 'close') {
                    this.content.remove()
                    this.destroy()

                } else if (this.options[action]) {
                    this.options[action](options)

                } else {
                    this.workspace.css('cursor', 'wait')

                    var that = this
                    var data = {'__action__': action}
                    for (var name in this.data) {
                        data[name] = this.data[name]
                    }

                    var params = this.form.serializeArray()
                    for (var k in params) {
                        data[params[k].name] = params[k].value
                    }

                    var onload = function(name, reader, data) {
                        return function() {data[name] = reader.result}
                    }

                    $('input[type="file"]', this.form).each(function() {
                        if (this.files.length) {
                            var reader = new FileReader()
                            that.readers[that.readers.length] = reader

                            reader.onload = onload(this.name, reader, data)
                            reader.readAsBinaryString(this.files[0])
                            data[this.name+'-filename'] = this.files[0].name
                            data[this.name+'-mimetype'] = this.files[0].type
                        }
                    })
                    this.__send(this, data)
                }
            }

            , create: function(data) {
                this.workspace.show()

                // create form
                if (typeof(this.tmpl) === 'undefined' || this.tmpl === null)
                    this.workspace.append(
                        this.templates.render('form-window',data))
                else
                    this.workspace.append(this.tmpl(data))

                this.form = $('form', this.workspace)

                // title
                var el = $('[data-type="window-title"]', this.workspace)
                this.title = el.text()
                el.remove()

                // load fields
                this.content = $('[data-place="content"]', this.workspace)
                if (this.formtmpl)
                    this.content.append(this.formtmpl(data))

                // create window
                var that = this
                var win = $('[data-type="window"]', this.workspace)
                var options = ptah.get_options(win.get(0))

                this.window = win
                this.create_window()
            }

            , message: function(data) {
                if (data['__close__']) {
                    this.content.empty()
                    this.destroy()
                    if (data.message) {
                        if (this.options.on_message)
                            this.options.on_message(data.message)
                        else if (this.on_message)
                            this.on_message(data.message)
                    }
                    return
                }

                if (!this.window) {
                    this.create(data)
                } else {
                    this.content.empty()
                    if (!this.formtmpl)
                        this.content.append(this.templates.render('form', data))

                    this.workspace.css('cursor', 'default')
                }
            }
        }

        return ptah.Form
    }
)


define (
    'ptah-form2', ['jquery', 'ptah', 'ptah-templates'],

    function($, ptah, templates) {
        "use strict";

        return ptah.View.extend({
            __name__: 'ptah.form'

            , __init__: function(connect, mtype, dom, options) {
                this.connect = connect
                this.mtype = mtype

                this._super(null, dom, options)
            }

            , init: function() {
                this.data = this.options.data
                this.connect.io.subscribe(this.mtype, this, this.message)

                // start interaction
                var d = {'__init__': true}
                for (var name in this.data) {
                    d[name] = this.data[name]
                }
                this.connect.send(this.mtype, d)
            }

            , destroy: function() {
                this.connect.io.unsubscribe(this.mtype, this.message)
                this._super()
            }

            , __send: function(self, data) {
                for (var i = 0; i < self.readers.length; i++) {
                    if (self.readers[i].readyState == 1) {
                        setTimeout(function() {self.__send(self, data)}, 200)
                        return
                    }
                }
                self.component.send(self.mtype, data)
            }

            , action: function(ev, el, options) {
                if (ev && ev.preventDefault)
                    ev.preventDefault()

                var action = $(el).attr('data-action')

                if (action === 'close') {
                    this.content.remove()
                    this.destroy()

                } else if (this.options[action]) {
                    this.options[action](options)

                } else {
                    this.workspace.css('cursor', 'wait')

                    var that = this
                    var data = {'__action__': action}
                    for (var name in this.data) {
                        data[name] = this.data[name]
                    }

                    var params = this.form.serializeArray()
                    for (var k in params) {
                        data[params[k].name] = params[k].value
                    }

                    var onload = function(name, reader, data) {
                        return function() {data[name] = reader.result}
                    }

                    $('input[type="file"]', this.form).each(function() {
                        if (this.files.length) {
                            var reader = new FileReader()
                            that.readers[that.readers.length] = reader

                            reader.onload = onload(this.name, reader, data)
                            reader.readAsBinaryString(this.files[0])
                            data[this.name+'-filename'] = this.files[0].name
                            data[this.name+'-mimetype'] = this.files[0].type
                        }
                    })
                    this.__send(this, data)
                }
            }

            , render: function() {
            }

            , render_form: function() {
            }

            , render_fields: function() {
            }

            , render_actions: function() {
            }

            , create: function(data) {
                // create form
                if (typeof(this.tmpl) === 'undefined' || this.tmpl === null)
                    this.__dom__.append(
                        this.templates.render('form-window',data))
                else
                    this.__dom__.append(this.tmpl(data))

                this.form = $('form', this.__dom__)

                // title
                //var el = $('[data-type="window-title"]', this.__dom__)
                //this.title = el.text()
                //el.remove()

                // load fields
                this.content = $('[data-place="content"]', this.__dom__)

                // create window
                //var that = this
                //var win = $('[data-type="window"]', this.workspace)
                //var options = ptah.get_options(win.get(0))
                //this.window = win
            }

            , message: function(data) {
                if (data['__close__']) {
                    this.destroy()
                    if (data.message) {
                        if (this.options.on_message)
                            this.options.on_message(data.message)
                        else if (this.on_message)
                            this.on_message(data.message)
                    }
                    return
                }

                if (!this.window) {
                    this.create(data)
                } else {
                    this.__dom__.empty()
                    this.__dom__.append(this.templates.render('form', data))
                    this.__dom__.css('cursor', 'default')
                }
            }
        })
    }
)
