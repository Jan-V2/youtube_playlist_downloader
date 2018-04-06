# class="ProfileNav-value"
from pprint import pprint

import certifi
import urllib3

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())

html = http.request('GET', 'https://twitter.com/BuienRadarNL/').data

with open('test.html', 'ab') as file:
    file.write(html)

print('done')