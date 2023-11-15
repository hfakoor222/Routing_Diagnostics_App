"""
This is the view layer of an MVC model.
It includes a lot of code, which is not appropriate to include in the "logic" modules.
This makes it less visually appealing, however if we were to refactor, or add more logic to our application
It keeps things organized and consistent.
"""

import argparse
import threading
import os
from napalm import get_network_driver
from napalm.base.exceptions import MergeConfigException
import re

from Sanity_Check_Diagnostics import get_valid_ip_addresses, get_valid_search_string
from Search_Configurations import get_configurations_threaded, search_configurations

from Connection_Handler import handle_ip_addresses, appending_to_ping_table, \
threaded_network_driver, obtain_bgp_table, initialize_device_connections, device_list_populator
from Connection_Handler import  device_connections #this is the one list that's necessary to import

import logging

import logging
logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

ping_results_before = {}
ping_results_after = {}
bgp_table_before = {}
config_dict_before = {}
output_dict_of_search_strings = {}



parser = argparse.ArgumentParser(description="Network Configuration and Diagnostics Tool")
parser.add_argument("--test-connectivity", action="store_true", help="Test IP Connectivity and proceed: abbreviation -> --test")
parser.add_argument("--other-functionality", action="store_true", help="Other Functionality (not implemented yet):  abbreviation --> --other")
args = parser.parse_args()

def center_text(text, width):
    padding = (width - len(text)) // 2
    return " " * padding + text
# terminal_width = os.get_terminal_size().columns

#This is a presantation layer
#I may update this with a CLI overlay, a web app seems overkill

def main(choice):
    if choice == "1":
        while True:
            sub_choice = input("Do you want to obtain the BGP table, search configurations, or return to Available Options? (bgp/search/return): ")
            if sub_choice.lower() == "bgp":
                obtain_bgp_table(device_connections, bgp_table_before)
                print(bgp_table_before)
            elif sub_choice.lower() == "search":
                print("You don't need to enter an exact configuration: i.e. entering: [router ospf 1, network 10.0.0.1 area 1]" \
                      " will suffice to find this configuration")
                search_strings = input(
                    'Please enter the list of search strings you want to find on devices: i.e: ["router bgp" , "address-family ipv6"] ' \
                    'will find all ipv6 enable bgp devices')
                while True:
                    search_strings = search_strings.strip('[]')
                    search_strings = re.split(r',\s*|\s*,\s*', search_strings)
                    integrity_check = get_valid_search_string(search_strings)
                    if integrity_check is not False:
                        print("here is your formatted list: " + str(integrity_check))
                        cont = input("Formatted correct? (Y|N)")
                        if cont.lower() == "y":
                            break
                        else:
                            # Prompt the user to re-enter the list
                            search_strings = input("Please re-enter the list of search strings: ")
                search_configurations(input_dict=config_dict_before , search_strings=search_strings,
                                      output_dict=output_dict_of_search_strings)
                """ 
                Below is a lot of code which updates a rollback configration file in your directory: logically it is better to place it here
                To clear the dictionary when new search strings for devices are inputted: Otherwise we could place it in the 
                load_merge_candidate  section of the code, as it uses the same nested loop and 
                a rollback is automatically geenrated on the device via NAPALM, and may slightly better in terms of speed:
                realistically we don't lose anything placing this code here via speed and gain logical clean code.
                Our output dict is a small subset of the devices which we found matching searches, so not too heavy in terms
                of time complexity
                """
                print("A rollback_file containing the device configuration has been saved in your directory")
                for key, value in output_dict_of_search_strings.items():
                    rollback_config = {}  # not needed, as we will save rollback configurations to a text file in directory, and also the router/switch itself
                    # print(device)  #--> device is our stored driver
                    for ip, result in config_dict_before.items():
                        if key == ip:
                            rollback_config[key] = config_dict_before[ip]
                            # rollback_config ={} This is the device's original config
                            rollback_config = {key: value for key, value in rollback_config.items() if value != ""}
                            # I hate using these memory hungry codes: it is used
                            # for faster loading of the config file to the device. Plus computers ares fast :)
                            rollback_file = "rollback_config.txt"  # creating a rollback file for NAPAM - NAPALM uses hard files for rolling back, similar to SCP
                            with open(rollback_file, "a+") as f:
                                f.write(
                                    str(rollback_config))  # we wrote the original configuration out to a text file, to be safe
                print()
                reset_options()  #output_dict_of_search_string will contain our search string to update



            elif sub_choice.lower() == "return":
                break
                # TODO:
                #  This return option is useful for when we extend out option set to beyond search strings
                #   napalm_device.get_interfaces_counters
                #    napalm_device.get_interfaces
                #    napalm_device.get_interfaces_ip
                #    napalm_device.get_facts
                #    napalm_device.get_environment (temp, fan speed, cpu)
                #    napalm_device.cli    (cli commands)
                #    napalm_device.get_arp_table
                #    napalm_device.get_bgp_config
                #    napalm_device.get_bgp_neighbors
                #    NAPALM includes about triple the fucntions I've listed


            else:
                print("Invalid choice. Please enter 'bgp', 'search', or 'return'.")
    elif choice == "2":
        # Implement other functionality
        print("Other functionality is not implemented yet.")
    elif choice == "3":
       return_to_main()

