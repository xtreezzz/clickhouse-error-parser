import os
import re
import json
import logging
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Manual mapping for missing ErrorCodes
# Add pairs 'ErrorCode': numeric_code here
manual_error_code_map = {
    'ERROR_CODE_FOR_UNEXPECTED_NAME': 100,
    'storage_already_exists_error_code': 101,
    'too_many_rows_exception_code': 102,
    'too_many_bytes_exception_code': 103,
    # Add other missing codes here
    'NO_ELEMENTS_IN_CONFIG': 106,  # Manually added for your example
    'SOME_CODE': 107,               # Manually added for macro example
    'TOO_MANY_ROWS': 108,           # Manually added for your example
}

# Regular expression to find throw Exception(...) statements
exception_pattern = re.compile(
    r"""throw\s+Exception\s*\(\s*                # throw Exception(
    (?P<error_code>[\w:]+)\s*,\s*               # ErrorCodes::SOME_CODE,
    "(?P<template>(?:[^"\\]|\\.)+)"\s*,?       # "Message template", accounting for escaped quotes
    (?:[^)]*)\)                                 # Remaining parameters until )
    """,
    re.VERBOSE | re.DOTALL
)

# Regular expression to parse ErrorCodes.cpp
error_code_pattern = re.compile(
    r"""M\s*\(\s*(?P<num>\d+)\s*,\s*(?P<code>[A-Z0-9_]+)\s*\)\\?""",
    re.VERBOSE
)

# Additional regular expression for alternative ErrorCodes definitions (if necessary)
alternative_error_code_pattern = re.compile(
    r"""const\s+int\s+(?P<code>[A-Z0-9_]+)\s*=\s*(?P<num>\d+)\s*;""",
    re.VERBOSE
)

# Dictionary to map ErrorCodes to their numeric values
error_code_map = {}

