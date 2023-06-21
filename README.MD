## First of first
pip install 

## Prepare 
Login to CLP and make sure to be able to login with user name and password method.
`https://services.clp.com.hk/`

## Test
Create a new file .env in the source code folder and,
write CLP `user name` and `password` by using .env.demo file format.

Run clp_lib.py by
```
python clp_lib.py
```

find the file `temp.test1.csv` to see if the hourly usage is valid. If the data in the file is correct, you are ready to put the data to influxDB.

## load CLP data to influxDB
Update .env file with the required influxDB configuration. To setup influxDB please refer to the influxDB website.

... to be continue

## REF
https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
