import socket
import threading
from queue import Queue
from netaddr import IPRange

# Lista de portas a serem validadas
PORTS_TO_SCAN = [
    80, 443, 22, 20, 25, 21, 23, 53, 3389, 110,
    143, 445, 123, 389, 137, 88, 1433, 1521, 3306,
    161, 67, 68, 5060, 50, 51, 1723, 1080, 1720
]

socket.setdefaulttimeout(0.25)
print_lock = threading.Lock()

def portscan(port, t_IP):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((t_IP, port))
        service = socket.getservbyport(port)
        with print_lock:
            print(f"{t_IP} ({service}) {port} open")
        con.close()
    except:
        pass

def threader():
    while True:
        worker, t_IP = q.get()
        portscan(worker, t_IP)
        q.task_done()

# get user input for range in form xxx.xxx.xxx.xxx-xxx.xxx.xxx.xxx
ipStart, ipEnd = input("Enter IP-IP: ").split("-")

# define IP range and sort them
iprange = sorted(IPRange(ipStart, ipEnd), key=lambda ip: ip.value)

q = Queue()

# Add IP addresses and their ports to the queue
for ip in iprange:
    t_IP = str(ip)
    for port in PORTS_TO_SCAN:
        q.put((port, t_IP))

# Start threads to process the queue
for x in range(30):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()

# Wait for all threads to finish processing
q.join()