def parse_error_codes(file_full_path):
    """
    Parses the ErrorCodes.cpp file to build a mapping from error code names to their numeric values.
    """
    try:
        with open(file_full_path, 'r', encoding='utf-8') as file:
            for line in file:
                match = error_code_pattern.search(line)
                if match:
                    num = int(match.group('num'))
                    code = match.group('code').strip()
                    if code in error_code_map:
                        logging.warning(f"Duplicate error code '{{code}}' found with number {{num}}. Previous number: {{error_code_map[code]}}.")
                    error_code_map[code] = num
                else:
                    # Attempt to find alternative definitions
                    match_alt = alternative_error_code_pattern.search(line)
                    if match_alt:
                        num = int(match_alt.group('num'))
                        code = match_alt.group('code').strip()
                        if code in error_code_map:
                            logging.warning(f"Duplicate error code '{{code}}' found with number {{num}}. Previous number: {{error_code_map[code]}}.")
                        error_code_map[code] = num
    except (UnicodeDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to read file {{file_full_path}}: {{e}}")

# Lists to store extracted data
orig_texts = []
error_codes = []
templates = []
exception_nums = []
file_paths = []
error_message_variables = []

def split_arguments(args_str):
    """
    Splits a string of arguments into a list, considering nested parentheses and quotes.
    """
    args = []
    current_arg = ''
    depth = 0
    in_quotes = False
    escape = False
    for char in args_str:
        if escape:
            current_arg += char
            escape = False
            continue
        if char == '\\':
            current_arg += char
            escape = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            current_arg += char
            continue
        if in_quotes:
            current_arg += char
            continue
        if char == '(':
            depth += 1
            current_arg += char
            continue
        if char == ')':
            depth -= 1
            current_arg += char
            continue
        if char == ',' and depth == 0:
            args.append(current_arg.strip())
            current_arg = ''
            continue
        current_arg += char
    if current_arg:
        args.append(current_arg.strip())
    return args

def parse_exceptions_in_file(file_full_path, relative_path):
    """
    Parses a single file to extract exceptions.
    """
    try:
        with open(file_full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for match in exception_pattern.finditer(content):
                orig_text = match.group(0).replace('\n', ' ').strip()
                error_code_full = match.group('error_code').strip()

                # Extract error code name without the ErrorCodes:: prefix
                if "::" in error_code_full:
                    error_code = error_code_full.split("::")[-1]
                else:
                    error_code = error_code_full  # If no prefix

                template = match.group('template').strip()

                # Parse arguments to extract error message variables
                # Assume that variables start from the third argument
                # Extract all arguments after the template
                template_start = orig_text.find('"')
                template_end = orig_text.find('"', template_start + 1)
                if template_start != -1 and template_end != -1:
                    args_substr = orig_text[template_end + 1:].strip()
                    if args_substr.startswith(','):
                        args_substr = args_substr[1:].strip()
                    args_list = split_arguments(args_substr)
                    error_vars = args_list
                else:
                    error_vars = []

                # Get numeric error code from the combined mapping
                exception_num = combined_error_code_map.get(error_code, None)
                if exception_num is None:
                    logging.warning(f"Error code '{error_code}' not found in ErrorCodes.cpp and manual mapping.")
                    exception_num = 0  # Assign a default value

                # Append extracted data to the respective lists
                orig_texts.append(orig_text)
                error_codes.append(error_code)
                templates.append(template)
                exception_nums.append(exception_num)
                file_paths.append(str(relative_path).replace('\\', '/'))
                error_message_variables.append(error_vars)
    except (UnicodeDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to read file {file_full_path}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse ClickHouse source code for exceptions.')
    parser.add_argument('-s', '--source_directory', required=True, help='Path to the ClickHouse source code directory.')
    parser.add_argument('-o', '--output_file', default='data/errors_clickhouse.json', help='Path to the output JSON file.')
    args = parser.parse_args()

    source_directory = Path(args.source_directory)
    output_file = Path(args.output_file)

    # Check if the source directory exists
    if not source_directory.exists():
        logging.error(f"Directory '{source_directory}' does not exist.")
        return

    # Update base_file_path based on the source_directory argument
    global base_file_path, error_codes_file_path
    base_file_path = source_directory
    error_codes_file_path = base_file_path / "src" / "Common" / "ErrorCodes.cpp"

    # Parse ErrorCodes.cpp
    if error_codes_file_path.exists():
        parse_error_codes(error_codes_file_path)
        logging.info(f"Parsing '{error_codes_file_path}' completed.")
    else:
        logging.error(f"File '{error_codes_file_path}' does not exist.")

    # Combine automatic and manual ErrorCodes mappings
    global combined_error_code_map
    combined_error_code_map = {**error_code_map, **manual_error_code_map}

    # Log a sample of the ErrorCodes mapping
    logging.info("Sample ErrorCodes mapping:")
    for i, (code, num) in enumerate(combined_error_code_map.items()):
        logging.info(f"{code}: {num}")
        if i >= 29:  # Display the first 30 entries for verification
            break

    # Walk through all files in the directory and parse exceptions
    total_files = 0
    for root, dirs, files in os.walk(base_file_path):
        # Exclude 'tests' directories (case-insensitive)
        dirs[:] = [d for d in dirs if d.lower() != 'tests']
        for file in files:
            if file.endswith(('.cpp', '.hpp', '.h', '.cxx', '.cc')):
                full_path = Path(root) / file
                try:
                    relative_path = full_path.relative_to(base_file_path)
                except ValueError:
                    # If the file is not within base_file_path, skip it
                    logging.warning(f"File '{full_path}' is not within '{base_file_path}'. Skipping.")
                    continue
                parse_exceptions_in_file(full_path, relative_path)
                total_files += 1

    # Calculate total exceptions found
    total_exceptions = len(orig_texts)

    # Log the results
    logging.info(f"Total files processed: {total_files}")
    logging.info(f"Total exceptions found: {total_exceptions}")

    if total_exceptions > 0:
        # Create a list of dictionaries for JSON output
        errors = []
        for i in range(total_exceptions):
            error_entry = {
                'file_path': file_paths[i],
                'error_code': exception_nums[i],
                'error_code_name': error_codes[i],
                'error_class_name': 'Exception',  # Since the regex only matches Exception
                'error_message_template': templates[i],
                'error_message_variables': error_message_variables[i],
                'severity_level': 'ERROR',
                'original_text': orig_texts[i]
            }
            errors.append(error_entry)

        # Save the results to a JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"errors": errors}, f, indent=4, ensure_ascii=False)
        logging.info(f"JSON successfully saved to '{output_file}'.")
        logging.info(f"Total exceptions: {total_exceptions}")
    else:
        logging.info("No exceptions found.")

    # Optionally, print the first few records for verification
    if total_exceptions > 0:
        logging.info("\nSample records:")
        for error in errors[:5]:
            print(json.dumps(error, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
