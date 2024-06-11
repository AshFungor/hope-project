#!/bin/python3

from upload import upload

# send all test data at once
if __name__ == '__main__':
    requests = {
        ('prefectures.csv', '/upload/csv/prefectures'),
        ('cities.csv', '/upload/csv/cities'),
        ('users.csv', '/upload/csv/users'),
    }
    for file, url in requests:
        upload(f'http://localhost{url}', file)