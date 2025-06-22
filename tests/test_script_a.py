import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    WebDriverException,
)
import logging
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import time
from selenium.webdriver.common.keys import Keys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("selenium_test_a.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建截图目录
screenshot_dir = "screenshots_a"
os.makedirs(screenshot_dir, exist_ok=True)

def take_screenshot(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")
    try:
        driver.save_screenshot(filepath)
        logger.info(f"截图已保存到: {filepath}")
    except Exception as e:
        logger.error(f"保存截图失败: {e}")

def click_element(driver, element):
    try:
        # 使用Actions类进行点击
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        logger.info("使用Actions类成功点击元素")
    except Exception as e:
        logger.warning(f"使用Actions类点击元素失败: {e}")
        try:
            # 尝试使用JavaScript点击
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)
            logger.info("使用JavaScript成功点击元素")
        except Exception as js_e:
            logger.error(f"使用JavaScript点击元素失败: {js_e}")
            raise

def set_time_and_submit_request(driver, wait, time_str, user_idx, charge_mode, charge_amount):
    """
    设置系统时间并提交充电申请
    :param driver: WebDriver实例
    :param wait: WebDriverWait实例
    :param time_str: 要设置的时间字符串，如"06:00:00"
    :param user_idx: 用户索引，从1开始
    :param charge_mode: 充电模式，"F"表示快充，"T"表示慢充
    :param charge_amount: 充电量，单位为度
    """
    # 切换回管理员界面设置时间
    driver.switch_to.window(driver.window_handles[0])
    logger.info(f"设置时间为 {time_str}")
    
    # 切换到时间控制面板
    time_control_menu = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
    )
    click_element(driver, time_control_menu)
    time.sleep(1)
    
    # 设置自定义时间
    custom_time_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[1]/div/div[2]/div/div/input'))
    )
    # 清除输入框
    custom_time_input.clear()
    # 输入新时间
    custom_time_input.send_keys(time_str)
    
    # 点击设置系统时间按钮
    set_time_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
    )
    click_element(driver, set_time_button)
    logger.info(f"已设置系统时间为 {time_str}")
    take_screenshot(driver, f"time_set_to_{time_str.replace(':', '')}")
    time.sleep(2)
    
    # 切换到用户窗口
    window_idx = user_idx  # 用户窗口索引从1开始
    if window_idx >= len(driver.window_handles):
        # 如果窗口不存在，创建新窗口
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[window_idx])
        
        # 登录用户
        logger.info(f"登录用户V{user_idx}")
        try:
            # 等待页面完全加载
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
            
            # 点击登录按钮
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/button[1]'))
            )
            click_element(driver, login_button)
            
            # 填写登录表单
            username_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/form/div[1]/div/div/div/div/input'))
            )
            password_input = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/main/div/div/form/div[2]/div/div/div/div/span/input'))
            )
            
            username = f"{user_idx}"  # 用户名为数字
            password = f"{user_idx}" * 6  # 密码为6位相同数字
            
            username_input.send_keys(username)
            password_input.send_keys(password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info(f"已提交用户V{user_idx}登录")
            time.sleep(2)
            take_screenshot(driver, f"userV{user_idx}_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户V{user_idx}登录失败: {e}")
            take_screenshot(driver, f"userV{user_idx}_login_failed")
            return
    else:
        # 切换到已存在的窗口
        driver.switch_to.window(driver.window_handles[window_idx])
    
    # 提交充电申请
    logger.info(f"用户V{user_idx}申请{'快充' if charge_mode == 'F' else '慢充'}{charge_amount}度电")
    try:
        # 点击申请充电按钮
        apply_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/section/section/main/div/div/div/div[2]/div/div/div/button'))
        )
        click_element(driver, apply_button)
        time.sleep(1)
        
        # 先选择车辆 - 使用多种方式尝试定位和点击下拉框
        try:
            logger.info("尝试方法1: 使用XPath定位车辆下拉框")
            select_vehicle = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'ant-select-selector')]"))
            )
            click_element(driver, select_vehicle)
        except Exception as e:
            logger.warning(f"方法1失败，尝试方法2: {e}")
            try:
                # 使用JavaScript直接点击
                logger.info("尝试方法2: 使用JavaScript定位车辆下拉框")
                select_vehicle = driver.find_element(By.XPATH, "//div[contains(@class,'ant-select')]")
                driver.execute_script("arguments[0].click();", select_vehicle)
            except Exception as e2:
                logger.warning(f"方法2失败，尝试方法3: {e2}")
                # 使用Tab键聚焦并点击
                logger.info("尝试方法3: 使用Tab键聚焦")
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.TAB)
                time.sleep(0.5)
                body.send_keys(Keys.SPACE)
        
        time.sleep(1)
        
        # 从下拉菜单选择一个车辆
        try:
            select_first_vehicle = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'ant-select-item-option')]"))
            )
            click_element(driver, select_first_vehicle)
        except Exception as e:
            logger.warning(f"选择车辆项失败，尝试另一种方法: {e}")
            # 使用键盘向下箭头和回车键
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.DOWN)
            time.sleep(0.5)
            body.send_keys(Keys.ENTER)
        
        time.sleep(1)
        
        # 选择充电模式
        if charge_mode == 'F':
            # 选择快充模式
            fast_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[1]/span[1]'))
            )
            click_element(driver, fast_charge)
        else:
            # 选择慢充模式
            slow_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[2]/span[1]'))
            )
            click_element(driver, slow_charge)
        
        time.sleep(1)
        
        # 输入充电量
        charge_amount_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
        )
        # 使用 Actions 类来操作输入框
        actions = ActionChains(driver)
        actions.click(charge_amount_input)
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        actions.send_keys(Keys.DELETE).perform()
        actions.send_keys(str(charge_amount)).perform()
        actions.send_keys(Keys.ENTER).perform()
        
        # 提交申请
        logger.info("尝试定位确认按钮")
        
        # 等待并点击确认按钮
        submit_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-modal-content .ant-btn-primary"))
        )
        driver.execute_script("arguments[0].click();", submit_button)
        logger.info("已点击确认按钮")
        time.sleep(5)

        # 刷新页面
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        
        logger.info(f"已提交用户V{user_idx}{'快充' if charge_mode == 'F' else '慢充'}申请: {charge_amount}度")
        take_screenshot(driver, f"userV{user_idx}_applied_{'fast' if charge_mode == 'F' else 'slow'}_charge_{charge_amount}")
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"用户V{user_idx}申请充电失败: {e}")
        take_screenshot(driver, f"userV{user_idx}_apply_charge_failed")
        return

    # 切回管理员界面刷新充电桩状态
    driver.switch_to.window(driver.window_handles[0])
    logger.info("切回管理员界面刷新充电桩状态")
    try:
        # 切换到充电桩状态页面
        pile_status_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
        )
        click_element(driver, pile_status_menu)
        # 点击刷新按钮
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        time.sleep(2)
        logger.info(f"已刷新充电桩状态 - 时间: {time_str}, 用户: V{user_idx}")
        take_screenshot(driver, f"admin_refreshed_pile_status_at_{time_str.replace(':', '')}")
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"刷新充电桩状态失败: {e}")
        take_screenshot(driver, "admin_refresh_pile_status_failed")


