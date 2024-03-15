#!/usr/bin/env python

import aiohttp
import asyncio

import random
import string

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

import time
import logging

import json

from datetime import datetime

import os

import ssl

from imapclient import IMAPClient

from aioimaplib import aioimaplib
from aioimaplib import STOP_WAIT_SERVER_PUSH

import re

import sys


class TimestampFilter(logging.Filter):
    def filter(self, record):
        record.timestamp = int(time.time())
        return True

# Create a formatter
log_format = "[%(asctime)s] [%(levelname)s] [%(timestamp)s] %(message)s"
date_format = "%d/%m/%Y %H:%M:%S"
formatter = logging.Formatter(log_format, datefmt=date_format)

# Create a handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Add the custom filter to the handler
handler.addFilter(TimestampFilter())

# Create a logger
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


configs = {
    'custom_domain': 'mdgtccount',
    'account_password': 'Github1!',
    'dob': ["1", "4", "1994"],
    'city': 'Roma',
    'zip_code': '00055',
    'name': 'Marco',
    'surname': 'Verdi',
    'domain': 'hotmail.com',
    'crew_name': 'ign_crew',
    'join_crew': True,
    'use_custom_domain': True,
    'captcha_timeout': 1000,
    'set_recovery_mail': True,
    'custom_recovery_mail_domain': 'mailinaboxdomain'
}


class RecoveryMail:
    def __init__(self, email: str, password: str, recovery_mail: str):
        self.email = email
        self.password = password
        self.recovery_mail = recovery_mail

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_recovery_mail(self):
        return self.recovery_mail
    
    async def start_listener(self):
        while True:
            await asyncio.sleep(0)
            try:                    
                imap_result = await wait_imap_verification_mail(email=self)
                if imap_result:
                    logging.info(f"Codice di verifica trovato: {imap_result} - Recovery Mail: {self.get_recovery_mail()}")
            except Exception as e:
                logging.info(f"Errore: {e}")
                continue
            
class email_outlook:
    def __init__(self, email: str, password: str, dob: list[str], city: str, zip_code: str, first_name: str, last_name: str, xbox_gametarg: str | None = None, psn_gametarg: str | None = None):
        self.email = email
        self.password = password
        self.dob = dob
        self.city = city
        self.zip_code = zip_code
        self.first_name = first_name
        self.last_name = last_name
        self.xbox_gametarg = xbox_gametarg
        self.psn_gametarg = psn_gametarg

    def get_email(self):
        return self.email

    def get_email_with_domain(self):
        return f"{self.email}@{configs['domain']}"
    
    def get_password(self):
        return self.password
    
    def get_dob(self):
        return self.dob
    
    def get_city(self):
        return self.city
    
    def get_zip_code(self):
        return self.zip_code
    
    def get_name(self):
        return self.first_name
    
    def get_surname(self):
        return self.last_name
    
    def get_xbox_gamertag(self):
        return self.xbox_gametarg
    
    def set_xbox_gamertag(self, gamertag: str):
        self.xbox_gametarg = gamertag

    def get_psn_gamertag(self):
        return self.psn_gametarg
    
    def set_psn_gamertag(self, gamertag: str):
        self.psn_gametarg = gamertag

    def get_recovery_mail(self):
        return self.recovery_mail
    
    def generate_and_set_recovery_mail(self):
        self.recovery_mail = f"{generate_random_email(16, True).get_email()}@{configs['custom_recovery_mail_domain']}"


def fix_accounts_files():
    logging.info("Controllo se ci sono file json nella cartella accounts, se si, li sposto in una cartella con lo stesso nome del file ma senza estensione.")
    # check if accounts directory exists, if yes, check if there are files json.
    if os.path.exists('accounts'):
        # if there are file json, move inside a new folder called with same name of the file but without extension.
        for file in os.listdir('accounts'):
            if file.endswith('.json'):
                file_name = file.split('.')[0]
                os.makedirs(f'accounts/{file_name}', exist_ok=True)
                os.rename(f'accounts/{file}', f'accounts/{file_name}/{file}')
    else:
        return

def count_account_numbers():
    try:
        with open('accounts.json', 'r') as file:
            data = file.read()
            count = data.count('{')
            return count
    except FileNotFoundError:
        return 0

