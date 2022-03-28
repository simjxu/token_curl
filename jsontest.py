import json


f = open('samplejson.json')
jsondata = json.load(f)

for item in jsondata['included']:
  if item['type'] == 'approvals' and item['attributes']['status'] != 'approved':
    print(item['attributes']['attachment_name'])
    print(item['attributes']['approval_statuses_compact'])