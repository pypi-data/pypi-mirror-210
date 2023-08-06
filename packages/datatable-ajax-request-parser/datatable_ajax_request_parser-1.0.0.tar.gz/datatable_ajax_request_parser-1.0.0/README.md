# Python Ajax Datatable Request Parser

This is a small package to help with parsing datatable requests


## Installation
simply do a `pip install datatable_ajax_request_parser`


## How to use

```python

from datatable_ajax_request_parser.parser import DTRequest, parse_datatable_raw_request_query 

sample_url = 'http://somedomain/?draw=1&columns%5B0%5D%5Bdata%5D=hostname&columns' \
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

parsed_query = parse_datatable_raw_request_query(sample_url)

```

By default, you will obtain a dict of the form
```python
{
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
```

If you wish to use the dataclasses defined, simply pass in `return_dt_request=True`. <br>
This will return an instance of `DTRequest` dataclass

## Django extension

If you are using this with Django, there's an extended version of the `DTRequest` dataclass `DjangoDTRequest`. <br>

Usage example:
```python
from datatable_ajax_request_parser.django_extension import get_django_datatable_query

sample_url = 'http://somedomain/?draw=1&columns%5B0%5D%5Bdata%5D=hostname&columns' \
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

parsed_query = get_django_datatable_query(sample_url)

```

get django-compliant order from request
`parsed_query.get_order_by()`

get django filters from request
`parsed_query.get_db_query_filter()`

You can pass in a parsed datatable dictionary to get an instance of `DjangoDTRequest` directly as well

```python
from datatable_ajax_request_parser.django_extension import DjangoDTRequest

DjangoDTRequest(parsed_dict=parsed_request)
```

## Footnote

Feel free to submit any PRs for improvements