def generate_random_email(length: int = 16, with_custom_domain: bool = False) -> email_outlook:

    if with_custom_domain:
        random_email = ''.join(random.choice(string.digits) for i in range(7))
        
        random_email = configs['custom_domain'] + random_email

        return email_outlook(random_email, configs['account_password'], configs['dob'], configs['city'], configs['zip_code'] , configs['name'], configs['surname'])
    
    characters = string.ascii_lowercase + string.digits

    random_email = ''.join(random.choice(characters) for i in range(length))
    while random_email[0].isdigit():
        random_email = ''.join(random.choice(characters) for i in range(length))

    return email_outlook(random_email, configs['account_password'], configs['dob'], configs['city'], configs['zip_code'] , configs['name'], configs['surname'])
    
def slow_type(element: WebElement, text: str, delay: float=0.1):
    for character in text:
        element.send_keys(character)
        time.sleep(delay)
 
def get_recovery_accounts() -> list[RecoveryMail]:
    recovery_accounts = []
    # open accounts folder, for each subfolder, check if there are json files, if yes, parse them and add them to recovery_accounts list.
    for folder in os.listdir('accounts'):
        if os.path.isfile(f'accounts/{folder}'):
            continue        
        for file in os.listdir(f'accounts/{folder}'):
            # check if file is a json file
            if file.endswith('.json'):
                with open(f'accounts/{folder}/{file}', 'r') as file:
                    account = json.load(file)
                    
                    for key, value in account.items():
                        if key == 'email':
                            email = value
                        elif key == 'password':
                            password = value
                        elif key == 'recovery_mail':
                            recovery_mail = value
                    recovery_accounts.append(RecoveryMail(email, password, recovery_mail))
    return recovery_accounts

def wait_imap_verification_mail_not_async(email: email_outlook | RecoveryMail) -> int:
    # create ssl context to set verify_ssl to False
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    print(f"Attendo email di verifica per {email.get_email()} - Recovery Mail: {email.get_recovery_mail()} - Password: {email.get_password()}")

    # Connect to the IMAP server
    with IMAPClient('YOURMAILINABOXURL', ssl_context=ssl_context) as client:
        # Login to the email account
        client.login(email.get_recovery_mail(), email.get_password())
        
        # Select the mailbox where verification emails are expected
        client.select_folder('INBOX')
        
        # while messages is empty, wait for the email to arrive
        pattern: str = r'Codice di sicurezza: (\d+)'
        while True:
            print(f"Attendo email di verifica per {email.get_email()} - Recovery Mail: {email.get_recovery_mail()} - Password: {email.get_password()}")
            messages = client.search(['FROM', 'account-security-noreply@accountprotection.microsoft.com', 'UNSEEN'])
            messages.sort(reverse=True)  # Ordina i messaggi in ordine decrescente di ID
            if messages:
                # Fetch the email body of the latest message
                raw_message = client.fetch(messages[0], ['BODY[]'])
                email_body = raw_message[messages[0]][b'BODY[]'].decode('utf-8')
                code = int(re.search(pattern, email_body).group(1))
                return code

async def wait_imap_verification_mail(email: email_outlook | RecoveryMail) -> int:
    pattern: str = r'Codice di sicurezza: (\d+)'

    # create ssl context to set verify_ssl to False
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Connect to the IMAP server
    imap_client = aioimaplib.IMAP4_SSL(host='YOURMAILINABOXDOMAIN', ssl_context=ssl_context)
    await imap_client.wait_hello_from_server()
    
    await imap_client.login(email.get_recovery_mail(), email.get_password())
        
    await imap_client.select()

    status, data = await imap_client.search('UNSEEN')
    if status == 'OK':
        unseen_emails = data[0].split()[::-1]

        for email_id in unseen_emails:
            status, data = await imap_client.fetch(message_set=email_id.decode('utf-8'), message_parts='BODY[]')
            if status == 'OK':
                try:
                    email_content = data[1].decode('utf-8')
                    code = int(re.search(pattern, email_content).group(1))
                    return code
                except:
                    pass
                    
            



    # Search for all unseen messages

async def wait_for_partial_url(driver: uc.Chrome, partial_url: str, timeout: int = 20):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: partial_url in driver.current_url
        )
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        return False
    return True

async def wait_for_url(driver: uc.Chrome, url: str, timeout: int = 20):
    try:
        WebDriverWait(driver, timeout).until(
            EC.url_to_be(url)
        )
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        return False
    return True

