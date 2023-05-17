import csv

def remove_duplicates(input_file, output_file):
    seen = set()  # Set to store unique rows
    rows = []     # List to store unique rows in order

    with open(input_file, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            # Convert each row to a tuple to make it hashable
            row_tuple = tuple(row)
            if row_tuple not in seen:
                seen.add(row_tuple)
                rows.append(row)

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Duplicates removed. Unique rows saved to '{output_file}'.")


# Usage example:
input_file = 'example.csv'
output_file = 'output_singles.csv'
remove_duplicates(input_file, output_file)
