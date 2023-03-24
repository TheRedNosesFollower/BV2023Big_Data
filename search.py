import sqlite3
import xlrd
import requests


def find_person(person_data):
    access_key = 'vk1.a.-UQERmI01OMK70BV71Lp0LyO0E5lUnrKG_iMswSMqSiSKRCBJAwhlcySYvWaH_qL9BcYtF1oK-qSOoVZDwgIFtoy2u1iFdu' \
                 'j6JtBHukH2e_d98pY-h4NF9bJtrJtOwAndYwyB-b12VQwhpSX-PhYySCAW-q8UtgFPwv7VSd7nDVpfdg_56r4vvzxBsfyMFIkCym' \
                 '3fCIv8niFN644Hpcvcg'
    url = 'https://api.vk.com/method/users.search'
    version = '5.131'
    params = {
        'access_token': access_key,
        'v': version,
        'q': person_data[0],
        'hometown': person_data[2],
        'fields': 'universities'
    }
    resp = requests.get(url, params)
    if not resp:
        print('ERROR', resp)

    resp_json = resp.json()
    #print(resp_json)
    if resp_json['response']['count'] == 0:
        #er_count += 1
        return None
    candidate = resp_json['response']['items'][0]
    for person in resp_json['response']['items']:
        if 'universities' in person and person_data[1] in person['universities']:
            candidate = person
            break
    return candidate


if __name__ == '__main__':
    workbook = xlrd.open_workbook('База Стратегия.xlsx')
    con = sqlite3.connect('Strategy.db')
    cur = con.cursor()

    rows = [131, 131, 280, 130]
    data = []

    sheet = 0
    for item in rows:
        worksheet = workbook.sheet_by_index(sheet)
        for row in range(item):
            curr = [' '.join(sorted(str(worksheet.cell(row, 0))[6:-1].split()[:2]))]
            if (sheet == 0):
                curr.append(str(worksheet.cell(row, 2))[6:-1])
            else:
                curr.append(str(worksheet.cell(row, 3))[6:-1])
            if (sheet != 0):
                curr.append(str(worksheet.cell(row, 2))[6:-1])
            else:
                curr.append(str(worksheet.cell(row, 1))[6:-1])
            data.append(curr)
        sheet += 1

    print(data)

    for item in data:
        request = cur.execute('''SELECT * FROM group_members WHERE name = ?''', (item[0],)).fetchall()
        if request:
            try:
                cur.execute('''INSERT INTO graduated(vk_id, name) VALUES(?, ?)''', (request[0][1], request[0][2],))
            except Exception:
                continue
        else:
            man = find_person(item)
            if man is None:
                continue
            try:
                cur.execute('''INSERT INTO graduated(vk_id, name) VALUES(?, ?)''', (man['id'],
                                                                                    ' '.join(sorted([man['first_name'], man['last_name']]))))
            except Exception:
                continue
        con.commit()
