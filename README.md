

<p align="center">
<img src=https://user-images.githubusercontent.com/74038190/225813708-98b745f2-7d22-48cf-9150-083f1b00d6c9.gif width="350" height="200"/>
</p>



$${\huge\color{Green}Routing \space \color{Green}Diagnostics \space \color{Green}App}$$


This CLI app runs diagnostics: Connectivity of subnets from each device, hardware information (fan speed, temperature), arp tables, and routing information. It saves to timestamped files, and reports are generated (see the report in the repository). After configuration changes it is ran again and major changes are generated into a report: loss of routing paths, cdp changes, major hardware changes. Currently it supports BGP and routing tables: extending it is easy as the program is modularized (for example obtaining where int he nwtwork OSPF link state packets are generated).

    
The program is created in modules, so adding extra diagnostics is easy: afterwards it simply needs to be placed in the right section of the view layer. 

My eventual plan is to add diagnostics to Connection_Handler.py, to include checking for open ports, https connections, VPN checker, and a IPSEC tunnel fragmentation functions, + more. There's an argument for adding a spoofed ip header functionality as well, to ping from the central node.

It is a CLI based app: update for curses library as an overlay, or a web hosted app may be added.

The app has been tested on Cisco 3660, 7200 routers  and more updated ios firmware with IP Base, IP Services, Enterprise Base, and Advanced Enterprise Services. It has been tested on both a GNS3 and a CCIE level eve-ng lab with about 50 devices:  (https://ccie4all.wordpress.com/)


To run it include a device_list.txt file in your code directory with device user, pass ,secret, ip_address (see example). The .txt file can be encrypted and decrypted when being rad by Python.

$${\color{Green}Collaboration}$$
If you would like to contribute on this  project I am open to any suggestions, and collaboration.
I am open to any contributions, including and not limited to refactoring the view layer, adding diagnostics, cloud API's.
Currently I've found an interesting project which batch updates cisco devices from a single GUI, which I may integrate here.



🤗
