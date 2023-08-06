from django.db.models import Q
from django.test import TestCase

from datatable_ajax_request_parser.django_extension import DjangoDTRequest, get_django_datatable_query
from datatable_ajax_request_parser.utils import assert_q_equal


class DjangoAjaxRequestTestCase(TestCase):
    def setUp(self):
        self.sample_datatable_ajax_request = 'http://somedomain/?draw=1&columns%5B0%5D%5Bdata%5D=hostname&columns' \
                                             '%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%' \
                                             '5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&colum' \
                                             'ns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=ip_' \
                                             'address&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=tr' \
                                             'ue&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5B' \
                                             'value%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5' \
                                             'D%5Bdata%5D=username&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsea' \
                                             'rchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5' \
                                             'Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&' \
                                             'columns%5B3%5D%5Bdata%5D=type&columns%5B3%5D%5Bname%5D=&columns%5B3' \
                                             '%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns' \
                                             '%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%' \
                                             '5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start' \
                                             '=0&length=10&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1672804547475'

    def test_get_order_by(self):
        parsed_request = get_django_datatable_query(self.sample_datatable_ajax_request)

        result = parsed_request.get_order_by()

        self.assertEqual(result, ['hostname'])

        parsed_request.order[0].direction = 'desc'

        result = parsed_request.get_order_by()

        self.assertEqual(result, ['-hostname'])

    # @skip("Test will fail, but the function should return the expected result")
    def test_query_filter(self):
        parsed_request = {
            'draw': '1',
            'columns': {
                '0': {'data': 'hostname', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': 'abc', 'regex': 'true'}},
                '1': {'data': 'ip_address', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '', 'regex': 'false'}},
                '2': {'data': 'username', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '1234', 'regex': 'true'}},
                '3': {'data': 'type', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': 'hshs', 'regex': 'false'}}
            },
            'order': {'0': {'column': '0', 'dir': 'asc'}},
            'start': '0', 'length': '10',
            'search': {'value': 'jjj', 'regex': 'false'},
            '_': '1672804547475'
        }

        parsed_request = DjangoDTRequest(parsed_dict=parsed_request)

        result = parsed_request.get_db_query_filter()

        # (OR: ('hostname__icontains', 'jjj'),
        # ('hostname__iregex', 'abc'),
        # ('ip_address__icontains', 'jjj'),
        # ('username__icontains', 'jjj'),
        # ('username__iregex', '1234'),
        # ('type__icontains', 'jjj'),
        # ('type__icontains', 'hshs'))

        expected_result = Q(hostname__icontains='jjj') | \
            Q(hostname__iregex='abc') | \
            Q(ip_address__icontains='jjj') | \
            Q(username__icontains='jjj') | \
            Q(username__iregex='1234') | \
            Q(type__icontains='jjj') | \
            Q(type__icontains='hshs')

        assert_q_equal(result, expected_result)