async def wait_verification_psn_opened(driver: uc.Chrome):
    while len(driver.window_handles) < 5:
        continue

    urls = [
        "https://my.account.sony.com/central/verification/?entry=email_address",
        "https://id.sonyentertainmentnetwork.com/id/email_verification"
    ]

    for window in driver.window_handles:
        driver.switch_to.window(window)
        print(f"Current title: {driver.title} - Current url: {driver.current_url}")
        for url in urls:
            if f"{url}" in driver.current_url:
                return True
            
    return False

async def sign_up_outlook(driver: uc.Chrome, email: email_outlook):
    driver.get('https://go.microsoft.com/fwlink/p/?linkid=2125440&clcid=0x410&culture=it-it&country=it')
    
    try:
        MemberName = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MemberName"))
        )
        MemberName.send_keys(email.get_email())

        LiveDomainBoxList = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "LiveDomainBoxList"))
        )
        
        Select(LiveDomainBoxList).select_by_value(configs['domain'])

        iSignupAction = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iSignupAction"))
        )
        iSignupAction.click()

        PasswordInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PasswordInput"))
        )
        PasswordInput.send_keys(email.get_password())


        iSignupAction = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iSignupAction"))
        )
        iSignupAction.click()

        FirstName = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "FirstName"))
        )

        FirstName.send_keys(email.get_name())

        LastName = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "LastName"))
        )
        LastName.send_keys(email.get_surname())

        iSignupAction = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iSignupAction"))
        )
        iSignupAction.click()

        day_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'BirthDay'))
        )
        month_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'BirthMonth'))
        )
        year_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'BirthYear'))
        )

        Select(day_element).select_by_value(email.get_dob()[0])
        Select(month_element).select_by_value(email.get_dob()[1])
        year_element.clear()
        year_element.send_keys(email.get_dob()[2])

        iSignupAction = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "iSignupAction"))
        )
        iSignupAction.click()

        try:
            hipEnforcementContainer = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "hipEnforcementContainer"))
            )
        except:
            input(f"Verifica numero di telefono rilevata, cambia ip e riprova a ricreare l'account! Premi INVIO per chiudere il programma.")
            return False
        
        logging.info(f"Resto in attesa del completamento del captcha... (attenderò {configs['captcha_timeout']} secondi)")
        userDisplayName = WebDriverWait(driver,configs['captcha_timeout']).until(
            EC.presence_of_element_located((By.ID, "userDisplayName"))
        )
        logging.info("Captcha completato con successo!")

        DontShowAgain = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "DontShowAgain"))
        )
        DontShowAgain.click()

        logging.info("Bottone non mostrare più cliccato!")
        
        #button_ids = ["idSIButton9", "acceptButton"]
        button_ids = ["acceptButton"]

        for button_id in button_ids:
            try:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.ID, button_id))
                )
                button.click()
                logging.info(f"Bottone per proseguire cliccato! [{button_id}]")
                break  
            except:
                continue

        await wait_for_url(driver, "https://outlook.live.com/mail/0/", 20)
        
        # setting recovery mail for outlook access.
        if configs['set_recovery_mail']:
            await set_up_recovery_mail(driver=driver,email=email)

        logging.info("Account Microsoft creato con successo, ora verrà effettuato il login sul sito xbox.com")
        return True

    except Exception as e:
        logging.info(f"Errore: {e}")
        return False

