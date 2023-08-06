from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from keras.utils import img_to_array
from keras.utils import load_img
from keras.models import load_model
from PIL import Image
from io import BytesIO
import requests
from urllib.parse import unquote
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
import cv2
import time
import json
import os
from shinherpro import vfcModel
from shinherpro import chormeDriver
import sys


###################################################
# V 1.6.4 By Yihuan Studio --> 2023/5/21/05:09:19

#############################################
#  vfcCode AI model 5.1  x4307 picture
##  image enhancement algorithm V1 By Sam

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

def urlGet():
    return "https://sai.tyai.tyc.edu.tw/online/"

def score_tolist(new_page_source):
    
    html = new_page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 提取考試科目成績
    subject_scores = []
    rows = soup.select('table.t02 tr.row')
    for row in rows:
        subject = row.select_one('td.top').text.strip()
        score_elements = row.select('td.top.right span')
        if len(score_elements) >= 2:
            user_score = score_elements[0].text.strip()
            class_average = score_elements[1].text.strip()
            subject_scores.append({'考試科目': subject, '個人成績': user_score, '全班平均': class_average})

    # 提取總分、平均分數、排名和科別排名
    total_score = soup.select_one('table.scoreTable-inline td.score').text.strip()

    average_score_elements = soup.select('table.scoreTable-inline td.score')
    average_score = average_score_elements[1].text.strip() if len(average_score_elements) >= 3 else "N/A"

    ranking_elements = soup.select('table.scoreTable-inline td.score')
    ranking = ranking_elements[2].text.strip() if len(ranking_elements) >= 3 else "N/A"
    department_ranking = ranking_elements[3].text.strip() if len(ranking_elements) >= 4 else "N/A"

    # 建立包含所有資訊的字典
    result = {
        'code': 0,
        '考試標題': soup.select_one('.center.pt-2 .bluetext').text.strip(),
        '學號': soup.select_one('.center.mobile-text-center .mr-3-ow:nth-of-type(1)').text.strip().replace('學號：', ''),
        '姓名': soup.select_one('.center.mobile-text-center .mr-3-ow:nth-of-type(2)').text.strip().replace('姓名：', ''),
        '班級': soup.select_one('.center.mobile-text-center .mr-3-ow:nth-of-type(3)').text.strip().replace('班級：', ''),
        '考試科目成績': subject_scores,
        '總分': total_score,
        '平均': average_score,
        '排名': ranking,
        '科別排名': department_ranking
    }

    return result

def logGenerate(start_time,result,vfcTry,vfcTryList):
    end_time = time.time()
    execution_time = end_time - start_time

    new_log = [
    {
        'runTime': execution_time,
        'VfcTry': vfcTry,
        'vfcTryList': vfcTryList
    }
    ]

    result['log'] = new_log
    return result

