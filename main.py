import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import random
opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")

driver = webdriver.Chrome(chrome_options=opts)
f = open("sopr.txt","r")
msg = f.read().strip()
f.close()
req = "Младший разработчик" #"Программист разработчик"

DATA_FOLDER = "contacts"
FILE_CONTACTS = DATA_FOLDER + "\\" + "contacts.csv"
SAVED_CONTACTS = set()

blackList = set()

def hhAuth(login):
    if os.path.exists("cookies.pkl"):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        driver.get("https://hh.ru")
        time.sleep(1)
        #print(cookies)
        for cookie in cookies:            
            driver.add_cookie(cookie)

    driver.get("https://hh.ru/account/login")    
    if not isAuthed():
        inpBlock = driver.find_element_by_class_name("bloko-form-item")
        all_children_by_xpath = inpBlock.find_elements_by_xpath(".//*")
        all_children_by_xpath[0].send_keys(login)
        time.sleep(2)
        driver.find_elements_by_class_name("bloko-button_primary")[-1].click()
        while not isAuthed():
            time.sleep(1)
        pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
    
def isAuthed():
    try:
        cl = driver.find_element_by_class_name("supernova-icon_profile")
        print("Authed")
        return True
    except:
        return False

def openSearch(text="Младший разработчик"):
    driver.get("https://hh.ru/search/vacancy?area=1&fromSearchLine=true&st=searchVacancy&text="+text.replace(" ","+"))

def parseText(text,findStart,findEnd,fromPos=0):
    frm = text.find(findStart,fromPos)
    if frm != -1:
        frm += len(findStart)
    t = text.find(findEnd,frm)
    return text[frm:t]

def addToBlackList(vacID):
    global blackList
    blackList.add(vacID)

def vacIDInBlackList(vacID):
    global blackList
    if vacID in blackList:
        return True
    return False

def addToSavedContacts(vacID):
    global SAVED_CONTACTS
    SAVED_CONTACTS.add(vacID)

def vacIDInSavedContacts(vacID):
    global SAVED_CONTACTS
    if vacID in SAVED_CONTACTS:
        return True
    return False

def getAndSaveContacts(listRequests=[]):
    if os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)
    for request in listRequests:
        openSearch(request)
        blocks = driver.find_elements_by_class_name("vacancy-serp-item")
        for i in range(len(blocks)):
            driver.execute_script("arguments[0].scrollIntoView();", blocks[i])
            btns = blocks[i].find_elements_by_class_name("vacancy-serp-item__control_gt-xs")
            if btns[1].text == "Показать контакты":
                btns[1].click()
            vacancyID = parseText(blocks[i].find_element_by_class_name("vacancy-serp-item__controls-item_response").get_attribute("innerHTML"), "vacancyId=", "&")
            if not vacIDInSavedContacts(vacancyID):
                info = driver.find_element_by_class_name("bloko-drop_fullscreen-on-xs bloko-drop_clickable").text.split("\n")
                name = info[0]
                phone = ""
                contacts = []
                address = info[-1] if len(info) > 1 and "@" not in info[-1] else ""
                for i in range(1, len(info)):
                    if "@" in info[i]:
                        contacts.append(info[i])
                    elif "+" in info[i]:
                        phone = info[i]
                addToSavedContacts(vacancyID)
                time.sleep(1)




def send(msg,resume="Программист-рaзработчик"):
    blocks = driver.find_elements_by_class_name("vacancy-serp-item")
    buttons = driver.find_element_by_class_name("vacancy-serp-item__controls-item_response")
    contacts = driver.find_element_by_class_name("vacancy-serp-item__control_gt-xs")
    FirstLink = driver.current_url
    for i in range(len(blocks)):
        driver.execute_script("arguments[0].scrollIntoView();", blocks[i])
        btns = blocks[i].find_elements_by_class_name("vacancy-serp-item__control_gt-xs")
        name = False
        if btns[1].text == "Показать контакты":
            loaded = False
            btns[1].click()
            while not loaded:
                try:
                    time.sleep(1)
                    nameText = driver.find_element_by_class_name("vacancy-contacts__fio").text.split(" ")            
                    loaded = True
                except:
                    print("Contacts not loaded")                    
                loaded = True                        
            if len(nameText) == 1:
                name = nameText[0]
            elif len(nameText) > 1:
                if len(nameText[1]) > 3 and nameText[1][-3:] in ["вна", "чна", "вич"]:
                    name = nameText[0]
                else:
                    name = nameText[1]

        msgSend = msg
        if name:
            msgSend = msgSend.replace("Уважаемый HR - менеджер",name)
        vacancyID = parseText(blocks[i].find_element_by_class_name("vacancy-serp-item__controls-item_response").get_attribute("innerHTML"),"vacancyId=","&")
        global blackList
        print(vacancyID, blackList)
        if vacIDInBlackList(vacancyID):
            continue
        blocks[i].find_element_by_class_name("vacancy-serp-item__controls-item_response").click()
        time.sleep(1)
        if FirstLink != driver.current_url:
            addToBlackList(vacancyID)
            break
        loaded = False
        while not loaded:
            try:
                time.sleep(1)
                driver.find_element_by_class_name("vacancy-response-popup-body").find_element_by_class_name("bloko-link-switch").click()
                loaded = True
            except:
                try:
                    driver.find_element_by_class_name("bloko-textarea_noresize").click()
                    loaded = True
                except:
                    print("direct not loaded")
        txtBlock = driver.find_element_by_class_name("bloko-textarea_noresize")
        txtBlock.clear()
        txtBlock.send_keys(msgSend)
        resumes = driver.find_element_by_class_name("vacancy-response-popup-body").find_elements_by_class_name("bloko-radio__text")        
        for i in range(len(resumes)):
            if resumes[i].text == resume:
                resumes[i].click()
                break        
        driver.find_element_by_class_name("vacancy-response-popup-body").find_element_by_class_name("bloko-button_primary").click()
        time.sleep(random.random()*1+1.5)
            
def startBot(emailOrPhone,vv, resumeName, sndMsg):
    hhAuth(emailOrPhone)
    while True:
        openSearch(vv)
        send(sndMsg)

#startBot( EMAIL_ON_HH.RU,           VACANCY NAME SEARCH            SELECT RESUME             SOPR
startBot("my_email_on_hh@gmail.com", "Младший разработчик Python", "Программист-рaзработчик", msg)

#driver.quit()
