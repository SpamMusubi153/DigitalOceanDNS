import time
import socket
import requests
import json

# Welcome!

# This script uses the Digital Ocean Domain Record APIs to update all of the "A" DNS records
# for a specific set of domains. It is written solely using Python and the Python Standard Library.

# This script can be used in one of two modes:
# 1: As a free dynamic IP service you can run on your own server to ensure your DigitalOcean domains stay
#    up to date with your public IP address. This makes it easier and more feasible to run a webserver in
#    unstable network situations, such as residential IPs, while still using a domain name.
# 2: As an IP mirror service. Choose this option if you already use a dynamic IP service, such as No-IP
#    and want to keep your DigitalOcean domains pointed to your most recent IP. If you choose this option,
#    you don't necessarily have to run the script on your own server, and can even run it for free using
#    DigitalOcean functions!

# It is also possible to easily update this script for use in other scenarios by appropriately
# updating the get_server_ip function.

# To get started, fill out the "Required Values" section of the script below. Then, copy the entire file
# into the main function of a Digital Ocean "function". You can then schedule the script to regularly 
# update the DNS records of your websites.

# Good luck with your webhosting projects!

# ――――――――――――――――――――― #
# Environment Variables #
# ――――――――――――――――――――― #

# 
# 1A. Required Values for All Modes
# 

# Select your mode by referring to the mode descriptions above.
SELECTED_MODE = 1

# A list of the domains 
DOMAINS_TO_UPDATE = [
    "example.com", # Do not list sub-domains, such as www.example.com; if these domains have an "A" DNS record, they will be automatically detected by this script.
    "yourwebsite.org",
]

# A list of subdomains that will be excluded from the update process.
SUBDOMAINS_TO_EXCLUDE = [
    "www",    
]

# Your Digital Ocean API Key
DIGITAL_OCEAN_API_KEY = "YourDigitalOceanAPIKey"

# 
# 1B. Required Values for Mode 2
# 

# The address provided by the dynamic DNS service
DYNAMIC_DNS_HOSTNAME = "YourDynamicServerIPHostname"

# ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――― #

# 
# 2. Optional Values and Code
# 

# The base path of the Digital Ocean API Endpoint
BASE_DIGITAL_OCEAN_BASE_API_URL = "https://api.digitalocean.com/v2/domains/"

# Description:
#   This function obtains your server's IP address.
def get_server_ip(hostname):

    # For now, internal functions are used allow wrapping of code by the "attempt" function
    # to attempt this operation multiple times if it fails.

    # Retrieve an IP from an existing host name.
    def get_ip_from_other(hostname):
        return socket.gethostbyname(hostname)

    # OR

    # Retrieve the current machine's public IP Address.
    def get_current_machine_public_ip_address():
        QUERY_URLS = [
            "https://api.ipify.org",
        ]

        query_ip_results = []

        for i, current_url in enumerate(QUERY_URLS):
            current_query_result = requests.get(current_url).text.strip()
            query_ip_results.append(current_query_result)

            # Check to make sure that the most recent retured IP matches all IP previously returned.
            for j in range(0, i):
                if current_query_result != query_ip_results[j]:
                    raise Exception(f"The public ip query result from {current_url} ({current_query_result}) does not match the query result from {QUERY_URLS[j]} ({query_ip_results[j]}).")

        return query_ip_results[0]

    # Potential Future Code to Retrieve a Machine's Local IP Address
    # def retrieve_local_ip_address():
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.settimeout(0)
    #     s.connect(("1.1.1.1", 80))
    #     return s.getsockname()[0]

    
    if SELECTED_MODE == 2:  
        return attempt(get_ip_from_other, arguments=(hostname,))
    else:
        return attempt(get_current_machine_public_ip_address, arguments={})


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
def attempt(code_to_attempt, arguments = {}, maximum_number_of_attempts = 10, attempt_delay_time = 5):
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
    
    # Loop over all of the records and remove any subdomain records on the exclude list.
    for i, current_record_name in enumerate(record_id_names_under_domain):
        if current_record_name in SUBDOMAINS_TO_EXCLUDE:
            print(f"\tExcluding record with name {current_record_name} and id {record_ids_under_domain[i]}.")
            del record_ids_under_domain[i]
            del record_id_names_under_domain[i]
    
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