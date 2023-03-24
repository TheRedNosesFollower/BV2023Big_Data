import requests
import sqlite3


if __name__ == '__main__':
    access_key = 'vk1.a.-UQERmI01OMK70BV71Lp0LyO0E5lUnrKG_iMswSMqSiSKRCBJAwhlcySYvWaH_qL9BcYtF1oK-qSOoVZDwgIFtoy2u1iFdu' \
                 'j6JtBHukH2e_d98pY-h4NF9bJtrJtOwAndYwyB-b12VQwhpSX-PhYySCAW-q8UtgFPwv7VSd7nDVpfdg_56r4vvzxBsfyMFIkCym' \
                 '3fCIv8niFN644Hpcvcg'
    group_id = '134723783'
    url = 'https://api.vk.com/method/groups.getMembers'
    version = '5.131'
    offset = 0
    public_size = 3337

    data = []

    while offset <= 5000:
        params = {'access_token': access_key,
                  'v': version,
                  'group_id': group_id,
                  'offset': offset,
                  'fields': 'bdate,sex,universities,relatives'}

        response = requests.get(url, params)
        if not response:
            print('ERROR')

        response_json = response.json()
        offset += 1000

        for member in response_json['response']['items']:
            row = ['-'] * 5
            row[0] = str(member['id'])
            row[1] = ' '.join(sorted([member['first_name'], member['last_name']]))
            if 'bdate' in member:
                row[2] = member['bdate']
            if 'sex' in member:
                row[3] = {2: 'Male', 1: 'Female', 0: '-'}[member['sex']]
            if 'universities' in member:
                for university in member['universities']:
                    try:
                        row[4] += f'{university["name"]}, {university["faculty_name"]};'
                    except KeyError:
                        row[4] += f'{university["name"]};'
            data.append(row)

    con = sqlite3.connect('Strategy.db')
    cur = con.cursor()

    for item in data:
        try:
            cur.execute(f"""INSERT INTO group_members(vk_id, name, sex, birth_date, education) VALUES(
                        {item[0]}, '{item[1].replace("'", '')}', '{item[3]}', '{item[2]}', '{item[4]}')""")
        except Exception as er:
            print(er.__class__.__name__, er, item)
    con.commit()
