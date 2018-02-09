[![build status](https://travis-ci.org/wvoliveira/burstcli.svg?branch=master)](https://travis-ci.org/wvoliveira/burstcli)

Burstcli
---------

Script for open some ticket in GLPI (v9.2).  

How to
-----

Download e configure
```bash
git clone git@github.com:wvoliveira/burstcli.git
cd burstcli
pip install .
```

For print example config file:
```
burst example
```

Output:
```
[sql]
server = 172.17.0.2
db = name
user = username
pass = password

[glpi]
url = http://172.17.0.3/front/ticket.form.php?id=

[ad]
server = domain.servers
prefix = domain.with.prefix
base = OU=Usuarios,OU=domain,DC=with,DC=prefix

```

Save and edit as needed:
```
burst example > myconfig.ini
```

Just run:
```
burst -c myconfig.ini
```
