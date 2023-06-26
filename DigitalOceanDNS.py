import time
import socket
import requests
import json

# Welcome!

# This script uses the Digital Ocean Domain Record APIs to update all of the "A" DNS records
# for a specific set of domains. It is written solely using Python and the Python Standard Library.

# When run as a Digital Ocean function, it is intended to update DNS records for a webserver 
# on a dynamically assigned IP address. This makes it easier and more feasible to run a webserver in
# unstable network situations, such as residential IPs, while still using a domain name.

# This script assumes the user already has access to a free dynamic IP service, such as No-IP that can
# be queried to provide the location of the server. It then enables a user to extend the service
# to other domains served by the same server.

# It is also possible to run this script on your own server, or in other scenarios by appropriately
# updating the get_server_ip function.

# To get started, fill out the "Required Values" section of the script below, and schedule the script
# to run regularly.

# Good luck on your webhosting projects!

# ――――――――――――――――――――― #
# Environment Variables #
# ――――――――――――――――――――― #

# 1. Required Values

# A list of the domains 
DOMAINS_TO_UPDATE = [
    "example.com", # Do not list sub-domains, such as www.example.com; if these domains have an "A" DNS record, they will be automatically detected by this script.
    "yourwebsite.org",
]

# The address provided by the dynamic DNS service
DYNAMIC_DNS_HOSTNAME = "YourDynamicServerIPHostname"

# Your Digital Ocean API Key
DIGITAL_OCEAN_API_KEY = "YourDigitalOceanAPIKey"

# ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #

# 2. Optional Values and Code

# The base path of the Digital Ocean API Endpoint
BASE_DIGITAL_OCEAN_BASE_API_URL = "https://api.digitalocean.com/v2/domains/"

# Description:
#   This function obtains your server's IP address.
def get_server_ip(hostname):

    # This internal function is used allow wrapping of this code by the "attempt" function
    # to attempt this operation multiple times if it fails.
    def get_ip(hostname):
        return socket.gethostbyname(hostname)
    
    return attempt(get_ip, arguments=(hostname,))


# ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #
# ――――――――――――――――― #
# Helper Functions  #
# ――――――――――――――――― #
# ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #

# Description:
#   This function queries the Digital Ocean API for a list of all of the "A" DNS records for a specific domain.
#   It then returns an array representing the record IDs as well as an array representing the record names.
def request_record_ids_for_domain(domain_name):
    response = requests.get(
        # Request all records associated with the current domain name, filtering for "A" records.
        BASE_DIGITAL_OCEAN_BASE_API_URL + domain_name + "/records?type=A",
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + DIGITAL_OCEAN_API_KEY
        },
    )

    # The raw json response is a dictionary that contains the keys: "domain_records", "links", and "meta".
    # Accessing the "domain_records" key yields an array with dictionaries that contain information about each "A" DNS record associated with the domain.
    # This includes the record id, which is required to update a record.

    # Two list comprehensions are used to extract the IDs and names from each record,
    # and are returned separately as arrays.
    return [record['id'] for record in response.json()['domain_records']], [record['name'] for record in response.json()['domain_records']]

# Description:
#   This function sends a patch request to the Digital Ocean API to update a specific "A" DNS record for a specific domain.
#   It requires the specific domain, record ID, and new server IP, and returns the request response.
def update_dns_record_ip(domain_name, record_id, new_ip):

    payload = {
        "data" : new_ip,
        "type" : "A",
    }

    response = requests.patch(
        BASE_DIGITAL_OCEAN_BASE_API_URL + domain_name + "/records/" + str(record_id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + DIGITAL_OCEAN_API_KEY
        },

        # Initial attempts to send the payload as a python dictionary failed,
        # likely due to interpretation as literal values.
        data = json.dumps(payload)
    )

    return response.json()

# Description:
#   This function determines if the written version of a number should include a letter "s".
def suffix(number):
    suffix = ""
    if(number > 1):
        suffix = "s"

    return suffix

# Description:
# 	This function repeatedly attempts to perform a passed in reference to a function of code (code_to_attempt) and ignores failures. 
# 	It will attempt the code until a specified number of attempts (maximum_number_of_attempts) is reached.
# 	Between attempts, it will wait for the specified attempt_delay_time in seconds.
# 	This function then returns the result of the function call, or returns "None" if all attempts failed.
def attempt(code_to_attempt, arguments = None, maximum_number_of_attempts = 10, attempt_delay_time = 5):
    current_attempt = 1
    
    while(current_attempt <= maximum_number_of_attempts):
        try:
            result = code_to_attempt(*arguments)
            return result
        except:
            current_attempt += 1
            time.sleep(attempt_delay_time)
    
    return None


# Determine the Server IP Address.
server_ip = get_server_ip(DYNAMIC_DNS_HOSTNAME)

# Count the number of user-specified domains to update, and summarize the program's pending actions to the user.
total_number_of_domains = len(DOMAINS_TO_UPDATE)
print(f"Now updating all \"A\" records under {total_number_of_domains} domain{suffix(total_number_of_domains)} to the new server IP address {server_ip}")

# Start a counter for the total number of variables updated.
total_number_of_records = 0

# Repeat the update process for each specified domain. 
for domain_name in DOMAINS_TO_UPDATE:

    # Determine the record IDs and record names.
    record_ids_under_domain, record_id_names_under_domain = request_record_ids_for_domain(domain_name)
    
    # Count the number of records to be updated under the domain and add the count to the total.
    numberOfRecords = len(record_ids_under_domain)
    total_number_of_records = total_number_of_records + numberOfRecords

    # Inform the user of the number of records found.
    print(f"\t{numberOfRecords} record{suffix(numberOfRecords)} were found under the domain {domain_name}")

    # Update each record and report the results.
    for i in range(numberOfRecords):
        response = update_dns_record_ip(domain_name, record_ids_under_domain[i], server_ip)
        print(f"\t\tThe record \"{record_id_names_under_domain[i]}\" was updated successfully!")
        print(f"\t\t\t{response['domain_record']}")

# Exit the program with a summary of the results.
print(f"\nAll {total_number_of_records} records under all {total_number_of_domains} domains have been updated successfully!\n")