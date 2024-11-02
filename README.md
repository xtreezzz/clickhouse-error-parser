# ClickHouse Error Parser

This project extracts error information from the ClickHouse source code by parsing exception throws. It outputs the data in a unified JSON format for further analysis or integration with other tools.

## Table of Contents

- [Features](#features)
- [Unified JSON Schema](#unified-json-schema)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Parses C++ source files in the ClickHouse project.
- Extracts detailed error information including:
  - File path
  - Error code
  - Error code name
  - Error class name
  - Error message template
  - Error message variables
  - Severity level
  - Original code line
- Outputs data in a unified JSON schema.

## Unified JSON Schema

```json
{
  "errors": [
    {
      "file_path": "string",
      "error_code": "string or number",
      "error_code_name": "string",
      "error_class_name": "string",
      "error_message_template": "string",
      "error_message_variables": ["array of strings"],
      "severity_level": "string",
      "original_text": "string"
    }
  ]
}
```

## Prerequisites

- Python 3.6 or higher
- Clickhouse source code available locally
  - Clone the Clickhouse repository from [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/xtreezzz/clickhouse-error-parser.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd clickhouse-error-parser
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Currently, there are no external dependencies. If you add any, list them in `requirements.txt`.*

## Usage

Run the parser script using the following command:

```bash
python src/clickhouse_parser.py -s /path/to/clickhouse/source -o data/errors_clickhouse.json
```

- `-s`, `--source_directory`: (Required) Path to the ClickHouse source code directory.
- `-o`, `--output_file`: (Optional) Path to the output JSON file. Defaults to `data/errors_clickhouse.json`.

### **Downloading ClickHouse Source Code**

To obtain the ClickHouse source code, follow these steps:

1. **Clone the ClickHouse Repository:**

   ```bash
   git clone https://github.com/ClickHouse/ClickHouse.git
   ```

2. **Navigate to the ClickHouse Directory:**

   ```bash
   cd ClickHouse
   ```

   *Note: Ensure that you have the necessary permissions and sufficient disk space to clone the repository.*

## Examples

**Example command:**

```bash
python src/clickhouse_parser.py -s ~/ClickHouse -o data/errors_clickhouse.json
```

This command parses the ClickHouse source code located at `~/ClickHouse` and saves the extracted error information to `data/errors_clickhouse.json`.

## Project Structure

```
clickhouse-error-parser/
├── src/
│   └── clickhouse_parser.py      # Main parsing script
├── data/
│   └── errors_clickhouse.json    # Output JSON file (created after running the parser)
├── tests/
│   └── test_clickhouse_parser.py # Unit tests
├── README.md                     # Project documentation
├── LICENSE                       # Project license
└── requirements.txt              # Python dependencies
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](clickhouse-error-parser/LICENSE) file for details.
