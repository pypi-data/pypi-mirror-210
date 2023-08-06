#!/usr/bin/env python3
# -fire CLI
from fire import Fire

from tdb_io.version import __version__

import pandas as pd

from influxdb import InfluxDBClient
#from pymongo import MongoClient
#import pymongo # to get ASCENDING
import datetime as dt
import time
import os
import json
import sys

import socket
import sys

# DEBUG=1  # will change in MAIN  args
ACTUAL_CREDENTIALS={}


# SSL warning
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


# if DEBUG:print("D...  project/module:  tdb_io/influx :", __version__ )


#OK
#===============================================================
def is_int(n):
    print(f"/{n}/")
    try:
        float_n = float(n)
        print(f"/{float_n}/")
        int_n = int(float_n)
        print(f"/{int_n}/")
    except ValueError:
        return False
    else:
        return float_n == int_n


def check_port(IP="127.0.0.1"):
    """
Checks if influx runs on IP
    """
    ok = False
    client = InfluxDBClient(host=IP, port=8086)
    try:
        client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chkport) )NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = True
    return ok



def check_databases(IP="127.0.0.1", user="", password=""):
    """
Checks if influx runs on IP AND shows databases
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

    """
    #if DEBUG:print("D... checkd: ",IP,user)
    ok = False
    autho = False
    dbs = []
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chkdb) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG = 0)

        # NO SSL
        gotit = False
        try:
            #if DEBUG:print("D... chkd:  getting client NO SSL")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
            client.get_list_database() # this checks error
            gotit = True
        except:
            print("X... exception without SSL, trying with SSL")

        if not gotit:
            try:
                #if DEBUG:print("D... chkd: getting client WITH SSL")
                client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=3)
                client.get_list_database() # this checks error
            except:
                print("X... ",IP, 8086,creds[0],creds[1],creds[2] )

        dbs = client.get_list_database()
    return dbs





