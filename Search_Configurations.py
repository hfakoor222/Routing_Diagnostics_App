"""
This file contains search functions to search through devices: I have placed it here as if and when we expland to other
network devices: eos, junos for example, this is the best place to organize everything
I may use my fuzzy_configuration_parser script to extend the search capabilities
"""
import re
import threading

config_search_results = {}
output_dict = {}
config_dict_before = {}



#this function takes the device_connections table, and configurations from each device to a master table
#it calls the get_configuration function, and applies threading. we pass config_master_table
# to get_configuration. In our program dictionary will be called config_table_before
def get_configurations_threaded(device_connections, config_dict_before  ={}):
    threads = []
    for device, (device_type, device_ip, username, password, secret) in device_connections.items():
        thread = threading.Thread(target=get_configuration, args=(device, device_ip, device_type, config_dict_before ))
        threads.append(thread)
        thread.start()


    for thread in threads:
        thread.join()
        # print(threading.current_thread().name)

# we can overload get_configuration, and get_configurations_threaded with extra functions, to obtain results other than get_config, or format them into classes
def get_configuration(device, device_ip, device_type, config_dict_before ):
    try:
        #device.open()
        config = device.get_config()
        config_dict_before[device_ip] = config
    except Exception as e:
        print(f"Failed to retrieve configuration for {device_ip}: {str(e)}")
    finally:
        print(threading.current_thread().name)



def search_configurations(input_dict={}, output_dict={}, search_strings=None, search_strings_dict = None, ):
    #arguments are input_dict: we find search_string in input_dict and append to output_dict
    #we use output_dict as a lookup for which devices we'd like to change configurations: output dict also contains
    #the piece of configuration we'd like to modify, good for quick lookups (nested loops), making it faster (i.e. searching 10 devices with a certain config rather than 100)
    print(search_strings)
    # search_strings = [item.strip() for item in search_strings] #stripping whitespaces, probably not needed unless
    # user accidentally enters multiple whitespaces  _-> i handled this function under CLI.py
    search_strings = "^.*?{}.*?$".format(".*?".join(map(re.escape, search_strings))) #-->this surrounds search string with any or 0 characters, and we can run regex on the devices
    search_strings = re.compile(search_strings, re.DOTALL) #escaping escape characters, probably not needed, unless user manually inputs escape characters: i.e. route-map
    for key, value in input_dict.items():
        # print("This is the key")
        print(key)
        value = str(value)
        value = value.strip("{}")
        # print("*" * 20)
        config_blocks = value.split('\\n!')
        for block in config_blocks:
            if search_strings.findall(block): # -->Findall is memory hungry, however a low level library.
                output_dict[key] = block
    for key, value in output_dict.items():
        print(f"{key} address has this configuration")
    print("Here is the the search strings we found, the ip address,  and also how they resolve in your output")
    for key, value in output_dict.items():
        # Strip leading and trailing '\\n' and ',' and replace any remaining '\\n' with ','
        value = value.strip("\\n,")
        value = value.replace("\\n", ',') #the replacement is for printing it out to screen - the user can copy paste from whats on the screen, and add more configurations to push
        print(f"{key}: {value}")
    return output_dict