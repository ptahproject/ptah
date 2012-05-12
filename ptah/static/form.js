define (
    'ptah-form', ['jquery', 'ptah', 'ptah-templates', 'bootstrap'],

    function($, ptah, templates) {
        "use strict";

        var form = {}

        form.Form = ptah.View.extend({
            __name__: 'ptah.Form',

            templates: templates.form

            , __init__: function(connect, mtype, data, options) {
                this.connect = connect
                this.mtype = mtype
                this.data = data

                var view = options.parent
                if (!view)
                    view = connect instanceof ptah.View?connect:connect.parent

                this._super(view, $('body'), options)
            }

            , init: function() {
                this.template = this.options.template
                this.connect.io.subscribe(this.mtype, this, this.message)

                // start interaction
                var d = {'__init__': true}
                for (var name in this.data) {
                    d[name] = this.data[name]
                }
                this.connect.send(this.mtype, d)

                // FileReader
                this.readers = []

                this.window = null
            }

            , destroy: function() {
                if (this.window)
                    this.window.modal('hide')

                this.connect.io.unsubscribe(this.mtype, this.message)
                this._super()
            }

            , __send: function(self, data) {
                for (var i = 0; i < self.readers.length; i++) {
                    if (self.readers[i].readyState == 1) {
                        setTimeout(function() {self.__send(self, data)}, 100)
                        return
                    }
                }
                self.connect.send(self.mtype, data)
            }

            , action_action: function(options) {
                var action = options.name

                if (action === 'close') {
                    this.destroy()

                } else if (this.options[action]) {
                    this.options[action](options)

                } else {
                    this.__dom__.css('cursor', 'wait')

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
                // create form
                if (typeof(this.template) === 'undefined')
                    this.__dom__.append(
                        this.templates.render('form-window',data))
                else
                    this.__dom__.append(this.template(data))

                this.form = $('form', this.__dom__)

                // title
                var el = $('[data-type="window-title"]', this.__dom__)
                this.title = el.text()
                el.remove()

                // fields
                this.content = $('[data-place="content"]', this.__dom__)

                // window
                var that = this
                this.window = $('[data-type="window"]', this.__dom__)
                this.window.modal()
                this.window.on('hidden', function() {that.destroy()})
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
                    this.content.empty()
                    this.content.append(this.templates.render('form', data))
                    this.__dom__.css('cursor', 'default')
                }
            }
        })


        form.Window = ptah.View.extend({
            __name__: 'ptah.Window',

            data: null,
            template: null

            , __init__: function(parent, options) {
                this._super(parent, $('body'), options)
            }

            , init: function() {
                var that = this

                this.__dom__.append(this.template(this.data))
                this.window = $('[data-type="window"]', this.__dom__)
                this.window.modal()
                this.window.on('hidden', function() {that.destroy()})
            }

            , destroy: function() {
                if (this.window)
                    this.window.modal('hide')
                this._super()
            }

            , action_close: function(options) {
                this.destroy()
            }
        })

        return form
    }
)
