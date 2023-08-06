import datetime
import json
import urllib.parse

from lxml import etree

if __name__ == '__main__':
    date_string = '2023-04-01T17:06:04.230z'

    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    date = datetime.datetime.strptime(date_string, fmt)

    s = date.timestamp()
    print(int(s))

    second = date.strftime("%s")
    print(second)