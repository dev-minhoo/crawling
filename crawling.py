###################################################################################################
import  os
import  sys
import  time
from    datetime import datetime
###################################################################################################
import sqlite3
###################################################################################################
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

###################################################################################################
import zoneUtils

###################################################################################################
g_dateStart         = datetime.now()
g_sBaseDir          = g_dateStart.strftime("%Y_%m_%d") # 오늘 날짜
g_nWaitMaxTime      = 3 # 대기 시간
g_sChromedriverPath = 'C:\\Python\\bin\\chromedriver.exe' # 크롬 드라이버
g_sMainURL  = '' # 접속 url
g_WebBroswer        = None
g_SQLite            = None
g_sVersion          = "1"

###################################################################################################
def initDB(sBaseDir) :
    sDataBase    = os.getcwd() + "\\" + sBaseDir + "\\" + "_Crawling.sqlite3"
    
    # 경로에 해당 DB 있는지 확인 후 없으면 생성
    if not os.path.exists(sBaseDir):
        os.mkdir(sBaseDir)

    # DB 존재 유무 확인 후 없으면 TABLE 생성
    bCreateTable = False
    if not os.path.exists(sDataBase):
        bCreateTable = True

    if  bCreateTable :
        # DB 생성 후
        os.mkdir(sBaseDir)
        oSQLite     = sqlite3.connect(sDataBase)
        cursor = oSQLite.cursor()
        if cursor is None:
            print("DB Create Cursor Error ...")
            oSQLite.close()
            return None

        cursor.execute(
            'CREATE TABLE "CRAWLING_TEST" (' +
                        '"CRAWLING_NO"	INTEGER NOT NULL, ' +  
                        '"CATALOG_PATH"	TEXT NOT NULL, ' + 
                        '"CATALOG"	TEXT NOT NULL, ' +                       
	                    '"COMMENT"	TEXT NOT NULL, ' +
                        '"CREATE_ON"	TIMESTAMP NOT NULL DEFAULT (datetime("now","localtime")), ' +  
                        '"DetailURL"  TEXT NOT NULL)')
        cursor.execute('CREATE INDEX "IDX_CRAWLING_CRAWLING_NO" ON "CRAWLING_TEST" ("CRAWLING_NO")')
        cursor.execute('CREATE INDEX "IDX_CRAWLING_CATALOG" ON "CRAWLING_TEST" ("CATALOG")')
        cursor.execute('CREATE INDEX "IDX_CRAWLING_CATALOG_PATH" ON "CRAWLING_TEST" ("CATALOG_PATH")')
        cursor.execute('CREATE INDEX "IDX_CRAWLING_CREATE_ON" ON "CRAWLING_TEST" ("CREATE_ON")')
        oSQLite.commit()
    else :
        # DB가 생성 되어 있다면 TABLE 생성이 되어 있다는 가정하에 DB 접속
        oSQLite     = sqlite3.connect(sDataBase)
        
    if oSQLite is None:
        print("DB Create Error : " + sDataBase)
        return None

    return oSQLite        

###################################################################################################
def getDBLastPath():
    global  g_SQLite

    ###############################################################################################
    cursor = g_SQLite.cursor()
    if cursor is None:
        print("DB Create Cursor Error ...")
        sys.exit(1)
        g_SQLite.close()

    sSQL = "SELECT CRAWLING_NO, CATALOG_PATH FROM CRAWLING_TEST ORDER BY CRAWLING_NO DESC LIMIT 1;"
    datas = cursor.execute(sSQL)

    sPath = ""
    if datas is not None :
        for row in datas:
            sPath = row[1]

    cursor.close()
    return sPath

###################################################################################################
def isDBCatalogPath(sFindPath):
    global  g_SQLite

    ###############################################################################################
    cursor = g_SQLite.cursor()
    if cursor is None:
        print("DB Create Cursor Error ...")
        sys.exit(1)
        g_SQLite.close()

    sSQL = 'SELECT COUNT(*) FROM CRAWLING_TEST WHERE CATALOG_PATH LIKE("' + sFindPath + '%")'
    datas = cursor.execute(sSQL)

    nCatalogPathCount = 0
    for row in datas:
        nCatalogPathCount = row[0]
        break

    cursor.close()
    return nCatalogPathCount

###################################################################################################
def isDBCatalogCode(sFindCatalogCode):
    global  g_SQLite

    ###############################################################################################
    cursor = g_SQLite.cursor()
    if cursor is None:
        print("DB Create Cursor Error ...")
        sys.exit(1)
        g_SQLite.close()

    sSQL = 'SELECT COUNT(*) FROM CRAWLING_TEST WHERE CatalogCode = "' + sFindCatalogCode + '"'
    datas = cursor.execute(sSQL)

    nCatalogPathCount = 0
    for row in datas:
        nCatalogPathCount = row[0]
        break

    cursor.close()
    return nCatalogPathCount    

