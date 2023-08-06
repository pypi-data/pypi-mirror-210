import json

def getLogNum(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        line_count = sum(1 for _ in file)
    return line_count


def saveLog(json_data, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        if json_data['code'] == 0:
            newLog = [{
                'num': getLogNum(file_path),
                'code': json_data['code'],
                'User': json_data['學號'],
                'class': json_data['班級'],
                'realName': json_data['姓名'],
                'grade': json_data['考試科目成績'],
                'gradeCount': [{'總分': json_data['總分'], '平均': json_data['平均'], '排名': json_data['排名'], '科別排名': json_data['科別排名']}],
                'runLog': json_data['log']
            }]
        else:
            newLog = [{
                'num': getLogNum(file_path),
                'code': json_data['code'],
                'reason': json_data['reason'],
                'runLog': json_data['log']
            }]

        json_line = json.dumps(newLog, ensure_ascii=False)
        file.write(json_line + '\n')
