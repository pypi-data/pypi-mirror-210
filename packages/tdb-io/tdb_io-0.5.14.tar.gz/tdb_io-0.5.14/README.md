Project: tdb~io~
================

*more or less actual at 0.5.12*

1.  A tool to get info on,data from,insert to - influx database -
    local,remote
2.  A tool to do backup to csv, parquet (pandas) or h5
3.  LIBRARY for pythonic oneline insertion to Influx database
4.  Even some plotting remained from the previous version

Use cases
---------

**You need** `~/.influx_userpassdb` on Linux or
`C:\Users\someone\.influx_userpassdb` on windows.

The content is

``` {.bash org-language="sh"}
username
password
dbname
```

### Python script to insert data

### CLI - List databases

``` {.bash org-language="sh"}
tdb_io ls infl
```

Or remote

``` {.bash org-language="sh"}
tdb_io ls infl -ip 10.10.104.21
```

### CLI - List measurements in db and save csv

Database named `test`

``` {.bash org-language="sh"}
tdb_io ls infl test
```

This will show and save the last 5 points of a measurements

``` {.bash org-language="sh"}
tdb_io ls infl test somemeasurement
```

This will show and save the last 555 points of a measurements

``` {.bash org-language="sh"}
tdb_io ls infl test somemeasurement 555
```

This will show and save the last 5 hours of a measurements

``` {.bash org-language="sh"}
tdb_io ls infl test somemeasurement 5h
```

This will show and save the last 1 day of a measurements from remote PC

``` {.bash org-language="sh"}
tdb_io ls infl test somemeasurement 1d -ip 10.10.104.21
```

AT THIS CASE:

-   **CSV** is always saved
-   **h5** is saved if `tables` is installed by pip
-   **parquet** of pandas saved if `pyarrow` is properly installed

### CLI - Backup all the measurements from the database

Database named `test`

``` {.bash org-language="sh"}
tdb_io ls infl test all 1d -ip 10.10.104.21
```

### CLI - Insert some data

``` {.bash org-language="sh"}
# later
```

### CLI - Insert some data with a faked timestamp

``` {.bash org-language="sh"}
# later
```

Using system influx client
--------------------------

### Insert data

In `influx` after *auth*

``` {.bash org-language="sh"}
INSERT cpu,host=serverA value=10
```

**carefull** the tag `host` will make the life difficult to tdb~io~!

### Show influx content

In `influx` after *auth*

``` {.bash org-language="sh"}
 show databases
 use test
 show measuremnts
# select * from meas limit 5 ??
```

Appendices:
===========

Setup letsencrypt keys
----------------------

### I already have autoupdate keys

Setup Grafana
-------------

### Newly-from repo

See
<https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-grafana-on-ubuntu-22-04>

``` {.bash org-language="sh"}
wget -q -O - https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install grafana
sudo systemctl enable --now grafana-server
sudo systemctl status grafana-server


```

### Basic docker

`docker run -d -p 3000:3000  grafana/grafana`

\[2021-04-14 Wed\] **When anonymous access needed**
`docker run --name grafana-gigajm-v2104a -d  -p 3000:3000 -e "GF_AUTH_ANONYMOUS_ENABLED=true" --restart=unless-stopped  grafana-gigajm-v2104`

What is the password? admin admin - change from webinterface now

But - once the password is set, and PC restarts, it is nice to have a
more persistent image.

``` {.bash org-language="sh"}
docker ps
docker commit  cdcc1c4a1816 grafana-gigajm
docker stop ...
docker rm ...
docker images

docker run -d --restart unless-stopped  grafana-mc2_vac

```

### Install plugins

Then, it is necessary to install a plugin and not to loose the
container.

``` {.shell}
docker ps
docker exec -it c4886ae1f59c bash
# INSIDE DOCKER
grafana-cli plugins install mtanda-histogram-panel
grafana-cli plugins install pr0ps-trackmap-panel

# I did a new commit
docker commit c4886ae1f59c  grafana-gigajm2
# and restarted the container
docker restart c4886ae1f59c
```

What is the password? admin admin - change from webinterface now

### DEFINE DATASOURCE in grafana

-   <http://x.x.x.x:8086>
-   no change anything
-   database user
-   pass
-   save

### Reset password in grafana

to admin admin

    sudo sqlite3 /var/lib/grafana/grafana.db

    sqlite> update user set password = '59acf18b94d7eb0694c61e60ce44c110c7a683ac6a8f09580d626f90f4a242000746579358d77dd9e570e83fa24faa88a8a6', salt = 'F3FAxVm33R' where login = 'admin';
    sqlite> .exit

