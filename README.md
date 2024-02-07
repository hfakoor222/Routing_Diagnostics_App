





$${\huge\color{Green}Routing \space \color{Green}Diagnostics \space \color{Green}App}$$


This CLI app runs diagnostics: Connectivity of subnets from each device, hardware information (fan speed, temperature, cdp tables + more), and routing information. It saves to timestamped files, and reports are generated (see the word doc in the repository). After configuration changes it is ran again and major changes are generated into a report.

Currently it supports BGP peering, routing tables, connectivity to all the ip addresses of a subnet, and hardware info: extending it is easy as the program is modularized. The underlying NAPALM library has built in device gathering commands (i.e. get arp table), that we can add to this, or manual code.

This is an agentless tool and does not require SNMP. It's great for comparing network and device changes after configuration changes.

In results_report (see result_report attachment above) we have available ram, power status of line cards on routers, fan status, cdp neighbors, entire routing tables with next hop, egress interface, and route metrics. When we make a change in the network and run reports:  if our next hop changes, or a route cost changes, or even the OSPF LSDB advertised link address changes for a route we will be notified. This makes it much faster than generating a workflow in SolarWinds or Cisco DNA Center. 

The program is threaded and runs in parallel on multiple devices - it handles multiple connections at once - i.e. for 200 devices it will take about 20 minutes to complete the reports.

All that is required is SSH port 22 to be open and the program can execute across sites.


This program has extended features: a search function: ["ospf, redistribute bgp"] will find all OSPF which redistributes bgp. ["ip access", "any", 80] finds all devices with ACL's that permit port 80 connections. This helps us find certain devices. If we want to batch update devices from the app we can do this.

The app also batch updates devices and batch rollsback devices. Firstly it saves a config file in your MongoDB as mentioned before; seccondly it saves a backup copy of the old config on the device itself (i.e. cisco router) by using secure copy. So for example we can find all devices that have ACL's with port 80 and batch update them with new ACL's: and generate reports. . This is great for making small configuration changes across multiple devices in your network.






https://github.com/hfakoor222/Routing_Diagnostics_App/assets/105625129/ec28c1b3-b104-4015-b5fb-41560f396447




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
