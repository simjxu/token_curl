from json import load
import requests
import time
import pexpect
import yaml
import threading

# Python script looks for a "credentials.yaml" and a "links.yaml" file.

ACCNT_NAME = None
PW = None
DAW_TOKEN = None
LINK = None
CLI_CMD = None

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
  LINK = loaded_links['Link1']['link']
  global CLI_CMD
  CLI_CMD = loaded_links['Link1']['cli']

  # Load current token
  with open('token.txt', 'r') as f:
    global DAW_TOKEN
    DAW_TOKEN = f.readline()

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
  data = response.json()
  print(data)

def main():
  # # Only needed if we decide to thread
  # # Load the YAML files
  # thread = threading.Thread(target=load_ymlFile)
  # thread.start()

  # # wait until thread is complete
  # thread.join()
  
  # # Generate a token
  # thread = threading.Thread(target=gen_token)
  # thread.start()

  # # wait until thread is complete
  # thread.join()

  # # Create GET request to the target link
  # curl_get()

  load_ymlFile()

  # First try to use the existing token, if it doesn't work, generate a new token. This saves some time
  try:
    curl_get()
  except:
    gen_token()
    curl_get()

if __name__ == '__main__':
    main()

