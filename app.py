
import socket
from flask import Flask, render_template, request
from netaddr import IPRange
import threading
from queue import Queue
import time

socket.setdefaulttimeout(0.25)

app = Flask(__name__)

results = []
q = Queue()
total_ports_checked = 0
total_time = 0


# Função para varredura de portas

def portscan(port, t_ip):
    global total_ports_checked  # Acessar a variável global total_ports_checked
    total_ports_checked += 1  # Incrementar o contador de portas verificadas
    global total_time
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        start_time = time.time()
        s.connect((t_ip, port))
        service = socket.getservbyport(port)
        end_time = time.time()  # Medindo o tempo final da verificação da porta
        total_time += end_time - start_time  # Incrementando o tempo total
        return f"{t_ip} ({service}) {port} open"
    except socket.error:
        return ""


# Função para processar a fila de IPs e portas usando threads
def threader():
    while True:
        worker, t_ip = q.get()
        result = portscan(worker, t_ip)
        if result:
            results.append(result)
        q.task_done()
        time.sleep(0.4)


@app.route('/')
def index():
    return render_template('Portscan.html')


@app.route('/scan', methods=['POST'])
def scan_ports():
    ip_range = request.form['ip_range']
    ipstart, ipend = ip_range.split("-")
    iprange = sorted(IPRange(ipstart, ipend), key=lambda ip: ip.value)

    # Portas a serem verificadas
    ports_to_scan = [
        *range(7, 25), 42, 43, 49, *range(53, 71), 79, *range(80, 89), 102, *range(110, 121),
        123, *range(135, 140), *range(143, 163), 177, 179, 194, 201, 264, 318, *range(381, 390),
        383, 389, 411, 412, 427, 443, 445, 464, 465, 497, *range(500, 516), *range(520, 522),
        540, 548, 554, *range(546, 548), 560, 587, 591, 593, 596, 631, 636, 639, 646, 691,
        860, 873, 902, 989, *range(990, 994), 995, *range(1025, 1030), 1080, 1194, 1214, 1241,
        1311, 1337, 1589, 1701, 1720, 1723, 1725, 1741, 1755, *range(1812, 1814), 1863, 1900,
        1985, 2000, 2002, 2049, 2082, 2083, 2100, 2222, 2302, 2483, 2484, 2745, 2967, 3050,
        3074, 3127, 3128, 3222, 3260, 3306, 3389, 3689, 3690, 3724, *range(3784, 3786), 4333,
        4444, 4500, 4664, 4672, 4899, 5000, 5001, *range(5004, 5006), 5050, 5060, 5061, 5190,
        *range(5222, 5224), 5353, 5432, 5554, *range(5631, 5633), 5800, *range(6000, 6002), 6112,
        6129, 6257, *range(6346, 6348), 6379, 6500, 6566, 6588, *range(6665, 6670), 6679, 6697,
        6699, *range(6881, 6902), 6970, *range(7000, 7002), 7199, *range(7648, 7650), 8000, 8080,
        *range(8086, 8088), 8118, 8200, 8222, 8500, 8767, 8866, 9042, *range(9100, 9104), 9119,
        9800, 9898, 9999, *range(10000, 10003), *range(10161, 10163), *range(10113, 10117)
    ]

    global results
    results = []

    global q
    q = Queue()

    global total_ports_checked  # Acessar a variável global total_ports_checked
    total_ports_checked = 0  # Reinicializar o contador de portas verificadas

    global total_time
    start_time = time.time()  # Medindo o tempo inicial

    # Adicionar IPs e portas à fila
    for ip_addr in iprange:
        t_ip = str(ip_addr)
        for port in ports_to_scan:
            q.put((port, t_ip))

    # Iniciar threads para processar a fila
    for x in range(50):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # Aguardar a conclusão do processamento da fila
    q.join()

    end_time = time.time()  # Medindo o tempo final
    total_time = end_time - start_time  # Calculando o tempo total em segundos

    return render_template('results.html', results=results, total_ports_checked=total_ports_checked,
                           total_time=total_time)


if __name__ == '__main__':
    app.run(debug=True)
