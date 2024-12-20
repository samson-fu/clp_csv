import os
from influxdb_client import InfluxDBClient

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
    lastRecordTime = lasttimeof_entity_id(queryRange="start: -1m")
    # lastRecordTime = lasttimeof_entity_id(queryRange="start: '202'")

    print(type(lastRecordTime), lastRecordTime)

if __name__ == '__main__':
    main()