async def sign_up_xbox(driver: uc.Chrome, email: email_outlook):
    driver.execute_script("window.open('https://www.xbox.com/it-IT/auth/msa?action=logIn&returnUrl=https://www.xbox.com/it-IT/live');")
    try:
        driver.switch_to.window(driver.window_handles[1])
        # check if #tilesHolder > div.tile-container > div > div selector is present
        await asyncio.sleep(3)
        try:
            tilesHolder = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div/div/div[1]/div/button'))
            )
            logging.info("Trovato il div per il login!")
            tilesHolder.click()
        except:
            logging.info("Login non trovato, procedo con form email preloggato!")
            i0118 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "i0118"))
            )
            i0118.send_keys(email.get_password())
            
            idSIButton9 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "idSIButton9"))
            )
            idSIButton9.click()

        create_account_gamertag_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "create-account-gamertag-input"))
        )
        logging.info("Trovato il campo per inserire il gamertag!")

        create_account_gamertag_suggestion_1 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "create-account-gamertag-suggestion-1"))
        )
        
        create_account_gamertag_suggestion_1.click()
        logging.info(f"Gamertag {create_account_gamertag_suggestion_1.text} selezionato!")
        
        await asyncio.sleep(3)

        create_account_gamertag_input_indicator = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID,"create-account-gamertag-input-indicator"))
        )
        
        if create_account_gamertag_input_indicator.get_attribute("class") != "success":
            success: bool = False
            for i in range(2, 4):
                create_account_gamertag_suggestion = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, f"create-account-gamertag-suggestion-{i}"))
                )
                create_account_gamertag_suggestion.click()
                await asyncio.sleep(3)
                logging.info(f"Gamertag {create_account_gamertag_suggestion.text} selezionato!")
                create_account_gamertag_input_indicator = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID,"create-account-gamertag-input-indicator"))
                )
                if create_account_gamertag_input_indicator.get_attribute("class") == "success":
                    success = True
                    email.set_xbox_gamertag(create_account_gamertag_suggestion.text)
                    break
        
            if not success:
                logging.info("Errore durante la selezione del gamertag, tutti e quattro i gamertag suggeriti sono già stati presi!")
                return False
            
        email.set_xbox_gamertag(create_account_gamertag_suggestion_1.text)
            
        inline_continue_control = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "inline-continue-control"))
        )
        logging.info("Trovato il bottone per proseguire!")
        inline_continue_control.click()
        logging.info("Bottone per proseguire cliccato!")
        await asyncio.sleep(1)
        
        is_continue_control_find: bool = False
        while is_continue_control_find == False:
            inline_continue_control = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "inline-continue-control"))
            )
            logging.info("Trovato il bottone per proseguire! (2)")
            inline_continue_control.click()
            logging.info("Bottone per proseguire cliccato! (2)")
            is_continue_control_find = True
            break

        WebDriverWait(driver, 20).until(
            EC.url_to_be("https://www.xbox.com/it-IT/live")
        )


        logging.info("Account Xbox creato con successo!")

        return True
    except Exception as e:
        logging.info(f"Errore: {e}")
        return False

async def join_crew(driver: uc.Chrome):
    # joining recoveryzone crew.
    driver.get(f'https://socialclub.rockstargames.com/crew/{configs["crew_name"]}/wall')
    
    wait_crew_button: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ui-name="join"]'))
    )
    wait_crew_button.click()
    logging.info("Bottone per unirsi al crew cliccato!")

async def sign_up_rockstar(driver: uc.Chrome, email: email_outlook):
    driver.execute_script("window.open('https://signin.rockstargames.com/tpa/xbl/login?cid=rsg&returnUrl=undefined');")

    try:
        driver.switch_to.window(driver.window_handles[2])

        idBtn_Accept = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "idBtn_Accept"))
        )
        idBtn_Accept.click()

        cid_rsg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Crea un nuovo account')]"))
        )
        cid_rsg.click()

        day_dropdown = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.DateOfBirth__dropdown__VK9IC[data-ui-name="dateOfBirth_day"] select.select'))
        ))

        day_dropdown.select_by_value(email.get_dob()[0])

        month_dropdown = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.DateOfBirth__dropdown__VK9IC[data-ui-name="dateOfBirth_month"] select.select'))
        ))
        month_dropdown.select_by_value(email.get_dob()[1])

        year_dropdown = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.DateOfBirth__dropdown__VK9IC[data-ui-name="dateOfBirth_year"] select.select'))
        ))
        year_dropdown.select_by_value(email.get_dob()[2])

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-page > div:nth-child(2) > div.Container__container__JWsGa.CreateAccount__dateOfBirthContainer__KD3ny > form > div > div > div > button'))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-page > div:nth-child(2) > div > form > div > div > div.LegalPolicy__checkbox__Pz8QO > span > label'))
        ).click()
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#app-page > div:nth-child(2) > div > form > div > div > div:nth-child(5) > div > button.UI__Button-socialclub__btn.UI__Button-socialclub__primary.UI__Button-socialclub__medium.LegalPolicy__next__bgMCq'))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
        ).send_keys(email.get_email_with_domain())

        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        slow_type(password, email.get_password())

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="nickname"]'))
        ).send_keys(email.get_xbox_gamertag())

        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-ui-name="nextButton"]'))
        )
        next_button.click()

        is_captcha_present: bool = False
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/iframe'))
            )
            is_captcha_present = True
            logging.info(f"Captcha rilevato, hai {configs['captcha_timeout']} secondi per completarlo!")
            while is_captcha_present:
                try:
                    WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ui-name="submitEmailVerifyButton"]'))
                    )
                    logging.info("Captcha completato con successo!")
                    break
                except:
                    continue
        except:
            pass
        
        logging.info(f"Inserisci il codice di verifica inviato all'email {email.get_email_with_domain()} e INCOLLALO O SCRIVILO NEL FORM, lo invierò automaticamente! (attendo {configs['captcha_timeout']} secondi)")

        while True:
            evCodeInput = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="evCode"]'))
            )
            if len(evCodeInput.get_attribute('value')) == 6:
                break
            continue

        submitEmailVerifyButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-ui-name="submitEmailVerifyButton"]'))
        )
        submitEmailVerifyButton.click()

        continueButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-ui-name="continueButton"]'))
        )
        continueButton.click()

        WebDriverWait(driver, 10).until(
            EC.url_to_be("https://www.rockstargames.com/undefined")
        )

        if configs['join_crew']:
            await join_crew(driver)

        logging.info("Account Rockstar creato con successo!")
        return True
    except Exception as e:
        logging.info(f"Errore: {e}")
        return False

