import json
import requests
import time
import pexpect
import yaml
import threading
from datetime import datetime

# Python script looks for a "credentials.yaml" and a "links.yaml" file.

# For colors being printed out
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Credential and HTTP globals
ACCNT_NAME = None
PW = None
DAW_TOKEN = None
LINK = None
CLI_CMD = None

# JSON file specific globals
APPROVERS = {}

def load_ymlFile():
  # Load the credentials
  with open('credentials.yaml', 'r') as stream:
    loaded_creds = yaml.safe_load(stream)
  global ACCNT_NAME
  ACCNT_NAME = loaded_creds['account_name']
  global PW
  PW = loaded_creds['password']
  
  # Load the links
  with open('links.yaml', 'r') as stream:
    loaded_links = yaml.safe_load(stream)
  global LINK
  LINK = loaded_links['Link2']['link']
  global CLI_CMD
  CLI_CMD = loaded_links['Link2']['cli']

  # Load current token
  with open('token.txt', 'r') as f:
    global DAW_TOKEN
    DAW_TOKEN = f.readline()
  
  # Load approver ids
  file = open('approvers.yaml','r')
  loaded_approvers = yaml.safe_load(file)
  global APPROVERS
  for key in loaded_approvers:
    APPROVERS[loaded_approvers[key]['id']] = loaded_approvers[key]['name']

def gen_token():

  # Generate a new token using appleconnect
  child = pexpect.spawn(CLI_CMD)
  child.expect(ACCNT_NAME + '\'s password:')
  child.sendline(PW)
  child.expect('DAW.*')
  global DAW_TOKEN 
  DAW_TOKEN = child.after[:-2].decode()     # :-2 removes the newline characters, decode() converts byte to string

  # Write to text file
  with open('token.txt', 'w') as f:
    f.write(DAW_TOKEN)

  # print(DAW_TOKEN)

def curl_get():

  cookies = {
      'dslang': 'US-EN',
      'geo': 'US',
      'acack': DAW_TOKEN
  }

  headers = {
      'Connection': 'keep-alive',
      'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
      'accept': 'application/vnd.api+json',
      'content-type': 'application/vnd.api+json',
      'sec-ch-ua-mobile': '?0',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
      'sec-ch-ua-platform': '"macOS"',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Dest': 'empty',
      'Accept-Language': 'en-US,en;q=0.9',
  }

  response = requests.get(LINK, headers=headers, cookies=cookies)
  return response.json()

def get_approver_status(jsondata):
  global APPROVERS
  for item in jsondata['included']:
    if item['type'] == 'approvals' and item['attributes']['status'] == 'available' and \
      len(item['attributes']['approval_statuses_compact']) != 0:

      entry_date = datetime.strptime(item['attributes']['created_at'],"%Y-%m-%dT%H:%M:%S.%fZ")
      if (datetime.today() - entry_date).days < 7:
        print(f"{bcolors.YELLOW}{item['attributes']['attachment_name']}{bcolors.HEADER}")
      else:
        print(f"{bcolors.HEADER}{item['attributes']['attachment_name']}{bcolors.HEADER}")
      
      for approver in item['attributes']['approval_statuses_compact']:
        if (datetime.today() - entry_date).days <= 7:
          print(f"{bcolors.YELLOW}{APPROVERS[approver['user_role_id']] + ': ' + approver['status']}{bcolors.HEADER}")
        else:
          print(f"{bcolors.HEADER}{APPROVERS[approver['user_role_id']] + ': ' + approver['status']}{bcolors.HEADER}")
      print("-------------------------------------------------------")


def main():

  load_ymlFile()

  # First try to use the existing token, if it doesn't work, generate a new token. This saves some time
  try:
    json_output = curl_get()
  except:
    gen_token()
    json_output = curl_get()
  
  # print(json_output)

  # Second parse the json data for unapproved approvals, and print approver status
  get_approver_status(json_output)

if __name__ == '__main__':
    main()

