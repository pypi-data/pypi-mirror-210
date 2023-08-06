# Network Calculator


"A Deep Dive into the Network Calculator: Understanding IP Address Management in Python"
Hello there! Today we'll be exploring the concept of network calculation and how it is applied in Python. To do so, we'll work with a snippet of Python code that simplifies IP address management tasks such as calculating subnet masks, network IDs, and more.

#####The What and Why of Network Calculations
In networking, IP addresses and subnet masks are crucial for defining the structure and reach of the network. However, doing these calculations manually can be cumbersome and error-prone. This is where Python, with its vast library support and simplicity, can be a lifesaver.

In this article, we'll delve into a Python class called I have created called the 'NetworkCalculator'. It is designed to automate common network calculation tasks. To fully understand this, it is recommended you have some basic knowledge of IP addresses, subnet masks, network IDs, broadcast IDs, and CIDR notation. There are a tone of online resources to help your understanding. 

**Cisco Networking Academy** - [Introduction to Networks]

https://www.netacad.com/node/127
2. Comprehensive course on foundational networking concepts. **Computer Networking : Principles, Protocols and Practice** https://www.cnp3book.info/book/html/chapter-3.html#ip-addressing-and-cidr
   
Remember, networking concepts can take some time to fully understand, so be patient with yourself and enjoy the process of learning!
Understanding the NetworkCalculator Class
Let's create a class called NetworkCalculator in Python. We will use the 'ipaddress' module, which simplifies tasks involving the manipulation of IPv4 and IPv6 addresses. 

Let's dive deeper into this class to understand its structure and functionality:
from ipaddress import IPv4Network, IPv4Address
class NetworkCalculator:


The NetworkCalculator class is initialized with an IP address in CIDR notation as input. CIDR (Classless Inter-Domain Routing) notation represents an IP address and its associated routing prefix. 

For instance, '192.168.1.10/24' is an example of an IP address in CIDR notation.
The __init__ method splits the IP address and the CIDR subnet prefix, and an IPv4Network object is created with these. The strict=False parameter allows the IP address part to be any IP address inside the network.
```python 
def __init__(self, ip_cidr):
    ...
    self.network = IPv4Network(f"{self.ip}/{self.cidr}", strict=False)

```
### Network Calculator Methods
After creating the NetworkCalculator object, Here are several methods can we create and us to perform network calculations:

get_subnet_mask(): Returns the subnet mask of the network. The subnet mask defines the size of the network.

get_network_id(): Returns the Network ID. This is the first IP address in the network and it identifies the network itself.

get_next_network(): Returns the Network ID of the next network. It's calculated by adding 2^(32 - CIDR) to the network address.

get_broadcast_id(): Returns the last IP address in the network, which is used for broadcasting messages to all devices in the network.

get_first_ip(): Returns the first usable IP address in the network. It's simply the Network ID plus one.

get_last_ip(): Returns the last usable IP address in the network, which is one less than the broadcast ID.

get_total_ips(): Returns the total number of usable IP addresses in the network.


### Method to calculate and return subnet mask
   ```python def get_subnet_mask(self):
        return str(self.network.netmask)

    # Method to calculate and return network id
    def get_network_id(self):
        return str(self.network.network_address)

    # Method to calculate and return the next network id
    def get_next_network(self):
        return str(IPv4Address(self.network.network_address + (1 << (32 - self.cidr))))

    # Method to calculate and return broadcast id
    def get_broadcast_id(self):
        return str(self.network.broadcast_address)

    # Method to calculate and return the first usable ip
    def get_first_ip(self):
        return str(IPv4Address(self.network.network_address + 1))

    # Method to calculate and return the last usable ip
    def get_last_ip(self):
        return str(IPv4Address(self.network.broadcast_address - 1))

    # Method to calculate and return the total number of usable ips
    def get_total_ips(self):
                return (1 << (32 - self.cidr)) - 2 if self.cidr < 31 else (1 << (32 - self.cidr))  
```
# Wrapping it All Up
At the end of the script, there is a function named print_network_info(ip_list).
This function is used to print information about a list of networks.

```python
 ip_list = ['10.1.1.55/28', '192.168.1.10/26', '172.16.0.5/16'] 
print_network_info(ip_list)
```

Here's the entire code block:
```python 
ipaddress import IPv4Network, IPv4Address



class NetworkCalculator:
    def __init__(self, ip_cidr):
        # Splitting the ip and cidr
        self.ip, self.cidr = ip_cidr.split('/')
        self.cidr = int(self.cidr)

        # Creating IPv4 Network object
        self.network = IPv4Network(f"{self.ip}/{self.cidr}", strict=False)

    # Method to calculate and return subnet mask
    def get_subnet_mask(self):
        return str(self.network.netmask)

    # Method to calculate and return network id
    def get_network_id(self):
        return str(self.network.network_address)

    # Method to calculate and return the next network id
    def get_next_network(self):
        return str(IPv4Address(self.network.network_address + (1 << (32 - self.cidr))))

    # Method to calculate and return broadcast id
    def get_broadcast_id(self):
        return str(self.network.broadcast_address)

    # Method to calculate and return the first usable ip
    def get_first_ip(self):
        return str(IPv4Address(self.network.network_address + 1))

    # Method to calculate and return the last usable ip
    def get_last_ip(self):
        return str(IPv4Address(self.network.broadcast_address - 1))

    # Method to calculate and return the total number of usable ips
    def get_total_ips(self):
        return (1 << (32 - self.cidr)) - 2 if self.cidr < 31 else (1 << (32 - self.cidr))

def print_network_info(ip_list):
    print("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format('CIDR', 'Subnet Mask', 'Network ID', 'Next Network', 'Broadcast ID', 'First IP', 'Last IP', 'Total IPs'))

    for ip_cidr in ip_list:
        net_calc = NetworkCalculator(ip_cidr)

        print("{:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format(
            ip_cidr,
            net_calc.get_subnet_mask(),
            net_calc.get_network_id(),
            net_calc.get_next_network(),
            net_calc.get_broadcast_id(),
            net_calc.get_first_ip(),
            net_calc.get_last_ip(),
            str(net_calc.get_total_ips())
        ))

# Use it like this:
ip_list = ['10.1.1.55/28', '192.168.1.10/26', '172.16.0.5/16']

# Call the function with the list of CIDR IP addresses
print_network_info(ip_list)
```

### About: 
Ray Bernard is a seasoned technologist specializing in cloud-based platforms, data science, and AI. He co-founded SuprFanz, a revolutionary cloud-based marketing company, and has held key roles at EMC, TicketMaster, and Compaq. As an Affiliate Developer, Systems Engineer, and Community Advocate, he demonstrated exceptional technical prowess and innovative thinking. 

Ray also taught Internet/Intranet Management & Design at Columbia University, further contributing to the field. With his vast experience and proactive problem-solving approach, he consistently drives digital transformation. 

Contact him at ray.bernard@outlook.com 
