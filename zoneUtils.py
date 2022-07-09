###################################################################################################
import os
import sys
import time
from stat import S_ISREG, ST_CTIME, ST_MODE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import get  # to make GET request

###################################################################################################
def getDirFileList(sDIR) :
    entries = (os.path.join(sDIR, fn)   for fn in os.listdir(sDIR))
    entries = ((os.stat(path), path)    for path in entries)
    entries = ((stat[ST_CTIME], path)   for stat, path in entries if S_ISREG(stat[ST_MODE]))
    entries = sorted(entries)
    for cdate, path in entries:
        print(time.ctime(cdate), os.path.basename(path))
        
    return entries

###################################################################################################
def seleniumLoadPage(driver, nWaitMaxTime, nMaxTryCount, sURL, sCSS) :
    driver.get(sURL)
    return seleniumGetCSSElements(driver, nWaitMaxTime, nMaxTryCount, sCSS)

###################################################################################################
def seleniumGetCSSElement(driver, nWaitMaxTime, nMaxTryCount, sCSS) :
    nTryCount = 0
    if nMaxTryCount <= 0 :
        nMaxTryCount = 1

    while nTryCount < nMaxTryCount:
        nTryCount = nTryCount + 1
        try:
            WebDriverWait(driver, nWaitMaxTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, sCSS)))
            element = driver.find_element_by_css_selector(sCSS)
        except:
            element = None
        if not element is None:
            break

    return element

###################################################################################################
def seleniumGetCSSElements(driver, nWaitMaxTime, nMaxTryCount, sCSS) :
    nTryCount = 0
    if nMaxTryCount <= 0 :
        nMaxTryCount = 1

    while nTryCount < nMaxTryCount:
        nTryCount = nTryCount + 1
        try:
            WebDriverWait(driver, nWaitMaxTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, sCSS)))
            elements = driver.find_elements_by_css_selector(sCSS)
        except:
            elements = None
        if not elements is None:
            break

    return elements


###################################################################################################
def seleniumGetCSSElementTextValue(driver, nWaitMaxTime, nMaxTryCount, sCSS, sDefVal) :
    elements = seleniumGetCSSElements(driver, nWaitMaxTime, nMaxTryCount, sCSS)
    if elements is None:
        return sDefVal

    sResult = ""
    for element in elements:
        sResult = element.text
        if len(sResult) > 0:
            return sResult
    return sResult

###################################################################################################
def seleniumGetXPathElements(driver, nWaitMaxTime, nMaxTryCount, sXPath) :
    nTryCount = 0
    if nMaxTryCount <= 0 :
        nMaxTryCount = 1

    while nTryCount < nMaxTryCount:
        nTryCount = nTryCount + 1
        try:
            WebDriverWait(driver, nWaitMaxTime).until(EC.presence_of_element_located((By.XPATH, sXPath)))
            elements = driver.find_elements_by_xpath(sXPath)
        except:
            elements = None
        if not elements is None:
            break

    return elements

###################################################################################################
def seleniumGetXPathElement(driver, nWaitMaxTime, nMaxTryCount, sXPath) :
    nTryCount = 0
    if nMaxTryCount <= 0 :
        nMaxTryCount = 1

    while nTryCount < nMaxTryCount:
        nTryCount = nTryCount + 1
        try:
            WebDriverWait(driver, nWaitMaxTime).until(EC.presence_of_element_located((By.XPATH, sXPath)))
            element = driver.find_element_by_xpath(sXPath)
        except:
            element = None
        if not element is None:
            break
        time.sleep(1)

    return element

###################################################################################################
def seleniumGetXPathElementTextValue(driver, nWaitMaxTime, nMaxTryCount, sXPath, sDefVal) :
    element = seleniumGetXPathElement(driver, nWaitMaxTime, nMaxTryCount, sXPath)
    if element is None:
        return sDefVal
  
    return element.text

###################################################################################################
def seleniumGetXPathElementsTextValue(driver, nWaitMaxTime, nMaxTryCount, sXPath, sDefVal) :
    elements = seleniumGetXPathElements(driver, nWaitMaxTime, nMaxTryCount, sXPath)
    if elements is None:
        return sDefVal

    sResult = ""
    for element in elements:
        sResult = element.text
        if len(sResult) > 0:
            return sResult
    return sResult

###################################################################################################
def downloadFile(url, file_name):
    headers = {'User-Agent': 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    with open(file_name, "wb") as file:   # open in binary mode
        response = get(url,headers=headers)               # get request
        file.write(response.content)      # write to file
    return 0
