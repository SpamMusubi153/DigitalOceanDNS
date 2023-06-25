# DigitalOceanDNS
Digital Ocean DNS for Dynamic IPs

### Welcome!

This script uses the Digital Ocean Domain Record APIs to update all of the "A" DNS records for a specific set of domains. It is written solely using Python and the Python Standard Library.

When run as a Digital Ocean function, it is intended to update DNS records for a webserver on a dynamically assigned IP address. This makes it easier and more feasible to run a webserver in unstable network situations, such as **residential IPs**, while still using a domain name.

This script assumes the user already has access to a free dynamic IP service, such as No-IP that can be queried to provide the location of the server. It then enables a user to extend the service to other domains served by the same server.

It is also possible to run this script on your own server, or in other scenarios by appropriately updating the get_server_ip function.

To get started, fill out the "Required Values" section of the script below, and schedule the script to run regularly.

**Good luck on your webhosting projects!**
