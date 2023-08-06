import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException,ElementClickInterceptedException,ElementNotInteractableException,StaleElementReferenceException,NoSuchElementException
import time
import random
import datetime
import colorama
import threading
from termcolor import colored
import asyncio

import getpass
import pickle
from cryptography import fernet
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import sys
import platform
from tinydb import TinyDB, Query,where
import traceback
import argparse

db = TinyDB(fr'rem_db.json')
User = Query()

colorama.init()



encryption_key = b'aJMvlGq62kjpx8o1tNwIRxW4CMqWBuvWyFZsa4XBzNU='

encrypt_creds = fernet.Fernet(encryption_key)

class Bot:
    def __init__(self,comment,window,username,password,encrypted,use_hashtags=False,use_target_users=False,logout=False):

        self.use_hashtags=use_hashtags
        self.use_target_users=use_target_users
        self.logout=logout

        self.exit_program = False

        self.block_thread = False

        self.continue_like = True
        self.continue_comment=True

        self.max_likes=1000
        self.max_comments=200

        self.username=username
        self.password=password
        self.encrypted=encrypted

        print(self.encrypted)


        self.liked_today = 0
        self.comment_today = 0
        self.now = datetime.datetime.today()

        liked_=db.search(User[f"{self.username}_date_today"]==str(self.now).split(" ")[0])


        if liked_:
            self.liked_today=liked_[0].get("liked_today")
            self.comment_today=liked_[0].get("comment_today")
            print(colored(f" [   ]{self.liked_today}  Liked today  ---  {self.comment_today} commented on today","blue"))
        else:
            db.update({f"{self.username}_date_today":str(self.now).split(" ")[0], "liked_today": self.liked_today, "comment_today": self.comment_today},User.encrypted==self.encrypted)

        self.tasks=0

        self.main_tasks=0

        if comment=="Y":

            self.comment=True

        else:
            self.comment = False

        self.quit_tasks()

        self.comments=[]

        self.target_usernames=[]

        self.hashtags = []

        settings_ = db.search(User.last_settings == "true")
        components_folder=settings_[0].get("components_path")

        for file in os.listdir(fr"{components_folder}"):
            f_=open(fr"{components_folder}/{file}").readlines()
            for data in f_:
                if file=="hashtags.txt":
                    self.hashtags.append(data.strip())
                if file=="comments.txt":
                    self.comments.append(data.strip())
                if file=="target_accounts.txt":
                    self.target_usernames.append(data.strip())
        print("")
        for k,comm in enumerate(self.comments):
            k = k + 1
            sys.stdout.write(colored(f"\r{datetime.datetime.now()} loading comments [  {k} {comm}   ]  progress [ { k/len(self.comments)*100}% ]","green"))
            sys.stdout.flush()
            time.sleep(0.01)

        for k,hash in enumerate(self.hashtags):
            k = k + 1
            sys.stdout.write(colored(f"\r{datetime.datetime.now()} loading hashtags [   {hash}   ]  progress [ { k/len(self.hashtags)*100}% ]","cyan"))
            sys.stdout.flush()
            time.sleep(0.01)

        for k,target in enumerate(self.target_usernames):
            k=k+1
            sys.stdout.write(colored(f"\r{datetime.datetime.now()} loading target accounts  [ {target} ]  progress [ { k/len(self.target_usernames)*100}% ]","yellow"))
            sys.stdout.flush()
            time.sleep(0.01)

        random.shuffle(self.comments)
        random.shuffle(self.target_usernames)
        random.shuffle(self.hashtags)

        if window=="Y":
            self.stealth=False
        else:
            self.stealth = True

        self.seconds=time.perf_counter()
        self.sleep_=3
        self.status="Starting bot"

        self.options = webdriver.ChromeOptions()
        os_detected=""
        if platform.system() == "Darwin":
            chrome_data=fr"Users/{getpass.getuser()}/Library/Application Support/Google/Chrome/Default"
            os_detected="MAC OS"

        if platform.system()=="Windows":
            chrome_data=fr"C:\Users\{getpass.getuser()}\AppData\Local\Google\Chrome\User Data\Default"

            os_detected="WINDOWS OS"
        if platform.system()=="Linux":
            chrome_data =fr"/home/{getpass.getuser()}/.config/google-chrome/default"
            os_detected="LINUX OS"

        if not os_detected:
            print("Can't detect your operating system")

        else:
            print(colored(f"\n[{datetime.datetime.now()}] {os_detected} Detected ","green"))
            self.options.add_argument(fr"--user-data-dir={chrome_data}")

        self.options.add_argument("--lang=en_US")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation","enable-logging"])

        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--start-maximized")

        prefs = {"credentials_enable_service": False,
                 "profile.password_manager_enabled": False,
                 "profile.default_content_setting_values.notifications": 2}

        self.options.add_experimental_option("prefs", prefs)

        if self.stealth:
            print(colored("\nbrowser window mode disabled", "green"))
            # self.options.add_argument(
            #     'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36')
            self.options.add_argument("--headless")
        else:
            print(colored("\nbrowser window mode is enabled", "red"))

        chrome_service=Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=chrome_service, options=self.options)

        # Get the screen height using JavaScript
        screen_height = self.driver.execute_script("return window.screen.height")


        self.driver.set_window_size(900,screen_height)

        

        self.action = ActionChains(self.driver)

        def login_thread():
            asyncio.run(self.main_login())

        th=threading.Thread(target=login_thread)
        th.start()
        while True:
            #  check if login thread is running

            if not th.is_alive():
                if self.logout:
                    break
                else:
                    self.block_thread = False
                    asyncio.run(self.main())
                    break

    
    async def login(self,username,password):
        try:
            self.driver.get("https://www.instagram.com/")

            self.sleep_ = random.randrange(1,4)
            self.seconds = time.perf_counter()
            self.status = "Getting instagram login page"

            await asyncio.sleep(self.sleep_)

            username_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
            self.sleep_ = random.randrange(1,5)
            self.seconds = time.perf_counter()
            self.status = "Sending username to login page"
            await asyncio.sleep(self.sleep_)
            username_field.send_keys(username)

            password_field = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.NAME, "password")))
            self.sleep_ = random.randrange(1, 5)
            self.seconds = time.perf_counter()
            self.status = "Sending password to login page"
            await asyncio.sleep(self.sleep_)
            password_field.send_keys(password)

            login_button = WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH,"//*[contains(text(),'Log in')]")))
            self.sleep_ = random.randrange(1, 5)
            self.seconds = time.perf_counter()
            self.status = "Logging in"
            await asyncio.sleep(self.sleep_)
            login_button.click()

            try:
                WebDriverWait(self.driver,5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'check your username')]")))

                print(colored(f"\n\nThe username you entered doesn't belong to an account. Please check your username and try again","red"))

                db.remove(where('credentials') == 'true')

            except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                    StaleElementReferenceException, NoSuchElementException) as e:
                pass

            try:
                WebDriverWait(self.driver,5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'password was incorrect')]")))

                print(colored(f"\n\n Sorry broski, your password was incorrect. Please double-check your password.","red"))
                db.remove(where('credentials') == 'true')

            except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                    StaleElementReferenceException, NoSuchElementException) as e:
                pass

            await self.click_save_creds()

        except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                StaleElementReferenceException, NoSuchElementException) as e:
            pass

        if self.logout:
            await self.logout_my_account()
            self.driver.quit()
            self.exit_program=True
        else:
            await self.my_account()

            self.block_thread=True


    async def logout_my_account(self):
        
        await self.my_account()

        buttons = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='_abl-']")))
        
        self.sleep_ = random.randrange(2, 5)
        self.seconds = time.perf_counter()
        self.status = f"Logging out of {self.username} step 1"
        await asyncio.sleep(self.sleep_)

        
        for element in buttons:

            if "Options" in element.get_attribute("innerHTML"):
        
                element.click()

                break

        self.sleep_ = random.randrange(2, 7)
        self.seconds = time.perf_counter()
        self.status = f"Logging out of {self.username} step 2"
        await asyncio.sleep(self.sleep_)


        
                # Wait for the button to be visible
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Log Out"]')))


        # Click the button
        button.click()
            

        
        
       
    async def my_account(self):

                # Find all elements that match the selector
        wait = WebDriverWait(self.driver, 10)  # Adjust the timeout as needed
        elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.x1n2onr6 a.x1i10hfl")))

        # Desired href value
        desired_href = self.username

        # Iterate over the elements
        for element in elements:
            # Check if the href value matches the desired href
            if desired_href in element.get_attribute("href") :
                # Click on the desired element
                element.click()
               
                break  # Exit the loop if the desired element is found

            else:
                print(element.get_attribute("href"))
        

        self.sleep_ = random.randrange(13, 20)
        self.seconds = time.perf_counter()
        self.status = f"Getting my account ( {self.username} ) info"
        await asyncio.sleep(self.sleep_)
        

        # Find all elements with the same class
        # Wait for the elements to be present
        wait = WebDriverWait(self.driver, 10)
        elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.x1i10hfl')))

        # Iterate over the elements and find the follower count
        for element in elements:
            if "followers" in element.text:
                follower_count = element.text.split(" ")[0]

            elif "following" in element.text:
                following_count = element.text.split(" ")[0]


        print(colored(f"\n {self.username}   [ {follower_count} followers ] [ {following_count} following ]","green"))

        print(" ")

       


    async def target_users_task(self):
        self.ran_targets = False

        while True:
            if self.use_target_users:
                self.driver.execute_script("window.open('https://www.instagram.com/', 'user_window')")
                for user in self.target_usernames:
                    await self.user_(user)
                
                self.driver.switch_to.window('user_window')
                self.driver.close()
                self.ran_targets=True

            else:
                break


    async def update_database(self):
                # Assuming this code is inside a class method
        username = self.username

        # Get today's date
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        # Check if the user's data exists in the database
        user_data = db.get(User.encrypted == self.encrypted)

        # Check if today's date exists as a key in user_data

        if f"{username}_date_today" in user_data:
            # Update the existing dictionary with the new data
            user_data[f"{username}_date_today"] = str(datetime.datetime.now()).split(" ")[0]
            user_data["liked_today"] = self.liked_today
            user_data["comment_today"] = self.comment_today
        else:
            # Create a new dictionary for today's date and assign the new data
            user_data= {
                f"{username}_date_today": str(datetime.datetime.now()).split(" ")[0],
                "liked_today": self.liked_today,
                "comment_today": self.comment_today
            }

        # Update the database with the modified user_data
        db.update(user_data, User.encrypted == self.encrypted)
       



    async def target_hashtags_task(self):
        while True:
            if self.use_hashtags:
                for hashtag in self.hashtags:
                    await self.main_window(f"{hashtag}")

            elif (not self.use_hashtags and not self.use_target_users) or self.ran_targets:
                self.exit_program = True
                self.driver.quit()
                exit()

    async def click_save_creds(self):

        save_button = WebDriverWait(self.driver, 200).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Not Now')]")))
        self.sleep_ = random.randrange(1, 5)
        self.seconds = time.perf_counter()
        self.status = "Getting pop up window"
        await asyncio.sleep(self.sleep_)
        save_button.click()


    
    async def user_(self, username):

        self.driver.switch_to.window('user_window')

        await self.search(username,1,False)

        self.driver.switch_to.window('user_window')

        try:

            posts = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'posts')]")))

            self.sleep_ = random.randrange(5,15)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} posts count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            posts_count = posts.text

            followers = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'followers')]")))

            self.sleep_ = random.randrange(5,15)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} followers count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            followers_count = followers.text

            following = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'following')]")))

            self.sleep_ = random.randrange(1, 5)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} following count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            following_count = following.text

            print(f"\n {username} {posts_count} {followers_count} {following_count}")

            last_scroll = 0
            get_total_posts = 8

            for row in range(0, get_total_posts):
                post_clicked = False
               
                print("")
                try:

                    
                    wait = WebDriverWait(self.driver, 50)
                    post = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_aabd')))

                     # Scroll the page to the element using JavaScript
                    self.driver.execute_script("arguments[0].scrollIntoView();", post[row])

                    post[row].click()
                    
                    self.sleep_ = random.randrange(5,20)
                    self.seconds = time.perf_counter()

                    self.status = f" {str(datetime.datetime.now())}  Getting post [{row}] [ {username} ] post"

                    await asyncio.sleep(self.sleep_)
                    self.driver.switch_to.window('user_window')
                   

                    post_clicked = True
                    
                                            # Find all elements with the class name
                    post_buttons = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='_abl-']")))
                    
                    for element in post_buttons:

                        if "Unlike" in element.get_attribute("innerHTML") or "Like" in element.get_attribute("innerHTML"):
                

                            check_like=element

                            break




                    if not "Unlike" in str(check_like.get_attribute("innerHTML")):
                        print(check_like.text)

                        check_like.click()

                        self.sleep_ = random.randrange(50,62)
                        self.seconds = time.perf_counter()
                        percentage_progress = get_total_posts - 1
                        self.status = f"[ {datetime.datetime.now()} ]   progress {row} -- {percentage_progress} {round(row / percentage_progress * 100, 3)}%  {username} posts liked "

                        self.liked_today += 1
                        
                        await self.update_database()

                        await asyncio.sleep(self.sleep_)

                        self.driver.switch_to.window('user_window')
                        print(" ")

                        if self.comment:
                            try:
                                                                # Find the button using its comment and title
                                for element in post_buttons:

                                    if "Comment" in element.get_attribute("innerHTML") :
                                
                                        comment_button=element

                                        break

                                # Perform the desired action on the element
                                comment_button.click()


                                comment_field = WebDriverWait(self.driver, 20).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, 'textarea[aria-label="Add a comment…"]')))

                                comment_field.send_keys(self.comments[random.randrange(len(self.comments))])

                                time.sleep(random.randrange(1, 4))

                                comment_field.send_keys(Keys.ENTER)

                                self.sleep_ = random.randrange(40,62)
                                self.seconds = time.perf_counter()

                                self.status = f" [ {str(datetime.datetime.now())} ] posted comment on [ {username} ] post"
                                self.tasks += 1

                                self.comment_today += 1
                                
                                
                                await self.update_database()

                                await asyncio.sleep(self.sleep_)

                                self.driver.switch_to.window('user_window')

                            except (
                            TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                            StaleElementReferenceException, NoSuchElementException) as e:
                                print(e)

                    else:
                        self.sleep_ = random.randrange(45,50)
                        self.seconds = time.perf_counter()
                        percentage_progress = get_total_posts - 1
                        self.status = f"[ {datetime.datetime.now()} ] {round(row / percentage_progress * 100, 3)}% you've liked this {username} post before "

                        await asyncio.sleep(self.sleep_)

                        self.driver.switch_to.window('user_window')

                    close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                    close.click()

                    post_clicked = False

                except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                        StaleElementReferenceException, NoSuchElementException) as e:
                    
                    traceback.print_exc()

                    if post_clicked:
                        close = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                        close.click()

                        post_clicked = False

                   

                if self.tasks >= 20:
                    self.sleep_bot()
                    self.tasks = 0
                    print(colored(
                        f" \n [   ]{self.liked_today}  Liked today  ---  {self.comment_today} commented on today",
                        "blue"))

                
                print("")

            print(f"Finished interacting with {username} recent posts")

        except Exception as e:
            traceback.print_exc()
            try:
                close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                close.click()

                print("closed pre opened post")

            except Exception as e:
                pass
            
            posts = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'posts')]")))

            self.sleep_ = random.randrange(5,15)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} posts count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            posts_count = posts.text

            followers = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'followers')]")))

            self.sleep_ = random.randrange(5,15)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} followers count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            followers_count = followers.text

            following = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'following')]")))

            self.sleep_ = random.randrange(1, 5)
            self.seconds = time.perf_counter()
            self.status = f"Getting {username} following count "

            await asyncio.sleep(self.sleep_)

            self.driver.switch_to.window('user_window')

            following_count = following.text

            print(f"\n {username} {posts_count} {followers_count} {following_count}")

            last_scroll = 0
            get_total_posts = 8

            for row in range(0, get_total_posts):
                post_clicked = False
               
                print("")
                try:

                    
                    wait = WebDriverWait(self.driver, 50)
                    post = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_aabd')))

                     # Scroll the page to the element using JavaScript
                    self.driver.execute_script("arguments[0].scrollIntoView();", post[row])

                    post[row].click()



                    self.sleep_ = random.randrange(5,20)
                    self.seconds = time.perf_counter()

                    self.status = f" {str(datetime.datetime.now())}  Getting post [{row}] [ {username} ] post"

                    await asyncio.sleep(self.sleep_)
                    self.driver.switch_to.window('user_window')
                   

                    post_clicked = True
                    
                                            # Find all elements with the class name
                    wait = WebDriverWait(self.driver, 50)

                    post_buttons= WebDriverWait(self.driver, 20).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='_abl-']")))

                   
                    for element in post_buttons:

                        if "Unlike" in element.get_attribute("innerHTML") or "Like" in element.get_attribute("innerHTML"):
                    
                            check_like=element

                            break

                   

                    if not "Unlike" in str(check_like.get_attribute("innerHTML")):
                        print(check_like.text)

                        check_like.click()

                        self.sleep_ = random.randrange(50,62)
                        self.seconds = time.perf_counter()
                        percentage_progress = get_total_posts - 1
                        self.status = f"[ {datetime.datetime.now()} ]   progress {row} -- {percentage_progress} {round(row / percentage_progress * 100, 3)}%  {username} posts liked "

                        self.liked_today += 1
                        
                        await self.update_database()

                        await asyncio.sleep(self.sleep_)

                        self.driver.switch_to.window('user_window')
                        print(" ")

                        if self.comment:
                            try:
                                for element in post_buttons:

                                    if "Comment" in element.get_attribute("innerHTML") :
                                
                                        comment_button=element

                                        break

                                # Perform the desired action on the element
                                comment_button.click()


                                comment_field = WebDriverWait(self.driver, 20).until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, 'textarea[aria-label="Add a comment…"]')))

                                comment_field.send_keys(self.comments[random.randrange(len(self.comments))])

                                time.sleep(random.randrange(1, 4))

                                comment_field.send_keys(Keys.ENTER)

                                self.sleep_ = random.randrange(40,62)
                                self.seconds = time.perf_counter()

                                self.status = f" [ {str(datetime.datetime.now())} ] posted comment on [ {username} ] post"
                                self.tasks += 1

                                self.comment_today += 1
                               
                                
                                await self.update_database()

                                await asyncio.sleep(self.sleep_)

                                self.driver.switch_to.window('user_window')

                            except (
                            TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                            StaleElementReferenceException, NoSuchElementException) as e:
                                traceback.print_exc()

                    else:
                        self.sleep_ = random.randrange(45,50)
                        self.seconds = time.perf_counter()
                        percentage_progress = get_total_posts - 1
                        self.status = f"[ {datetime.datetime.now()} ] {round(row / percentage_progress * 100, 3)}% you've liked this {username} post before "

                        await asyncio.sleep(self.sleep_)

                        self.driver.switch_to.window('user_window')

                    close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                    close.click()

                    post_clicked = False

                except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                        StaleElementReferenceException, NoSuchElementException) as e:
                    traceback.print_exc()

                    if post_clicked:
                        close = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                        close.click()

                        post_clicked = False

                    
                if self.tasks >= 20:
                    self.sleep_bot()
                    self.tasks = 0
                    print(colored(
                        f" \n [   ]{self.liked_today}  Liked today  ---  {self.comment_today} commented on today",
                        "blue"))

                
                print("")

            print(f"Finished interacting with {username} recent posts")


    async def main_window(self,search_key):

        win_handle = self.driver.window_handles
        self.driver.switch_to.window(win_handle[0])

        await self.search(search_key,0)

        self.driver.switch_to.window(win_handle[0])

        try:

            hashtags_posts=300

            for row in range(0,hashtags_posts):
            
                
                wait = WebDriverWait(self.driver, 50)  

                post = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_aabd')))

               

                    # Scroll the page to the element using JavaScript
                self.driver.execute_script("arguments[0].scrollIntoView();", post[row])

                post[row].click()


                                    # Wait for the presence of the div element
                wait = WebDriverWait(self.driver, 10)
                div_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._aaqt")))

                # Get the text of the div element
                username = div_element.text


                self.sleep_ = random.randrange(15,25)
                self.seconds = time.perf_counter()

                self.status = f" {str(datetime.datetime.now())}  Getting [ {username} ] post"

                await asyncio.sleep(self.sleep_)
                self.driver.switch_to.window(win_handle[0])

                

                post_buttons = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='_abl-']")))

                

                for element in post_buttons:

                    if "Unlike" in element.get_attribute("innerHTML") or "Like" in element.get_attribute("innerHTML"):
                
                        check_like=element

                        break

                

                if not "Unlike" in str(check_like.get_attribute("innerHTML")):

                    
                    check_like.click()

                    self.liked_today += 1
                    
                    await self.update_database()

                    self.sleep_ = random.randrange(35,65)
                    self.seconds = time.perf_counter()

                    self.status = f" {str(datetime.datetime.now())}  liked [ {username} ] post"

                    await asyncio.sleep(self.sleep_)
                    self.driver.switch_to.window(win_handle[0])
                    print("")

                    if self.comment:
                        try:
                                                        # Find the button using its comment
                                                        # Wait for the element to be clickable
                            for element in post_buttons:

                                if "Comment" in element.get_attribute("innerHTML") :
                            
                                    comment_button=element

                                    break

                            # Perform the desired action on the element
                            comment_button.click()


                            comment_field = WebDriverWait(self.driver, 20).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, 'textarea[aria-label="Add a comment…"]')))

                            comment_field.send_keys(self.comments[random.randrange(len(self.comments))])

                            time.sleep(random.randrange(1, 4))

                            comment_field.send_keys(Keys.ENTER)

                            self.sleep_ = random.randrange(40,62)
                            self.seconds = time.perf_counter()

                            self.status = f" [ {str(datetime.datetime.now())} ] posted comment on [ {username} ] post"
                            self.tasks += 1

                            self.comment_today += 1
                            
                            
                            await self.update_database()

                            await asyncio.sleep(self.sleep_)

                            self.driver.switch_to.window(win_handle[0])

                        except (
                        TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                        StaleElementReferenceException, NoSuchElementException) as e:
                            traceback.print_exc()

                    self.tasks += 1

                else:
                    self.sleep_ = random.randrange(1, 5)
                    self.seconds = time.perf_counter()

                    self.status = f" you've liked {username} post before"
                    print("")

                    await asyncio.sleep(self.sleep_)
                self.driver.switch_to.window(win_handle[0])

                time.sleep(random.randrange(1, 5))

                close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                close.click()

                if self.tasks >= 20:
                    self.sleep_bot()
                    self.tasks=0
                    print(colored(
                        f" \n[   ]{self.liked_today}  Liked today  ---  {self.comment_today} commented on today",
                        "blue"))

        

                if self.main_tasks>=500:
                    self.sleep_bot(timer=random.randrange(2400,3600))
                    self.main_tasks=0

                    print("\n\n")
        except Exception as e:
            traceback.print_exc()
            try:
                close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                close.click()

                print("error occured in main win ")

            except Exception as e:
                pass

            for row in range(0,hashtags_posts):
                print("")
               
            
               
                wait = WebDriverWait(self.driver, 50)  

                post = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_aabd')))

                    # Scroll the page to the element using JavaScript
                self.driver.execute_script("arguments[0].scrollIntoView();", post[row])

                post[row].click()


                                    # Wait for the presence of the div element
                wait = WebDriverWait(self.driver, 10)
                div_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._aaqt")))

                # Get the text of the div element
                username = div_element.text


                self.sleep_ = random.randrange(15,25)
                self.seconds = time.perf_counter()

                self.status = f" {str(datetime.datetime.now())}  Getting [ {username} ] post"

                await asyncio.sleep(self.sleep_)
                self.driver.switch_to.window(win_handle[0])

                


                post_buttons = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[class='_abl-']")))

                

                for element in post_buttons:

                    if "Unlike" in element.get_attribute("innerHTML") or "Like" in element.get_attribute("innerHTML"):
                
                        check_like=element

                        break

                

                if not "Unlike" in str(check_like.get_attribute("innerHTML")):

                    
                    check_like.click()

                    self.liked_today += 1
                    
                    await self.update_database()

                    self.sleep_ = random.randrange(35,65)
                    self.seconds = time.perf_counter()

                    self.status = f" {str(datetime.datetime.now())}  liked [ {username} ] post"

                    await asyncio.sleep(self.sleep_)
                    self.driver.switch_to.window(win_handle[0])
                    print("")

                    if self.comment:
                        try:
                                                         # Find the button using its comment
                                                        # Wait for the element to be clickable
                            for element in post_buttons:

                                if "Comment" in element.get_attribute("innerHTML") :
                            
                                    comment_button=element

                                    break

                            # Perform the desired action on the element
                            comment_button.click()



                            comment_field = WebDriverWait(self.driver, 20).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, 'textarea[aria-label="Add a comment…"]')))

                            comment_field.send_keys(self.comments[random.randrange(len(self.comments))])

                            time.sleep(random.randrange(1, 4))

                            comment_field.send_keys(Keys.ENTER)

                            self.sleep_ = random.randrange(40,62)
                            self.seconds = time.perf_counter()

                            self.status = f" [ {str(datetime.datetime.now())} ] posted comment on [ {username} ] post"
                            self.tasks += 1

                            self.comment_today += 1
                            
                            
                            await self.update_database()

                            await asyncio.sleep(self.sleep_)

                            self.driver.switch_to.window(win_handle[1])

                        except (
                        TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                        StaleElementReferenceException, NoSuchElementException) as e:
                            traceback.print_exc()

                    self.tasks += 1

                else:
                    self.sleep_ = random.randrange(1, 5)
                    self.seconds = time.perf_counter()

                    self.status = f" you've liked {username} post before"
                    print("")

                    await asyncio.sleep(self.sleep_)
                self.driver.switch_to.window(win_handle[0])

                time.sleep(random.randrange(1, 5))

                close = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Close']")))

                close.click()

                if self.tasks >= 20:
                    self.sleep_bot()
                    self.tasks=0
                    print(colored(
                        f" \n[   ]{self.liked_today}  Liked today  ---  {self.comment_today} commented on today",
                        "blue"))

        

                if self.main_tasks>=500:
                    self.sleep_bot(timer=random.randrange(2400,3600))
                    self.main_tasks=0

                    print("\n\n")

    async def search(self,search_key,win_name,hashtag=True):
        
        wait = WebDriverWait(self.driver, 20)

        # Wait until the element with "Search" key is clickable and click on it
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'x1i10hfl') and contains(., 'Search')]")))
    
        
        element.click()

        self.sleep_ = random.randrange(1, 5)
        self.seconds = time.perf_counter()
        self.status = f"searching {search_key}"

        for e in range(self.sleep_):
            e+=1
            sys.stdout.write(f"\r{self.status} [{round(e/self.sleep_*100,4)}]%")
            sys.stdout.flush()
            time.sleep(1)

        send_search = WebDriverWait(self.driver, 50).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            "input[aria-label='Search input']")))
    
        
        print(search_key)

        if "#" not in search_key and hashtag:
            search_key = f"#{search_key}"

        if search_key in send_search.text:
            search_key.clear()

        print(search_key)

        send_search.send_keys(search_key)

        self.sleep_ = random.randrange(13,23)
        self.seconds = time.perf_counter()
        self.status = "sending search keyword"
        for e in range(self.sleep_):
            e+=1
            sys.stdout.write(f"\r{self.status} [{round(e/self.sleep_*100,4)}]%")
            sys.stdout.flush()
            time.sleep(1)

        attempts = 0

        while True:
            try:
                                     
                                # Wait for the elements to be present
                elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, f"//div[@role='none']//span[contains(text(), '{search_key}')]"))
                )

                # Click on the first element
                element=elements[0]
                

                self.sleep_ = random.randrange(1, 5)
                self.seconds = time.perf_counter()
                self.status = f"navigating to {search_key} page"

                for e in range(self.sleep_):
                    e+=1
                    sys.stdout.write(f"\r{self.status} [{round(e/self.sleep_*100,4)}]%")
                    sys.stdout.flush()
                    time.sleep(1)


                if search_key in element.text:
                    print(colored(f"\n{element.text}\n found","yellow"))
                    # Click on the element
                    element.click()

                    time.sleep(random.randrange(4,9))
                    break
                else:
                    attempts+=1

            except (TimeoutException, ElementClickInterceptedException, ElementNotInteractableException,
                    StaleElementReferenceException, NoSuchElementException) as e:
                attempts += 1

            if attempts >= 5:
                print(colored(" \n[  ] Something went wrong","red"))
                break

    def sleep_bot(self, timer=random.randrange(850, 1220), reason=""):
        sleep_time = timer
        lengths = [e for e in range(0, 10)]
        timer = time.perf_counter()
        char = "▓"
        for e in range(sleep_time):
            percentage = e / sleep_time * 100
            current_time = time.perf_counter() - timer
            time_remaining = datetime.timedelta(seconds=sleep_time - current_time)
            if "max liked posts" in reason:
                sleep_mins = "Remaining Time" + str(time_remaining)
                time_remaining = ""
            else:
                sleep_mins = str(time_remaining).split(":")[1] + " mins"
                time_remaining = ""
            
            line = f"[{sleep_mins}] {reason} sleep Timeout started | progress {time_remaining}{char} {round(percentage, 4)}%"
            sys.stdout.write(colored(f"\r{line.ljust(len(line))}", "green"))
            sys.stdout.flush()
            
            char_concatenate = round(percentage / 10) + 1
            char = "▓" * char_concatenate
            
            if len(char) in lengths:
                print("")
                lengths.remove(len(char))
            
            time.sleep(1)

    
    def quit_tasks(self):
        if self.liked_today>=700:
            print(colored(f"\n ⚠ Hey {self.username} you are approaching the maximum limit of 1000 likes per day [ {self.liked_today/self.max_likes*100}% ] used up","red"))

        if self.liked_today>=self.max_likes and self.continue_like:
            print(
                colored(f"\n ⛔ {self.username} you've reached the maximum limit of 1000 likes per day [ {self.liked_today/self.max_likes*100}% ] used up", "red"))
            limit_option=input("would you like to continue liking or enter into sleep mode ? \nenter Q to enter sleep mode or C to continue:")
            remaining_timer = db.search(User[f"{self.username}_freeze_time"]== "true")
            if limit_option.capitalize()=='Q' or remaining_timer:

                if remaining_timer:
                    timer_=remaining_timer[0].get("time_stamp")
                    timer_=datetime.datetime.fromtimestamp(timer_)
                    time_remaining=timer_-datetime.datetime.now()

                    sleep_mins=time_remaining.seconds
                else:
                    sleep_mins = 86400
                    sleep_timer_now=datetime.datetime.now()+datetime.timedelta(seconds=sleep_mins)
                    db.update({f"{self.username}_freeze_time":"true","time_stamp":sleep_timer_now.timestamp()},User.encrypted==self.encrypted)

                self.sleep_bot(timer=sleep_mins,reason="[ max liked posts reached ] sleep mode ")
    

                # Update the values in the database
                db.update({f"{self.username}_freeze_time": "false", "time_stamp": 0}, User.encrypted == self.encrypted)

            if limit_option.capitalize()=='C':
                self.continue_like=False
                pass
        if self.comment_today>=100:
            print(colored(
                f"\n ⚠ Hey {self.username} you are approaching the maximum limit of 200 comments per day [ {self.comment_today /self.max_comments *100} ] used up",
                "blue"))

        if self.comment_today >=self.max_comments and self.continue_comment:
            print(
                colored(
                    f"\n ⛔ {self.username} you've reached the maximum limit of 200 comments per day [ {self.comment_today /self.max_comments * 100} ] used up",
                    "red"))
            limit_option = input(
                "would you like to continue commenting or disable commenting for 24 hours ? \n( disable ) commenting recommended \n enter Q to disable comments or C to continue:")
            if limit_option.capitalize() == 'Q':
                self.comment=False
                print(colored("\nCOMMENTS DISABLED","green"))
            if limit_option.capitalize() == 'C':
                self.continue_comment = False
                print(colored(f"\ncontinue using comments,\n bad idea broski", "red"))
                pass


    
    async def main_login(self):
        # run login thread 
        task1 = asyncio.create_task(self.login(self.username, self.password))
        task2 = asyncio.create_task(self.art())

        await task1
        await task2


    # run rest of code

    async def main(self):
        try:
            task2 = asyncio.create_task(self.art())
            task3 = asyncio.create_task(self.target_users_task())
            task4 = asyncio.create_task(self.target_hashtags_task())
            await task2
            await task3
            await task4
        except Exception as e:
            print(f"An error occurred: {e}")




    async def art(self):
        self.spinner = "..::::.."
        color = "yellow"

        while True:
            self.quit_tasks()
            now_ = time.perf_counter() - self.seconds
            mins = datetime.timedelta(seconds=self.sleep_ - now_)
            char_ = ""

            if self.exit_program or self.block_thread:
                break
            for k, char in enumerate(self.spinner):
                try:
                    char_ += char
                    if "liked" in self.status:
                        color="green"

                    if "you've liked" in self.status:
                        color="cyan"
                    if "comment" in self.status:
                        color="yellow"

                    sys.stdout.write(
                        colored(f"\r {char}{char}{char} ", color) + colored(f"{self.status} {str(mins)} ",
                                                                                color) + colored(
                            f"{char_.replace('.', f'{char}')}", color))
                    sys.stdout.flush()

                    await asyncio.sleep(0.01)
                except Exception as e:
                    await asyncio.sleep(0.01)