async def sign_up_psn(driver: uc.Chrome, email: email_outlook):
    driver.execute_script("window.open('https://id.sonyentertainmentnetwork.com/id/create_account_ca/');")
    try:
        driver.switch_to.window(driver.window_handles[3])
        
        ember18 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember18"))
        )
        ember18.click()

        ember45 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember45"))
        )
        
        ember45.click()

        bday_day = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "bday-day"))
        )
        logging.info("Trovato il campo per inserire il giorno di nascita!")

        bday_month = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "bday-month"))
        )
        logging.info("Trovato il campo per inserire il mese di nascita!")

        bday_year = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "bday-year"))
        )

        logging.info("Trovato il campo per inserire l'anno di nascita!")

        Select(bday_day).select_by_value(email.get_dob()[0])
        Select(bday_month).select_by_value(email.get_dob()[1])
        Select(bday_year).select_by_value(email.get_dob()[2])
        
        logging.info("Data di nascita inserita con successo!")

        ember62 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ember62"))
        )
        
        ember62.click()

        logging.info("Bottone per proseguire cliccato!")

        await wait_for_url(driver, 'https://id.sonyentertainmentnetwork.com/id/create_account_ca/#/create_account/wizard/account_info_page1?entry=create_account')

        await asyncio.sleep(1)

        mail = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )

        logging.info("Trovato il campo per inserire l'email!")

        mail.send_keys(email.get_email_with_domain())

        logging.info("Email inserita con successo!")

        ember77 = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember77"))
        )

        logging.info("Trovato il campo per inserire la password!")

        ember77.send_keys(email.get_password())

        logging.info("Password inserita con successo!")


        ember80 = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember80"))
        )

        logging.info("Trovato il campo per inserire la seconda password!")

        ember80.send_keys(email.get_password())

        logging.info("Seconda password inserita con successo!")

        await asyncio.sleep(1)

        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "next-button"))
        )

        logging.info("Trovato il bottone per proseguire!")

        next_button.click()

        logging.info("Bottone per proseguire cliccato!")
        try:
            is_captcha_present: bool = False
            WebDriverWait(driver, configs['captcha_timeout']).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="ember-root"]/div[4]/iframe'))
            )
            is_captcha_present = True
            logging.info(f"Captcha rilevato, hai {configs['captcha_timeout']} secondi per completarlo!")
            while is_captcha_present:
                try:
                    wait_url = WebDriverWait(driver, 10).until(
                        EC.url_to_be("https://id.sonyentertainmentnetwork.com/id/create_account_ca/#/create_account/wizard/agreement?entry=create_account")
                    )
                    logging.info("Captcha completato con successo!")
                    break
                except:
                    continue
            pass
        except:
            input(f"Completa il captcha se richiesto e/o premi INVIO per continuare...")
            

        create_account_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember102"))
        )

        logging.info("Trovato il bottone per creare l'account!")

        create_account_button.click()

        await wait_for_url(driver,'https://id.sonyentertainmentnetwork.com/id/create_account_ca/#/create_account/wizard/finish?entry=create_account')

        logging.info("Bottone per creare l'account cliccato!")


        confirm_account_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember122"))
        )

        logging.info("Trovato il bottone per confermare l'account!")

        confirm_account_button.click()

        logging.info("Bottone per confermare l'account cliccato!")

        await wait_for_partial_url(driver,'https://id.sonyentertainmentnetwork.com/id/upgrade_account_ca/?entry=upgrade_account&pr_referer=upgrade')
    
        customize_account_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember11"))
        )

        logging.info("Trovato il bottone per customizzare l'account!")

        customize_account_button.click()

        logging.info("Bottone per customizzare l'account cliccato!")

        await asyncio.sleep(3)


        proceed_account_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember23"))
        )

        logging.info("Trovato il bottone per procedere con la customizzazione dell'account!")

        proceed_account_button.click()

        logging.info("Bottone per procedere con la customizzazione dell'account cliccato!")

        await asyncio.sleep(1)

        driver.get('https://id.sonyentertainmentnetwork.com/id/management_ca/')

        logging.info(f"E' Necessario confermare l'account tramite email {email.get_email_with_domain()}, verrà aperta una nuova scheda del browser per confermare l'account!")
        driver.switch_to.window(driver.window_handles[0])

        result = await wait_verification_psn_opened(driver)
        while result == False:
            result = await wait_verification_psn_opened(driver)
            if result:
                break

        for window in driver.window_handles:
            driver.switch_to.window(window)
            if "https://my.account.sony.com/central/signin/?entry=ca" in driver.current_url:
                logging.info(f"Selezionato window con index {driver.window_handles.index(window)}")
                break
        
        await asyncio.sleep(2)

        confirm_account_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ember14"))
        )

        logging.info("Trovato il bottone per confermare l'account! (verifica email)")

        confirm_account_button.click()

        await wait_for_partial_url(driver,'https://id.sonyentertainmentnetwork.com/id/management_ca/?entry=p&pr_referer=cam#/p/personal_info/list')

        #await asyncio.sleep(5)

        msg_profile = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ember10"]/ul/li[2]/ul/li[1]/div/button'))
        )

        logging.info("Trovato il bottone per modificare il profilo!")

        msg_profile.click()

        logging.info("Bottone per modificare il profilo cliccato!")
        
        await wait_for_partial_url(driver,'https://id.sonyentertainmentnetwork.com/id/management_ca/?gated=true&pr_referer=cam&ui=pr&entry=psn_profile')

        ember46 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ember46"))
        )

        logging.info("Trovato il campo per proseguire!")    

        ember46.click()

        logging.info("Bottone per proseguire cliccato!")

        #await asyncio.sleep(3)
        await wait_for_partial_url(driver,'https://id.sonyentertainmentnetwork.com/id/upgrade_account_ca/?entry=upgrade_account')


        push_to_create_online_id = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember12"))
        )

        logging.info("Trovato il bottone per proseguire alla creazione id!")

        push_to_create_online_id.click()

        await asyncio.sleep(3)

        logging.info("Bottone per proseguire alla creazione id cliccato!")

        address_level2 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "address-level2"))
        )

        logging.info("Trovato il campo per inserire la città!")

        address_level2.send_keys(email.get_city())

        logging.info("Città inserita con successo!")

        address_level1 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "address-level1"))
        )

        logging.info("Trovato il campo per inserire la provincia!")

        address_level1.send_keys(email.get_city())

        logging.info("Provincia inserita con successo!")

        postal_code = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "postal-code"))
        )

        logging.info("Trovato il campo per inserire il codice postale!")

        postal_code.send_keys(email.get_zip_code())

        logging.info("Codice postale inserito con successo!")

        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember31"))
        )

        logging.info("Trovato il bottone per proseguire!")

        next_button.click()

        logging.info("Bottone per proseguire cliccato!")

        await asyncio.sleep(2)

        next_button = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ember52"]/button'))
        )

        logging.info("Trovato il bottone per proseguire! (2)")
        onlineId: str | None = None
        for button in next_button:
            try:
                button.click()                
                logging.info(f"Bottone per proseguire cliccato! (2)")
                logging.info("Bottone per proseguire cliccato! (2)")
            except:
                pass

        ember39 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ember39"))
        )

        # extract the text, is a textbox.
        onlineId = ember39.get_attribute('value')

        logging.info(f"ID PSN: {onlineId}")



        if onlineId is not None:
            email.set_psn_gamertag(onlineId)
        
        given_name = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "given-name"))
        )

        logging.info("Trovato il campo per inserire il nome!")

        given_name.send_keys(email.get_name())

        logging.info("Nome inserito con successo!")

        family_name = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "family-name"))
        )

        logging.info("Trovato il campo per inserire il cognome!")

        family_name.send_keys(email.get_surname())

        logging.info("Cognome inserito con successo!")


        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "ember49"))
        )

        logging.info("Trovato il bottone per proseguire!")

        next_button.click()

        logging.info("Bottone per proseguire cliccato!")

        await wait_for_partial_url(driver,'https://id.sonyentertainmentnetwork.com/id/management_ca/?gated=true&pr_referer=cam&ui=pr&entry=psn_profile')

        driver.get('https://socialclub.rockstargames.com/settings/linkedaccounts')

        linkedAccounts = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="linkedAccountsFalse"]/div[1]/div[3]/button'))
        )

        logging.info("Trovato il bottone per collegare gli account!")

        linkedAccounts.click()

        logging.info("Bottone per collegare gli account cliccato!")

        continueButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-ui-name="continueButton"]'))
        )
        continueButton.click()

        logging.info("Account PSN creato e linkato con successo!")
        return True

    except Exception as e:
        logging.info(e)
        return False

