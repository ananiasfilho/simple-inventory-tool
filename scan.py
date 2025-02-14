import os
import subprocess
import socket
import ipaddress
import csv
import paramiko
import concurrent.futures
import logging

# Configuração do log
LOG_FILE = "scan_errors.log"
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def read_config(file_path):
    """Lê o arquivo environment.cfg e retorna um dicionário com as configurações."""
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        logging.error(f"Erro: Arquivo de configuração '{file_path}' não encontrado.")
        exit(1)
    return config

def validate_parallel_scan(config):
    """Valida a configuração de paralelismo."""
    parallel_scan = config.get("PARALLEL_SCAN", "1")
    try:
        parallel_scan = int(parallel_scan)
        if not (1 <= parallel_scan <= 10):
            raise ValueError
    except ValueError:
        logging.error("Erro: PARALLEL_SCAN deve estar entre 1 e 10. Usando valor padrão (1).")
        parallel_scan = 1
    return parallel_scan

def read_file_lines(file_path):
    """Lê um arquivo e retorna uma lista com suas linhas (removendo espaços em branco)."""
    if not os.path.exists(file_path):
        logging.warning(f"Aviso: Arquivo '{file_path}' não encontrado.")
        return []
    
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def is_host_online(ip):
    """Verifica se um host está online via ping."""
    try:
        response = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Erro ao executar ping em {ip}: {e}")
        return False

def is_ssh_open(ip):
    """Verifica se a porta SSH (22) está aberta."""
    try:
        with socket.create_connection((ip, 22), timeout=3):
            return True
    except (socket.timeout, ConnectionRefusedError) as e:
        logging.error(f"Erro ao verificar SSH em {ip}: {e}")
        return False

def get_hostname(client):
    """Obtém o hostname do servidor via SSH."""
    try:
        stdin, stdout, stderr = client.exec_command("hostname")
        hostname = stdout.read().decode().strip()
        return hostname if hostname else "Desconhecido"
    except Exception as e:
        logging.error(f"Erro ao obter hostname: {e}")
        return "Erro"

def try_ssh_login(ip, users, passwords, keys):
    """Tenta login SSH no host usando usuários e senhas ou chaves SSH e retorna o hostname."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for user in users:
        for password in passwords:
            try:
                client.connect(ip, username=user, password=password, timeout=5, allow_agent=False, look_for_keys=False, banner_timeout=3, auth_timeout=5)
                hostname = get_hostname(client)
                client.close()
                return user, password, "", hostname
            except (paramiko.ssh_exception.SSHException, EOFError) as e:
                logging.error(f"Erro SSH ao conectar em {ip} com usuário {user}: {e}")
            except Exception as e:
                logging.error(f"Falha ao conectar em {ip} com usuário {user}: {e}")
        
        for key_path in keys:
            try:
                key = paramiko.RSAKey(filename=os.path.expanduser(key_path))
                client.connect(ip, username=user, pkey=key, timeout=5, allow_agent=False, look_for_keys=False, banner_timeout=3, auth_timeout=5)
                hostname = get_hostname(client)
                client.close()
                return user, "", key_path, hostname
            except (paramiko.ssh_exception.SSHException, EOFError) as e:
                logging.error(f"Erro SSH ao conectar em {ip} com chave {key_path}: {e}")
            except Exception as e:
                logging.error(f"Falha ao conectar em {ip} com chave {key_path}: {e}")
    
    logging.warning(f"Nenhuma credencial funcionou para {ip}.")
    return "", "", "", ""

def expand_network_ranges(ranges):
    """Expande faixas de rede (CIDR) para listar IPs individuais."""
    ips = []
    for net in ranges:
        try:
            network = ipaddress.ip_network(net, strict=False)
            ips.extend(str(ip) for ip in network.hosts())
        except ValueError as e:
            logging.error(f"Erro: '{net}' não é uma faixa de rede válida. {e}")
    return ips

def scan_host(ip, ssh_users, ssh_passwords, ssh_keys):
    """Executa o escaneamento de um único host."""
    ping_status = "Ok" if is_host_online(ip) else "Fail"
    ssh_status = "Ok" if is_ssh_open(ip) else "Fail"
    status = "Online" if ping_status == "Ok" or ssh_status == "Ok" else "Offline"
    user, password, key, hostname = ("", "", "", "")
    
    if status == "Online":
        user, password, key, hostname = try_ssh_login(ip, ssh_users, ssh_passwords, ssh_keys)
    
    return [ip, hostname, status, ping_status, ssh_status, user, password, key]

# Caminho do arquivo environment.cfg
CONFIG_FILE = 'environment.cfg'

# Lendo o arquivo de configuração
config = read_config(CONFIG_FILE)
parallel_scan = validate_parallel_scan(config)

# Lendo os arquivos referenciados no environment.cfg
net_ranges = read_file_lines(config.get('FILE_NET_RANGE', ''))
ssh_users = read_file_lines(config.get('FILE_USERS_SSH', ''))
ssh_passwords = read_file_lines(config.get('FILE_PASSWORD_SSH', ''))
ssh_keys = read_file_lines(config.get('FILE_SSH_KEYS', ''))

# Expandir faixas de rede para IPs individuais
ip_list = expand_network_ranges(net_ranges)

# Criar e escrever os resultados no arquivo CSV
csv_filename = "scan_results.csv"
with open(csv_filename, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile, delimiter='|')
    csv_writer.writerow(["ip", "hostname", "status", "ping", "ssh", "usuario", "senha", "chave"])
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_scan) as executor:
        results = list(executor.map(lambda ip: scan_host(ip, ssh_users, ssh_passwords, ssh_keys), ip_list))
    
    csv_writer.writerows(results)

print(f"Resultados salvos em {csv_filename}")
print(f"Erros registrados em {LOG_FILE}")

