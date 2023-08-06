from bs4 import BeautifulSoup
import json
html_data = """

soup = BeautifulSoup(html_data, 'html.parser')

student_info = soup.find('div', class_='center').text.strip().split('\xa0')
class_name = student_info[0].split('：')[1]
seat_number = student_info[2].split('：')[1]
student_id = student_info[4].split('：')[1]
student_name = student_info[6].split('：')[1]

subjects = []
table_rows = soup.find('table', id='restudyList').find_all('tr')
print(table_rows)
for row in table_rows[1:]:
    cells = row.find_all('td')
    subject_code = cells[0].text.strip()
    subject_name = cells[1].text.strip()
    retake_semester = cells[2].text.strip()
    historical_records = cells[3].text.strip()
    credits = cells[4].text.strip()
    subjects.append({
        '科目代碼': subject_code,
        '科目名稱': subject_name,
        '重補修學期': retake_semester,
        '歷年成績記錄': historical_records,
        '學分': credits
    })

electronic_rows = soup.find_all('tr', class_='電子二甲')
electronic_contents = []
for row in electronic_rows:
    cells = row.find_all('td')
    content = [cell.text.strip() for cell in cells]
    electronic_contents.append(content)

bt_rows = soup.find_all('tr', class_='bt')
bt_contents = []
for row in bt_rows:
    cells = row.find_all('td')
    content = [cell.text.strip() for cell in cells]
    bt_contents.append(content)

merged_contents = electronic_contents + bt_contents

data = {
    '班級': class_name,
    '座號': seat_number,
    '學號': student_id,
    '姓名': student_name,
    '不及格科目': subjects,
    '學分': merged_contents,
}

json_data = json.dumps(data, ensure_ascii=False)






# 打印JSON字符串
print(json_data)