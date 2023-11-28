import ipaddress
import re


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


#this class will be overloaded for parsing Cisco Devices
"""
 class DeviceParser
In a cisco show ip route the routing table info for IOS has remained the same for over a decade: 
we are screen scraping here which is not something I like, the alternative is setting up snmp on the devices.
Generally speaking screen scraping config files and show commands is not unsafe as long as you test
"""

#This class parses the routing table on each device, add ECMP routes to decitionaries etc.
#make into class useful to overload for other vendors, sadly i'm not saving memory or time instantiating this class
#inside Search_configurations.py, which may be soemthing to look into at some point
class DeviceParser:
    def __init__(self, device_ip, routing_dict):
        self.device_ip = device_ip
        self.routing_dict = routing_dict

    def parse_routing_info(self, routing_info):
        current_ip = None
        current_interface = None
        via_ip = None

        ip_pattern = re.compile(r'\d{1,3}(\.\d{1,3}){3}(?:/\d{1,2})?')  # Regex for IP address
        major_subnet_pattern = re.compile(r'\d{1,3}(\.\d{1,3}){3}/\d{1,2} is (?:subnetted|variably subnetted)')
        interface_pattern = re.compile(r"(Loopback|Ethernet|Fast|Serial|Virtual)\S+")
        # interface_pattern =  = r'(?<=, )\b[A-Z].*$'  #both do same thing one easier to read
        via_pattern = re.compile(r"via \S+")
        attached_ip = re.compile(r"^\s{0,4}") #checks for empty spaces beginning of line, mixed in with not finding an ip subnet /xx in the elif statement, to recursively add the ecmp routes
        printable_character = re.compile(r"^\S{1}")
        for line in routing_info.splitlines():
            major_subnet_match = major_subnet_pattern.search(line)
            current_ip_match = ip_pattern.search(line)
            interface_match = interface_pattern.search(line)
            via_match = via_pattern.search(line)
            attached_match =  attached_ip.match(line)  #.match searches only the beginning of the line anyway, may seem redundant, i leave it up to the developer
            printable_match = printable_character.match(line)
            if major_subnet_match:
                continue
            if (current_ip_match and printable_match): #if line has an ip subnet /xx and associated protocol
                current_ip = current_ip_match.group()
                current_interface = interface_match.group() if interface_match else None
                via_ip = via_match.group() if via_match else None
                self.routing_dict.setdefault(self.device_ip, []).append({
                    'ip_address': current_ip,
                    'via': via_ip,
                    'interface': current_interface,
                })
            # recursively adds ECMP routes to the previous ip address: if line is an ECMP o0r extra route associated with previous subnet
            elif (not printable_match and  current_ip_match):
                # print("no match printable")
                if current_ip_match:
                    # Append interface and via to the previous IP subnet: we keep our previous ip address as this is ECMP
                    # here is the result:
                    # {'ip_address': '10.0.5.0/29', 'via': 'via 10.0.1.130,', 'interface': ['FastEthernet1/0']},
                    # {'ip_address': '10.0.5.0/29', 'via': 'via 10.0.1.2,', 'interface': 'FastEthernet0/0'}
                    #we could have appended nested lists via a reverse lookup: I chose appending as its easier for report generation
                    current_interface = interface_match.group() if interface_match else None
                    via_ip = via_match.group() if via_match else None   #this next hop is good for BGP updates, which may be redistributed without an interface in the routing table
                    # if current_interface:
                    #     print("Current_Interface "  + str(current_interface))
                    # print("Str of get function " + str(self.routing_dict.get(self.device_ip)))
                    res = self.routing_dict.get(self.device_ip)
                    if res:
                        # print("Appending res")
                        # print("*" * 20)
                        res.append({
                            'ip_address': current_ip,
                            'via': via_ip,
                            'interface': current_interface,
                        })



"""This section includes comparison functions"""
def compare_routing_dicts(before_dict, after_dict):
    #the commented code should be applied in view layer
    # current_directory = os.getcwd()
    # print(current_directory)
    # subdirectory_path = os.path.join(current_directory, 'diagnostics_results')
    # before_dict_path = os.path.join(subdirectory_path, 'routing_dict_before.txt')
    # after_dict_path = os.path.join(subdirectory_path, 'routing_dict_after.txt')
    # with open(before_dict_path, 'r') as before_file, open(after_dict_path, 'r') as after_file:
    #     # Load JSON content from files
    #     before_dict = json.load(before_file)
    #     after_dict = json.load(after_file)
    differences = []

    for ip_address, before_routes in before_dict.items():
        if ip_address in after_dict:
            after_routes = after_dict[ip_address]

            # Iterate over each route in both dictionaries
            for before_route in before_routes:
                # Check if the route is still present in the new dictionary based on ip_address
                matching_routes = [route for route in after_routes if route["ip_address"] == before_route["ip_address"]]

                # Check if there is at least one match for both "via" and "interface"
                via_matches = any(matching_route.get("via") == before_route.get("via") for matching_route in matching_routes)
                interface_matches = any(matching_route.get("interface") == before_route.get("interface") for matching_route in matching_routes)

                if via_matches and interface_matches:
                    # If there is a match for both "via" and "interface," no difference
                    continue

                # Check for changes in via for each matching ip_address
                for matching_route in matching_routes:
                    if matching_route.get("via") != before_route.get("via"):
                        differences.append(f"Change in via for {ip_address}: {before_route} -> {matching_route}")

                    # Check for changes in interface for each matching ip_address
                    elif matching_route.get("interface") != before_route.get("interface"):
                        differences.append(f"{ip_address}: Change in interface for {ip_address}: {before_route} -> {matching_route}")

            # Check for new routes in the new dictionary for each matching ip_address
            for after_route in after_routes:
                matching_routes = [route for route in before_routes if route["ip_address"] == after_route["ip_address"]]
                if not matching_routes:
                    differences.append(f"New route for {ip_address}: {after_route}")

    print(differences)
    return differences
def ping_comparison(input_dict = {}, output_dict = {}):
    pass
