import ipaddress

def is_valid_ip(ip):
    try:
        ipaddress.ip_network(ip.strip(), strict=False)
        return True
    except ValueError:
        return False

def get_valid_ip_addresses():
    while True:
        ip_addresses_input = input(
            "Enter IP address subnets with possible 0's (comma-separated): Example: 192.168.0.0/16, 172.168.0.0/24 etc: ")
        ip_addresses = ip_addresses_input.split(',')
        if all(is_valid_ip(ip) for ip in ip_addresses):
            return ip_addresses
        else:
            print("Invalid IP address format. Please enter valid IP addresses.")

#this function is used throughout our view layer to format user input
def get_valid_search_string(inlist):
    formatted_inlist = []
    if type(inlist) != list:
        print("This could not be parsed into a list, reinput your search|configuration")
        return False
    for item in inlist:
        if "," in item:
            print("Warning: Quotes not allowed around commas. Reinitializing search strings.")
            return False  # Return False to indicate an issue
        else:
            formatted_item = item
        item.strip('"').strip("'")
        formatted_inlist.append(formatted_item)
    formatted_inlist = [item for item in formatted_inlist if item.strip()] # this strips out empty strings inputted by user
    return formatted_inlist

def ping_comparison(input_dict = {}, output_dict = {}):
    pass
