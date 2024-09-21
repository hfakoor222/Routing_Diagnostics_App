





$${\huge\color{Green}Routing \space \color{Green}Diagnostics}$$


Program logs in parallel into multiple Cisco, Juniper, Arista devices performs network connectivity (to a range of IP subnets), obtains routing table, next hop, device hardware analysis, using NAPALM library (popular library built on SSH port 22) and stores into a report. It also stored the configuration to file repository.

After configuration changes in network devices we run the program again and a second report is compared to the first: Changes are outputted to a second report highlighting:
Connectivity loss (ping sweep of inputted subnet range), outgoing interface changes, next-hop changes bgp peering changes + more.


Snippets of the report:

```


{'ip_address': '10.0.6.128/29', 'via': 'via 10.0.1.130,', 'interface': 'FastEthernet1/0'}
...
get_arp_table: [
  {
    "interface": "FastEthernet0/0",
    "mac": "CA:04:4B:E2:00:00",
    "ip": "10.0.1.1",
    "age": 57.0
  },
...
Ping Results Grouped by IP Address (Ping Sweep)
IP Address: 10.0.1.2
11.0.1.1
11.0.1.2
...
Snapshot Of BGP Neighbors:
{
  "global": {
    "router_id": "10.0.1.1",
    "peers": {
      "10.0.0.2": {
        "local_as": 65000,
        "remote_as": 65000,
        "remote_id": "10.0.1.2",
        "is_up": True,
        "is_enabled": True,
        "description": "internal-2",
        "uptime": 4838400,
        "address_family": {
          "ipv4": {
            "sent_prefixes": 637213,
            "accepted_prefixes": 3142,
            "received_prefixes": 3142
          },
          "ipv6": {
            "sent_prefixes": 36714,
            "accepted_prefixes": 148,
            "received_prefixes": 148
          }
        }
      }
...
get_environment: {
  "cpu": {
    "0": {
      "%usage": 12.0
    }
  },
  "memory": {
    "used_ram": 55938912,
    "available_ram": 424734348
  },
  "temperature": {
    "invalid": {
      "is_alert": false,
      "is_critical": false,
      "temperature": -1.0
    }

```



The second report lists all the changes in devices against the first report. We can narrow down which changes we want to see by modifying the Python code.

There are many more functions built into NAPALM, 

NAPALM Functions:<br />
get_arp_table<br />
get_bgp_neghbors<br />
get_ipv6_neighbors_detail<br />
get_ntp_servers<br />
get_snmp_information<br />
get_vlans<br />

https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix

I've included custom functions as well (subnet ping sweep, nested regular expression search function (to pinpoint devices with certain configurations), routing table functions (changes in default route, Administrative Distance, Next Hop).


The program is multi-threaded, so it performs more than one device connection at once (about 10 connections for a 4 core system).

All that is required is SSH port 22 to be open and the program can execute across sites.


This program has extended features: a search function: ["ospf, redistribute bgp"] will find all OSPF which redistributes bgp. ["ip access", "any", 80] finds all devices with ACL's that permit port 80 connections. This helps us find certain devices. If we want to batch update devices from the app we can do this. We can then use a script to batch update devices (there's also a batch update and rollback tool integrated into the current code)


https://github.com/hfakoor222/Routing_Diagnostics_App/assets/105625129/ec28c1b3-b104-4015-b5fb-41560f396447

def threaded_napalm(device_connections, result_dict = None):
    for device, (device_type, device_ip, username, password, secret) in device_connections.items():

        threads = []
        for func in functions:
            thread = threading.Thread(target=napalm_functions, args=(device,))
            thread.start()
            threads.append(thread)
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
            # we include an optional result_dict in funciton signature so we can pass it in directly or pass the function to a dict itself
        return result_dict```





<p>
  <br>
  <br>
</p>

  $${\large\color{Green}Collaboration}$$
If you would like to contribute on this  project:
I am open to any contributions, including and not limited to refactoring the view layer, adding diagnostics (HTTP checker, IPsec fragmentation checker, MTU checker: refer to the issues tab above for more), cloud API's (i.e running diagnostics on AWS routers/switches).

<p align="center">
<img src=https://user-images.githubusercontent.com/74038190/225813708-98b745f2-7d22-48cf-9150-083f1b00d6c9.gif width="350" height="200"/>
</p>
