import os
import pandas as pd
from influxdb_client import InfluxDBClient

def findDiffTime(df, entity_id="clp_energy_usage_hourly", queryRange="start: -1y"):
    """
    Compares a given DataFrame with data from an InfluxDB database to find the first difference.
    Parameters:
    df (pd.DataFrame): The DataFrame to compare against InfluxDB data.
    entity_id (str): The entity ID to filter the InfluxDB data. Default is "clp_energy_usage_hourly".
    queryRange (str): The time range for the InfluxDB query. Default is "start: -1y".
    Returns:
    pd.DataFrame: A DataFrame containing the differences between the input DataFrame and the InfluxDB data.
    """
    result = None
    # Connection settings
    # Set the active organization and bucket
    bucket = os.environ.get('INFLUXDB_BUCKET')
    # bucket = 'fuhomeha' # UAT debug
    org = os.environ.get('INFLUXDB_ORG')
    token = os.environ.get('INFLUXDB_TOKEN')
    url = os.environ.get('INFLUXDB_URL')
    print("Comparing DF and Influx to find first difference...")
    client = InfluxDBClient(url=url, token=token, org=org)
    try:
        # Create a Flux query, and then format it as a Python string.
        query = f'''
        from(bucket:"{bucket}")
        |> range({queryRange})
        |> filter(fn: (r) => r["entity_id"] == "{entity_id}")
        |> yield(name: "influxData")
        '''

        # Pass the query() method two named parameters:org and query.
        query_result = client.query_api().query(org=org, query=query)

        # Extract data from the query result
        influx_data = []
        for table in query_result:
            for record in table.records:
                influx_data.append({
                    'time': record.get_time(),
                    'value': record.get_value()
                })
        
        # Convert the InfluxDB data to a DataFrame
        influx_df = pd.DataFrame(influx_data)
        
        # Ensure 'time' is in datetime format
        influx_df['time'] = pd.to_datetime(influx_df['time'])
        
        # Merge DataFrames on time and value to find differences
        merged_df = pd.merge(df, influx_df, on=['time', 'value'], how='outer', indicator=True)

        # Identify differences
        differences = merged_df[merged_df['_merge'] != 'both']

    except Exception as error:
        print("An exception occurred:", error)
    finally:
        # Close the client connection
        client.__del__()
        return result

def lasttimeof_entity_id(entity_id="clp_energy_usage_hourly", queryRange="start: -1y"):
    result = None
    # Connection settings
    # Set the active organization and bucket
    bucket = os.environ.get('INFLUXDB_BUCKET')
    # bucket = 'fuhomeha' # UAT debug
    org = os.environ.get('INFLUXDB_ORG')
    token = os.environ.get('INFLUXDB_TOKEN')
    url = os.environ.get('INFLUXDB_URL')

    # Create InfluxDB client instance
    print("InfluxDB.bucket:", bucket)
    print("InfluxDB.org:", org)
    print("InfluxDB.token:", token)
    print("InfluxDB.url:", url)
    client = InfluxDBClient(url=url, token=token, org=org)
    try:
        # Create a Flux query, and then format it as a Python string.
        query = f'''
        from(bucket:"{bucket}")
        |> range({queryRange})
        |> filter(fn: (r) => r["entity_id"] == "{entity_id}")
        |> last()
        |> yield(name: "last")
        '''

        # Pass the query() method two named parameters:org and query.
        query_result = client.query_api().query(org=org, query=query)
        # print("result: ", result)

        # results = []
        for table in query_result:
            # for column in table.columns:
            for record in table.records:
                result = record.get_time()
        #         d2 = time.strftime("")
        #         results.append({ "field": record.get_field(), "value": record.get_value(), "time": record.get_time()})

        # print("results: ", results)
    except Exception as error:
        print("An exception occurred:", error)
    finally:
        # Close the client connection
        client.__del__()
        return result

def main():
    lastRecordTime = lasttimeof_entity_id()

    print(type(lastRecordTime), lastRecordTime)

if __name__ == '__main__':
    main()
