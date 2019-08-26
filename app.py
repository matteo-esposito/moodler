# -*- coding: UTF-8 -*-
import wget
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import getpass
from bs4 import BeautifulSoup
import os
import time
import requests
import sys

moodle_page = 'https://moodle.concordia.ca/moodle/login/index.php'
course_page = 'https://moodle.concordia.ca/moodle/course/view.php?id=112046' # COMP352

class Moodler:
    def __init__(self, username, password):
        """Moodler. Your automated Moodle pdf downloader.

        Arguments:
            username {string} -- Moodle username
            password {string} -- Moodle password
        """
        self.username = username
        self.password = password
        opts = webdriver.FirefoxOptions()
        opts.headless = False
        self.bot = webdriver.Firefox(options=opts)

    def login(self):
        """Uses username and password to login to the moodle.
        """
        # Goto site
        bot = self.bot
        bot.get(moodle_page)

        # Locate and populate user and pwd fields.
        user_field = bot.find_element_by_xpath(
                "//input[@id='username'][@name='username'][@type='text']")
        pwd_field = bot.find_element_by_xpath(
                "//input[@id='password'][@name='password'][@type='password']")
        user_field.clear()
        user_field.send_keys(self.username)
        pwd_field.clear()
        pwd_field.send_keys(self.password)
        pwd_field.send_keys(Keys.RETURN)
        time.sleep(4)

        if bot.current_url == 'https://moodle.concordia.ca/moodle/':
            pass
        else:
            print('Login failed.')
            print('Re-run the program.')
            sys.exit(1)
        print("✓ Logged in successfully.")

    def goto_class(self):
        bot = self.bot
        bot.find_element_by_xpath('//a[@href="' + course_page + '"]').click()
        time.sleep(3.5)
        print("✓ Got to course page.")

    def get_pdflist(self):
        bot = self.bot

        # Scrape
        soup = BeautifulSoup(bot.page_source, features="lxml")
        divs = soup.findAll('div', attrs={'class' : 'activityinstance'})
        pdf_links = []
        for div in divs:
            pdf_links.append(div.find('a')['href'])

        # Keep pdf links
        cleaned_links = [x for x in pdf_links if x[:48] == 'https://moodle.concordia.ca/moodle/mod/resource/']

        # Instead of just visiting the known links, click on the pdfs...annoying but the only way to get through Moodle's login refreshing -_-
        for i, link in enumerate(cleaned_links[:1]):
            outpath = folder_location + 'file_{}.pdf'.format(i)
            bot.find_element_by_xpath('//a[@href="' + link + '"]').click()
            time.sleep(1.5)        
            temp = bot.find_element_by_xpath(
            '//input[@class="toolbarButton" and @id="download"]').click()
            time.sleep(2)
            temp.send_keys(Keys.RETURN)
            bot.back()

        print("✓ Saved all available files.")

if __name__ == '__main__':
    
    # Accept user input for username, password and semester
    user = input('Username: ')
    pwd = getpass.getpass()
    moodler = Moodler(user, pwd)

    # Login
    moodler.login()
    moodler.goto_class()

    # Create destination folder in the case where it doesn't exist.
    folder_location = '/Users/Matteo/Desktop/pdfs/'
    if not os.path.exists(folder_location):
        os.mkdir(folder_location)

    # print(moodler.get_pdflist())