def empty_operation(driver, wait, time_sleep):
    # 切换到时间控制面板
    time_control_menu = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
    )
    click_element(driver, time_control_menu)
    # 设置为60倍速
    speedup_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
    )
    click_element(driver, speedup_button)
    logger.info("已设置时间加速为60倍速")
    
    time.sleep(time_sleep)

    # 取消时间加速，恢复正常速度
    normal_speed_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
    )
    click_element(driver, normal_speed_button)
    logger.info("已恢复正常速度")


def main():
    # 配置Edge选项
    options = Options()
    # 如果需要无头模式，可以启用以下选项
    # options.add_argument('--headless')
    options.add_argument("--start-maximized")  # 最大化窗口以避免元素被遮挡

    # 管理员账号
    admin_username = "root"
    admin_password = "root123"

    # 初始化WebDriver
    try:
        driver = webdriver.Edge(options=options)
        logger.info("已启动Edge浏览器实例")
    except WebDriverException as e:
        logger.error(f"无法启动Edge WebDriver: {e}")
        return

    wait = WebDriverWait(driver, 20)  # 增加等待时间至20秒

    try:
        # 1. 打开首页并登录管理员账号
        logger.info("打开首页: http://localhost:5173/")
        driver.get("http://localhost:5173/")
        take_screenshot(driver, "homepage_loaded")

        # 等待页面完全加载
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "container")))
        logger.info("页面容器已加载")

        # 尝试点击登录按钮
        logger.info("尝试点击登录按钮")
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/button[1]'))
        )
        logger.info("找到登录按钮，尝试点击")
        click_element(driver, login_button)
        logger.info("已点击登录按钮")
        take_screenshot(driver, "after_click_login")

        # 填写登录表单
        logger.info("填写管理员登录表单")
        try:
            username_input = driver.find_element(By.XPATH, '//*[@id="app"]/main/div/div/form/div[1]/div/div/div/div/input')
            password_input = driver.find_element(By.XPATH, '//*[@id="app"]/main/div/div/form/div[2]/div/div/div/div/span/input')

            username_input.send_keys(admin_username)
            password_input.send_keys(admin_password)
            logger.info("已填写管理员用户名和密码")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"填写登录表单失败: {e}")
            take_screenshot(driver, "fill_login_form_failed")
            return

        # 提交登录表单
        logger.info("提交登录表单")
        try:
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已点击提交登录表单按钮")
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as e:
            logger.error(f"提交登录表单失败: {e}")
            take_screenshot(driver, "submit_login_failed")
            return

        # 验证登录成功
        logger.info("验证管理员登录是否成功")
        try:
            success_message = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".ant-message-success"))
            )
            assert "登录成功" in success_message.text
            logger.info("管理员登录成功")
            take_screenshot(driver, "admin_login_success")
        except (TimeoutException, NoSuchElementException, AssertionError) as e:
            logger.error(f"管理员登录验证失败: {e}")
            take_screenshot(driver, "admin_login_verification_failed")
            return
        
        # 2. 进入时间控制面板
        logger.info("进入时间控制面板")
        try:
            # 点击左侧菜单中的时间控制面板选项
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            logger.info("已点击时间控制面板菜单")
            take_screenshot(driver, "time_control_panel_clicked")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"进入时间控制面板失败: {e}")
            take_screenshot(driver, "time_control_panel_failed")
            return
        
        # 3. 按照测试用例依次提交充电申请
        
        # 设置初始时间为6:00:00
        # 按照测试用例表格，依次执行操作
        
        # 6:00:00 (A,V1,T,14)
        set_time_and_submit_request(driver, wait, "06:00:00", 1, "T", 14)
        
        # 6:05:00 (A,V2,T,21)
        set_time_and_submit_request(driver, wait, "06:05:00", 2, "T", 21)
        
        # 6:10:00 (A,V3,F,30)
        set_time_and_submit_request(driver, wait, "06:10:00", 3, "F", 30)
        
        # 6:15:00 (A,V4,F,45)
        set_time_and_submit_request(driver, wait, "06:15:00", 4, "F", 45)
        
        # 6:20:00 (A,V5,T,7)
        set_time_and_submit_request(driver, wait, "06:20:00", 5, "T", 7)
        
        # 6:25:00 (A,V6,T,14)
        set_time_and_submit_request(driver, wait, "06:25:00", 6, "T", 14)
        
        # 6:30:00 (A,V7,F,30)
        set_time_and_submit_request(driver, wait, "06:30:00", 7, "F", 30)
        
        # 6:35:00 (A,V8,F,15)
        set_time_and_submit_request(driver, wait, "06:35:00", 8, "F", 15)
        
        # 6:40:00 (A,V9,T,10.5)
        set_time_and_submit_request(driver, wait, "06:40:00", 9, "T", 10.5)
        
        # 6:45:00 (A,V10,F,15)
        set_time_and_submit_request(driver, wait, "06:45:00", 10, "F", 15)
        
        # 6:50:00 (A,V11,T,3.5)
        set_time_and_submit_request(driver, wait, "06:50:00", 11, "T", 3.5)
        
        # 6:55:00 (A,V12,T,5.25)
        set_time_and_submit_request(driver, wait, "06:55:00", 12, "T", 5.25)
        
        # 7:00:00 (A,V13,T,1.75)
        set_time_and_submit_request(driver, wait, "07:00:00", 13, "T", 1.75)
        
        # 7:05:00 (A,V14,F,30)
        set_time_and_submit_request(driver, wait, "07:05:00", 14, "F", 30)
        
        # 7:10:00 (A,V15,T,7)
        set_time_and_submit_request(driver, wait, "07:10:00", 15, "T", 7)
        
        # 7:15:00 (A,V16,F,50)
        set_time_and_submit_request(driver, wait, "07:15:00", 16, "F", 50)
        
        # 7:20:00 (A,V17,F,60)
        set_time_and_submit_request(driver, wait, "07:20:00", 17, "F", 60)
        
        # 7:25:00 (A,V18,T,14)
        set_time_and_submit_request(driver, wait, "07:25:00", 18, "T", 14)
        
        # 7:30:00 (A,V19,T,10.5)
        set_time_and_submit_request(driver, wait, "07:30:00", 19, "T", 10.5)
        
        # 7:35:00 (A,V20,T,14)
        set_time_and_submit_request(driver, wait, "07:35:00", 20, "T", 14)
        
        # 7:40:00 - 无事件
        driver.switch_to.window(driver.window_handles[0])
        logger.info("设置时间为07:40:00")
        # 切换到时间控制面板
        time_control_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
        )
        click_element(driver, time_control_menu)
        time.sleep(1)
        # 设置自定义时间
        custom_time_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[1]/div/div[2]/div/div/input'))
        )
        custom_time_input.clear()
        custom_time_input.send_keys("07:40:00")
        # 点击设置系统时间按钮
        set_time_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
        )
        click_element(driver, set_time_button)
        logger.info("已设置系统时间为07:40:00")
        take_screenshot(driver, "time_set_to_0740")
        
        # 刷新充电桩状态
        pile_status_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
        )
        click_element(driver, pile_status_menu)
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        take_screenshot(driver, "pile_status_at_0740")
        
        # 7:45:00 - 无事件
        driver.switch_to.window(driver.window_handles[0])
        logger.info("设置时间为07:45:00")
        # 切换到时间控制面板
        time_control_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
        )
        click_element(driver, time_control_menu)
        time.sleep(1)
        # 设置自定义时间
        custom_time_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[1]/div/div[2]/div/div/input'))
        )
        custom_time_input.clear()
        custom_time_input.send_keys("07:45:00")
        # 点击设置系统时间按钮
        set_time_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
        )
        click_element(driver, set_time_button)
        logger.info("已设置系统时间为07:45:00")
        take_screenshot(driver, "time_set_to_0745")
        
        # 刷新充电桩状态
        pile_status_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
        )
        click_element(driver, pile_status_menu)
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        take_screenshot(driver, "pile_status_at_0745")

        # 10分钟空闲
        empty_operation(driver, wait, 10)
        
        # 8:00:00 (A,V21,F,60)
        set_time_and_submit_request(driver, wait, "08:00:00", 21, "F", 60)
        
        # 8:10:00 (A,V22,F,45)
        set_time_and_submit_request(driver, wait, "08:10:00", 22, "F", 45)
        
        # 8:15:00 - 无事件
        driver.switch_to.window(driver.window_handles[0])
        logger.info("设置时间为08:15:00")
        # 切换到时间控制面板
        time_control_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
        )
        click_element(driver, time_control_menu)
        time.sleep(1)
        # 设置自定义时间
        custom_time_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[1]/div/div[2]/div/div/input'))
        )
        custom_time_input.clear()
        custom_time_input.send_keys("08:15:00")
        # 点击设置系统时间按钮
        set_time_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
        )
        click_element(driver, set_time_button)
        logger.info("已设置系统时间为08:15:00")
        take_screenshot(driver, "time_set_to_0815")
        
        # 刷新充电桩状态
        pile_status_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
        )
        click_element(driver, pile_status_menu)
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        take_screenshot(driver, "pile_status_at_0815")
        
        # 45分钟空闲
        empty_operation(driver, wait, 45)

        # 9:05:00 - 无事件
        driver.switch_to.window(driver.window_handles[0])
        logger.info("设置时间为09:05:00")
        # 切换到时间控制面板
        time_control_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
        )
        click_element(driver, time_control_menu)
        time.sleep(1)
        # 设置自定义时间
        custom_time_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[1]/div/div[2]/div/div/input'))
        )
        custom_time_input.clear()
        custom_time_input.send_keys("09:05:00")
        # 点击设置系统时间按钮
        set_time_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
        )
        click_element(driver, set_time_button)
        logger.info("已设置系统时间为09:05:00")
        take_screenshot(driver, "time_set_to_0905")
        
        # 刷新充电桩状态
        pile_status_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
        )
        click_element(driver, pile_status_menu)
        refresh_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
        )
        click_element(driver, refresh_button)
        take_screenshot(driver, "pile_status_at_0905")

        # 50分钟空闲
        empty_operation(driver, wait, 50)
        
        # 10:00:00 (A,V23,T,14)
        set_time_and_submit_request(driver, wait, "10:00:00", 23, "T", 14)

        # 测试完成后，恢复系统实时时间
        logger.info("测试完成，恢复系统实时时间")
        try:
            # 切换回时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            
            # 点击恢复实时时间按钮
            reset_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'恢复实时时间')]"))
            )
            click_element(driver, reset_time_button)
            logger.info("已恢复系统实时时间")
            take_screenshot(driver, "time_reset_to_real")
            time.sleep(2)
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"恢复系统实时时间失败: {e}")
            take_screenshot(driver, "reset_real_time_failed")
            
        logger.info("充电桩系统测试完成")
        take_screenshot(driver, "test_completed")
        
    except Exception as e:
        logger.error(f"发生未预料的错误: {e}")
        take_screenshot(driver, "unexpected_error")
    finally:
        logger.info("关闭浏览器")
        driver.quit()

if __name__ == "__main__":
    main()