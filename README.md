[![build status](https://travis-ci.org/wvoliveira/burstcli.svg?branch=master)](https://github.com/wvoliveira/burstcli)
Burstcli
---------

Script capaz de abrir varios chamados no GLPI (v9.2).  

How to
-----

Download e configure
```bash
git clone git@github.com:wvoliveira/burstcli.git
cp conf/example.ini conf/own.ini
```

Altere o arquivo conf/own.ini conforme suas credenciais de acesso:
```
[sql]
mysql_server = 172.17.0.2
mysql_db = name
mysql_user = username
mysql_pass = password

[glpi]
url = http://172.17.0.3/front/ticket.form.php?id=

[active_directory]
domain_servers = domain.vs
domain_name = domain.with.prefix
base_dn = OU=Users,OU=Domain,DC=With,DC=Prefix
```

Agora só rodar:
```bash
./burstcli.py -c conf/own.ini
```

Ainda nao inseri logging nesse projeto.
