import requests
import json
from datetime import datetime, timedelta, date
from events import *
from time import sleep
import pygsheets
import set_parameters
import logging
# file_id = "1XFvj4TmOSFeB8fcxMuqwCctZoalR0bDFoKCEsJFnVdw"
credentials = {"acces_token": ""}
headers = None
number_of_days = 1
# date_start_str = "2020-05-19 08:00:00"
SETTINGS_FILE = "settings_sd.json"
# ADMIN = 3010354

# class_1 = {1830118: [28311004, 28311523, 143],
#          1928572: [28997893, 28997896, 30349033, 30349033, 31355701, 143]}
# class_2 = {1866724: [28600273, 28600276]}


def get_new_token_pair():
    """ Get the new pair of tokens
         return dict
    """
    tokens_dict = settings["access_data"]
    url = init_url+settings["api_urls"]["access_token_refresh"]["url"]
    r = requests.post(url, json=tokens_dict)
    if r.status_code != 200:
        #print("Error", r.status_code)
        logging.error('This is an error message %s', r.status_code)
        return -1
    else:
        return r.json()


def refresh_credentials():
    global access_token
    global headers
    tokens = get_new_token_pair()
    if tokens == -1:
        return -1
    print(tokens)
    settings["access_token"] = tokens["access_token"]
    settings["access_token_time"] = int(datetime.now().timestamp())
    settings["token_type"] = tokens["token_type"]
    settings["access_token_expire"] = tokens["expires_in"]
    settings["access_data"]["refresh_token"] = tokens["refresh_token"]
    access_token = settings["access_token"]
    headers = {
        "Authorization": "Bearer "+access_token,
        "User-Agent": "amoCRM-oAuth-client/1.0"
    }
    set_settings(SETTINGS_FILE, settings)


def create_href(user, cls, t_start, t_stop):
    f_begin = "?limit=100&filter[created_by]={0}"+"&filter[type]=lead_status_changed" + \
        "&filter[created_at]="+str(t_start)+","+str(t_stop)
    filter_statuses = "&filter[value_after][leads_statuses][{0}][pipeline_id]={1}&filter[value_after][leads_statuses][{0}][status_id]={2}"
    s = ""
    i = 0
    for pipeline in cls:
        for status in cls[pipeline]:
            s = s+filter_statuses.format(i, pipeline, status)
            i += 1
    return f_begin.format(user)+s


def put_data_json(filename, data):

    with open(filename, "w") as write_file:
        json.dump(data, write_file, ensure_ascii=False)


def get_data_json(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


def get_settings(file):
    settings = get_data_json(file)

    return settings


def set_settings(file, settings):
    put_data_json(file, settings)


def get_events(url):
    # print(url)
    # events = []
    r = requests.get(url, headers=headers)
    if r.status_code == 401:
        logging.error(
            "Get events function, authorization failed %s", r.status_code)
        # print("*******************************", r.status_code,
        # "**********************************")
        ret = refresh_credentials()
        if ret == -1:
            return -1
    elif r.status_code == 204:
        print("X"*20)
        return None
    return r.json()["_embedded"]["events"]


def test_credentials(url):
    r = requests.get(url, headers=headers)
    if r.status_code == 401:
        logging.error(
            "test credentials function, authorization failed %s", r.status_code)
        ret = refresh_credentials()
        if ret == -1:
            return -1
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            logging.info("Credentials were updated")
            return 0
        else:
            return -1
    return 0


def check_for_exlude(event):
    """
        Checking, is the event present in exclude list
    """
    pipeline_id = str(event["value_before"][0]["lead_status"]["pipeline_id"])
    event_id = str(event["value_before"][0]["lead_status"]["id"])
    # print(type(pipeline_id), '***', type(event_id))
    if pipeline_id in param['cls3'] and event_id in param['cls3'][pipeline_id]:
        return True
    return False


logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)  # filename=u'mylog.log'

settings = get_settings(SETTINGS_FILE)
param = set_parameters.setup_parameters()
# print(param)


gc = pygsheets.authorize(service_file=set_parameters.SSHEET_SECRETS)
ssht = gc.open(set_parameters.WORK_SSHEET)

init_url = "https://"+settings["subdomain"]+"."+settings["domain"]
access_token = settings["access_token"]
headers = {
    "Authorization": "Bearer "+access_token,
    "User-Agent": "amoCRM-oAuth-client/1.0"


}


date_start = date(2020, 5, 1)
# temp_date = date(2020, 6, 8)
d = datetime.today().date() - date_start
row_start = int(param["date_row_start"])+d.days+2  # времмено добавил на июнь

url_api = settings["api_urls"]["events"]["url"]
if "period" not in param:
    date_start_str = str(datetime.today().date())+" 08:00:00"
    # date_start_str = str(temp_date) + " 08:00:00"

users_col = param["users_column"]
users = param["users"]
# print(users_col)
logging.info("Users columns in spreadsheet: %s", users_col)
url = "https://"+settings["subdomain"]+"."+settings["domain"] + \
    settings["api_urls"]["account"]["url"]+"?"+"with=users"

# print(url)
logging.debug("test access url - %s", url)
test_credentials(url)


worksheet = ssht.worksheet_by_title("test")
for user in users:
    logging.info("user: %s", user)
    i = 0
    date = datetime.strptime(date_start_str, "%Y-%m-%d %H:%M:%S")
    while i < number_of_days:
        count = 0
        logging.info("date: % s", date)
        timestamp_start = int(date.timestamp())
        timestamp_stop = int(
            (date+timedelta(hours=15, minutes=59)).timestamp())
        url = init_url+url_api + \
            create_href(user, param["cls1"], timestamp_start, timestamp_stop)
        events = get_events(url)
        if events == -1:
            logging.critical("Programm stopped")
            exit()
        # print(events)
        if events is not None:
            num = set()
            for item in events:
                if not check_for_exlude(item):
                    num.add(item["entity"]["id"])
            count = len(num)
        else:
            print("No status changed for user")
        cell = users_col[user]+str(row_start+i)
        worksheet.update_value(cell, count)
        print("подсчитано: ", count)
        # print(create_href(users[0], class_1, timestamp_start, timestamp_stop))
        i = i+1
        date = date+timedelta(days=1)
        # sleep(3)
