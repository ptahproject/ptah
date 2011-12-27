import ptah
from ptah.testing import TestCase


class TestPagination(TestCase):

    def test_pagination_values(self):
        page = ptah.Pagination(10)

        self.assertEqual(page.page_size, 10)
        self.assertEqual(page.left_neighbours, 3)
        self.assertEqual(page.right_neighbours, 3)

        page = ptah.Pagination(11, 5, 2)
        self.assertEqual(page.page_size, 11)
        self.assertEqual(page.left_neighbours, 5)
        self.assertEqual(page.right_neighbours, 2)

        self.assertEqual(page.offset(3), (page.page_size*2, page.page_size))

    def test_pagination_nb_begin(self):
        page = ptah.Pagination(10, 2, 2)

        self.assertRaises(ValueError, page, 1000, 0)

        self.assertEqual(
            page(1000, 1)[0], [1, 2, 3, None, 100])

        self.assertEqual(
            page(1000, 2)[0], [1, 2, 3, 4, None, 100])

        self.assertEqual(
            page(1000, 3)[0], [1, 2, 3, 4, 5, None, 100])

        self.assertEqual(
            page(1000, 4)[0], [1, 2, 3, 4, 5, 6, None, 100])

        self.assertEqual(
            page(1000, 5)[0], [1, None, 3, 4, 5, 6, 7, None, 100])

        self.assertEqual(
            page(1000, 6)[0], [1, None, 4, 5, 6, 7, 8, None, 100])


    def test_pagination_nb_end(self):
        page = ptah.Pagination(10, 2, 2)

        self.assertEqual(
            page(1000, 95)[0], [1, None, 93, 94, 95, 96, 97, None, 100])

        self.assertEqual(
            page(1000, 96)[0], [1, None, 94, 95, 96, 97, 98, None, 100])

        self.assertEqual(
            page(1000, 97)[0], [1, None, 95, 96, 97, 98, 99, 100])

        self.assertEqual(
            page(1000, 98)[0], [1, None, 96, 97, 98, 99, 100])

        self.assertEqual(
            page(1000, 99)[0], [1, None, 97, 98, 99, 100])

        self.assertEqual(
            page(1000, 100)[0], [1, None, 98, 99, 100])

    def test_pagination_zero_nb(self):
        page = ptah.Pagination(10, 0, 0)

        self.assertEqual(
            page(1000, 1)[0], [1, None, 100])

        self.assertEqual(
            page(1000, 2)[0], [1, 2, None, 100])

        self.assertEqual(
            page(1000, 3)[0], [1, None, 3, None, 100])

    def test_pagination_one_nb(self):
        page = ptah.Pagination(10, 1, 1)

        self.assertEqual(
            page(1000, 1)[0], [1, 2, None, 100])

        self.assertEqual(
            page(1000, 2)[0], [1, 2, 3, None, 100])

        self.assertEqual(
            page(1000, 3)[0], [1, 2, 3, 4, None, 100])

        self.assertEqual(
            page(1000, 4)[0], [1, None, 3, 4, 5, None, 100])

    def test_pagination_prev_next(self):
        page = ptah.Pagination(10, 3, 3)

        self.assertEqual(page(1000, 1)[1], None)
        self.assertEqual(page(1000, 2)[1], 1)
        self.assertEqual(page(1000, 3)[1], 2)
        self.assertEqual(page(1000, 100)[1], 99)

        self.assertEqual(page(1000, 100)[2], None)
        self.assertEqual(page(1000, 99)[2], 100)
        self.assertEqual(page(1000, 98)[2], 99)
        self.assertEqual(page(1000, 1)[2], 2)
