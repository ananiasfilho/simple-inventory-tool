# _tuba_-SIT

**_tuba_ is a Simple Inventory Tool**

_Tuba_-SIT foi desenvolvido para executar algumas atividades simples como:

- O ip está em uso? (Online e/ou Offline)
- Tem **ssh** habilitado?
- Qual dos usuários/senha/chaves a partir de um repositório, terei acesso ssh ao Sistema Operacional deste IP?

* Linguagem: Python

* Interface WEB: Flask

## Arquivos e Configurações

É necessário basicamente configurar o arquivo environment.cfg conforme a seguir:
```
# Quantidade máxima de scan paralelos.
PARALLEL_SCAN=10
# Arquivo contendo os ips/ranges a serem scaneadas.
FILE_NET_RANGE=files/net_range.txt
# Arquivo contendo os usuários que serão utilizados durante as tentativas de conexões via ssh.
FILE_USERS_SSH=files/users_ssh.txt
# Arquivo contendo as senhas que serão utilizadas durante as tentativas de conexão ssh.
FILE_PASSWORD_SSH=files/password_ssh.txt
# Arquivo contendo os caminhos das chaves ssh que serão utilizadas durante as tentativas de conexão ssh. 
FILE_SSH_KEYS=files/ssh_keys.txt
```

O arquivo net_range.txt deve conter os ips no formato CIDR conforme abaixo:

_Utilize uma range por linha_
```
10.10.4.101/32
10.10.6.56/29
192.168.0.0/24
10.10.0.0/16
```
Arquivo users_ssh.txt
```
root
ubuntu
azureuser
ec2-user
```

Arquivo password_ssh.txt
```
$3cr3t3
123@mudar
M3gaS3nha
```

Arquivo ssh_keys.txt
```
~/.ssh/id_rsa
/home/ec2-user/.ssh/id_rsa_custom
/home/azureuser/Downloads/chave-servidor.pem
```

## Instalação

Utilizando virtualenv

```
mkdir -p /opt/tuba

cd /opt/tuba

git clone https://github.com/ananiasfilho/simple-inventory-tool.git

virtualenv python

source python/bin/activate

cd simple-inventory-tool

# Iniciando o scan

pip install -r requirements.txt

python scan.py

# Aguardo o script finalizar

cd web

python app.py
```

## Acessando a interface WEB - GUI

Abra o navegador e veja o resultado.

http://localhost:5000
