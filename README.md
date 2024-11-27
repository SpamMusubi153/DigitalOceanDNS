# DigitalOceanDNS
Digital Ocean DNS for Dynamic IPs

### Welcome!

# Welcome!

This script uses the Digital Ocean Domain Record APIs to update all of the "A" DNS records for a specific set of domains. It is written solely using Python and the Python Standard Library.

This script can be used in one of two modes:

1. As a **free dynamic IP service** you can run on your own server to ensure your DigitalOcean domains stay up to date with your public IP address. This makes it easier and more feasible to run a webserver in unstable network situations, such as **residential IPs**, while still using a domain name.

 2. As an **IP mirror service**. Choose this option **if you already use a dynamic IP service**, such as No-IP and want to keep your DigitalOcean domains pointed to your most recent IP. If you choose this option, you don't necessarily have to run the script on your own server, and can even run it for free using DigitalOcean functions!

It is also possible to easily update this script for use in other scenarios by appropriately updating the get_server_ip function.

To get started, fill out the "Required Values" section of the script below. Then, copy the entire file into the main function of a Digital Ocean "function". You can then schedule the script to regularly update the DNS records of your websites.

**Good luck with your webhosting projects!**

<br>

<noscript><a href="https://liberapay.com/MusubiToTheMax/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a></noscript>

Thank you for stopping by! At this time, I am still working through college. If you found this project helpful, I would appreciate any support you are able to lend.
