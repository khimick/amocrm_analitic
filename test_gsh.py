import requests
import json
from datetime import datetime, timedelta, date
import pygsheets
import set_parameters

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


worksheet = ssht.worksheet_by_title("develop")
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
