import os
from influxdb_client import InfluxDBClient, Point, WriteOptions
import pandas as pd
# from mysecrets import CONFIG_INFLUXDB
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import requests
import datetime
from bs4 import BeautifulSoup

def download_clp(username, password, fn = f"consumption_history_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"):
    # Login information
    # username = os.environ.get('CLP_USER')
    # password = os.environ.get('CLP_PASS')
    # Make a RESTful API request with the obtained session and cookies
    url_queue = [
        "https://services.clp.com.hk/en/dashboard/index.aspx"
        # ,"https://services.clp.com.hk/en/login/index.aspx"
    ]
    url_login = "https://services.clp.com.hk/Service/ServiceLogin.ashx"
    login_data = f"username={username}&password={password}&rememberMe=true&loginPurpose=&magentoToken=&domeoId=&domeoPointsBalance=&domeoPointsNeeded="
    api_url = f"https://services.clp.com.hk/Service/ServiceConsumptionDownload.ashx?caNo={username}&mode=H&outputFormat=csv"

    default_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "devicetype": "web",
        "html-lang": "en",
        "pragma": "no-cache",
    }

    """
    Converts a cookiejar object to a string.
    Args:
        cookies (cookiejar): A cookiejar object.
    Returns:
        str: A string representation of the cookiejar object.
    """
    def cookie2str(cookies):
        # get the cookies as a dictionary
        cookies_dict = requests.utils.dict_from_cookiejar(cookies)
        # convert the cookies dictionary to a string
        cookies_str = json.dumps(cookies_dict)
        return cookies_str

    # Create a session
    with requests.Session() as session:
        try:
            ## init session
            session.headers.update(default_headers)

            ## find XCSRFToken and add to session header
            for u in url_queue:
                print("loading : ", u)
                response = session.get(u, allow_redirects=True)
                # cookies = response.cookies
                # print("content: ", response.content)
                w = response.content.decode("utf8", "ignore")
                soup = BeautifulSoup(w, 'html.parser')
                csrf_token_obj = soup.find("meta", {'name': 'csrf-token'})
                if csrf_token_obj!=None:
                    auth_token = csrf_token_obj.get('content')
                    if len(auth_token)>0:
                        session.headers["X-CSRFToken"] = auth_token

            # login to clp
            response = session.post(url_login, data=login_data)
            login_result = json.loads(response.content)
            if (login_result['status']=="Y"):
                print("Login Success, downloading csv.")
                api_response = session.get(api_url)

                # download CSV if login success.
                # d = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                # fn = f"consumption_history_{d}.csv"
                if api_response.status_code == 200:
                    with open(fn, "wb") as file:
                        file.write(api_response.content)
                        file.close()
                        print("CSV file saved successfully!")
                        return fn
                else:
                    print("API request failed:", api_response.status_code)
            else:
                print("Login Failed !!!")
        except Exception as e:
            print("error found:", e)
            return ""
        finally:
            # Close the session
            session.close()

def fix_clp_csv(input_file, output_file):
    """
    Reads an input text file, fixes the format, and writes the modified text into a new file.

    Parameters:
    - input_file (str): The path to the input text file.
    - output_file (str): The path to the output text file.

    Returns:
    - bool: True if the modified text is written to the output file successfully, False otherwise.
    """
    csv_header = 'Account Number,Start time,End time,Total Consumption'

    # Read the input text file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    n = len(lines)
    print("read lines:", n)
    if n>1:
        # Replace the first line with a constant string
        lines[0] = csv_header + '\n'

        # Find the empty line and remove all text from that line onwards
        for i, line in enumerate(lines):
            if line.strip() == '':
                lines = lines[:i]
                break

        # Write the modified text into a new text file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(lines)
            print("write lines:",len(lines))

        print(f"Modified text written to {output_file} successfully.")
        return True
    else:
        return False

def read_clp_csv(csv_file):
    """
    Reads a CSV file, performs data processing, and returns a pandas DataFrame.

    Parameters:
    - csv_file (str): The path to the CSV file.

    Returns:
    - pandas.DataFrame: The processed data as a DataFrame.
    """    
    try:
        df = pd.read_csv(csv_file)
        # print("record count", len(df.index))
        # print("is empty", df.empty)
        # print("Total records read from csv:", len(df))
        # print(df.columns)
        # start_times = df['Total Consumption'].head(10)
        # print(start_times)

        # Convert date format to ISO format
        # remove invalid 'Total Consumption' records
        df['Total Consumption'] = pd.to_numeric(df['Total Consumption'], errors='coerce')
        df = df.dropna(subset=['Total Consumption'])

        # add Time column
        df['Time'] = pd.to_datetime(df['End time'], format='%d/%m/%Y %H:%M') #.dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        df['Time'] = df['Time'].dt.tz_localize('Asia/Hong_Kong') # .dt.tz_convert('Asia/Hong_Kong')

        # df['Time'] = (pd.to_numeric(df['Time']) / 1000000000).astype(int)

        # convert Time format for Start time and End time
        # NO NEED for influx import
        # df['Start time'] = pd.to_datetime(df['Start time'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        # df['End time'] = pd.to_datetime(df['End time'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        # print("Total records for importing:", len(df))

        # print(df.columns)
        # start_times = df.head(5)
        # end_times = df.tail(5)
        # print(start_times)
        # print("...")
        # print(end_times)

        return df
    except Exception as e:
        print("Unable to read from csv file:", e)
        return []

def clp_df2influx(df, entity_id="clp_energy_usage_hourly"):
    """
    Writes data from a DataFrame to InfluxDB.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data to be written.
    """
    bucket = os.environ.get('INFLUXDB_BUCKET')
    org = os.environ.get('INFLUXDB_ORG')
    token = os.environ.get('INFLUXDB_TOKEN')
    url = os.environ.get('INFLUXDB_URL')

    # Create InfluxDB client instance
    client = InfluxDBClient(url=url, token=token, org=org)
    try:
        data_points = []
        for _, row in df.iterrows():
            point = Point("kWh") \
                .tag("domain", "import") \
                .tag("entity_id", entity_id) \
                .field("value", row["Total Consumption"]) \
                .time(row["Time"])
            data_points.append(point)

        print("Data points for importing:", len(data_points))
        if len(data_points)>0:
            print("The first point:", data_points[0])

            # Write data to InfluxDB
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                write_api.write(bucket=bucket, org=org, record=data_points) #, write_options=WriteOptions(batch_size=5000))
    finally:
        # Close the client connection
        client.__del__()

def main():
    # fin = "./consumption_history_20230613-153656.csv"
    # fout = "./consumption_history_20230613-153656-fixed.csv"
    # fix_clp_csv(fin, fout)
    # df = read_clp_csv("./consumption_history_20230613-153656.csv")
    clpuser = os.environ.get("CLP_USER_SK")
    clppass = os.environ.get("CLP_PASS")
    print(clpuser,clppass)

    download_clp(clpuser, clppass, "temp.test1.csv")

if __name__ == '__main__':
    main()
