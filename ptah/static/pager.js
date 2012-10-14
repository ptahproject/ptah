define (
    'ptah-pager', ['jquery', 'pyramid', 'ptah-templates'],

    function ($, pyramid, templates) {
        "use strict";

        return pyramid.View.extend({
            templates: templates.pager

            , init: function() {
                var options = this.options | {}

                this.size = options.size | 0
                this.current = options.current | 1
                this.page_size = options.page_size | 30
                this.left_neighbours = options.left_neighbours | 3
                this.right_neighbours = options.right_neighbours | 3

                this.events = new pyramid.EventChannel('on_pager_')
            }

            , set_size: function(size) {
                this.size = size
                this.select_page(1)
            }

            , offset: function(current) {
                if (!current)
                    current = this.current
                return {offset: (current - 1) * this.page_size,
                        limit: this.page_size}
            }

            , build_pages: function(total, current) {
                var size = Math.round(total / (this.page_size+0.4))

                var pages = []
                var first = 1
                var last = size

                var prevIdx = current - this.left_neighbours
                var nextIdx = current + 1

                if (first < current)
                    pages[pages.length] = {no: first, 'cls': ''}
                if (first + 1 < prevIdx)
                    pages[pages.length] = {'cls': 'disabled'}

                for (var i=prevIdx; i<prevIdx + this.left_neighbours; i++) {
                    if (first < i)
                        pages[pages.length] = {no: i, 'cls': ''}
                }
                pages[pages.length] = {no: current, 'cls': 'active'}

                for (var i=nextIdx; i<nextIdx + this.right_neighbours; i++) {
                    if (i < last)
                        pages[pages.length] = {no: i, 'cls': ''}
                }

                if ((nextIdx + this.right_neighbours) < last)
                    pages[pages.length] = {'cls': 'disabled'}

                if (current < last)
                    pages[pages.length] = {no: last, 'cls': ''}

                // prev/next idx
                var prev = (current <= 1) ? null : current - 1
                var next = current >= size ? null : current + 1

                return {pages: pages,
                        prev: prev,
                        next: next}
            }

            , select: function(offset) {
            }

            , select_page: function(page) {
                this.current = page
                this.redraw(this.build_pages(this.size, page))
            }

            , action_page: function(options) {
                this.select_page(parseInt(options.page))
                this.events.publish('select', options.page)
            }

            , redraw: function(data) {
                this.__dom__.empty()
                this.__dom__.append(
                    this.templates.render('pager', data))
            }
        })
    }
)
