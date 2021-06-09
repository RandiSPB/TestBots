import os
import json

admins_id = ['923092219', '369738935']
stat_dict = {}

with open('edstyle.txt', 'r', encoding='UTF-8') as edstyle_logs:
    res = edstyle_logs.read().split('\n\n')
    i, j = 0, 2
    tmp = []
    while j < len(res):
        tmp.append((res[i], res[j]))
        i += 4
        j += 4
    res = {}
    for i in tmp:
        user_id = i[0].split(':')[0][:-1:]
        if user_id not in admins_id:
            res[user_id] = i[1][3:-4:]
    for i in res.keys():
        tmp3 = {}
        tmp2 = res[i].split('\n')
        for j in tmp2:
            tmp4 = j.split(' - ')
            tmp3[tmp4[0]] = tmp4[1]
        res[i] = tmp3
    print(res)
    with open('edstyle_res.json', 'w', encoding='UTF-8') as res_json:
        json.dump(res, res_json, ensure_ascii=False, indent=4)

