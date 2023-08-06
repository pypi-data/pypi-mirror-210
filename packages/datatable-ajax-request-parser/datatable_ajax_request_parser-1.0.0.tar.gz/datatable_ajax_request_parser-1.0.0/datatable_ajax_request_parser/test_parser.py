from unittest import TestCase

from .dataclasses import DTColumn, DTOrder

from .parser import DTRequest, parse_datatable_raw_request_query


class ParserTestCase(TestCase):

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

    def test_parse_pure_dict(self):
        expected_answer = {
            'draw': '1',
            'columns': {
                '0': {'data': 'hostname', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '', 'regex': 'false'}},
                '1': {'data': 'ip_address', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '', 'regex': 'false'}},
                '2': {'data': 'username', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '', 'regex': 'false'}},
                '3': {'data': 'type', 'name': '', 'searchable': 'true', 'orderable': 'true',
                      'search': {'value': '', 'regex': 'false'}}
            },
            'order': {'0': {'column': '0', 'dir': 'asc'}},
            'start': '0', 'length': '10',
            'search': {'value': '', 'regex': 'false'},
            '_': '1672804547475'
        }

        answer = parse_datatable_raw_request_query(self.sample_datatable_ajax_request, False)

        self.assertEqual(expected_answer, answer)

    def test_parse_converted_dict(self):
        expected_answer = {'columns': [{'data': 'hostname',
                                        'name': '',
                                        'orderable': True,
                                        'search_is_regex': False,
                                        'search_value': '',
                                        'searchable': True},
                                       {'data': 'ip_address',
                                        'name': '',
                                        'orderable': True,
                                        'search_is_regex': False,
                                        'search_value': '',
                                        'searchable': True},
                                       {'data': 'username',
                                        'name': '',
                                        'orderable': True,
                                        'search_is_regex': False,
                                        'search_value': '',
                                        'searchable': True},
                                       {'data': 'type',
                                        'name': '',
                                        'orderable': True,
                                        'search_is_regex': False,
                                        'search_value': '',
                                        'searchable': True}],
                           'draw': 1,
                           'length': 10,
                           'order': [{'column': 0, 'direction': 'asc', 'index': 0}],
                           'search_regex': False,
                           'search_value': '',
                           'start': 0}

        answer = parse_datatable_raw_request_query(self.sample_datatable_ajax_request, True)

        self.assertEqual(expected_answer, answer.to_dict())

    def test_parse_as_dataclass(self):
        columns = []
        for column in [{'data': 'hostname',
                        'name': '',
                        'orderable': True,
                        'search_is_regex': False,
                        'search_value': '',
                        'searchable': True},
                       {'data': 'ip_address',
                        'name': '',
                        'orderable': True,
                        'search_is_regex': False,
                        'search_value': '',
                        'searchable': True},
                       {'data': 'username',
                        'name': '',
                        'orderable': True,
                        'search_is_regex': False,
                        'search_value': '',
                        'searchable': True},
                       {'data': 'type',
                        'name': '',
                        'orderable': True,
                        'search_is_regex': False,
                        'search_value': '',
                        'searchable': True}]:
            columns.append(DTColumn(**column))

        expected_answer = DTRequest(**{'columns': columns,
                                       'draw': 1,
                                       'length': 10,
                                       'order': [DTOrder(**{'column': 0, 'direction': 'asc', 'index': 0})],
                                       'search_regex': False,
                                       'search_value': '',
                                       'start': 0})

        answer = parse_datatable_raw_request_query(self.sample_datatable_ajax_request, True)

        self.assertEqual(expected_answer, answer)

