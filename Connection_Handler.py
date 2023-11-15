from napalm import get_network_driver
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException
import threading
import time
from Sanity_Check_Diagnostics import get_valid_ip_addresses
import ipaddress
import time
"""
program tests conenctivity before and after config changes, by using candidate configs stored in the routers
flash --> https://pynet.twb-tech.com/blog/adding-cisco-ios-to-napalm.html. In link: : The rollback command will cause 
the 'rollback_config.txt' file to become the running-config (once again using Cisco's 'configure replace' command). 
Note, the current running-config is saved to rollback_config.txt on any commit operation.


Will soon be adding functionality for testing SSH, https, http, connections throughout the network,
as well as various other diagnostics
"""
# Define your Cisco device information


ping_results_before = {}
ping_results_after = {}
# we comare results before and after
device_connections = {}
bgp_dict_before = {}  #stores bgp table for before config updates
config_dict_before = {}

# I'm including command dicts now for when we expand the program to other than cisco devices
repeat = 3
timeout = 2
pings_dict = {'ios': 'ping {} repeat {} timeout {}', 'junos': 'ping {} count {} wait {}', }

bgp_summary_dict = {"ios": "show ip bgp", "junos": "show route protocol bgp", "eos" : "show ip bgp"}
output_dict_lock = threading.Lock()


def device_list_populator(infile = "device_list.txt"):
    device_list = open(infile, "r")
    device_list = [line.strip('[]\n').split(", ") for line in device_list] # Split it into variables
    device_list = [[element.strip('"') for element in line] for line in device_list]
    return device_list

# ip_addresses = get_valid_ip_addresses()
#handle_ip_addresses() is basically testing pings: it is threaded under appending_to_ping_table()
def handle_ip_addresses(device, ip_addresses, driver_type, output_dictionary={}):

    for ip_address in ip_addresses:
        ip_network = ipaddress.ip_network(ip_address.strip())
        for ip in ip_network.hosts():
            ip_str = str(ip)
            try:
                ping_output = device._send_command(
                    pings_dict[driver_type].format(ip_str, repeat, timeout)
                )
                if "!" in ping_output or "from" in ping_output:
                    output_dictionary.setdefault(device.hostname, []).append(ip_str)
                    print(f"Thread-{threading.current_thread().name}: {output_dictionary}")
            except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
                print(f"Error while pinging {ip_str} on {device.hostname}: {str(e)}")

""" 
I may combine threaded_ping_results and _appending_to_ping_table, it seems redundant and a bit confusing
"""
#for appending_ping_results in the main layer of our program, we feed in the optional output_dictionary,
#so we can get ping results before and after changes
def appending_to_ping_table(ip_address_list, device_connections, output_dictionary={}):
    ping_thread_list = []
    for device, (driver_type, device_ip, username, password, secret) in device_connections.items():
        pinging_thread = threading.Thread(target=handle_ip_addresses, args=(device, ip_address_list, driver_type, output_dictionary))
        ping_thread_list.append(pinging_thread)
        pinging_thread.start()
    for ping in ping_thread_list:
        print(ping.name) #Printing and verifying the threads are working - this is the function that takes the longes time
        ping.join()

#this function populates our device_conenctions list, with conenction variables (username, pass, ip, device_type
def initialize_device_connections(item,):
    #we unpack the .txt file of devices to get the variables below
    device_type, device_ip, username, password, secret = item
    driver = get_network_driver(device_type) #NAPALMs built-in get_network_driver

    print("The driver: " +  str(driver))
    napalm_device = driver(device_ip, username, password, optional_args = {"read_timeout":50,"global_delay_factor":8,"dest_file_system":"disk0:","auto_file_prompt":True,"secret":secret,"inline_transfer":True})
    #the dest_file_system is where to save rollback and merge. For Cisco devices make sure to enable SCP, file transfers in netmiko are done via SCP.
    #the auto_file_prompt option is to override prompts for file transfers: typically not needed unless set explicitly on the remote device, this overrides it.
    # delay_factor to avoid premature errors.
    napalm_device.open() #NAPALMs open method: This is the point in our program where we enable the device for the first time
    # napalm_device.device._send_command("enable") # optional send commands
    # we append a dictionary with the napalm device object, and the conenction variables: now use for consistent diagnostics
    device_connections[napalm_device] = device_type, device_ip, username, password, secret



#this threads threaded_network_driver and is an API
def threaded_network_driver(device_list,):
    threads = []
    for item in device_list:
        thread = threading.Thread(target=initialize_device_connections, args=(item,))
        threads.append(thread)
        thread.start()
        time.sleep(.5) #simulates concurrency: introducing a for loop below is what does this, however this time.sleep helps if threaded_network_driver is called immediately after threading the device connections
    for thread in threads:
        thread.join()
        # print(device_connections)



def obtain_bgp_table(device_connections, output_dictionary={}):
    for device, (device_type, device_ip, username, password, secret) in device_connections.items():
        bgp_table = napalm_device._send_command(bgp_summary_dict[device_type])
        if bgp_table is not None:
            bgp_dict_before[device_ip] = bgp_table_before
        print(bgp_dict_before)








""" 
We only use the below if conencting to more than 200-300+ devices:
max_workers = 100
semaphore = threading.Semaphore(max_workers)
place this under threaded_ping_results()  --> semaphore.release() 
"""