def check_series(database="", series="",
                 qlimit=5,
                 IP="127.0.0.1",
                 user="", password="",
                 delete=False):
    """
Checks if influx runs on IP, fir each DATABASE it shows ALL SERIES
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

    """
    #if DEBUG:print("D... checks: ",IP,user)

    ok = False
    autho = False
    dbs = []
    liseries = []
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chkser) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG=0)

        # NO SSL
        gotit = False
        limit_int = True
        mytimeout =3 # below 10000 events

        # ------------ make time possible  1h 1d 1w
        #  > SELECT "water_level" FROM "h2o_feet" WHERE time > now() - 1h
        if type(qlimit) is str:
            limit_int = False
            if not qlimit[-1] in ["s","m","h","d","w"]:
                print("X...   limit is string but it is not 1s 1m 1h 1d 1w:", qlimit)
                print("X.... exit")
                sys.exit(1)
            intnum = "".join(qlimit[:-1])
            if  not is_int(intnum):
                print("X...   limit is string but it is not  integer s m h d w:", qlimit, intnum)
                print("X.... exit")
                sys.exit(1)
            mytimeout = 30 # worst case scenario
        #-------------
        if limit_int:
            if qlimit > 10000:
                mytimeout = 10
            if qlimit > 60000:
                mytimeout = 20
            if qlimit > 120000:
                mytimeout = 30


        try:
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=mytimeout)
            dbs = client.get_list_database() # generates exception
            gotit = True
        except:
            print("X... chks: exception without SSL")

        if not gotit:
            #if DEBUG:print("D... chks: trying with SSL")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=mytimeout)
            dbs = client.get_list_database() # generates excep

        #if DEBUG:print("D... client obtained - nossl")
        dbs = client.get_list_database()
    #print("D... list of databases obtained", dbs)


    TERMW = 55
    try:
        TERMW, rows = os.get_terminal_size(0)
    except:
        rows = 20
        #TERMW-=1
    #-------------------------------- if series not given, list them
    if series == "":
        #if DEBUG:print("D... stage check....")
        for i in dbs:
            if i["name"].find("_")==0:
                continue
            if (database!="")and(database!=i["name"]):
                continue
            print("\n",i['name'],"_"*(TERMW-len(i['name'])-2) )
            sers = client.get_list_series( i['name'] )
            # print(sers)

            maxlen=1
            for j in sers:
                #print(j,len(j))
                if len(j)>maxlen:
                    maxlen=len(j)
            maxlen+=2
            one = int(TERMW/maxlen)

            #print("D... "*50, maxlen, one )
            k = 0
            for j in sers:
                k+= 1
                liseries.append(j)
                print( "{ss:{maxlens}}".format(ss=j, maxlens=maxlen), end="" )
                if k % one == 0:
                    print()
            print()
        print()
        return liseries

    #-----series given....we go to "read" option
    #if DEBUG:print("D... stage read....")
    dbs = [i['name'] for i in dbs]
    if not database in dbs:
        print("X ... no such database - exit", database,"in", dbs)
        sys.exit(1)# quit()
    i = database
    print(i,"_"*(TERMW-len(i)-2) )

    sers = client.get_list_series( i )
    if not series in sers:
        print("X ... no such series found - exit", series)
        sys.exit(1)# quit()

    client.switch_database(i)
    #
    # i must find columns:

    #r = client.query('SELECT "temp" FROM "autogen"."'+series+'" ')

    # print("________________________________")
    # if limit_int:
    #     print("i... quering INC with limit: ", qlimit)
    #     r = client.query('SELECT * FROM "autogen"."'+series+'" ORDER BY time ASC LIMIT '+str(qlimit)  )
    # else:
    #     print("i... quering INC with time: ", qlimit)
    #     r = client.query('SELECT * FROM "autogen"."'+series+'" WHERE TIME > now() - '+str(qlimit) +" ORDER BY time ASC " )

    # #print(r.raw)
    # cols = r.raw['series'][0]['columns']
    # points = r.get_points()
    # print(cols)
    # print()
    # ppoints=0
    # dfdict = {}
    # divme = 1000
    # #h5 = h5py.File("savetest.h5")
    # for p in points:
    #     #print(p, type(p))
    #     dfdict[ppoints] = p
    #     ppoints+=1
    #     if (ppoints % divme)==0:
    #         print("{:9.0f} * {}  ".format(ppoints/ divme, divme ), end="\r" )
    # print("\nCOLUMNS:",cols)
    # print("TOTAL: {} points printed, the demanded number was {}".format( ppoints, qlimit ) )
    # df = pd.DataFrame.from_dict(dfdict, "index")
    # print(df.head() )
    # print(df.tail() )

    print("________________________________")
    if limit_int:
        print("i... quering DESC with limit: ", qlimit)
        r = client.query('SELECT * FROM "autogen"."'+series+'" ORDER BY time DESC LIMIT '+str(qlimit)  )
    else:
        print("i... quering DESC with time: ", qlimit)
        r = client.query('SELECT * FROM "autogen"."'+series+'" WHERE TIME > now() - '+str(qlimit) +" ORDER BY time DESC " )

    # r = client.query('SELECT * FROM "autogen"."'+series+'" ORDER BY time DESC LIMIT '+str(qlimit)  )

    #print(r.raw)
    cols = r.raw['series'][0]['columns']
    points = r.get_points()
    print(cols)
    print()
    ppoints=0
    dfdict = {}
    divme = 1000
    #h5 = h5py.File("savetest.h5")
    for p in points:
        #print(p, type(p))
        dfdict[ppoints] = p
        ppoints+=1
        if (ppoints % divme)==0:
            print("{:9.0f} * {}  ".format(ppoints/ divme, divme ), end="\r" )
    print("\nCOLUMNS:",cols)
    print("TOTAL: {} points printed, the DEMANDED number was {}".format( ppoints, qlimit )," - latest first" )

    df = pd.DataFrame.from_dict(dfdict, "index")
    #print(df.head() )
    #print(df.tail() )
    print(df)

    #hdf = HDFStore("influx_{}_{}.h5".format(series,ppoints) )
    now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = "influx_{}_{}_{}".format(series,now,ppoints)
    fnameh5 = "{}.h5".format(fname)
    fnamecsv = "{}.csv".format(fname)
    fnameparq = "{}.parquet".format(fname)

    # tables NEEDE HERE
    if 'tables' in globals():
        print("i... saving h5", fnameh5)
        df.to_hdf( fnameh5, series ,format ="table", mode = 'a' ) # this was ment as incremental .... sorry
    else:
        print("i... NOT saving h5", fnameh5, "format=table nedds tables: doesnt work in windows")

    print("i... saving csv", fnamecsv)
    df.to_csv( fnamecsv )
    print("i... saving parquet", fnameparq)
    df.to_parquet( fnameparq )

    if delete:
        DELETE = 'DELETE  FROM "'+series+'" '
        print( DELETE )
        res = input("REALLY DELETE? y/n")
        if res == "y":
            r = client.query( DELETE)

    print()
    return