async def push_mail_creation_to_mitb(email: str, password: str) -> bool:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = f'email={email}&password={password}'
    
    aiohttp_session: aiohttp.ClientSession = aiohttp.ClientSession()
    try:
        async with aiohttp_session.post('https://YOURMAILINABOXDOMAIN/admin/mail/users/add', headers=headers, data=data, auth=aiohttp.BasicAuth('adminmail','adminpassword'),verify_ssl=False) as response:
            print(await response.text())
            if response.status == 200:
                return True
            return False
    finally:
        await aiohttp_session.close()

async def set_up_recovery_mail(driver: uc.Chrome, email: email_outlook):
    email.generate_and_set_recovery_mail()
    recovery_mail: str = email.get_recovery_mail()
    mail_added: bool = await push_mail_creation_to_mitb(recovery_mail, email.get_password())
    if mail_added:
        logging.info(f"Email di recupero {recovery_mail} aggiunta con successo!")
    else:
        logging.info(f"Errore durante l'aggiunta dell'email di recupero {recovery_mail}!")
        return False
    
    driver.get('https://account.live.com/proofs/manage/additional?mkt=it-IT&refd=account.microsoft.com&refp=security')
    # wait for the page to load
    mail_box: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'EmailAddress'))
    )

    mail_box.send_keys(email.get_recovery_mail())

    # wait iNext input appear
    iNext: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'iNext'))
    )

    # click on iNext
    iNext.click()

    code: str = wait_imap_verification_mail_not_async(email)

    # wait until iOttText input appear
    iOttText: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'iOttText'))
    )
        
    iOttText.send_keys(code)

    iNext: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'iNext'))
    )

    iNext.click()
    
    select_user_wait: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div'))
    )

    select_user_wait.click()

    mail_field: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[2]/div[3]/div/div/input'))
    )

    mail_field.send_keys(email.get_recovery_mail())

    next_xpath: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[3]/div/div/div/div/input'))
    )

    next_xpath.click()

    code: str = wait_imap_verification_mail_not_async(email)

    otc_input: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'otc'))
    )

    otc_input.send_keys(code)
    
    next_xpath: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[6]/div/div/div/div[2]/input'))
    )
    
    next_xpath.click()
    await wait_for_partial_url(driver, 'https://privacynotice.account.microsoft.com/notice')
    driver.get('https://outlook.live.com/mail/0/')

