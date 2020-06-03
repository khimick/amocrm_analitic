import random

main = {}
ddd = {}


def count_per_user(dictionary):
    users = {}
    for item in dictionary:
        user = dictionary[item]
        if user in users:
            users[user] = users[user]+1
        else:
            users[user] = 1
    return users


def pipe3(event):
    status = event["value_after"][0]["lead_status"]["id"]
    user = event["created_by"]
    # if user == ADMIN:
    #    pass
    if status in main:
        for i in range(len(main[status])):
            if main[status][i]["user"] == user:
                main[status][i]["count"] += 1
                return
        tmp = {}
        tmp["user"] = user
        tmp["count"] = 1
        main[status].append(tmp)
    else:
        tmp_l = []
        tmp_d = {}
        tmp_d["user"] = user
        tmp_d["count"] = 1
        tmp_l.append(tmp_d)
        main[status] = tmp_l

# ********************************************


def pipe12(event):
    global main
    if event["entity"]["type"] != "lead":  # проверяем тип события переход на этап сделки или нет
        return -1
    id_lead = event["entity"]["id"]   # взять номер сделки
    # взять ответсвенного за событие менеджера

    user = event["created_by"]
    if id_lead not in ddd:
        ddd[id_lead] = user
    else:
        if user != ddd[id_lead]:
            # если у сделки меняется ответсвенный добавляем для подсчета фиктивную сделку для предыдущего менеджера
            ddd[hash(random.random()*20000+1)] = ddd[id_lead]
            ddd[id_lead] = user  # записываем сделку на нового менеджера


def print_events(events):
    i = 0
    for item in events:
        i = i+1
        print(i, item["id"])
        print(item["type"])
    pass


def check_category(event, sett):
    status = event["value_after"][0]["lead_status"]["id"]
    pipeline = event["value_after"][0]["lead_status"]["pipeline_id"]
    if pipeline in sett["1"]:
        if status in sett["1"][pipeline]:
            return 1
        else:
            return -1
    if pipeline in sett["2"]:
        if status in sett["2"][pipeline]:
            return 2
        else:
            return -1

    return -1