def _read_series(database="test", series='idx0', IP="127.0.0.1", user="", password="", delete = False):
    """
READS ONE SERIES - MOST COMPELETE FUNCTION HERE
r=client.query('SELECT "temp" FROM "autogen"."idx232"')

    """
    ok = False
    autho = False
    dbs = []
    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        # print(ex)
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (rdser) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials( DEBUG=0)
        # NO SSL
        client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
        #if DEBUG:print("D... client obtained - empty")
        dbs = client.get_list_database()
    dbs = [i['name'] for i in dbs]
    #if DEBUG:print("D... list of databases obtained", dbs)


    TERMW = 55
    try:
        TERMW, rows = os.get_terminal_size(0)
    except:
        rows = 20

    if not database in dbs:
        print("X ... no such database - exit", database,"in", dbs)
        sys.exit(1)#quit()
    i = database
    print(i,"_"*(TERMW-len(i)-2) )

    sers = client.get_list_series( i )
    if not series in sers:
        print("X ... no such series found - exit", series)
        sys.exit(1)# quit()

    client.switch_database(i)
    #
    # i must find columns:
    #

    #r = client.query('SELECT "temp" FROM "autogen"."'+series+'" ')
    r = client.query('SELECT * FROM "autogen"."'+series+'" ')
    #print(r.raw)
    cols = r.raw['series'][0]['columns']
    points = r.get_points()
    print(cols)
    for p in points:
        print(p)
    print("\nCOLUMNS:",cols)

    if delete:
        DELETE = 'DELETE  FROM "'+series+'" '
        print( DELETE )
        res = input("REALLY DELETE? y/n")
        if res == "y":
            r = client.query( DELETE)

    return
    return




def checkout_hostname_database(database="test", series='idx0', IP="127.0.0.1", user="", password="", delete = False):
    """
    Check Hostname in the LOCAL influx DATABASES --- IF DIFFER: DROP;
    """

    MYHOSTNAME = socket.gethostname()
    NEWDB = "i_am_" + MYHOSTNAME
    #if DEBUG:print("D... gethostname:", MYHOSTNAME, NEWDB )

    IP = "127.0.0.1"
    ok = False
    autho = False
    dbs = []

    if user=="":
        client = InfluxDBClient(host=IP, port=8086)
    else:
        client = InfluxDBClient(host=IP, port=8086, username=user, password=password)
    try:
        dbs = client.get_list_database()
        ok = True
    except Exception as ex:
        if type(ex).__name__.find("ConnectionError")==0:
            print("X... (chhodb) NO DATABASE ON ",IP)
        if  type(ex).__name__.find("InfluxDBClientError")==0:
            print("i... database exists, authorization needed")
            ok = False
            autho = True
    if autho and user=="":
        print("I... trying with credentials from CONFIG")
        creds,ips = read_infl_credentials(DEBUG=0)

        # NO SSL
        gotit = False
        try:
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
            dbs = client.get_list_database()
            gotit = True
            #if DEBUG:print("D... client obtained with NO SSL")
        except:
            print("X... NO SSL - didnt work, I try SSL")

        if not gotit:
            try:
                #if DEBUG:print("D... client trying with  SSL")
                client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, timeout=3)
                dbs = client.get_list_database()
                #if DEBUG:print("D... client obtained with WITH SSL")
            except:
                print("X... WITH SSL - didnt work", IP, 8086,creds[0],creds[1],creds[2])


        dbs = client.get_list_database()
    dbs = [i['name'] for i in dbs]

    #if DEBUG:print("D... list of databases obtained", dbs)

    host_present = False
    ohost_present = False
    ohost_name = "x"
    for i in dbs:
        if i == NEWDB:
            host_present = True
        elif i.find("i_am_")==0:
            ohost_present = True
            ohost_name = i
    if ohost_present:
        print("!... other host present:",ohost_name," - DROP it:", ohost_present)
        client.drop_database(ohost_name)
        #return
    if host_present:
        #if DEBUG:print("D... all ok, my hostname is there with i_am_...")
        return
    print("!... CREATE DATABASE myself:", NEWDB)
    client.create_database(NEWDB)