###################################################################################################
def insertDBProduct(sCatalogPath, sCatalog, sProduct, nDepth, sProductURL):
    global  g_SQLite, g_sVersion

    ###############################################################################################
    cursor = g_SQLite.cursor()
    if cursor is None:
        print("DB Create Cursor Error ...")
        sys.exit(1)
        g_SQLite.close()

    sSQL = "INSERT INTO CRAWLING_TEST (Version, Depth, CatalogPath, CatalogCode, Code, DetailURL)"\
           "            VALUES (?, ?, ?, ?, ?, ?);"

    cursor.execute(sSQL, (g_sVersion, nDepth, sCatalogPath + sCatalog, sCatalog, sProduct, sProductURL))
    g_SQLite.commit()
    return

###################################################################################################
def isFindCatalogPath(sCatalogPath, sCatalogCode) :
    arPath = sCatalogPath.split("\\")

    for sPath in arPath:
        if sPath == sCatalogCode:
            return True

    return False

###################################################################################################
def getEnumCatalogListPages(driver, nWaitMaxTime, sLastCatalogPath, sURL, sCatalogPath, nDepth, bFindCatalogPath) :
    # 해당 url로 부터 카탈로그 가져오기
    sCatalogCode            = getCatalogCodeFromURL(sURL)

    if isFindCatalogPath(sCatalogPath, sCatalogCode):
        return

    sCurrentCatalogPath     = sCatalogPath + sCatalogCode
    bCurrentFindCatalogPath = True

    # 해당 카탈로그 저장되어 있는지 확인
    if bFindCatalogPath :
        if sLastCatalogPath.find(sCurrentCatalogPath) == 0 :
            bCurrentFindCatalogPath = True
        else :
            if isDBCatalogPath(sCurrentCatalogPath) > 0 :
                return
            bCurrentFindCatalogPath = False
    else :
        bCurrentFindCatalogPath = False
    
    ###############################################################################################
    if not bCurrentFindCatalogPath:
        # 카틸로그 중복저장 확인
        if isDBCatalogCode(sCatalogCode) > 0 :
            return

    ###############################################################################################
    elements = zoneUtils.seleniumLoadPage(driver, nWaitMaxTime, 10, sURL, "li a[href*='controller-page.html?TablePage']")
    
    
    if elements is None:
        # 크로링 데이터가 존재 할때
       appendProducts(driver, nWaitMaxTime, sCatalogCode, sCatalogPath, nDepth + 1)
       return 
    else :
         # 크로링 데이터가 존재하지 않을때 
        insertDBProduct(sCatalogPath, sCatalogCode, "", nDepth, "")

    return 

###################################################################################################
def appendProducts(driver, nWaitMaxTime, sCatalogCode, sCatalogPath, nDepth) :
    elements = zoneUtils.seleniumGetCSSElements(driver, 1, 1, "td[abbr] a")
    if elements is not  None:
        for element in elements:
            sProductURL = element.get_attribute("href")
            sProduct    = getProductCodeFromURL(sProductURL)
            insertDBProduct(sCatalogPath, sCatalogCode, sProduct, nDepth, sProductURL)

    return 

###################################################################################################
def getProductCodeFromURL(sURL) :
    arURL    = sURL.split("?")
    sProduct = "########"
    if len(arURL) > 0 :
        arURL = arURL[0].split("/")
        if len(arURL) >= 1 :
            sProduct = arURL[len(arURL) -1]
    return sProduct

###################################################################################################
def getCatalogCodeFromURL(sURL) :
    arURL = sURL.split("?")
    sCatalog = "########"
    if len(arURL) > 1 :
        arURL = arURL[1].split("=")
        if len(arURL) > 1 :
            sCatalog = arURL[1]
    return sCatalog

###################################################################################################
def initCrawling():
    ###############################################################################################
    global  g_sBaseDir, g_dateStart, g_nWaitMaxTime, g_sChromedriverPath, g_sMainURL 
    global  g_WebBroswer, g_SQLite

    ###############################################################################################
    # Init
    ###############################################################################################
    while 1:
        ###########################################################################################
        # DB 접속
        g_SQLite = initDB(g_sBaseDir)

        # 접속 DB 확인
        if g_SQLite is None:
            break
        # 마지막 데이터 값 path 확인
        sLastPath = getDBLastPath()

        ###########################################################################################
        # 웹 브라우져 접속
        g_WebBroswer = webdriver.Chrome(g_sChromedriverPath)
        if g_WebBroswer is None:
            break

        ###########################################################################################
        # page 내용 가져오기
        elements     = zoneUtils.seleniumLoadPage(g_WebBroswer, g_nWaitMaxTime, 10, g_sMainURL,  "a[id*='cssId값']")
        if elements is None:
            break

        arrCatalogs  = {}
        # 첫page 카타로그 확인
        i=0
        if elements is not  None:
            for element in elements:
                href   = element.get_attribute('href')
                if href.find("controller-page.html?TablePage") > 0 :                   
                    arrCatalogs[i] = href
                    i = i+1

        for catalog in arrCatalogs:
            getEnumCatalogListPages(g_WebBroswer, g_nWaitMaxTime, sLastPath, catalog, "", 0, True)

        break
    ###############################################################################################
    # UnInit
    ###############################################################################################
    if g_SQLite is not None:
        g_SQLite.close()
    if g_WebBroswer is not None:        
        g_WebBroswer.quit()

    ###############################################################################################
    return

###################################################################################################
initCrawling()