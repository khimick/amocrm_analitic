import pygsheets


END_ROW = 20
END_COL = 20
WORK_SSHEET = "Аналитика из amoCRM"
SSHEET_SECRETS = 'client_secret.json'


def setup_parameters():
    gc = pygsheets.authorize(service_file=SSHEET_SECRETS)
    ssht = gc.open(WORK_SSHEET)
    worksheet = ssht.worksheet_by_title("settings")
    parameters = {}  # в этом словаре будут собираться параметры
    pvalues_mat = worksheet.get_values(
        start=(1, 1), end=(END_ROW, END_COL), returnas='matrix')  # получаем часть таблицы в ввиде матрицы

#  собираем словарь заголовков параметров - в каких колонках какой
    column_headers = {}

    i = 0
    for item in pvalues_mat[0]:
        if item != "":
            column_headers[item] = i
            # print()
        i += 1
# начинаем устанавливать параметры
    parameters["admin"] = pvalues_mat[1][column_headers["admin"]]
    parameters["date_row_start"] = pvalues_mat[1][column_headers["date 1 may 2020"]]
    j = 1
    tmp_arr = []
    while pvalues_mat[j][column_headers["users"]] != "":
        tmp = []
        tmp_arr.append(pvalues_mat[j][column_headers["users"]])
        j += 1
    parameters["users"] = tmp_arr
    j = 1
    tmp = {}
    while pvalues_mat[j][column_headers["columns"]] != "":
        tmp[pvalues_mat[j][column_headers["users"]]
            ] = pvalues_mat[j][column_headers["columns"]]
        j += 1
    parameters["users_column"] = tmp

    tmp = {}
    i = 1
    j1 = column_headers["class 1 / pipeline"]
    j2 = column_headers["class 1 / status"]
    pipeline = pvalues_mat[i][j1]
    tmp_arr = []
    while i < len(pvalues_mat):
        if pvalues_mat[i][j1] == "":
            break

        if pipeline == pvalues_mat[i][j1]:
            tmp_arr.append(pvalues_mat[i][j2])
        else:
            tmp[pipeline] = tmp_arr
            pipeline = pvalues_mat[i][j1]
            tmp_arr = []
            tmp_arr.append(pvalues_mat[i][j2])
        i += 1
    tmp[pipeline] = tmp_arr
    parameters["cls1"] = tmp

    tmp = {}
    i = 1
    j1 = column_headers["class 2 / pipeline"]
    j2 = column_headers["class 2 / status"]
    pipeline = pvalues_mat[i][j1]
    tmp_arr = []
    while i < len(pvalues_mat):
        if pvalues_mat[i][j1] == "":
            break

        if pipeline == pvalues_mat[i][j1]:
            tmp_arr.append(pvalues_mat[i][j2])
        else:
            tmp[pipeline] = tmp_arr
            pipeline = pvalues_mat[i][j1]
            tmp_arr = []
            tmp_arr.append(pvalues_mat[i][j2])
        i += 1
    tmp[pipeline] = tmp_arr
    parameters["cls2"] = tmp

    tmp = {}
    i = 1
    j1 = column_headers["class 3 / pipeline"]
    j2 = column_headers["class 3 / status"]
    pipeline = pvalues_mat[i][j1]
    tmp_arr = []
    while i < len(pvalues_mat):
        if pvalues_mat[i][j1] == "":
            break

        if pipeline == pvalues_mat[i][j1]:
            tmp_arr.append(pvalues_mat[i][j2])
        else:
            tmp[pipeline] = tmp_arr
            pipeline = pvalues_mat[i][j1]
            tmp_arr = []
            tmp_arr.append(pvalues_mat[i][j2])
        i += 1
    tmp[pipeline] = tmp_arr
    parameters["cls3"] = tmp
    return parameters