async def initialize_webdriver():
    options: uc.ChromeOptions = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--incognito')
    driver = uc.Chrome(headless=False,use_subprocess=True, options=options)
    return driver

async def main(): 
    logging.info("GTA V Xbox + Social Club + PSN Account Creator")
    print("-------------------------")
    fix_accounts_files()
    print(f"Account attuali: {count_account_numbers()}")
    print("-------------------------")
    email = generate_random_email(with_custom_domain=configs['use_custom_domain'])
    # initialize webdriver
    driver: uc.Chrome = await initialize_webdriver()


    # run sign_up outlook
    start_time = time.time()
    microsoft_creation: bool = await sign_up_outlook(driver, email)
    if not microsoft_creation:
        logging.info("Errore durante la creazione dell'account Microsoft! riavviare il programma e riprovare!")
        return

    # run signup xbox
    xbox_creation: bool = await sign_up_xbox(driver, email)

    if not xbox_creation:
        logging.info("Errore durante la creazione dell'account Xbox! riavviare il programma e riprovare!")
        return

    # run signup rockstar
    rockstar_creation: bool = await sign_up_rockstar(driver, email)

    if not rockstar_creation:
        logging.info("Errore durante la creazione dell'account Rockstar! riavviare il programma e riprovare!")
        return
    
    psn_creation: bool = await sign_up_psn(driver, email)

    if not psn_creation:
        logging.info("Errore durante la creazione dell'account PSN! riavviare il programma e riprovare!")
        return

    json_data = {
        "email": email.get_email_with_domain(),
        "recovery_mail": email.get_recovery_mail(),
        "password": email.get_password(),
        "dob": email.get_dob(),
        "city": email.get_city(),
        "zip_code": email.get_zip_code(),
        "first_name": email.get_name(),
        "last_name": email.get_surname(),
        "xbox_gamertag": email.get_xbox_gamertag(),
        "psn_gamertag": email.get_psn_gamertag(),
        "creation_date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    json_data = json.dumps(json_data, indent=4)
    logging.info(f"Email: {email.get_email_with_domain()} - Password: {email.get_password()} - DOB: {email.get_dob()} - City: {email.get_city()} - Zip Code: {email.get_zip_code()} - First Name: {email.get_name()} - Last Name: {email.get_surname()} - Xbox Gamertag: {email.get_xbox_gamertag()} - PSN Gamertag: {email.get_psn_gamertag()} - Creation Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Recovery Mail: {email.get_recovery_mail()}")

    logging.info("Salvo l'account in accounts.json")

    with open('accounts.json', 'a') as f:
        f.write(json_data)
        f.write('\n\n')

    os.makedirs('accounts', exist_ok=True)

    os.makedirs(f'accounts/{email.get_email()}_{email.get_xbox_gamertag()}_{email.get_psn_gamertag()}', exist_ok=True)
    with open(f'accounts/{email.get_email()}_{email.get_xbox_gamertag()}_{email.get_psn_gamertag()}/{email.get_email()}_{email.get_xbox_gamertag()}_{email.get_psn_gamertag()}.json', 'w') as f:
        f.write(json_data)

    logging.info("Account salvato con successo! il driver verrà chiuso a breve!")

    WebDriverWait(driver, 10).until(
        EC.url_to_be('https://socialclub.rockstargames.com/settings/linkedaccounts')
    )
    
    driver.save_screenshot(f'accounts/{email.get_email()}_{email.get_xbox_gamertag()}_{email.get_psn_gamertag()}/linkedaccounts.png')

    await asyncio.sleep(2)

    driver.quit()

    logging.info(f"Tempo impiegato: {time.time() - start_time} secondi = {round((time.time() - start_time) / 60, 2)} minuti")

    input("Premi INVIO per chiudere il programma!")

async def mail_listener(accounts: list[RecoveryMail]):
    logging.info("Mail listener avviato! da ora in poi verranno ascoltate le email di recupero!")
    tasks = []
    for account in accounts:
        tasks.append(asyncio.create_task(account.start_listener()))
    await asyncio.gather(*tasks)

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "mail_listener":
            try:
                accounts: list[RecoveryMail] = get_recovery_accounts()
            except json.decoder.JSONDecodeError as e:
                logging.info("Errore durante la lettura del file accounts.json, nessun account di recupero rilevato, verrà chiuso il programma!")
                sys.exit()

            if len(accounts) == 0:
                logging.info("Nessun account di recupero rilevato, verrà chiuso il programma!")
                sys.exit()

            asyncio.run(mail_listener(accounts))
    else:
        asyncio.run(main())
