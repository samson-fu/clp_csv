import os
from lib.influx_lib import lasttimeof_entity_id
from lib.clp_lib import fix_clp_csv, read_clp_csv, clp_df2influx
import argparse
from dotenv import load_dotenv

import_filename='temp.82841722098.fix.csv'

def main(args):
    # run fetchClp.py to get the lateset hourly csv
    # copy cookies from browser to the above .py first!
    # after fetched csv, input the file name here and run the script to import the record to influxDB.
    username = args.login
    password = args.pwd
    print("username:", username)
    print("password:", password)

    idb = dict(url = args.idb_url, 
        bucket=args.idb_bucket, 
        org=args.idb_org, 
        token=args.idb_token,
        entity_id=args.idb_entity)
    print("entity_id:", idb["entity_id"])
    print("idb:", idb)
    # validate influxDB config
    if idb["url"]==None:
        print("InfluxDB url is required!")
        return(-1)

    # load fixed csv
    df = read_clp_csv(import_filename)
    if len(df)<=0:
        print("The fixed csv is not valid, please check:", import_filename)
        return(-1)
    print("Total records read from csv:", len(df.index)) # or shape df to count records
    
    # # filter data: only keep the records after last imported
    # if entity_last_time!=None:
    #     df = df.loc[df['Time']>entity_last_time]
    nor = len(df.index)
    print("Total records being imported to influxdb:", nor)

    if nor>0:
        print(df.columns)
        start_times = df.head(5)
        end_times = df.tail(5)
        print(start_times)
        print("...")
        print(end_times)
    
    clp_df2influx(df, idb["entity_id"])

    print("Import completed.")

    print("Done")
    return(0)

if __name__ == '__main__':
    load_dotenv()
    parser = argparse.ArgumentParser(
      prog='CLP to influxDB',
      description="Download CLP hourly usage and import to influxDB",
      epilog="Use at yourown risk.",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-login", help="CLP Login ID.", default=os.environ.get("CLP_USER"))
    parser.add_argument("-pwd", help="CLP Login Password.", default=os.environ.get("CLP_PASS"))
    parser.add_argument("-idb", help="Import to InfluxDB. Need to provide InfluxDB details if specified this flag.", action='store_true')
    parser.add_argument("-idb_url", help="InfluxDB URL.", default=os.environ.get("INFLUXDB_URL"))
    parser.add_argument("-idb_bucket", help="InfluxDB BUCKET.", default=os.environ.get("INFLUXDB_BUCKET"))
    parser.add_argument("-idb_org", help="InfluxDB ORG.", default=os.environ.get("INFLUXDB_ORG"))
    parser.add_argument("-idb_token", help="InfluxDB TOKEN.", default=os.environ.get("INFLUXDB_TOKEN"))
    parser.add_argument("-idb_entity", help="Entity ID to import the data.", default=os.environ.get("INFLUXDB_ENTITY_ID"))
    parser.add_argument("-idb_purgeFile", help="Delete downloaded csv after imported to INFLUXDB.", action='store_true')
    args = parser.parse_args()
    runResult = main(args)
    if runResult!=0:
        exit(runResult)
