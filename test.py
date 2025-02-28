import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform


def getPreset():
    #key: id, pw, time, link
    with open('setting.txt', 'r', encoding='utf-8') as idpwFile:
        preset_data = {}

        data = idpwFile.readlines()
        for i in data:
            tempdata = i.split(']')
            key = tempdata[0].strip()
            value = tempdata[1].strip()
            
            if value == '':
                preset_data[key] = ''
            else:
                preset_data[key] = value
        idpwFile.close()
    
    
    print('-' * 20)
    print(preset_data)
    print('-' * 20)

    return preset_data


def target_set(target_h, target_m, target_s, itime = time.localtime()):
    target_time_struct = time.struct_time((itime[0], itime[1], itime[2],
                                           target_h, target_m, target_s,
                                           itime[6], itime[7], 0))
    target_time = time.mktime(target_time_struct)
    
    return target_time


def wait_element(_driver, t, element, clickable=False):
    target = WebDriverWait(_driver, t).until(EC.visibility_of_element_located(element))
    if clickable:
        target.click()
    return target


def kakao_login(_driver, _id, _pw):
    print('카카오 로그인')
    wait_element(_driver, 10, (By.ID, "loginout"), clickable=True)
    time.sleep(2)  # 대기하며 로그인 창이 유지되는지 확인
    try:
        wait_element(5, (By.ID, 'label-saveSignedIn'), True)
        _driver.find_element(By.ID, 'loginId--1').send_keys(_id)
        _driver.find_element(By.ID, 'password--2').send_keys(_pw)
        _driver.find_element(By.CLASS_NAME, 'btn_g.highlight.submit').click()
        time.sleep(1)
        try:
            wait_element(_driver, 5, (By.CLASS_NAME, 'desc_login'))
            input('카카오 로그인 인증을 완료 한 후 아무 문자와 함께 엔터: ')
        except:
            print('기존 로그인 정보 입력으로 로그인 시도')
    except:
        print('기존 로그인 정보로 로그인 시도')


def applyform_setting(_driver, presetData):
    time.sleep(3)
    # iframe으로 전환 (반드시 필요)
    # WebDriverWait(_driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
    # 참여하기 버튼
    wait_element(_driver, 5, (By.ID, 'btn_apply_new'), True)

    # 참여 폼 등장까지 대기
    while len(_driver.window_handles) == 1: 
        time.sleep(1)
    _driver.switch_to.default_content()  # iframe에서 빠져나오기
    _driver.switch_to.window(_driver.window_handles[1])

    form_name = wait_element(_driver, 5, (By.ID, 'answer_16019'))
    form_name.send_keys(presetData['name'])
    _driver.find_element(By.ID, 'answer_16020').send_keys(presetData['phonenum'])
    _driver.find_element(By.ID, 'answer_16021').send_keys(presetData['birth'])
    _driver.find_element(By.ID, 'answer_16022').send_keys(presetData['fan_num'])


def apply_form_and_get_result(_driver, _target_t, t_ms):
    #시간 조정 및 참여 버튼 누르기 기능
    apply_button = _driver.find_element(By.ID, 'btnSaveView')
    #시간 조정 대기
    _target_t += (t_ms/1000)
    print('참여 버튼 누르기 대기')
    while (_target_t - time.time() > -.001):
        if _target_t - time.time() > 5: # 5초 이상 남으면
            time.sleep(1)
        else:
            time.sleep(.001)
    apply_button.click()
    try:
        while len(_driver.window_handles) > 1: 
            apply_button.click()
            # time.sleep()
    except:
        pass
    finally:
        print('참여 완료')
        _driver.switch_to.window(_driver.window_handles[0])

    time.sleep(1)
    # iframe으로 전환 (반드시 필요)
    WebDriverWait(_driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
    while True:
        time.sleep(1)
        rows = WebDriverWait(_driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "apply_item"))
        )
        for row in rows:
            # colspan 속성 확인
            colspan = row.get_attribute("colspan")
            if colspan:
                refreshed = False
                break
            else:
                refreshed = True
        if refreshed:
            break
    #참여자 수 체크
    apply_count = _driver.find_element(By.ID, 'apply_count').text

    time_element = _driver.find_element(By.CLASS_NAME, "date")
    datetime_value = time_element.get_attribute("datetime")

    return int(apply_count), int(datetime_value[-2:])


def delete_form(_driver):
    # 참여 내역 버튼
    _driver.find_element(By.CLASS_NAME, 'apply_item').click()
    while len(_driver.window_handles) == 1: 
        time.sleep(1)
    _driver.switch_to.default_content()  # iframe에서 빠져나오기
    _driver.switch_to.window(_driver.window_handles[1])

    wait_element(_driver, 5, (By.ID, 'btnDelApply'), True)
    wait_element(_driver, 5, (By.ID, 'btnMsgOk'), True)

    _driver.switch_to.window(_driver.window_handles[0])

    time.sleep(1)
    # iframe으로 전환 (반드시 필요)
    WebDriverWait(_driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "down")))
    while True:
        time.sleep(1)
        rows = WebDriverWait(_driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "apply_item"))
        )
        for row in rows:
            # colspan 속성 확인
            colspan = row.get_attribute("colspan")
            if colspan:
                refreshed = True
                break
            else:
                refreshed = False
        if refreshed:
            break


############ INIT Selenium ##################
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
print('your OS is ', platform.system())
if platform.system() == 'Windows':
    chrome_options.add_argument('user-data-dir=C:\\user_data\\user')
elif platform.system() == 'Darwin':
    pass # Mac용 유저 데이터 저장 위치 알아내기
driver = webdriver.Chrome(options=chrome_options)
#############################################

presetData = getPreset()

if presetData['link'] == '':
    driver.get("https://cafe.daum.net/IVEstarship")
    input('목표 공방페이지로 이동 후 아무 키나 누르고 엔터: ')
else:
    driver.get(presetData['link'])

time.sleep(5)
# iframe으로 전환 (반드시 필요)
iframe = WebDriverWait(driver, 10).until(
    EC.frame_to_be_available_and_switch_to_it((By.ID, "down"))
)

kakao_login(driver, presetData['id'], presetData['pw'])

#initalize time
itime = time.localtime()
t_time = list(map(int, presetData['target_time'].split(':')))
print(f'target time: {t_time[0]}h: {t_time[1]}m: {t_time[2]}s')
target_timestamp = target_set(t_time[0], t_time[1], t_time[2], itime)

print(time.time())
print(target_timestamp)
print('*'*10, 'target time', '*'*10)
print(time.ctime(target_timestamp))
print('*'*33)

binary_ms = [500, 999]
target_ms = 750
practice_min = itime[4] # 연습용 분

print('Start Practicing. left min: ', (t_time[0] - itime[3]) * 60 + t_time[1] - itime[4])
while ((t_time[0] - itime[3]) * 60 + t_time[1] - itime[4]) > 3: # practice parts
    itime = time.localtime()
    if itime[5] > 50: # 50초 이상 이라면 59초로
        applyform_setting(driver, presetData)
        practice_t = target_set(itime[0], practice_min, 59, itime)
        apply_count, result_sec = apply_form_and_get_result(driver, practice_t)
    else:
        applyform_setting(driver, presetData)
        practice_t = target_set(itime[0], practice_min, itime[5]+5, itime)
        apply_count, result_sec = apply_form_and_get_result(driver, practice_t)
        

    delete_form(driver)