def reset_options():
    while True:
        print("Reset Options:")
        print("1. Clear all tables and restart the program")
        print("2. Merge candidate configurations: Will merge configs based on your search parameters entered before")
        print("3. Return to the top of the program")

        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            # Clear all tables and restart the program
            ping_results_before.clear()
            ping_results_after.clear()
            bgp_table_before.clear()
            config_dict_before .clear()
            output_dict_of_search_strings.clear()
            print("All tables have been cleared.")
            return  # Return to the main program loop :
            #TODO
            # here I should add logic to retrun to if name == main execution

        elif choice == "2":
            rollback_devices = []
            for key, value in output_dict_of_search_strings.items():  # this comes before device_connections - less lookups in the for loop: this is where we saved our matching strings
                processed_devices = []
                print("processed devices" + str(processed_devices))
                for device, (device_type, device_ip, username, password, secret) in device_connections.items():
                    # doing a double nested loop with limited lookups resolves to a  O(n log n) algorithm
                    if device_ip == key and device_ip not in processed_devices:
                        # if device_ip equals our key to the search parameter results we entered earlier
                        processed_devices.append(device_ip)
                        device.open()  # If we take too long in between updating configs, need to re-enable
                        rollback_devices.append(device)

                        while True:  # to really error check we'd indent this under if device_ip in config_dict_before

                            print("Will be updating Dev Ip: " + str(device_ip))
                            new_route_config = input(
                                "Enter a list of config statements, seperated by commas and outer brackets i.e. router ospf 1, network 10.0.0.1 0.0.0.7 area 1" \
                                " This config will merge into the previous config")
                            new_route_config = new_route_config.strip('[]')  # we strip these if user did or did not input them in
                            new_route_config = re.split(r',\s*|\s*,\s*',new_route_config)  # we split by a comma or comma with a space
                            # print(type(new_route_config)) #should be a list; re.split
                            # new_route_config = list(new_route_config)
                            try:
                                new_route_config = get_valid_search_string(new_route_config)  # we validate
                            except ValueError as e:
                                print("Value Error detected with search string:" + str(e))
                                continue  # go back to top of loop if we cant do get_valid_search_string(new_route_config)
                            if not new_route_config:
                                print("Invalid input. Please try again.")
                                # Go back to the top of the while loop
                                continue
                            new_route_config = "\n".join(new_route_config)  # adding a newline to each configuration command  to push it now to device
                            new_route_config = str(new_route_config).strip("[]")
                            new_route_config = new_route_config + str("\nend")
                            print(new_route_config)
                            print()
                            # this entire set of code mitigates bad inputs by the user - no quotations, quoted commas, with or without brackets, empty strings stripped, or pushed
                            print()
                            print("moving on to loading merge")
                            device.load_merge_candidate(filename=None, config=new_route_config)
                            print("The difference in configurations (+|-)")
                            print()
                            print(str(device.compare_config()))
                            break

                            # TODO:
                            #  Here we can place other comparisons: https, https, open ports, ssh ports, default routes
                            #  Trace routes, VPN checkers, and even changes in ip routing metrics
                            #  It may also be a good idea to compare total connectivity after config changes
                            #  and offer a complete rollback of all devices

                        choice_res = input("Rollback or commit changes? (C|R)")
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
                            #TODO
                            # A try except around the double while has no effect, the while loops handle this, for the most part, however it can catch other system level errors
            # # except Exception as e:
            # #     print(f"Failed to apply configuration changes to {device_ip}: {str(e)}")

            """
            We can run network diagnostics before commiting:  And what if an outage happens? This is why I commit everything first, and have option of rolling back
            after the fact, insteaf leaving merged configurations without commits, then running diagnostics
            """
            new_ping_results = {}  # Create a new dictionary to store ping results after the merge
            for ip, value in output_dict_of_search_strings.items():
                print("output_dict_of_search_before ping")
                print(ip)

                device, (device_type, device_ip, username, password, secret) in device_connections.items()
                if ip ==  device_ip:
                    appending_to_ping_table(ip_addresses, device_connections, new_ping_results)
            for key, value in new_ping_results.items():
                if key in ping_results_before:
                    corresponding_value = ping_results_before[key]
                    if sorted(value) == sorted(
                            corresponding_value):  # Using sorted() has a time complexity of O(n log n), more effecient than individual comparisons
                        print(f"Values for key {key} are the same in both dictionaries.")
                    else:
                        # Find the differences
                        connectivity_loss = set(corresponding_value) - set(value)
                        new_connectivity = set(value) - set(corresponding_value)

                        # Print the differences
                        if connectivity_loss:
                            print(f"Connectivity loss for key {key}: {list(connectivity_loss)}")
                        if new_connectivity:
                            print(f"New connectivity for key {key}: {list(new_connectivity)}")
            rewrite_rollback = input(
                "Do you want to rewrite the rollback_config on all devices? (Y/N): ").strip().lower()

            while True:
                if rewrite_rollback.lower() == 'y':
                    for device in rollback_devices:
                        try:
                            device.open()
                            device.load_replace_candidate(
                                filename='rollback_config.txt')  # Assuming 'rollback_config.txt' is the file you want to use
                            device.commit_config()
                            print(f"rollback_config has been rewritten on {device.hostname}.")
                        except Exception as e:
                            print(f"Failed to rewrite rollback_config on {device.hostname}: {str(e)}")
                        finally:
                            device.close()
                    break
                elif rewrite_rollback.lower() == 'n':
                    print("Rollback_config has not been rewritten on any devices.")
                    break
                rewrite_rollback = input(
                    "Do you want to rewrite the rollback_config on all devices? (Y/N): ").strip().lower()



        elif choice == "3":
            # Return to the top of the program
            return

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    print("*************************************************")
    print("*                                               *")
    print("*   Welcome to the Network Configuration and    *")
    print("*         Diagnostics Tool!                     *")
    print("*                                               *")
    print("*************************************************")
    print()

    device_list = device_list_populator("device_list.txt")  # basic device list populator
    print("Here is a summary of your devices in device_list.txt:")
    print(device_list[:2])
    print()

    try:
        threaded_network_driver(device_list) #populating device_connections
    except Exception as e:
        print("An error occurred during device connection initialization:")
        print(e)
        import traceback   # I am not a fan of verbose code, or importing even standard libraries when I can avoid it, it is necessary here
        traceback.print_exc()
        print("There seems to be an error: This is probably due to your device_list.txt file not existing, or its formatting")
        print("Please refer to the exception trace above, supply a list in the programs directory and reload the program")


    print()
    print("Populating the device_connections table")
    print("Here is a summary list of the active conenctions now kept in memory:")
    placeholder = list(device_connections.items())
    # Calculate the padding for centering
    print("First item:   " + str(placeholder[0]))
    print("Last item:   " + str(placeholder[-1]))
    print()

    ip_addresses = get_valid_ip_addresses()
    print(ip_addresses)
    print()
    # Ask the user if the IP address list is okay: put it in a list
    # the next 20 lines of code either resets the list, or extends it again I dislike verbose code but sometimes it is necessary
    ip_addresses_input = input("Is the list of IP addresses okay? (Y/N): ").strip().lower()
    while True:
        if ip_addresses_input == 'n':
            print("clearing your previous input")
            ip_addresses = []
            ip_addresses = get_valid_ip_addresses()
        elif ip_addresses_input == 'y':
            break  # Continue with the program
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
        ip_addresses_input = input("Is the list of IP addresses okay? (Y/N): ").strip().lower()

    while True:
        # Ask if the user wants to add more IP addresses
        add_more_ip = input("Do you want to add more IP addresses? (Y/N): ").strip().lower()
        if add_more_ip == 'n':
            break  # Exit the loop
        elif add_more_ip == 'y':
            # Add more IP addresses
            more_ip_addresses = get_valid_ip_addresses()
            ip_addresses.extend(more_ip_addresses)
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


    print("Now I will run prepatory diagnostics and connectivity check in your network")

    appending_to_ping_table(ip_addresses, device_connections, ping_results_before) #pre-config ping results
    print("This is a list of your network connectivity before configuration changes")
    print(ping_results_before)
    print()
    print("Finally I save all the running configurations of the supplied devices into memory")
    get_configurations_threaded(device_connections, config_dict_before)



    print()
    print("Welcome to the Network Configuration and Diagnostics Tool!")
    print()
    print("Please choose one of the following options:")
    print("1. Manage configurations and updates (--test-connectivity)")
    print("     This option for pushing configuration changes")
    print()
    print("2. Other Functionality (not implemented yet) (--other-functionality)")
    print("3. Return to top of the program")
    print()


    def return_to_main(): #loops back to top of program
        choice = input("Enter the option number (1, 2, or 3): ")

        while True:
            if choice in ["1", "2", "3"]:
                main(choice)
        else:
            print("Invalid choice. Please enter '1' for Configuration Management, '2' for other-functionality, or '3' to manually input an option.")
            choice = input("Enter the option number (1, 2, or 3): ")

    return_to_main()