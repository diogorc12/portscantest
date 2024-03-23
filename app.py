from flask import Flask, render_template, request
import subprocess

app = Flask(__name__, template_folder='templates')
app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return render_template('Portscan.html')


@app.route('/scan', methods=['POST'])
def scan_ports():
    ip_range = request.form['ip_range']
    port_range = request.form['port_range']

    # Executa o script de varredura de portas e captura a saída
    result = subprocess.run(['python', 'portscanv2.py'], input=f'{ip_range}\n{port_range}\n', text=True,
                            capture_output=True)

    # Captura apenas a saída relevante, removendo a mensagem "Enter IP-IP: Enter port-port: "
    output_lines = result.stdout.split('\n')
    relevant_output = '\n'.join(line for line in output_lines if not line.startswith('Enter IP-IP: Enter port-port: '))

    # Retorna a saída relevante como resposta
    return relevant_output


if __name__ == '__main__':
    app.run(debug=True)
