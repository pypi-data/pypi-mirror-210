def transform_to_bool(bool_value: str | bool) -> bool:
    if type(bool_value) == bool:
        return bool_value

    if not bool_value:
        return False

    if bool_value == 'true':
        return True
    elif bool_value == 'false':
        return False

    raise ValueError(f'Value {bool_value} is not recognised')


# https://jamescooke.info/comparing-django-q-objects-in-python-3-with-pytest.html
# helper from james cook to test django q objects equality
def assert_q_equal(left, right):
    from django.db.models import Q
    """
    Test two Q objects for equality. Does is not match commutative.

    Args:
        left (Q)
        right (Q)

    Raises:
        AssertionError: When -
            * `left` or `right` are not an instance of `Q`
            * `left` and `right` are not considered equal.
    """
    assert isinstance(left, Q), f'{left.__class__} is not subclass of Q'
    assert isinstance(right, Q), f'{right.__class__} is not subclass of Q'
    assert str(left) == str(right), f'Q{left} != Q{right}'
