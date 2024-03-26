import socket
from flask import Flask, render_template, request
from netaddr import IPRange
import threading
from queue import Queue

socket.setdefaulttimeout(0.25)

app = Flask(__name__)

# Função para varredura de portas
def portscan(port, t_IP):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((t_IP, port))
        service = socket.getservbyport(port)
        return f"{t_IP} ({service}) {port} open"
        con.close()
    except:
        return ""

# Função para processar a fila de IPs e portas usando threads
def threader():
    while True:
        worker, t_IP = q.get()
        result = portscan(worker, t_IP)
        if result:
            results.append(result)
        q.task_done()

@app.route('/')
def index():
    return render_template('Portscan.html')

@app.route('/scan', methods=['POST'])
def scan_ports():
    ip_range = request.form['ip_range']
    ipStart, ipEnd = ip_range.split("-")
    iprange = sorted(IPRange(ipStart, ipEnd), key=lambda ip: ip.value)

    # Portas a serem verificadas
    ports_to_scan = [
        20, 21, 179, 80, 443, 22, 23, 25, 53, 3389,
        110, 143, 445, 123, 389, 137, 88, 1433, 1521,
        3306, 161, 67, 68, 5060, 50, 51, 1723, 1080, 1720
    ]

    global results
    results = []

    global q
    q = Queue()

    # Adicionar IPs e portas à fila
    for ip in iprange:
        t_IP = str(ip)
        for port in ports_to_scan:
            q.put((port, t_IP))

    # Iniciar threads para processar a fila
    for x in range(30):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # Aguardar a conclusão do processamento da fila
    q.join()

    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
