# parser for csv-files
def parse_csv(file):
    header = file.readline().decode('utf-8-sig').strip().split(';')
    print(header)
    rows = [row.decode('utf-8-sig').strip().split(';') for row in file.readlines()]
    print(rows)
    table = []
    for row in rows:
        new_row = {}
        for i in range(len(row)):
            new_row[header[i]] = row[i]
        table.append(new_row)
    return table