def login(username, password, driver, model,LowConfidence=85,stepPrint=False):
    
    try:
        if stepPrint == False :
            sys.stdout = open(os.devnull, 'w')

        start_time = time.time()
        while True:
            allConfidence = 0
            vfcTry = 1
            vfcTryList = []

            while allConfidence <= LowConfidence :
                vfc = ""
                findImgCount = 0
                while(True):
                    findImgCount = findImgCount + 1
                    try:
                        imgvcode = driver.find_element(By.XPATH, '//img[@id="imgvcode"]')
                        break
                    except:
                        if findImgCount <= 3 :
                            driver.refresh()
                        else:
                            return {"code":1,'reason':[{'reason':'img[@id="imgvcode can\'t find'}]}

                src = imgvcode.get_attribute('src')
                print('Image source:', src)

                screenshot_path = 'captcha.png'
                driver.save_screenshot(screenshot_path)
                location = imgvcode.location
                size = imgvcode.size
                imgvcode_image = Image.open(screenshot_path)
                imgvcode_image = imgvcode_image.crop((location['x'], location['y'], location['x'] + size['width'], location['y'] + size['height']))
                width, height = imgvcode_image.size

                part_width = width // 4
                imgvcode_images = []
                for i in range(4):
                    left = i * part_width
                    right = (i + 1) * part_width
                    part = imgvcode_image.crop((left, 0, right, height))
                    part = vfcModel.vfcCodeFilter(part)
                    part_path = f'captcha_part{i}.png'
                    part.save(part_path)
                    imgvcode_images.append(part_path)

                confidence_threshold_low = 50
                confidence_threshold_medium = 80
                
                confidence = [0, 0, 0, 0]
                count = 0

                for imgvcode_image_path in imgvcode_images:
                    predicted_label, predicted_confidence = vfcModel.predict_image(imgvcode_image_path, imgvcode_image, model)
                    vfc += str(predicted_label)
                    predicted_confidence = predicted_confidence * 100
                    confidence[count] = predicted_confidence
                    count += 1

                    if predicted_confidence < confidence_threshold_low:
                        print(f"{RED}驗證碼: {predicted_label} 置信度: {predicted_confidence} %{RESET}")
                    elif predicted_confidence < confidence_threshold_medium:
                        print(f"{YELLOW}驗證碼: {predicted_label} 置信度: {predicted_confidence} %{RESET}")
                    else:
                        print(f"{GREEN}驗證碼: {predicted_label} 置信度: {predicted_confidence} %{RESET}")

                allConfidence = confidence[0] * confidence[1] * confidence[2] * confidence[3] * 0.000001
                print("\033[33m 驗證碼影像辨識:" + str(vfc) + "  本次準確率:" + str(allConfidence) + " % \033[0m")
                vfcTryList.append((vfc,allConfidence))
                if allConfidence <= LowConfidence :
                    driver.refresh()
            print("\033[36m 驗證碼準確率達標 \033[0m")

            vcode = vfc

            username_element = driver.find_element(By.ID, 'Loginid')
            username_element.send_keys(username)
            password_element = driver.find_element(By.ID, 'LoginPwd')
            password_element.send_keys(password)
            vcode_element = driver.find_element(By.ID, 'vcode')
            vcode_element.send_keys(vcode)
            login_button = driver.find_element(By.ID, 'btnLogin')
            login_button.click()

            try:
                alert = Alert(driver)
                popup_text = alert.text
                print(popup_text)
                alert.dismiss()
                if popup_text == "驗證碼輸入錯誤，請重新輸入。":
                    print("驗證碼輸入錯誤,重新嘗試")
                    vfcTryList.append("vfc wrong")
                    vfcTry = vfcTry + 1
                elif popup_text == "帳號或密碼錯誤,請重新登入!":
                    if stepPrint==False : sys.stdout = sys.__stdout__
                    return {'code':1,'runTime':time.time()-start_time,'result':False}
                else:
                    reason = popup_text
                    if stepPrint==False : sys.stdout = sys.__stdout__
                    return {'code':2,'runTime':time.time()-start_time,'result' : popup_text }
    
            except:
                print(f"{GREEN}密碼正確.{RESET}",end="")
                break

        print(f"{GREEN}驗證碼正確.{RESET}")
        if stepPrint==False : sys.stdout = sys.__stdout__
        return {'code':0,'runTime':time.time()-start_time,'result':True}
    except:
        return {'code':33,'runTime':time.time()-start_time,'reason':'something Wrong'}

def Credit_html_to_json(html):
    html_data = html

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
    return json_data