def figlet():
    if platform.system() == "Darwin":
        os_detected = "MAC OS"

    if platform.system() == "Windows":
        os_detected = "WINDOWS OS"
    if platform.system() == "Linux":
        os_detected = "LINUX OS"

    figlet_color = ["cyan", "yellow", "green", "magenta"]
    random.shuffle(figlet_color)
    ascii_ = f'''                          
      
     _____                              
    (, /                                
      / __   _  _/_ _   _   __  _  ___  
  ___/__/ (_/_)_(__(_(_(_/_/ (_(_(_// (_
(__ /                 .-/               
                     (_/                
             ______                     
            (, /    )                   
              /---(  ____/_              {time.ctime()}
           ) / ____)(_) (__             
          (_/ (                         

        '''
    if os_detected == "WINDOWS OS":
        clear_console = "cls"
    else:
        clear_console = "clear"

    for e in range(20):
        if e == 19:
            for k in range(6):
                print(colored(ascii_[::-1], "green"))
                time.sleep(0.002)
                os.system(clear_console)
                print(colored(ascii_, "green"))
                os.system(clear_console)
                if k == 5:
                    print(colored(ascii_, f"{figlet_color[0]}"))
        elif 19 > e > 0:
            e = 19 - e
            print(colored(ascii_[::-e], "yellow"))
            time.sleep(0.002)
            os.system(clear_console)


    
