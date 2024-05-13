## First
For Python 3.11 !

Install required libraries:
```
pip install -r requirements.txt
```

Prepare `.env` file as below:
```
#CLP LOGIN
CLP_USER=myusername
CLP_PASS=mypassword
# INFLUXDB Config
INFLUXDB_URL=http://192.168.2.1:1234
INFLUXDB_BUCKET=mypowerbucket
INFLUXDB_ORG=myorg
INFLUXDB_TOKEN=nOhM3Wi4u9cYa122Zk_jTDq_3lfSdf0m2s5mC0HeG1jwjdqu1895jWypaXMAY9W6VVzoFu--07YhjV9m6EgU6A==
INFLUXDB_ENTITY_ID=clp_energy_usage_hourly
```

Prepare `crontab` file, as cron job file format as below:
```
1 8 * * * cd /app && python /app/clp2influxdb.py -login 1234567890 -idb -idb_entity clp_energy_usage_hourly -idb_purgeFile
```


## Prepare 
Make sure can login with user name and password method to CLP.
`https://services.clp.com.hk/`

## Test
Create a new file .env in the source code folder and,
write CLP `user name` and `password` by using .env.demo file format.

Run clp_lib.py by
```
python lib/clp_lib.py
```

find the file `temp.test1.csv` to see if the hourly usage is valid. If the data in the file is correct, you are ready to put the data to influxDB.

## load CLP data to influxDB
Update .env file with the required influxDB configuration. To setup influxDB please refer to the influxDB website.

... to be continue

## REF
https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/

## Examples:
1. Download clp csv file only
```
python3 clp2influxdb.py -login 81234567890 -pwd abCD1234
```

2. Download import CLP data to influxDB 
```
python3 clp2influxdb.py -login 81234567890 -pwd abCD1234 -idb -idb_url http://192.168.2.1:1234 -idb_bucket mypowerbucket -idb_org myorg -idb_token nOhM3Wi4u9cYa122Zk_jTDq_3lfSdf0m2s5mC0HeG1jwjdqu1895jWypaXMAY9W6VVzoFu--07YhjV9m6EgU6A== -idb_entity lungwa_clp_energy_usage_hourly -idb_purgeFile
```

3. Save all parameters in .env file as the format of .env.demo. Run the following to import clp to influxDB
```
python3 clp2influxdb.py -idb -idb_purgeFile
```
