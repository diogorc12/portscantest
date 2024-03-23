import socket
import threading
from queue import Queue
from netaddr import IPRange

socket.setdefaulttimeout(0.25)

print_lock = threading.Lock()

def portscan(port, t_IP):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((t_IP, port))
        service = socket.getservbyport(port)
        with print_lock:
            print(f"{t_IP}:{port} ({service}) is open")
        con.close()
    except:
        pass

def threader():
    while True:
        worker = q.get()
        if worker is None:
            break
        portscan(*worker)
        q.task_done()

# get user input for range in form xxx.xxx.xxx.xxx-xxx.xxx.xxx.xxx and xx-xx
ipStart, ipEnd = input("Enter IP-IP: ").split("-")
portStart, portEnd = input("Enter port-port: ").split("-")

# cast port string to int
portStart, portEnd = int(portStart), int(portEnd)

# define IP range and sort them
iprange = sorted(IPRange(ipStart, ipEnd), key=lambda ip: ip.value)

q = Queue()

# Add IP addresses and their ports to the queue
for ip in iprange:
    t_IP = str(ip)
    for port in range(portStart, portEnd + 1):
        q.put((port, t_IP))

# Start threads to process the queue
thread_list = []
for _ in range(600):  # Aumentamos o número de threads
    t = threading.Thread(target=threader)
    t.start()
    thread_list.append(t)

# Wait for all threads to finish processing
q.join()

# Stop the threads
for _ in range(600):
    q.put(None)

for t in thread_list:
    t.join()
