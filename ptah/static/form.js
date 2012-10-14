define (
    'ptah-form', ['jquery', 'pyramid', 'ptah-templates', 'bootstrap'],

    function($, pyramid, templates) {
        "use strict";

        var form = {}

        form.Form = pyramid.View.extend({
            __name__: 'ptah.Form',

            templates: templates.form

            , __init__: function(connect, mtype, data, options) {
                this.connect = connect
                this.mtype = mtype
                this.data = data

                var view = options ? options.parent : null
                if (!view)
                    view = connect instanceof pyramid.View?connect:connect.parent

                this._super(view, $('body'), options)
            }

            , init: function() {
                this.template = this.options.template
                this.connect.io.subscribe(this.mtype, this, this.message)

                // start interaction
                var d = [['__init__', true]]
                for (var name in this.data)
                    d.push([name, this.data[name]])

                this.connect.send(this.mtype, d)

                this.window = null
            }

            , destroy: function() {
                if (this.window)
                    this.window.modal('hide')

                this.connect.io.unsubscribe(this.mtype, this.message)
                this._super()
            }

            , action_action: function(options) {
                var action = options.name

                if (action === 'close') {
                    this.destroy()

                } else if (this.options[action]) {
                    this.options[action](options)

                } else {
                    this.__dom__.css('cursor', 'wait')

                    // predefined data
                    var data = [['__action__', action]]
                    for (var name in this.data)
                        data.push([name, this.data[name]])

                    // form data
                    var params = this.form.serializeArray()
                    for (var i=0; i<params.length; i++)
                        data.push([params[i].name, params[i].value])

                    // file fields
                    var form_files = []
                    $('input[type="file"]', this.form).each(function() {
                        if (this.files.length)
                            form_files.push(this)
                    })

                    var idx = 0
                    var that = this

                    var process_files = function() {
                        if (idx >= form_files.length) {
                            that.connect.send(that.mtype, data)
                            return
                        }

                        var f = form_files[idx]

                        idx += 1

                        if (f.files.length) {
                            var fidx = 0
                            var name = f.name

                            var process_file = function(files) {
                                var file = files[fidx]
                                var reader = new FileReader()
                                reader.onload = function (ev) {
                                    data.push([name+'-filename', file.name])
                                    data.push([name+'-mimetype', file.type])
                                    data.push([name, reader.result])

                                    fidx += 1
                                    if (fidx < files.length)
                                        process_file(files)
                                    else
                                        process_files()
                                }
                                reader.readAsBinaryString(file)
                            }

                            process_file(f.files)
                        }
                    }

                    if (form_files.length)
                        process_files()
                    else
                        this.connect.send(this.mtype, data)
                }
            }

            , create: function(data) {
                // create form
                if (typeof(this.template) === 'undefined')
                    this.__dom__.append(
                        this.templates.render('form-window',data))
                else {
                    this.__dom__.append(this.template(data))
                    $('[data-tag="fields"]', this.__dom__).append(
                        this.templates.render('form', data))
                }

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


        form.Window = pyramid.View.extend({
            __name__: 'ptah.Window',

            data: null,
            template: null

            , __init__: function(parent, options) {
                this._super(parent, $('body'), options)
            }

            , init: function() {
                this.create()
            }

            , create: function() {
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
