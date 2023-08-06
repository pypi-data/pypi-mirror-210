import csv
import json

def json2csv(json_data, csv_path):
    """
    This function takes in a JSON data string and a CSV file path as parameters.
    The function converts the given JSON data into CSV format and writes it to the specified file.
    
    Args:
    json_data (str): A string containing JSON formatted data
    csv_path (str): A string representing the path to the CSV file
    
    Returns:
    None: The converted data is written to the specified CSV file location
    
    """
    # Load the JSON data
    data = json.loads(json_data)

    # Extract the header fields from the JSON data
    header_fields = set()
    for item in data:
        header_fields.update(item.keys())

    # Write the data to CSV
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_fields)
        writer.writeheader()
        writer.writerows(data)