def getGrades(username, password, driver, model,examname,LowConfidence=85,stepPrint=False):
    
    stepSave = 0
    try:
        if stepPrint == False :
            sys.stdout = open(os.devnull, 'w')
        
        start_time = time.time()
        loginResult = login(username,password,driver,model,LowConfidence,stepPrint)
        
        if stepPrint == False :
            sys.stdout = open(os.devnull, 'w')

        if loginResult['code'] == 1 :
            if stepPrint==False : sys.stdout = sys.__stdout__
            return {'code':1,'runTime':time.time()-start_time,'reason':"帳號或密碼錯誤,請重新登入!"}
        elif loginResult['code'] == 2 :
            if stepPrint==False : sys.stdout = sys.__stdout__
            return {'code':2,'runTime':time.time()-start_time,'reason':loginResult[loginResult]}

        stepSave = 1

        # 進入成績查詢頁面
        # 切換到左測選單
        chormeDriver.switch_frame(False, ["left"], driver)
        student_data_link = driver.find_element(By.ID, 'lnkStudentData')  # 按鈕名稱 "學生 xxx 的資料"
        student_data_link.click()
        # 尋找按鈕名稱 "查詢學生資料"
        button_name = '查詢學生資料'
        button_elements = driver.find_elements(By.CSS_SELECTOR, 'td.SubMenuItem') 
        for button in button_elements:
            button_text = button.text
            if button_text == button_name:
                button.click()
                break
                
        stepSave = 2

        # 切換到框架"right"的框架"right_below"
        chormeDriver.switch_frame(True, ["right", "right_below"], driver)
        # 找到查詢資料按鈕
        button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='window.open']")
        button.click()
        # 切換到框架"right"的框架"right_below"
        chormeDriver.switch_frame(True, ["right", "right_top"], driver)
        # 找到各式成績查詢按鈕
        button = driver.find_element(By.XPATH, "//img[@title='各式成績查詢']")
        button.click()
        # 選擇彈出選擇考試的選單
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[-1])  # 切换到最新打开的窗口
        # 等待下拉框載入完成
        ddl_exam_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ddlExamList')))
        # 創建 Select 對象
        select = Select(ddl_exam_list)
        # 選擇下拉選單中的選項
        select.select_by_visible_text(examname)
        # 切换回原始窗口
        driver.switch_to.window(window_handles[0])
        
        stepSave = 3

        # 成績讀取

        # 切换到右侧框架
        chormeDriver.switch_frame(True, ["right", "right_below"], driver)
        # 獲取新窗口的頁面內容(成績表格)
        new_page_source = driver.page_source
        # 成績表格分析
        JsonGrade = score_tolist(new_page_source)
        loginScess = True

        driver.delete_all_cookies()
        driver.refresh()

        stepSave = 4

        JsonResult = JsonGrade

        if stepPrint==False : sys.stdout = sys.__stdout__
        return JsonResult
    
    except:

        if stepPrint==False : sys.stdout = sys.__stdout__
        return {'code':33,'reason':f'something Wrong ,step {stepSave}'}

def getCredit(username, password, driver, model,LowConfidence=85,stepPrint=False):
    
    try:
        stepSave = 0
        
        if stepPrint == False :
            sys.stdout = open(os.devnull, 'w')
            
        start_time = time.time()
        loginResult = login(username,password,driver,model,LowConfidence,stepPrint)
            
        if stepPrint == False :
            sys.stdout = open(os.devnull, 'w')

        if loginResult['code'] == 1 :
            if stepPrint==False : sys.stdout = sys.__stdout__
            return {'code':1,'runTime':time.time()-start_time,'reason':"帳號或密碼錯誤,請重新登入!"}
        elif loginResult['code'] == 2 :
            if stepPrint==False : sys.stdout = sys.__stdout__
            return {'code':2,'runTime':time.time()-start_time,'reason':loginResult[loginResult]}

        stepSave = 1

        # 進入成績查詢頁面
        # 切換到左測選單
        chormeDriver.switch_frame(False, ["left"], driver)
        student_data_link = driver.find_element(By.ID, 'lnkStudentData')  # 按鈕名稱 "學生 xxx 的資料"
        student_data_link.click()

        button_element = driver.find_element(By.XPATH, '//a[text()="查詢各學期不及格科目"]')
        button_element.click()

        stepSave = 2
        driver.switch_to.default_content()
        chormeDriver.switch_frame(False,['right'],driver)

        new_page_source = driver.page_source

        driver.delete_all_cookies()
        driver.refresh()

        json_result = Credit_html_to_json(new_page_source)

        if stepPrint==False : sys.stdout = sys.__stdout__
        return json_result
    
    except:
        if stepPrint==False : sys.stdout = sys.__stdout__
        return {'code':33,'reason':f'something Wrong ,step {stepSave}'}\
        
