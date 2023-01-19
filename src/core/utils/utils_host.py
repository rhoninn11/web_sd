
def host_string_to_dict(host_string):
    addresses = host_string.split(" ")
    address_dict = {}
    for address in addresses:
        ip, port = address.split(":")
        address_dict[address] = (ip, int(port))
    return address_dict

def host_to_string(host):
    return host[0] + ":" + str(host[1])

def host_dict_to_string(host_dict):
    addresses = []
    for key in host_dict:
        addresses.append(key)
    return " ".join(addresses)