from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.implicitly_wait(.1)
    #maximize browser
    driver.maximize_window()
    #launch URL
    driver.get("https://ab2.gallery/manage")
    input('Hit return when finished with login') # wait for login
    # loginButton = driver.find_element_by_css_selector('body > div > div.main-container > div > div > div.connect-to-wallet > button')
    createButton = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > button')
    createButton.click()
    automatic = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div > div > div.component > div > div > div:nth-child(2) > div > div > div > div > div')
    automatic.click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > form')))
    print('starting...')
    
    form = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > form')
    inputs = form.find_elements_by_class_name('el-input__inner')
    #inputs: Asset Name, Unit Name, Total Supply
    inputs[0].send_keys('nice rocks')
    inputs[1].send_keys('rock.0')
    inputs[2].send_keys('1')
    
    description = form.find_element_by_class_name('el-textarea__inner')
    description.send_keys('some nice rocks I found')
    imagePath = r'/Users/benjamincole/Downloads/IMG_0902.jpg'
    uploadButton = form.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > form > div:nth-child(5) > div > div > div > button')
    uploadFileInput = form.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > form > div:nth-child(5) > div > div > input[type=file]')
    uploadFileInput.send_keys(imagePath)
    termsCheck = form.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > form > div:nth-child(7) > div > label > span.el-checkbox__input > span')
    termsCheck.click()
    continueButton = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(1) > div > div > button.el-button.el-button--primary')
    continueButton.click()
    main_window_handle = driver.current_window_handle
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(2) > div > div.footer > button.el-button.el-button--primary')))
    confirm1 = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(2) > div > div.footer > button.el-button.el-button--primary')
    confirm1.click()
    signin_window_handle = None 
    while not signin_window_handle:
        for handle in driver.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break
    driver.switch_to_window(signin_window_handle) #CDwindow-73A8CA9C85E67F12255665EFC134090C
    #add wait for approve button
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#root > div > div > div > div.fix-in-the-bottom > div.buttons-section > div > div > button.custom-btn.btn.btn-secondary')))
    approveButton = driver.find_element_by_css_selector('#root > div > div > div > div.fix-in-the-bottom > div.buttons-section > div > div > button.custom-btn.btn.btn-secondary')
    approveButton.click()
    
    #wait for password input
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.form-group > div.input-group-password.input-group > input')))
    passInput = driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.form-group > div.input-group-password.input-group > input')
    passInput.send_keys('mytestwallet123#')
    siginButton = driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.align-space-between > button.custom-btn.btn.btn-secondary')
    siginButton.click()
    
    driver.switch_to_window(main_window_handle)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(2) > div > div.footer > button.el-button.el-button--primary')))
    time.sleep(.2)
    confirm2 = driver.find_element_by_css_selector('#pane-available > div > div.asa-manager > div:nth-child(1) > div > div > div > div > div.el-dialog__body > div > div:nth-child(2) > div > div.footer > button.el-button.el-button--primary')
    confirm2.click()
    signin_window_handle = None 
    while not signin_window_handle:
        for handle in driver.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break
    driver.switch_to_window(signin_window_handle)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#root > div > div > div > div.fix-in-the-bottom > div.buttons-section > div > div > button.custom-btn.btn.btn-secondary')))
    continueButton = driver.find_element_by_css_selector('#root > div > div > div > div.fix-in-the-bottom > div.buttons-section > div > div > button.custom-btn.btn.btn-secondary')
    continueButton.click()
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.form-group > div.input-group-password.input-group > input')))
    passInput = driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.form-group > div.input-group-password.input-group > input')
    passInput.send_keys('mytestwallet123#')
    driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.modal.fade.show > div > div > div.modal-body > div > div > div > form > div.align-space-between > button.custom-btn.btn.btn-secondary').click()
    driver.switch_to_window(main_window_handle)
    #repeat
    input('done')
if __name__ == '__main__':
    main()