def getUserPhoto(username, password, driver, model,LowConfidence=85,stepPrint=False):
    
    stepSave = 0
    
    if stepPrint == False :
        sys.stdout = open(os.devnull, 'w')
        
    start_time = time.time()
    loginResult = login(username,password,driver,model,LowConfidence,stepPrint)
        
    if stepPrint == False :
        sys.stdout = open(os.devnull, 'w')

    if loginResult['code'] == 1 :
        if stepPrint==False : sys.stdout = sys.__stdout__
        return {'code':1,'runTime':time.time()-start_time,'reason':"帳號或密碼錯誤,請重新登入!"}
    elif loginResult['code'] == 2 :
        if stepPrint==False : sys.stdout = sys.__stdout__
        return {'code':2,'runTime':time.time()-start_time,'reason':loginResult[loginResult]}

    stepSave = 1

    # 進入成績查詢頁面
    # 切換到左測選單
    chormeDriver.switch_frame(False, ["left"], driver)
    student_data_link = driver.find_element(By.ID, 'lnkStudentData')  # 按鈕名稱 "學生 xxx 的資料"
    student_data_link.click()
    # 尋找按鈕名稱 "查詢學生資料"
    button_name = '查詢學生資料'
    button_elements = driver.find_elements(By.CSS_SELECTOR, 'td.SubMenuItem') 
    for button in button_elements:
        button_text = button.text
        if button_text == button_name:
            button.click()
            break
                
    stepSave = 2

    # 切換到框架"right"的框架"right_below"
    chormeDriver.switch_frame(True, ["right", "right_below"], driver)
    # 找到查詢資料按鈕
    button = driver.find_element(By.CSS_SELECTOR, "button[onclick*='window.open']")
    button.click()
    # 切換到框架"right"的框架"right_below"
    chormeDriver.switch_frame(True, ["right", "right_top"], driver)
    # 找到各式成績查詢按鈕
    button = driver.find_element(By.XPATH, "//img[@title='查詢基本資料']")
    button.click()
    chormeDriver.switch_frame(True, ["right","right_below"], driver)
    new_page_source = driver.page_source
    #print(new_page_source)
    soup = BeautifulSoup(new_page_source, 'html.parser')

    img_tag = soup.find('img')
    src = img_tag['src']

    url = "https://sai.tyai.tyc.edu.tw/online" + src[2:]
    img_element = driver.find_element(By.CSS_SELECTOR, 'img.lazyLoadImage')

    screenshot_path = 'PhotoSave\\screenshot.png'
    driver.save_screenshot(screenshot_path)

    location = img_element.location
    size = img_element.size

    x = location['x'] + 220
    y = location['y'] + 55
    width = size['width'] - 0
    height = size['height'] - 0

    screenshot = Image.open('PhotoSave\\screenshot.png')
    image_cropped = screenshot.crop((x, y, x + width, y + height))
    imgPath = 'PhotoSave\\UserPhoto' + username + '.png'
    image_cropped.save(imgPath)
    return {'imgPath':imgPath,'url':url}


model = vfcModel.setup("E:\\project\\vfc_AiModel_5.1_VGG16_black.h5")
driver = chormeDriver.setup(urlGet(),True)


result =  getUserPhoto("013333","B123742969",driver,model,stepPrint=True)


print(result)