

<p align="center">
<img src=https://user-images.githubusercontent.com/74038190/225813708-98b745f2-7d22-48cf-9150-083f1b00d6c9.gif width="350" height="200"/>
</p>



$${\huge\color{Green}Routing \space \color{Green}Diagnostics \space \color{Green}App}$$


This CLI app runs diagnostics: Connectivity of subnets from each device, hardware information (fan speed, temperature), arp tables, and routing information. It saves to timestamped files, and reports are generated (see the word doc in the repository). After configuration changes it is ran again and major changes are generated into a report: loss of routing paths, cdp changes, major hardware changes. 

Currently it supports BGP and routing tables: extending it is easy as the program is modularized: i.e where ospf Link State default route packets are generated.


Eventual plan is to add diagnostics to Connection_Handler.py, to include checking for open ports, https connections, VPN checker, and a IPSEC tunnel fragmentation functions, + more. 

It is a CLI based app: a web hosted version may be added.

Advantage is manually setting conditions with code: something which may be difficult to do with SolarWinds:  i.e RFC 3101 sets P-Bit clear for OSPF redistribution. Cisco devices use 3101, yet it works different for Junos devices. We can account for this through code when testing redistribution issues.

To run it include a device_list.txt file in your code directory with device user, pass ,secret, ip_address (see example). The .txt file can be encrypted and decrypted when being read by Python

<p>The app has been tested on Cisco 3660, 7200 routers  and more updated ios firmware with IP Base, IP Services, Enterprise Base, and Advanced Enterprise Services. It has been tested on both a GNS3 and a CCIE level eve-ng lab with about 50 devices:  (https://ccie4all.wordpress.com/)  <br><br><br><p></p>








https://github.com/hfakoor222/Routing_Diagnostics_App/assets/105625129/ec28c1b3-b104-4015-b5fb-41560f396447




<p>
  <br>
  <br>
</p>

  $${\large\color{Green}Collaboration}$$
If you would like to contribute on this  project I am open to any suggestions, and collaboration.
I am open to any contributions, including and not limited to refactoring the view layer, adding diagnostics (HTTP checker, IPsec fragmentation checker, MTU checker: refer to the issues tab above for more), cloud API's (i.e running diagnostics on AWS routers/switches).
Currently I've found an interesting project which batch updates cisco devices from a single GUI, which I may integrate here.



🤗
