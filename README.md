# Routing_Diagnostics_App


This is a modularized program which updates networking routers and switches with configurations: there is a ping checker before and after the updates which pings ip_addres library compliant (RFC compliant)
address subnets, inputted by the user. It connects to every network device before and after configuration changes, runs dignostics, and compares those diagnostics. 
The user is able to rollback the devices in batch, by typing in "Y", as rollback_configs are saved in directory and on the device. The configs
are transitted using SCP (which network devices support). Obtaining the device configurations, and running network diagnostics is threaded,
so the processes run in parallel (considering GIL). 

The program is created in modules, so adding extra diagnostics is easy: it simply needs to be placed in the right section of the view layer.

It is a CLI based app: update for curses library as an overlay, or a web hosted app may be added.

I've minimized 3rd party library use to stable libraries. Uses NAPALM, time, os, re, logging, threading, and ipaddress libraries.

The program is geared more towards improving time complexity rather than memory use, as this is better for connecting to and writing/reading to devices.

It's mostly ran on dictionaries, with minimal list usage or modifications, which is better for memory (Python holds it's native info as dicts, and managing lists has high memory cost).


The functions themselves are built for multi-use: for example the get_configurations_threaded, and get_configurations functions under Search_Configurations.py
are used in different contexts: it is possible to refactor these into classes and overload them, i may consider this while developing the program further.

The functions throughout the modules are used in different contexts to populate dictionaries for comparisons. 

I will be deciding between overloading classes, or simply using NAPALM's built in functions: 

Here is about 1/3 of its supported functions:
                #     napalm_device.get_interfaces_counters
                #    napalm_device.get_interfaces
                #    napalm_device.get_interfaces_ip
                #    napalm_device.get_facts
                #    napalm_device.get_environment (temp, fan speed, cpu)
                #    napalm_device.cli    (cli commands)
                #    napalm_device.get_arp_table
                #    napalm_device.get_bgp_config
                #    napalm_device.get_bgp_neighbors
                #    NAPALM includes about triple the fucntions I've listed

This might mean overloading classes is not necessary.

My eventual plan is to add diagnostics to Connection_Handler.py, which include checking for open ports, https connections, VPN checker, and a IPSEC tunner fragmentation functions.

Adding these in only means updating the view layer which is presented as CLI.

The one area I may refactor a good bit is the CLI.py itself and rework the while loops into functions.
i.e.
                        while True:
                            if choice_res.lower() == "r":
                                device.discard_config()  # for production
                                # pass #quicker in testing environments
                            elif choice_res.lower() == "c":
                                try:
                                    device.commit_config()
                                    print("Merge Successful")
                                except Exception as e:
                                    print(f"merge error" + str({e}))
                                    print("If receiving a pattern detected error: make sure to have archive path, scp enabled," \
                                          "a nd proper formatting of your disk:/flash: directory on the device \n"
                                          "also make sure file prompt quiet is turned off on device, or set the variable to False")
                                    break
                            else:
                                choice_res = input("Rollback or commit changes? (C|R)")
                            device.close()  # finally closing the device: remember to explicitly open the device on each new call(done in functions)
                            break


This may be prudent as the program grows, and not to have a view layer running with long code. However this layer might be bettwe as a hosted web app
via Javascript and HTML.


if you would like to help on this project I am open to any suggestions, and collaboration.
          
