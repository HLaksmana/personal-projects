from selenium import webdriver
import codecs
import os
from webdriver_manager.chrome import ChromeDriverManager
def main():
    chrome_options = webdriver.ChromeOptions()
    adBlock = r'/Users/benjamincole/Library/Application Support/Google/Chrome/Default/Extensions/cjpalhdlnbpafiamejdnhcphjbkeiagm/1.38.6_15'
    chrome_options.add_argument('load-extension=' + adBlock)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.implicitly_wait(.1)
    #maximize browser
    driver.maximize_window()
    #launch URL
    driver.get("https://www.novelhall.com/Martial-Master-16537/4261325.html")
    nextButton = driver.find_element_by_css_selector('#main > div > div > nav > a:nth-child(5)')
    while(nextButton.get_attribute("href")):
        
        #get file path to save page
        title = 'MM_' + driver.find_element_by_xpath('//*[@id="main"]/div/div/article/div[1]/h1').text
        print(title)
        dirname = os.path.dirname(__file__)
        n=os.path.join(dirname,f"MM/{title}.html")
        #open file in write mode with encoding
        f = codecs.open(n, "w", "utf−8")
        #obtain page source
        h = driver.find_element_by_xpath('//*[@id="htmlContent"]').get_attribute('innerHTML')
        #write page source content to file
        f.write(h)
        nextButton.click()
        nextButton = driver.find_element_by_css_selector('#main > div > div > nav > a:nth-child(5)')
        

    #close browser
    driver.quit()
    
if __name__ == '__main__':
    main()