def logout_user(comment,window,run_hashtags,run_target_accounts,logout):
    encrypt_creds = fernet.Fernet(encryption_key)
    credentials = db.search(User.credentials == 'true')
    if credentials:
        # print(credentials)
        encrypted_creds=credentials[0].get("encrypted")

        decrypt_credentials=credentials[0].get("encrypted").encode()

        encrypted = encrypt_creds.decrypt(decrypt_credentials)
        decrypt_pickle2 = pickle.loads(encrypted)
        username = decrypt_pickle2.get("username", "specify a username")
        password = decrypt_pickle2.get("password", "specify a password")

        Bot(comment, window,username,password,encrypted_creds, use_hashtags=run_hashtags, use_target_users=run_target_accounts, logout=logout)

        decrypt_credentials = credentials[0].get("encrypted").encode()

        decrypt_cryptography = encrypt_creds.decrypt(decrypt_credentials)
        decrypt_pickle2 = pickle.loads(decrypt_cryptography)
        username = decrypt_pickle2.get("username", "specify a username")

        db.remove(where("credentials") == 'true')
       
        print(colored(f"\nLogged out {username} and deleted all settings","green"))
        exit()
    else:
        print(colored("No logged in users ","cyan"))
        print("\nlogin")



def user():
    
    credentials = db.search(User.credentials == 'true')
    if credentials:
        decrypt_credentials = credentials[0].get("encrypted").encode()

        decrypt_cryptography = encrypt_creds.decrypt(decrypt_credentials)
        decrypt_pickle2 = pickle.loads(decrypt_cryptography)
        username = decrypt_pickle2.get("username", "specify a username")
        return username


