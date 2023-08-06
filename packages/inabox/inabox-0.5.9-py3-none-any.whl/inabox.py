import requests
import subprocess

def check_dns_resolution(hostname):
    command = ['dig', '+short', hostname]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        dns_output = result.stdout.strip()
        if dns_output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def setupdns(hostname, ip4):
  data = { "hostname": hostname, "ip_address": ip4 }

  url = "https://dns.openknowit.com/dns"
  headers = {"Content-Type": "application/json"}

  response = requests.post(url, json=data, headers=headers)

  if response.status_code == 200:
    print("DNS entry added successfully.")
  else:
    print(f"Failed to add DNS entry. Status code: {response.status_code}")


def inacbox():
  hostname = 'inabox.openknowit.com'
  if check_dns_resolution(hostname):
    print(f"The DNS resolution for {hostname} is correct.")
  else:
    print(f"The DNS resolution for {hostname} is incorrect or unavailable.")
   
