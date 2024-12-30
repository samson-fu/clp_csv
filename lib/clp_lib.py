import os
from influxdb_client import InfluxDBClient, Point, WriteOptions
import pandas as pd
# from mysecrets import CONFIG_INFLUXDB
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import requests
# import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

def get_dates(days_before_today=90):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    # Get today's date
    today = datetime.now().astimezone()
    
    # Format today's date as YYYYMMDD
    today_str = today.strftime('%Y%m%d235959')
    
    # Calculate the date a specified number of days before today
    date_before_today = today - timedelta(days=days_before_today)
    
    # Format the date a specified number of days ago as YYYYMMDD
    date_before_today_str = date_before_today.strftime('%Y%m%d000000')
    
    return date_before_today_str, today_str

def ensure_folder_exists(filename):
    """
    Checks if the folder for the given filename exists, 
    and creates the folder if it doesn't.
    
    Parameters:
        filename (str): The path to the file whose folder needs to be checked/created.
    """
    # Extract the folder path from the filename
    folder_path = os.path.dirname(filename)
    if (folder_path!=""):
        # Check if the folder exists, and create it if it doesn't
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")

def download_clp(username, password, fn = f"./history/consumption_history_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"):
    # Login information
    # username = os.environ.get('CLP_USER')
    # password = os.environ.get('CLP_PASS')
    # Make a RESTful API request with the obtained session and cookies
    url_queue = [
        "https://services.clp.com.hk/en/dashboard/index.aspx"
        # ,"https://services.clp.com.hk/en/login/index.aspx"
    ]
    url_login = "https://api.clp.com.hk/ts1/ms/profile/accountManagement/loginByPassword"
    login_data = f'{{"username":"{username}","password":"{password}"}}'
    startDate , expireDate = get_dates()
    api_url = f"https://api.clp.com.hk/ts1/ms/consumption/download?ca={username}&expireDate={expireDate}&startDate={startDate}&outputFormat=csv&mode=Hourly"

    default_headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Device-Type": "web",
        "Connection": "keep-alive",
        "cache-control": "no-cache",
        "Content-Type": "application/json",
        "Accept-Language": "en",
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

            # ## find XCSRFToken and add to session header
            # for u in url_queue:
            #     print("loading : ", u)
            #     response = session.get(u, allow_redirects=True)
            #     data = response.json()
            #     # Extract the access_token
            #     auth_token = data.get('access_token')
            #     session.headers["Authorization"] = auth_token

            # login to clp
            print("Login to clp...")
            response = session.post(url_login, data=login_data)
            data = response.json()
            # login_result = json.loads(response.content)
            # if (login_result['status']=="Y"):
            if (data.get('code') == 200):
                print("Login Success, downloading csv.")
                # Extract the access_token
                auth_token = data['data']['access_token']
                session.headers["Authorization"] = auth_token
                print(f"access_token = {auth_token}")
                print(f"Downloading file from: {api_url}")
                api_response = session.get(api_url)

                # download CSV if login success.
                # d = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                # fn = f"consumption_history_{d}.csv"
                if api_response.status_code == 200:
                    ensure_folder_exists(fn)
                    with open(fn, "wb") as file:
                        file.write(api_response.content)
                        file.close()
                        print("CSV file saved successfully!")
                        return fn
                else:
                    print("API request failed:", api_response.status_code)
                    print("data")
                    print(data)
                    print("api_response.content")
                    print(api_response.content)
            else:
                print("Login Failed !!!")
                print(data)
            return ""
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

def clp_df2influx(df, entity_id):
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
    load_dotenv()
    # fin = "./consumption_history_20230613-153656.csv"
    # fout = "./consumption_history_20230613-153656-fixed.csv"
    # fix_clp_csv(fin, fout)
    # df = read_clp_csv("./consumption_history_20230613-153656.csv")
    clpuser = os.environ.get("CLP_USER")
    clppass = os.environ.get("CLP_PASS")
    print(clpuser,clppass)

    download_clp(clpuser, clppass, "temp.test1.csv")

if __name__ == '__main__':
    main()