### Reset certbot

-   goto /etc/letsencrypt
-   see there are certificates there
-   check, where influxdb expects them:
    -   `less /etc/influxdb/influxdb.conf`
    -   `https-certificate = "/etc/ssl/fullchain.pem"`
    -   `https-private-key = "/etc/ssl/privkey.pem"`
-   `cd /etc/ssl`
-   `cd /etc/letsencrypt/archive/www.xxxxxxxx.cz`
-   `chown influxdb:influxdb *` was useless in the moment
-   `` cp `ls -1 privkey*.pem | tail -1` /etc/ssl/privkey.pem ``
-   `` cp `ls -1 fullchain*.pem | tail -1` /etc/ssl/fullchain.pem ``
-   `systemctl restart influxdb.service`
-   reload grafana web and influx is seen.

I HAVE PUT IT INTO A CODE `update_keys.py`:

``` {.python}
#!/usr/bin/env python3

from fire import Fire
from os import listdir
from os.path import isfile, join
import glob
import os
import subprocess as sp


def chk_influx():
    print("D... check influx ssl file's directory")
    with open("/etc/influxdb/influxdb.conf") as f:
        res = f.readlines()
    res = [ x for x in res if x.find("#")<0 ]
    res = [ x.strip() for x in res if x.find("ssl")>0 ]
    res = [ x.split("=")[1].strip().strip('"')  for x in res ]

    print("D... influx needs these two:",res)
    full = [x for x in res if x.find("fullchain.pem")>0]
    pkey = [x for x in res if x.find("privkey.pem")>0]

    return full[0],pkey[0]

def main():
    fullchain,pkey = chk_influx()

    print("D... main update keys for grafana reading influx")
    print(" ... i assume that grafana has own certificate (due to domainname grafana.)  ")
    print(" ... i assume influx is accessed on www. ")
    certpath = "/etc/letsencrypt/archive"
    dirs = glob.glob(certpath+"/*/")
    print("D... dirs seen:",dirs)
    for i in dirs:
        #print("D..>",i[0],i[-1], i[-2])
        #============== WWW.CZ================
        if (i.find("www.")>=0) and (i[-2]=="z"):
            #wdir = certpath+"/"+i
            print(f"D... globbing {i}")

            files = glob.glob( i+"fullchain*" )
            #print( files )
            latest_fullchain = max(files, key=os.path.getctime)
            print(latest_fullchain)

            files = glob.glob( i+"privkey*" )
            #print( files )
            latest_privkey = max(files, key=os.path.getctime)
            print(latest_privkey)

            # execute ========================
            CMD1 = f"cp {latest_fullchain} {fullchain}"
            CMD2 = f"cp {latest_privkey} {pkey}"
            print(CMD1)
            print(CMD2)

            status = sp.call( CMD1 , shell=True)
            status = sp.call( CMD2 , shell=True)

            CMD = "systemctl restart influxdb.service"
            print(CMD)
            status = sp.call( CMD , shell=True)
            print(status)



if __name__=="__main__":
    Fire(main)

```

And grafana.site started to display again on the first attempt.

Setup influxdb
--------------

### Install

    apt install influxdb
    apt install influxdb-client

`emacs /etc/influxdb/influxdb.conf` and `auth-enabled = false`
`systemctl restart influxdb`

`CREATE USER admin WITH PASSWORD 'asd' WITH ALL PRIVILEGES`

### Create databases

    influx
    > show databases
    > create database test
    > create database data
    > show databases
    name: databases
    name
    ----
    _internal
    test
    data

### Create user

    influx
    > create user xxx with password 'xxxxxx'
    > show users
    user admin
    ---- -----
    xxx  false

GRANT USER

    > grant all on  test to  xxx
    > grant all on  data to xxx
    > quit

### RESTART with auth

`emacs /etc/influxdb/influxdb.conf` and `auth-enabled = true`

    systemctl restart influxdb
    systemctl status influxdb
    influx
    show databases
    auth
    show databases

### Problem with ssl, unsafe ssl

Try to run `influx -ssl -unsafeSsl`

### Geo information for track-map

    use test
    Using database test
    > show measurements
    name: measurements
    name
    ----
    > insert geotest,host=me longitude=15.134,latitude=49.1234

### Access from grafana

If the certifictes are for www.blabla, use

URL: `https://www.websitename.cz:8086`

Module: mongo
-------------