def start():
    figlet()
    settings=db.search(User.last_settings=="true")

    encrypt_creds = fernet.Fernet(encryption_key)


    if settings:
        settings[0].pop("last_settings")
        print(colored(settings[0],"green"))
        if settings[0].get("dont_ask")=="Y":
            print(colored(f"\nStarting .... \n\nTo logout of {user()} run the following command and reset your settings \n\npython3 -m natalify -logout","cyan"))
            run_target_accounts = settings[0].get("run_target_accounts")
            run_hashtags = settings[0].get("run_hashtags")
            comment = settings[0].get("comment")
            window = settings[0].get("window")
            components_path = settings[0].get("components_path")

            credentials=db.search(User.credentials == 'true')

            if credentials:
                # print(credentials)
                decrypt_credentials=credentials[0].get("encrypted").encode()

                encrypted = encrypt_creds.decrypt(decrypt_credentials)
                decrypt_pickle2 = pickle.loads(encrypted)
                username = decrypt_pickle2.get("username", "specify a username")
                password = decrypt_pickle2.get("password", "specify a password")
            time.sleep(5)
        else:
            previous_setting=input(colored("\nThese are your previous settings ,\ntype E for edit or Y to proceed with previous settings \n \nwould you like to proceed Y/E:","yellow"))

            if previous_setting.capitalize()=="Y":

                run_target_accounts=settings[0].get("run_target_accounts")
                run_hashtags=settings[0].get("run_hashtags")
                comment=settings[0].get("comment")
                window=settings[0].get("window")
                components_path = settings[0].get("components_path")

                credentials=db.search(User.credentials == 'true')

                if credentials:
                    # print(credentials)
                    encrypted_creds=credentials[0].get("encrypted")

                    decrypt_credentials=credentials[0].get("encrypted").encode()

                    encrypted = encrypt_creds.decrypt(decrypt_credentials)
                    decrypt_pickle2 = pickle.loads(encrypted)
                    username = decrypt_pickle2.get("username", "specify a username")
                    password = decrypt_pickle2.get("password", "specify a password")

                save = input(r"Don't ask again Y\N:").capitalize()
                if save=="Y":

                                        # Update the values in the database
                    db.update(
                        {"last_settings": "true", "components_path": components_path,
                        "run_target_accounts": run_target_accounts, "run_hashtags": run_hashtags,
                        "comment": comment, "dont_ask": save, "window": window},
                        User.encrypted == encrypted_creds
                    )

                    print(colored(
                        f"\nStarting .... \n\nTo logout of {user()} you can always run the following command and reset your settings\n\npython3 -m natalify -logout","cyan"))

            else:

                print(colored("\nEdit your settings","cyan"))
                components_path=input(r"Enter your components folder path:")
                 # Assuming filePath contains the file path with backslashes
                components_path = components_path.replace('\\', '/') if platform.system() == 'Darwin' else components_path

                run_target_accounts = input(r"run on Target accounts Y\N:").capitalize()

                run_hashtags = input(r"run on hashtags Y\N:").capitalize()

                print("")

                comment = input(r"Allow commenting Y\N:").capitalize()

                window = input(r"Enable browser window Y\N:").capitalize()
                print("")

                save = input(r"Don't ask again Y\N:").capitalize()

                credentials=db.search(User.credentials == 'true')

                if credentials:
                    # print(credentials)
                    encrypted_creds=credentials[0].get("encrypted")

                    decrypt_credentials=credentials[0].get("encrypted").encode()

                    encrypted = encrypt_creds.decrypt(decrypt_credentials)
                    decrypt_pickle2 = pickle.loads(encrypted)


                    username = decrypt_pickle2.get("username", "specify a username")
                    password = decrypt_pickle2.get("password", "specify a password")

                db.update(
                    {"last_settings": "true","components_path":components_path ,"run_target_accounts": run_target_accounts, "run_hashtags": run_hashtags,
                     "comment": comment,"dont_ask":save,"window": window},
                     User.encrypted==encrypted_creds)

    else:
        if len(sys.argv) >= 2:
            if sys.argv[1] == "-logout":
                print("no logged in users")
                exit()

        components_path = input(r"Enter your components folder path:")
        # Assuming filePath contains the file path with backslashes
        components_path = components_path.replace('\\', '/') if platform.system() == 'Darwin' else components_path

        run_target_accounts = input(r"run on Target accounts Y\N:").capitalize()

        run_hashtags = input(r"run on hashtags Y\N:").capitalize()

        print("")

        comment = input(r"Allow commenting Y\N:").capitalize()

        window = input(r"Enable browser window Y\N:").capitalize()

        encrypt_creds = fernet.Fernet(encryption_key)
    

        
        print(colored(f"[{time.perf_counter()}] no logged in users found in database", "green"))
        print(colored(f"[{time.perf_counter()}] !password may not show on console as you type,hit Enter when done "
                        f"for each field", "cyan"), end="\n")

        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")

        credentials = {"username": username, "password": password}
        pickled_credentials = pickle.dumps(credentials)

        encrypted = encrypt_creds.encrypt(pickled_credentials)

        encrypted_creds=encrypted.decode("utf-8")


    
        db.insert({"last_settings":"true","components_path":components_path,"run_target_accounts":run_target_accounts,"run_hashtags":run_hashtags,"comment":comment,"dont_ask":"N","window":window,"encrypted":encrypted_creds,"credentials":"true"})

    if run_hashtags=="Y":
        run_hashtags=True
    else:
        run_hashtags = False

    if run_target_accounts=="Y":
        run_target_accounts=True
    else:
        run_target_accounts = False

    parser = argparse.ArgumentParser()
    parser.add_argument('-logout', action='store_true', help="Logout from the account")
    args = parser.parse_args()

    if args.logout:
        print(colored("You'll be logged out of your account", "red"))
        logout_user(comment, window, run_hashtags, run_target_accounts, True)
    else:
        Bot(comment,window,username,password,encrypted_creds,use_hashtags=run_hashtags,use_target_users=run_target_accounts)

if __name__=="__main__":
    start()
        