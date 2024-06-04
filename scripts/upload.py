# Use this to upload data to server
import requests
import pandas
import sys


def upload(url: str, filepath: str, is_header_preset: bool = True):
    print(f'reading data from {filepath}')
    header = 0 if is_header_preset else None
    frame = pandas.read_csv(filepath, header=header)
    print(f'receiving data: \n{frame}')
    print(f'sending to {url}')
    response = requests.post(url, data=frame.to_csv())
    print(f'request completed, response status: {response.status_code}')


if __name__ == '__main__':
    filepath = input('enter filepath to csb data: ')
    header = input('is header on top line? (Y/n): ')
    handle = int(input('where do you want to upload? (1 - users, 2 - cities, 3 - prefectures): '))
    host = input('enter host name: ')
    urls = {
        1: '/upload/csv/users',
        2: '/upload/csv/cities',
        3: '/upload/csv/prefectures'
    }
    if handle not in urls:
        print('you entered wring option for handle.')
        sys.exit(1)
    upload(f'http://{host}{urls[handle]}', filepath, header in ' yY')