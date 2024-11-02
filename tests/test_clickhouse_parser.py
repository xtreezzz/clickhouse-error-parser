import unittest
from src.clickhouse_parser import split_arguments, extract_error_message_variables

class TestClickHouseParser(unittest.TestCase):

    def test_split_arguments_simple(self):
        argument_string = 'ErrorCodes::NO_ELEMENTS_IN_CONFIG, "No such connection '{}'", connection'
        expected = ['ErrorCodes::NO_ELEMENTS_IN_CONFIG', '"No such connection '{}'"', 'connection']
        result = split_arguments(argument_string)
        self.assertEqual(result, expected)

    def test_split_arguments_with_nested_parentheses(self):
        argument_string = 'ErrorCodes::INVALID_FUNCTION_ARGUMENT, "Invalid argument: {}", getArgument()'
        expected = ['ErrorCodes::INVALID_FUNCTION_ARGUMENT', '"Invalid argument: {}"', 'getArgument()']
        result = split_arguments(argument_string)
        self.assertEqual(result, expected)

    def test_extract_error_message_variables_simple(self):
        original_text = 'throw Exception(ErrorCodes::NO_ELEMENTS_IN_CONFIG, "No such connection '{}' in connections_credentials", connection);'
        expected_template = "No such connection '{}' in connections_credentials"
        expected_variables = ['connection']
        variables, template = extract_error_message_variables(original_text)
        self.assertEqual(template, expected_template)
        self.assertEqual(variables, expected_variables)

    def test_extract_error_message_variables_no_variables(self):
        original_text = 'throw Exception(ErrorCodes::UNKNOWN_ERROR, "An unknown error occurred.");'
        expected_template = "An unknown error occurred."
        expected_variables = []
        variables, template = extract_error_message_variables(original_text)
        self.assertEqual(template, expected_template)
        self.assertEqual(variables, expected_variables)

    def test_extract_error_message_variables_multiple_variables(self):
        original_text = 'throw Exception(ErrorCodes::TOO_MANY_ROWS, "Too many rows: {}", row_count);'
        expected_template = "Too many rows: {}"
        expected_variables = ['row_count']
        variables, template = extract_error_message_variables(original_text)
        self.assertEqual(template, expected_template)
        self.assertEqual(variables, expected_variables)

    def test_extract_error_message_variables_complex(self):
        original_text = 'throw Exception(ErrorCodes::COMPLEX_ERROR, "Error with values: {}, {}", val1, val2);'
        expected_template = "Error with values: {}, {}"
        expected_variables = ['val1', 'val2']
        variables, template = extract_error_message_variables(original_text)
        self.assertEqual(template, expected_template)
        self.assertEqual(variables, expected_variables)

if __name__ == '__main__':
    unittest.main()
