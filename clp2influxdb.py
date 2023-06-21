import os
from influx_lib import lasttimeof_entity_id
from clp_lib import fix_clp_csv, read_clp_csv, clp_df2influx
from clp_lib import download_clp

def main():
    # run fetchClp.py to get the lateset hourly csv
    # copy cookies from browser to the above .py first!
    # after fetched csv, input the file name here and run the script to import the record to influxDB.
    username = os.environ.get('CLP_USER')
    password = os.environ.get('CLP_PASS')

    raw_csv_filename = download_clp(username, password)
    if raw_csv_filename=="":
        print("csv download from CLP failed, program terminate.")
        return (-1)
    print("CSV downloaded:", raw_csv_filename)

    fixed_csv_filename = os.path.splitext(raw_csv_filename)[0]+'-fixed.csv'

    # get last time of clp entity
    entity_id ="clp_energy_usage_hourly"
    entity_last_time = lasttimeof_entity_id(entity_id)
    if (entity_last_time==None):
        print("Error in getting entity record from influxDB.")
        exit(-1)
    print("entity_last_time in influxDB: ", entity_last_time)

    # fix the csv read from clp
    csvValid = fix_clp_csv(raw_csv_filename, fixed_csv_filename)
    if not csvValid:
        print("Unable to fix the csv from clp, please check: ", raw_csv_filename)
        exit(-1)
    print("CSV fixed to:", fixed_csv_filename)

    # load fixed csv
    df = read_clp_csv(fixed_csv_filename)
    if len(df)<=0:
        print("The fixed csv is not valid, please check:", fixed_csv_filename)
        exit(-1)
    print("Total records read from csv:", len(df.index)) # or shape df to count records

    # filter data: only keep the records after last imported
    df = df.loc[df['Time']>entity_last_time]
    nor = len(df.index)
    print("Total records are being imported to influxdb:", nor)

    if nor>0:
        print(df.columns)
        start_times = df.head(5)
        end_times = df.tail(5)
        print(start_times)
        print("...")
        print(end_times)
    
    clp_df2influx(df)
    print("Done")

if __name__ == '__main__':
    main()