#def drop_measurement():





def read_infl_credentials(config="~/.influx_userpassdb", DEBUG=True):
    """ READ and RETURN Influxdb  Credentials
    """
    ips=[]
    ips1=[]
    ips2=[]
    filemis = False
    try:
        with open( os.path.expanduser("~/.seread_discover8086") ) as f:
            ips1=f.readlines()
    except:
        filemis = True
        if DEBUG:
            print("X... NO FILE ~/.seread_discover8086 with automatic IPs")

    try:
        with open( os.path.expanduser("~/.seread_permanent8086") ) as f:
            ips2=f.readlines()
        filemis = False
    except:
        filemix = True
        if DEBUG:
            print("X... NO FILE ~/.seread_permanent8086 with permanent IPs")

    if filemis: print("X... no .seread_permanent8086 NEITHER seread_discover8086 with servers!")

    ips=ips1+ips2
    ips=[ i.strip() for i in ips]
    #================ credentials HERE============
    try:
        with open(os.path.expanduser( config ) ) as f:
            creds=f.readlines()
        creds=[ i.strip() for i in creds ]
    except:
        print("X... no credentials in",config )
        sys.exit(1)
        return (["","","test"],ips)
    if DEBUG:print("D... exiting with",creds,ips)
    return (creds,ips)






#=================================================

def influxwrite( DATABASE="test", MEASUREMENT="test",
                 values="" ,
                 IP="127.0.0.1",
                 initialconfig="2DOlater" , DEBUG = False):
    """write data to influx. DATABASE=test,MEASUREMENT=hostname; ./influx.py influxwrite -values b=1
    """
    if DEBUG:print("D... ************************ writin to influx ******************************")
    creds,ips=read_infl_credentials( DEBUG=DEBUG)
    # print( creds ,"##", ips )

    for IP in ips:
        if DEBUG:print("D... IP=",IP)
        if len(IP)<7:
            print("X... IP too short......... skip")
            continue
        if IP[0].isdigit(): #
            print("i... IP is number......... no ssl used")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=False, timeout=3)
        else:
            if DEBUG:print("D... IP is text. ...........I do ssl ")
            client = InfluxDBClient(IP, 8086,creds[0],creds[1],creds[2],ssl=True, verify_ssl=False,timeout=8)

        MYHOSTNAME=socket.gethostname()
        if DEBUG:print("D....................MYHOST=",MYHOSTNAME )


        if DEBUG:print("D....................INFLUX WRITING= DB/MEASUREMENT",DATABASE,MEASUREMENT )

        if len(values)==0:
            if DEBUG:print("D....  no values given ... do you need to look at current values? -exit")
            #mongo2h5( DATABASE, COLLECTION, nlimit=100000, write_h5=False)
            #quit()
            sys.exit(1)
        insertvals=values.split(",")
        if DEBUG:print("D... insert pairs:", insertvals)
        INSERTDICT={}
        for i in insertvals:
            if DEBUG:print("D... insert pair:",i)
            key=i.split("=")[0]
            val=float(i.split("=")[1])
            INSERTDICT[key]=val
        if DEBUG:print("D... INSERT DICT:", INSERTDICT )

        ###json_body = [ {"measurement":MYHOSTNAME+"_test4"} ]
        json_body = [ {"measurement":MYHOSTNAME+"_"+MEASUREMENT} ]
        #json_body[0]["fields"]={}
        json_body[0]["fields"]=INSERTDICT
        if DEBUG:print("D... ",json_body)
        res = client.write_points(json_body)
        #print("writepoints response=",res)
        if DEBUG:print("D... ************************ influx DONE ******************************")
        return res # client write response






#=================================================


#=============================================================
#=============================================================
#=============================================================
if __name__=="__main__":


    print("F... you can run ")
    print('  ./influx.py influxwrite test testmes "a=1" --DEBUG  ')
    print()
    Fire( {
      'influxwrite':influxwrite ,
      'check_port':check_port ,
      'check_dbs':check_databases ,
      'check_series':check_series ,
#      'read_series':read_series ,
#      'help': help
  } )
