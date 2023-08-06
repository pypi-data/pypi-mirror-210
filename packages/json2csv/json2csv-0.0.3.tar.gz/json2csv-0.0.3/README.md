# json2csv

json2csv is a Python library for converting JSON data to CSV format.

## Installation

You can install json2csv using pip:
    
    ```bash
    pip install json2csv
    ```

## Usage
    
    ```python
    import json2csv

    json_input = [
        {
            'name': 'John',
            'age': 30,
            'city': 'New York'
        },
        {
            'name': 'Jane',
            'age': 25,
            'city': 'London'
        },
        {
            'name': 'Bob',
            'age': 40,
            'city': 'Paris'
        }
    ]

    convertor = json2csv()

    convertor.convert(json_input, 'output.csv')
    ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
        

