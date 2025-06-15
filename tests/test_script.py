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
        logging.FileHandler("selenium_test.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建截图目录
screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def take_screenshot(driver, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join("screenshots", f"{name}_{timestamp}.png")
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

def main():
    # 配置Edge选项
    options = Options()
    # 如果需要无头模式，可以启用以下选项
    # options.add_argument('--headless')
    options.add_argument("--start-maximized")  # 最大化窗口以避免元素被遮挡

    # 管理员账号
    admin_username = "root"
    admin_password = "root123"
    
    # 普通用户账号
    user1_username = "1"
    user1_password = "111111"
    user2_username = "2"
    user2_password = "222222"
    user3_username = "3"
    user3_password = "333333"
    user4_username = "4"
    user4_password = "444444"
    user5_username = "5"
    user5_password = "555555"
    user6_username = "6"
    user6_password = "666666"
    user7_username = "7"
    user7_password = "777777"
    user8_username = "8"
    user8_password = "888888"

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
        
        # 3. 执行测试用例
        
        # 设置初始时间为6:00:00并添加第一批充电请求
        logger.info("设置时间为06:00:00并提交第一批充电请求")
        try:
            # 点击6:00:00时间按钮
            time_600_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[1]/button[1]'))
            )
            click_element(driver, time_600_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为06:00:00")
            take_screenshot(driver, "time_set_to_0600")
            time.sleep(2)
            
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_page")
            time.sleep(1)
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置初始时间或查看充电桩状态失败: {e}")
            take_screenshot(driver, "time_set_or_pile_status_failed")
            return
        
        # 为用户1打开新窗口
        logger.info("为用户1打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[1])  # 切换到新窗口
        
        # 登录用户1
        logger.info("登录用户1")
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
            
            username_input.send_keys(user1_username)
            password_input.send_keys(user1_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户1登录")
            time.sleep(2)
            take_screenshot(driver, "user1_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户1登录失败: {e}")
            take_screenshot(driver, "user1_login_failed")
            return
        
        # 用户1申请慢充7度电
        logger.info("用户1申请慢充7度电")
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
            
            # 选择慢充模式
            slow_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[2]/span[1]'))
            )
            click_element(driver, slow_charge)

            time.sleep(1)
            
            # 找到 ant-input-number 的输入框
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('7').perform()
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

            # 刷新充电桩状态
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            
            logger.info("已提交用户1慢充申请")
            take_screenshot(driver, "user1_applied_slow_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户1申请慢充失败: {e}")
            take_screenshot(driver, "user1_apply_charge_failed")
            return
            
        # 为用户2打开新窗口
        logger.info("为用户2打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[2])  # 切换到新窗口
        
        # 登录用户2
        logger.info("登录用户2")
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
            
            username_input.send_keys(user2_username)
            password_input.send_keys(user2_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户2登录")
            time.sleep(2)
            take_screenshot(driver, "user2_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户2登录失败: {e}")
            take_screenshot(driver, "user2_login_failed")
            return
            
        # 用户2申请快充30度电
        logger.info("用户2申请快充30度电")
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
            
            # 选择快充模式
            fast_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[1]/span[1]'))
            )
            click_element(driver, fast_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('30').perform()
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
            
            logger.info("已提交用户2快充申请")
            take_screenshot(driver, "user2_applied_fast_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户2申请快充失败: {e}")
            take_screenshot(driver, "user2_apply_charge_failed")
            return
        
        # 切回管理员界面检查充电状态
        driver.switch_to.window(driver.window_handles[0])
        logger.info("切回管理员界面刷新充电桩状态")
        try:
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "admin_refreshed_pile_status")
            
            # 设置时间加速
            logger.info("设置时间加速")
            # 切换回时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近6:30
            logger.info("等待时间接近6:30")
            time.sleep(15)  # 假设60倍速下，15秒实际时间约为15分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set")
            time.sleep(1)
            
            # 设置时间到6:30:00
            logger.info("设置时间为06:30:00")
            # 点击6:30:00时间按钮
            time_630_button = wait.until(
                EC.element_to_be_clickable((By.XPATH,'//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[1]/button[2]'))
            )
            click_element(driver, time_630_button)
            time.sleep(1)
            
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为06:30:00")
            take_screenshot(driver, "time_set_to_0630")
            time.sleep(2)
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_0700")
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"刷新充电桩状态或设置时间失败: {e}")
            take_screenshot(driver, "admin_refresh_or_time_set_failed")
            return
        
        # 为用户3打开新窗口
        logger.info("为用户3打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[3])  # 切换到新窗口
        
        # 登录用户3
        logger.info("登录用户3")
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
            
            username_input.send_keys(user3_username)
            password_input.send_keys(user3_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户3登录")
            time.sleep(2)
            take_screenshot(driver, "user3_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户3登录失败: {e}")
            take_screenshot(driver, "user3_login_failed")
            return
            
        # 用户3申请慢充28度电
        logger.info("用户3申请慢充28度电")
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
            
            # 选择慢充模式
            slow_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[2]/span[1]'))
            )
            click_element(driver, slow_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('28').perform()
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
            
            logger.info("已提交用户3慢充申请")
            take_screenshot(driver, "user3_applied_slow_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户3申请慢充失败: {e}")
            take_screenshot(driver, "user3_apply_charge_failed")
            return
        
        # 为用户4打开新窗口
        logger.info("为用户4打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[4])  # 切换到新窗口
        
        # 登录用户4
        logger.info("登录用户4")
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
            
            username_input.send_keys(user4_username)
            password_input.send_keys(user4_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户4登录")
            time.sleep(2)
            take_screenshot(driver, "user4_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户4登录失败: {e}")
            take_screenshot(driver, "user4_login_failed")
            return
            
        # 用户4申请快充120度电
        logger.info("用户4申请慢充120度电")
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
            
            # 选择快充模式
            fast_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[1]/span[1]'))
            )
            click_element(driver, fast_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('120').perform()
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
            logger.info("已提交用户4快充申请")
            time.sleep(2)
            take_screenshot(driver, "user4_applied_fast_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户4申请快充失败: {e}")
            take_screenshot(driver, "user4_apply_charge_failed")
            return
        
        # 切回管理员界面设置时间加速
        driver.switch_to.window(driver.window_handles[0])
        logger.info("切回管理员界面设置时间加速")
        try:
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "admin_refreshed_pile_status")

            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近7:00
            logger.info("等待时间接近7:00")
            time.sleep(15)  # 假设60倍速下，15秒实际时间约为15分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set_before_7")
            time.sleep(1)
            
            # 设置时间到7:00:00
            logger.info("设置时间为07:00:00")
            # 点击7:00:00时间按钮
            time_700_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[1]/button[3]'))
            )
            click_element(driver, time_700_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为07:00:00")
            take_screenshot(driver, "time_set_to_0700")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_0700")
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置时间加速或时间到7:00失败: {e}")
            take_screenshot(driver, "time_set_to_0700_failed")
            return
        
        # 为用户5打开新窗口
        logger.info("为用户5打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[5])  # 切换到新窗口        
        # 登录用户5
        logger.info("登录用户5")
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
            
            username_input.send_keys(user5_username)
            password_input.send_keys(user5_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户5登录")
            time.sleep(2)
            take_screenshot(driver, "user5_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户5登录失败: {e}")
            take_screenshot(driver, "user5_login_failed")
            return
        # 用户5申请慢充24.5度电
        logger.info("用户5申请慢充24.5度电")
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
            
            # 选择慢充模式
            slow_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[2]/span[1]'))
            )
            click_element(driver, slow_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('24.5').perform()
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
            
            logger.info("已提交用户5慢充申请")
            take_screenshot(driver, "user5_applied_slow_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户5申请慢充失败: {e}")
            take_screenshot(driver, "user5_apply_charge_failed")
            return
        
        # 为用户6打开新窗口
        logger.info("为用户6打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[6])  # 切换到新窗口
        
        # 登录用户6
        logger.info("登录用户6")
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
            
            username_input.send_keys(user6_username)
            password_input.send_keys(user6_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户6登录")
            time.sleep(2)
            take_screenshot(driver, "user6_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户6登录失败: {e}")
            take_screenshot(driver, "user6_login_failed")
            return
            
        # 用户6申请快充45度电
        logger.info("用户6申请慢充45度电")
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
            
            # 选择快充模式
            fast_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[1]/span[1]'))
            )
            click_element(driver, fast_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('45').perform()
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
            logger.info("已提交用户6快充申请")
            time.sleep(2)
            take_screenshot(driver, "user6_applied_fast_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户6申请快充失败: {e}")
            take_screenshot(driver, "user6_apply_charge_failed")
            return
        

        # 切回管理员界面设置时间加速
        driver.switch_to.window(driver.window_handles[0])
        logger.info("切回管理员界面设置时间加速")
        try:
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "admin_refreshed_pile_status")

            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近8:00
            logger.info("等待时间接近8:00")
            time.sleep(45)  # 假设60倍速下，45秒实际时间约为45分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set_before_8")
            time.sleep(1)
            
            # 设置时间到8:00:00
            logger.info("设置时间为08:00:00")
            # 点击8:00:00时间按钮
            time_800_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[2]/button[1]'))
            )
            click_element(driver, time_800_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为08:00:00")
            take_screenshot(driver, "time_set_to_0800")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_0800")
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置时间加速或时间到8:00失败: {e}")
            take_screenshot(driver, "time_set_to_0800_failed")
            return
        
        # 为用户7打开新窗口
        logger.info("为用户7打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[7])  # 切换到新窗口        
        # 登录用户7
        logger.info("登录用户7")
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
            
            username_input.send_keys(user7_username)
            password_input.send_keys(user7_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户7登录")
            time.sleep(2)
            take_screenshot(driver, "user7_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户7登录失败: {e}")
            take_screenshot(driver, "user7_login_failed")
            return
        # 用户7申请快充75度电
        logger.info("用户7申请快充75度电")
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
            
            # 选择快充模式
            fast_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[1]/span[1]'))
            )
            click_element(driver, fast_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('75').perform()
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
            
            logger.info("已提交用户7慢充申请")
            take_screenshot(driver, "user7_applied_slow_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户7申请慢充失败: {e}")
            take_screenshot(driver, "user7_apply_charge_failed")
            return
        
        # 切回管理员界面设置时间加速
        driver.switch_to.window(driver.window_handles[0])
        logger.info("切回管理员界面设置时间加速")
        try:
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "admin_refreshed_pile_status")

            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近9:00
            logger.info("等待时间接近9:00")
            time.sleep(45)  # 假设60倍速下，45秒实际时间约为45分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set_before_8")
            time.sleep(1)
            
            # 设置时间到9:00:00
            logger.info("设置时间为09:00:00")
            # 点击9:00:00时间按钮
            time_900_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[2]/button[3]'))
            )
            click_element(driver, time_900_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为09:00:00")
            take_screenshot(driver, "time_set_to_0900")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_0900")
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置时间加速或时间到9:00失败: {e}")
            take_screenshot(driver, "time_set_to_0900_failed")
            return
        
        # 为用户8打开新窗口
        logger.info("为用户8打开新窗口")
        driver.execute_script("window.open('http://localhost:5173/');")
        windows = driver.window_handles
        driver.switch_to.window(windows[8])  # 切换到新窗口        
        # 登录用户8
        logger.info("登录用户8")
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
            
            username_input.send_keys(user8_username)
            password_input.send_keys(user8_password)
            
            submit_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/div/div/form/div[3]/div/div/div/div/button'))
            )
            submit_login.click()
            logger.info("已提交用户8登录")
            time.sleep(2)
            take_screenshot(driver, "user8_logged_in")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户8登录失败: {e}")
            take_screenshot(driver, "user8_login_failed")
            return
        # 用户8申请慢充14度电
        logger.info("用户8申请慢充14度电")
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
            
            # 选择慢充模式
            slow_charge = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="form_item_chargeType"]/label[2]/span[1]'))
            )
            click_element(driver, slow_charge)
            
            time.sleep(1)
            
            # 输入充电量
            charge_amount = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form_item_chargingAmount"]'))
            )
            # 使用 Actions 类来操作输入框
            actions = ActionChains(driver)
            actions.click(charge_amount)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            actions.send_keys('14').perform()
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
            
            logger.info("已提交用户8慢充申请")
            take_screenshot(driver, "user8_applied_slow_charge")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"用户8申请慢充失败: {e}")
            take_screenshot(driver, "user8_apply_charge_failed")
            return

        # 切回管理员界面设置时间加速
        driver.switch_to.window(driver.window_handles[0])
        logger.info("切回管理员界面设置时间加速")
        try:
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "admin_refreshed_pile_status")

            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近9:00
            logger.info("等待时间接近9:00")
            time.sleep(45)  # 假设60倍速下，45秒实际时间约为45分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set_before_8")
            time.sleep(1)
            
            # 设置时间到10:00:00
            logger.info("设置时间为10:00:00")
            # 点击10:00:00时间按钮
            time_1000_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[3]/button[1]'))
            )
            click_element(driver, time_1000_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为10:00:00")
            take_screenshot(driver, "time_set_to_1000")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
            pile_status_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'充电桩状态')]"))
            )
            click_element(driver, pile_status_menu)
            logger.info("已切换到充电桩状态页面")
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            take_screenshot(driver, "pile_status_at_1000")
            time.sleep(2)

            # 设置T2充电桩故障
            t2_fault_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div/div/div/div/div/div/div/table/tbody/tr[4]/td[9]/div/div[2]/button')
            click_element(driver, t2_fault_button)
            time.sleep(2)
            take_screenshot(driver, "t2_pile_set_fault")
            # 提交申请
            logger.info("尝试定位确认按钮")
            
            # 等待并点击确认按钮
            submit_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-modal-content .ant-btn-primary"))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            logger.info("已点击确认按钮")
            time.sleep(5)
            # 点击刷新按钮
            refresh_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'refresh-button')]"))
            )
            click_element(driver, refresh_button)
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置故障失败: {e}")
            take_screenshot(driver, "time_set_fault_failed")
            return
            
        # 设置时间到10:30:00并修复充电桩故障
        logger.info("设置时间为10:30:00并修复充电桩故障")
        # 切回管理员界面设置时间加速
        logger.info("切回管理员界面设置时间加速")
        try:
            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近10:30
            logger.info("等待时间接近10:30")
            time.sleep(15)  # 假设60倍速下，15秒实际时间约为15分钟系统时间
            
            # 取消时间加速，恢复正常速度
            normal_speed_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[1]'))
            )
            click_element(driver, normal_speed_button)
            logger.info("已恢复正常速度")
            take_screenshot(driver, "normal_speed_set_before_7")
            time.sleep(1)
            
            # 设置时间到10:30:00
            logger.info("设置时间为10:30:00")
            # 点击10:30:00时间按钮
            time_1030_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[3]/button[2]'))
            )
            click_element(driver, time_1030_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为10:30:00")
            take_screenshot(driver, "time_set_to_1030")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_1030")
            time.sleep(2)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置时间加速或时间到10:30失败: {e}")
            take_screenshot(driver, "time_set_to_1030_failed")
            return
            
            
        try:
            # 修复T2充电桩
            t2_repair_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div/div/div/div/div/div/div/table/tbody/tr[4]/td[9]/div/div/button')
            click_element(driver, t2_repair_button)
            logger.info("已修复T2充电桩故障")
            time.sleep(2)
            take_screenshot(driver, "t2_pile_repaired")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"修复充电桩故障失败: {e}")
            take_screenshot(driver, "repair_pile_fault_failed")
            return

        
        # 设置时间到11:00:00并修复充电桩故障
        logger.info("设置时间为11:00:00并修复充电桩故障")
        # 切回管理员界面设置时间加速
        logger.info("切回管理员界面设置时间加速")
        try:
            # 切换到时间控制面板
            time_control_menu = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'时间控制面板')]"))
            )
            click_element(driver, time_control_menu)
            time.sleep(1)
            
            # 设置为60倍速
            speedup_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[4]/div[2]/div/button[3]'))
            )
            click_element(driver, speedup_button)
            logger.info("已设置时间加速为60倍速")
            take_screenshot(driver, "time_speedup_set_after_user3")
            time.sleep(5)  # 等待一段时间让时间加速生效
            
            # 等待时间接近11:00
            logger.info("等待时间接近11:00")
            time.sleep(15)  # 假设60倍速下，15秒实际时间约为15分钟系统时间
            
            # 设置时间到11:00:00
            logger.info("设置时间为11:00:00")
            # 点击11:00:00时间按钮
            time_1100_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[2]/div[3]/button[3]'))
            )
            click_element(driver, time_1100_button)
            time.sleep(1)
            
            # 点击设置系统时间按钮
            set_time_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/section/main/div/div/div[6]/div[1]/div[2]/div/div/div/div/button'))
            )
            click_element(driver, set_time_button)
            logger.info("已设置系统时间为11:00:00")
            take_screenshot(driver, "time_set_to_1100")
            time.sleep(2)
            
            # 切换到充电桩状态页面查看状态
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
            logger.info("已切换到充电桩状态页面")
            take_screenshot(driver, "pile_status_at_1100")
            time.sleep(50)
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"设置时间加速或时间到11:00失败: {e}")
            take_screenshot(driver, "time_set_to_1100_failed")
            return
            
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
