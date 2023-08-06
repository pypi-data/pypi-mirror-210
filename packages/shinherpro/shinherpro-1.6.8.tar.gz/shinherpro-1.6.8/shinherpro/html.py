from bs4 import BeautifulSoup
import json

html_content = """<html><head>
    <meta http-equiv="Content-Language" content="zh-tw">
    <meta http-equiv="Content-Type" content="text/html; charset=big5">
    <meta name="author" content="ShinHer Information Co.,Ltd.">
    <meta name="keywords" content="欣河資訊">
    <meta name="description" content="線上查詢系統">
    <meta name="copyright" content="Copyright © 1988-2023 ShinHer Information Co.,Ltd. All rights reserved.">
    <link id="lnkShortcutIcon" media="all" rel="Shortcut Icon" type="image/x-icon" href="/online/image/icon/favicon.ico">
    <meta name="Pragma" content="no-cache">
    <meta http-equiv="Pragma" content="no-cache">
    <meta name="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta name="Cache-Control" content="post-check=0, pre-check=0">
    <meta name="Cache-Control" content="private">
    <meta http-equiv="Expires" content="-1">
    <title>線上查詢系統-賴奕寰缺曠統計資料</title>
    <link href="../css/page_all.css?20220506093854" type="text/css" rel="stylesheet">
    <style type="text/css">
        @media print {
            @page {
                size: A4 portrait;
            }
        }

        body {
            width: 210mm;
        }
    </style>
    <script src="../JS/common.js?20230103153532" type="text/javascript"></script>
    <script src="../JS/struct.js?20230103153532" type="text/javascript"></script>
</head>
<body class="si_15" marginwidth="0" marginheight="0">
    <div class="tbody01">
        <div style="vertical-align: bottom;">班級：電子二甲&nbsp;座號：33&nbsp;學號：013333&nbsp;姓名：賴奕寰
            </div>
        <table border="0" class="padding2 spacing0" style="font-size: 12px; width: 590px;">
            <tbody><tr class="td_03 si_12 le_05 top center">
                <td>週別</td>
                <td>日期</td>
                <td>星期</td>
                <td>早</td>
                <td>升</td>
                <td>1</td>
                <td>2</td>
                <td>3</td>
                <td>4</td>
                <td>午</td>
                <td>5</td>
                <td>6</td>
                <td>7</td>
                <td>8</td>
                <td>降</td>
                <td>9</td>
                <td>10</td>
                <td>11</td>
                <td>12</td>
        </tr>
        <tr><td class="top center" style="">上1</td><td class="top center" style="">2022/9/1</td><td class="top center" style="">四</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">遲</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上3</td><td class="top center" style="">2022/9/14</td><td class="top center" style="">三</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上4</td><td class="top center" style="">2022/9/20</td><td class="top center" style="">二</td><td class="top center" style="width: 20px;">遲</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上6</td><td class="top center" style="">2022/10/3</td><td class="top center" style="">一</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上6</td><td class="top center" style="">2022/10/4</td><td class="top center" style="">二</td><td class="top center" style="width: 20px;">缺</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上7</td><td class="top center" style="">2022/10/14</td><td class="top center" style="">五</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;">事</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上9</td><td class="top center" style="">2022/10/27</td><td class="top center" style="">四</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td></tr>
        <tr><td class="top center" style="">上16</td><td class="top center" style="">2022/12/14</td><td class="top center" style="">三</td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;"></td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 20px;">公</td><td class="top center" style="width: 2 """

soup = BeautifulSoup(html_content, "html.parser")

data = []

# find all 'tr' elements in the table
rows = soup.find('table', class_='padding2 spacing0').find_all('tr')[1:]  # exclude the header row

for row in rows:
    cells = row.find_all('td')
    date = cells[1].get_text()
    record = [cell.get_text() for cell in cells[3:]]  # start from '早'
    
    attendance = {
        '曠課': record.count('缺'),
        '公假': record.count('公'),
        '請假': record.count('事'),
    }
    
    data.append({
        '日期': date,
        '出勤情況': attendance,
    })

# convert data to JSON
json_data = json.dumps(data, ensure_ascii=False, indent=4)

print(json_data)
