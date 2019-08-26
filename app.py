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

class Moodler:
    def __init__(self, username, password, course_page, outpath):
        """Moodler. Your automated Moodle pdf downloader.

        Arguments:
            username {string} -- Moodle username.
            password {string} -- Moodle password.
            course_page {string} -- Moodle course page where files are.
            outpath {string} -- Destination folder.
        """
        self.username = username
        self.password = password
        self.course_page = course_page
        self.outpath = outpath
        
        mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", self.outpath)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
        fp.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
        fp.set_preference("pdfjs.disabled", True)

        opts = webdriver.FirefoxOptions()
        opts.headless = True
        
        self.bot = webdriver.Firefox(options=opts, firefox_profile=fp)

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
        """Get to desired class page.
        """
        bot = self.bot
        bot.find_element_by_xpath('//a[@href="' + self.course_page + '"]').click()
        time.sleep(3.5)
        print("✓ Got to course page.")

    def get_docs(self):
        """Download files from moodle page.
        """
        bot = self.bot

        # Scrape
        soup = BeautifulSoup(bot.page_source, features="lxml")
        divs = soup.findAll('div', attrs={'class' : 'activityinstance'})
        pdf_icon = 'https://moodle.concordia.ca/moodle/theme/image.php/clean/core/1565843043/f/pdf-24'
        pdf_links = []
        for div in divs:
            href = div.find('a')['href']
            if div.find('img')['src'] == pdf_icon:
                pdf_links.append(href)

        # Keep pdf links
        cleaned_links = [x for x in pdf_links if x[:48] == 'https://moodle.concordia.ca/moodle/mod/resource/']

        all_files = []
        new_files = []
        for i, link in enumerate(cleaned_links[:5], 1):
            all_files = os.listdir(self.outpath) # Before
            bot.find_element_by_xpath('//a[@href="' + link + '"]').click()
            time.sleep(1)
            new_files = os.listdir(self.outpath) # After
            most_recent_file = list(set(new_files) - set(all_files))
            print('{}. {} saved.'.format(i, most_recent_file[0]))

        print("✓ Saved all available files.")

if __name__ == '__main__':
    
    # Accept user input for username, password and file output path
    user = input('Username: ')
    pwd = getpass.getpass()
    cse_pg = input('Course page: ')
    outpath = input('Destination folder: ')

    # Create destination folder in the case where it doesn't exist.
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    moodler = Moodler(user, pwd, cse_pg, outpath)

    # Login & get to class page
    moodler.login()
    moodler.goto_class()

    # Download files
    moodler.get_docs()
