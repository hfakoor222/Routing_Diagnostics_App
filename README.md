

<p align="center">
<img src=https://user-images.githubusercontent.com/74038190/225813708-98b745f2-7d22-48cf-9150-083f1b00d6c9.gif width="350" height="200"/>
</p>



$${\huge\color{Green}Routing \space \color{Green}Diagnostics \space \color{Green}App}$$


This CLI app runs diagnostics: Connectivity of subnets from each device, hardware information (fan speed, temperature, cdp tables + more), and routing information. It saves to timestamped files, and reports are generated (see the word doc in the repository). After configuration changes it is ran again and major changes are generated into a report.

Currently it supports BGP peering, routing tables, connectivity to all the ip addresses of a subnet, and hardware info: extending it is easy as the program is modularized. The underlying NAPALM library has built in device gathering commands (i.e. get arp table), that we can add to this, or manual code.


It is a CLI based app: a web hosted version may be added.

Advantage is manually setting conditions with code: something which may be difficult to do with SolarWinds. We have a lot of control on the changes we are tracking, when they were made, and the timestamped device configurations for those changes. The information is saved in a MongoDB document database.

This program has two extended features: a search function: ["ospf, redistribute bgp"] will find all OSPF which redistributes bgp. ["ip access", "any", 80] finds all devices with ACL's that permit port 80 connections. The app also batch updates devices and batch rollsback devices. Firstly it saves a config file in your MongoDB as mentioned before; seccondly it saves a backup copy of the old config on the device itself (i.e. cisco router) by using secure copy. So for example we can find all devices that have ACL's with port 80 and batch update them with new ACL's: and generate reports on routing tables - the reports show us the differences in routing conenctivity, next hop, cost metrics, + others - we can rollback if we don't like the results.

The program is of course threaded, so it runs multiple operations at once depending on cpu core count.

See the example report located above in this repository.

To run it include a device_list.txt file in your code directory with device user, pass ,secret, ip_address (see example). The .txt file can be encrypted and decrypted when being read by Python

<p>The app has been tested on Cisco 3660, 7200 routers  and more updated ios firmware with IP Base, IP Services, Enterprise Base, and Advanced Enterprise Services. It has been tested on both a GNS3 and a CCIE level eve-ng lab with about 50 devices:  (https://ccie4all.wordpress.com/)  <br><br><br><p></p>








https://github.com/hfakoor222/Routing_Diagnostics_App/assets/105625129/ec28c1b3-b104-4015-b5fb-41560f396447




<p>
  <br>
  <br>
</p>

  $${\large\color{Green}Collaboration}$$
If you would like to contribute on this  project:
I am open to any contributions, including and not limited to refactoring the view layer, adding diagnostics (HTTP checker, IPsec fragmentation checker, MTU checker: refer to the issues tab above for more), cloud API's (i.e running diagnostics on AWS routers/switches).



Currently I've found an interesting project which batch updates cisco devices from a single GUI, which I may integrate here.



🤗
