"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal
import pytest

from tests.test_utils import UnitTestContextValidator
from validataclass.exceptions import RequiredValueError, InvalidTypeError, ListItemsValidationError, ListLengthError, \
    InvalidValidatorOptionException
from validataclass.validators import ListValidator, IntegerValidator, StringValidator, DecimalValidator


class ListValidatorTest:
    # Test ListValidator with valid lists of different types

    @staticmethod
    def test_valid_integer_list():
        """ Test ListValidator with IntegerValidator as item validator with valid integers. """
        validator = ListValidator(item_validator=IntegerValidator())
        assert validator.validate([123, 0, -42, 123]) == [123, 0, -42, 123]

    @staticmethod
    def test_valid_integer_list_empty():
        """ Test ListValidator with IntegerValidator as item validator with an empty list. """
        validator = ListValidator(item_validator=IntegerValidator())
        assert validator.validate([]) == []

    @staticmethod
    def test_valid_decimal_list():
        """ Test ListValidator with DecimalValidator as item validator with valid decimal strings. """
        validator = ListValidator(item_validator=DecimalValidator())
        output_list = validator.validate(['3.1415', '-0.42', '0'])
        assert all(isinstance(item, Decimal) for item in output_list)
        assert output_list == [Decimal('3.1415'), Decimal('-0.42'), Decimal('0')]

    @staticmethod
    def test_valid_nested_list():
        """ Test nested ListValidator to validate lists of lists of decimals. """
        input_list = [['3.1415', '42', '0'], ['-1.2', '2.4']]
        expected_list = [[Decimal('3.1415'), Decimal('42'), Decimal('0')], [Decimal('-1.2'), Decimal('2.4')]]

        validator = ListValidator(ListValidator(DecimalValidator()))
        output_list = validator.validate(input_list)

        for sublist in output_list:
            assert isinstance(sublist, list)
            assert all(isinstance(item, Decimal) for item in sublist)
        assert output_list == expected_list

    # Test ListValidator with invalid data

    @staticmethod
    def test_invalid_none():
        """ Check that ListValidator raises exceptions for None as value. """
        validator = ListValidator(item_validator=IntegerValidator())
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', 123, True, {'foo': 'bar'}])
    def test_invalid_not_a_list(input_data):
        """ Check that ListValidator raises exceptions for values that are not of type 'list'. """
        validator = ListValidator(item_validator=StringValidator())
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'list',
        }

    @staticmethod
    def test_invalid_decimal_list_items():
        """ Test ListValidator with DecimalValidator as item validator with invalid list items. """
        validator = ListValidator(item_validator=DecimalValidator())
        with pytest.raises(ListItemsValidationError) as exception_info:
            # Indices 1 and 4 are valid; indices 0, 2, 3 raise errors
            validator.validate([
                12,
                '1.234',
                None,
                'foobar',
                '42',
            ])

        assert exception_info.value.to_dict() == {
            'code': 'list_item_errors',
            'item_errors': {
                0: {'code': 'invalid_type', 'expected_type': 'str'},
                2: {'code': 'required_value'},
                3: {'code': 'invalid_decimal'},
            }
        }

    # Test ListValidator with a context-sensitive item validator

    @staticmethod
    def test_with_context_arguments():
        """ Test that ListValidator passes context arguments down to the item validator. """
        validator = ListValidator(item_validator=UnitTestContextValidator())
        assert validator.validate(['unit', 'test']) == [
            "unit / {}",
            "test / {}",
        ]
        assert validator.validate(['unit', 'test'], foo=42) == [
            "unit / {'foo': 42}",
            "test / {'foo': 42}",
        ]

    # Check that ListValidator actually discards invalid items

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_output', [
            ([-22, 0, 7], [-22, 0, 7]),
            ([-14, 0, 'lol', 42], [-14, 0, 42]),
            (['no', 'valid', 'items'], [])
        ]
    )
    def test_discard_integer_list(input_data, expected_output):
        """ Test ListValidator with IntegerValidator as item validator to discard invalid items. """
        validator = ListValidator(item_validator=IntegerValidator(), discard_invalid=True)
        assert validator.validate(input_data) == expected_output

    # Test list length requirement checks

    @staticmethod
    @pytest.mark.parametrize(
        'min_length, max_length, input_data', [
            # min_length only
            (0, None, []),
            (1, None, [42]),
            (1, None, [1, 2, 3]),
            (3, None, [1, 2, 3]),
            (3, None, [0, 0, 0, 0, 0, 0]),
            # max_length only
            (None, 0, []),
            (None, 1, []),
            (None, 1, [42]),
            (None, 3, []),
            (None, 3, [1, 2, 3]),
            # min_length and max_length
            (0, 0, []),
            (0, 1, []),
            (0, 1, [42]),
            (1, 3, [42]),
            (1, 3, [42, 42]),
            (1, 3, [123, 456, 789]),
            (2, 2, [42, -42]),
        ]
    )
    def test_list_length_valid(min_length, max_length, input_data):
        """ Test ListValidator with length requirements with lists of the correct length. """
        validator = ListValidator(IntegerValidator(), min_length=min_length, max_length=max_length)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'min_length, max_length, input_data', [
            # min_length only
            (1, None, []),
            (3, None, []),
            (3, None, [42]),
            (3, None, [1, 2]),
            # max_length only
            (None, 0, [1]),
            (None, 0, [1, 2, 3]),
            (None, 1, [1, 2]),
            (None, 3, [1, 2, 3, 4, 5, 6]),
            (None, 3, [0, 0, 0, 0]),
            # min_length and max_length
            (0, 0, [1]),
            (0, 1, [1, 2]),
            (0, 1, [0, 0, 0]),
            (1, 3, []),
            (1, 3, [12, 34, 56, 78]),
            (2, 2, []),
            (2, 2, [42]),
            (2, 2, [42, 0, -42]),
        ]
    )
    def test_list_length_invalid(min_length, max_length, input_data):
        """ Test ListValidator with length requirements with lists of the wrong length. """
        validator = ListValidator(IntegerValidator(), min_length=min_length, max_length=max_length)

        # Construct error dict with min_length and/or max_length, depending on which is specified
        expected_error_dict = {'code': 'list_invalid_length'}
        expected_error_dict.update({'min_length': min_length} if min_length is not None else {})
        expected_error_dict.update({'max_length': max_length} if max_length is not None else {})

        with pytest.raises(ListLengthError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == expected_error_dict

    @staticmethod
    @pytest.mark.parametrize(
        'min_length, max_length, input_data, expected_output', [
            # min_length only
            (1, None, [10, 'foo'], [10]),
            (1, None, [411, 2207, 'bar', 'baz'], [411, 2207]),
            (3, None, [1, 2, 3, 'nope', 5, 6], [1, 2, 3, 5, 6]),
            # max_length only
            (None, 1, ['ban'], []),
            (None, 3, [1, 2, 'gav'], [1, 2]),
            (None, 3, ['no', 'valid', 'item'], []),
            # min_length and max_length
            (1, 3, ['hell', 'sky', 5], [5]),
            (3, 5, [999, 999, 'poof', 999], [999, 999, 999])
        ]
    )
    def test_list_discard_length_valid(min_length, max_length, input_data, expected_output):
        """ Test ListValidator with lists of the correct length after discarding invalid items. """
        validator = ListValidator(IntegerValidator(), min_length=min_length, max_length=max_length,
                                  discard_invalid=True)
        assert validator.validate(input_data) == expected_output

    @staticmethod
    @pytest.mark.parametrize(
        'min_length, max_length, input_data', [
            # min_length only
            (1, None, ['foo']),
            (3, None, [1, 5, 'woosh', 'nah']),
            # max_length only
            (None, 1, ['lorem', 'ipsum', 1]),
            (None, 3, [1, 4, 'reit', 'plur']),
            # min_length and max_length
            (1, 1, ['strike']),
            (1, 2, ['sub', 'mar']),
            (1, 3, ['never', 'gonna', 'give', 'you', 'up']),
            (1, 5, ['never', 'gonna', 'let', 'you', 'down']),
            (3, 7, [13, 21, 'say', 'goodbye'])
        ]
    )
    def test_list_discard_length_invalid(min_length, max_length, input_data):
        """ Test ListValidator with length requirements with lists of the wrong length. """
        validator = ListValidator(IntegerValidator(), min_length=min_length, max_length=max_length,
                                  discard_invalid=True)

        # Construct error dict with min_length and/or max_length, depending on which is specified
        expected_error_dict = {'code': 'list_invalid_length'}
        expected_error_dict.update({'min_length': min_length} if min_length is not None else {})
        expected_error_dict.update({'max_length': max_length} if max_length is not None else {})

        with pytest.raises(ListLengthError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == expected_error_dict

    # Invalid validator parameters

    @staticmethod
    def test_min_length_greater_than_max_length():
        """ Check that ListValidator raises exception when min_length is greater than max_length. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            ListValidator(IntegerValidator(), min_length=4, max_length=3)
        assert str(exception_info.value) == 'Parameter "min_length" cannot be greater than "max_length".'

    @staticmethod
    def test_min_length_negative():
        """ Check that ListValidator raises exception when min_length is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            ListValidator(IntegerValidator(), min_length=-1)
        assert str(exception_info.value) == 'Parameter "min_length" cannot be negative.'

    @staticmethod
    def test_max_length_negative():
        """ Check that ListValidator raises exception when max_length is less than 0. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            ListValidator(IntegerValidator(), max_length=-1)
        assert str(exception_info.value) == 'Parameter "max_length" cannot be negative.'
