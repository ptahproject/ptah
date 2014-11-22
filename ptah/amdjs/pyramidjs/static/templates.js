define('pyramid:templates', ['handlebars'],
function (handlebars) {
    "use strict";

    var templates = {

        bundles: {},

        language: 'en',

        setLanguage: function(lang) {
            templates.language = lang
        },

        getBundle: function(name, category) {
            var bundle = templates.bundles[name]
            if (!bundle)
                throw Error("Can't find templates bundle: "+name)

            if (category) {
                if (!bundle[category])
                    throw Error("Can't find templates category: "+category)
                return bundle[category]
            }
            return bundle
        },

        i18n: function(bundle, context, fn, options) {
            var text = fn.call(context, context, options)

            if (bundle.__i18n__ &&
                bundle.__i18n__[text] &&
                bundle.__i18n__[text][templates.language])
                return bundle.__i18n__[text][templates.language]

            return text
        }
    }

    templates.Bundle = function (name, templates, categories) {
        this.name = name
        this.templates = templates
        if (categories) {
            for (var n in categories)
                this[n] = categories[n]
        }
    }

    templates.Bundle.prototype = {
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
                    console.log(e, name)
                }
            }
            return ''
        }
    }

    return templates
})
