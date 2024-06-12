#!/bin/python3

from upload import upload

# send all test data at once
if __name__ == '__main__':
    requests = [
        ('sample_data/prefectures.csv', '/upload/csv/prefectures'),
        ('sample_data/cities.csv', '/upload/csv/cities'),
        ('sample_data/users.csv', '/upload/csv/users'),
        ('sample_data/products.csv', '/upload/csv/products')
    ]
    for file, url in requests:
        upload(f'http://localhost{url}', file)