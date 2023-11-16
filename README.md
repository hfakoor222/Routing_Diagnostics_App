


$${\color{Green}Routing \space \color{Green}Diagnostics \space \color{Green}App}$$

This program updates networking routers and switches with configurations. It connects to every network device before and after configuration changes, runs dignostics, and compares those diagnostics. 

The user is able to rollback the devices in batch, by typing in "Y", as rollback_configs are saved in directory and on the device. The configs
are transmitted using SCP (which network devices support). Obtaining the device configurations, and running network diagnostics is threaded,
so the processes run in parallel (considering GIL). 

Obtaining configurations is done via regex.findall: the configurations from devices are split into blocks. So searching for the first and last item in a block, or any and any item,  returns results. The user can search for  

     
      [router ospf, redistribute bgp]  
      and it finds all OSPF configs which redistribute bgp
 
       
     [router bgp, address-family ipv6]
     finds all ipv6 enabled bgp devices





    
The program is created in modules, so adding extra diagnostics is easy: afterwards it simply needs to be placed in the right section of the view layer. 



I've minimized 3rd party library use to stable libraries: NAPALM, time, os, re, logging, threading, and ipaddress.
Program is platform independent. Written in Python 3.

The program is geared more towards improving time complexity rather than memory use, as this is better for connecting to and writing/reading to devices.



The functions themselves are built for multi-use: it is possible to refactor these into classes and overload them, I may consider this while developing the program further.


I will be deciding between overloading classes, or simply using NAPALM's built in functions: 
<p align="center">
Here is about 1/3 of NAPALM's supported functions:  
  
                #    napalm_device.get_interfaces_counters  
                #    napalm_device.get_interfaces  
                #    napalm_device.get_interfaces_ip  
                #    napalm_device.get_facts  
                #    napalm_device.get_environment (temp, fan speed, cpu)  
                #    napalm_device.cli    (cli commands)  
                #    napalm_device.get_arp_table  
                #    napalm_device.get_bgp_config  
                #    napalm_device.get_bgp_neighbors  
                #    NAPALM includes about triple the fucntions I've listed  
                
</p>


My eventual plan is to add diagnostics to Connection_Handler.py, to include checking for open ports, https connections, VPN checker, and a IPSEC tunnel fragmentation functions, route costs. There's an argument for adding a spoofed ip header functionality as well, to ping from the central node.

Adding these in only means updating the view layer which is presented as CLI.
It is a CLI based app: update for curses library as an overlay, or a web hosted app may be added.

The one area I may refactor a good bit is the CLI.py view layer itself and rework the while loops into functions.

The app has been tested on Cisco 3660, 7200 routers  and more updated ios firmware with IP Base, IP Services, Enterprise Base, and Advanced Enterprise Services. It has been tested on both a GNS3 and a CCIE level eve-ng lab with about 50 devices:  (https://ccie4all.wordpress.com/)


To run it include a device_list.txt file in your code directory with device user, pass ,secret, ip_address (see example).

$${\color{Green}Collaboration}$$
If you would like to contribute on this  project I am open to any suggestions, and collaboration.
I am open to any contributions, including and not limited to refactoring the view layer, adding diagnostics, cloud API's.
Currently I've found an interesting project which batch updates cisco devices from a single GUI, which I may integrate here.



🤗
