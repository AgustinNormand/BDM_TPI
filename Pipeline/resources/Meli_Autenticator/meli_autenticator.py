# -*- coding: utf-8 -*-

import requests
from dotenv import dotenv_values
import os.path
import logging

class Meli_Autenticator:
    def __init__(self, fresh_start=False):
        logging.basicConfig(level=logging.INFO)
        self.dotenv_values = dotenv_values("Meli_Autenticator/.env")
        self.html_client = requests
        self.APP_ID = self.dotenv_values["APP_ID"]
        self.CLIENT_SECRET = self.dotenv_values["CLIENT_SECRET"]
        self.REDIRECT_URI = self.dotenv_values["REDIRECT_URI"]
        self.access_token_filepath = "Meli_Autenticator/"+self.dotenv_values["ACCESS_TOKEN_FILENAME"]
        self.refresh_token_filepath = "Meli_Autenticator/"+self.dotenv_values["REFRESH_TOKEN_FILENAME"]
        self.brand_new_tokens = False

        self.load_or_obtain_tokens()

        if not self.brand_new_tokens and fresh_start:
            logging.info("Tokens were valid, but refreshing because of 'fresh_start'")
            self.refresh_access_token()
        else:
            if not self.token_fresh():
                logging.info("Token is expired, refreshing")
                self.refresh_access_token()

    def load_or_obtain_tokens(self):
        if os.path.isfile(self.access_token_filepath) and os.path.isfile(self.refresh_token_filepath):
            logging.info("Tokens files found")
            with open(self.access_token_filepath) as f:
                self.access_token = f.read()
            with open(self.refresh_token_filepath) as f:
                self.refresh_token = f.read()
            logging.info("Tokens readed")
        else:
            logging.info("No tokens files found, first autentication needed")
            self.first_autentication()

    def persist_tokens(self, response):
        if "access_token" in list(response.json().keys()):
            with open(self.access_token_filepath, 'w') as f:
                self.access_token = response.json()["access_token"]
                f.write(self.access_token)
            with open(self.refresh_token_filepath, 'w') as f:
                self.refresh_token = response.json()["refresh_token"]
                f.write(self.refresh_token)
                logging.info("Tokens persisted")
        else:
            logging.error("response in persist_tokens didnt have access_token. {}".format(response.json()))

    def first_autentication(self):
        self.INIT_AUTH_URL = 'https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id={}'.format(
            self.APP_ID)
        print("Enter here: {}".format(self.INIT_AUTH_URL))
        server_generated_authorization_code = input("Paste TG-... here: ")
        ACCESS_TOKEN_POST_URL = "https://api.mercadolibre.com/oauth/token?grant_type=authorization_code&client_id=" \
                                "{}&client_secret={}&code={}&redirect_uri={}".format(self.APP_ID,
                                                                                     self.CLIENT_SECRET,
                                                                                     server_generated_authorization_code,
                                                                                     self.REDIRECT_URI)
        response = self.html_client.post(ACCESS_TOKEN_POST_URL)
        self.persist_tokens(response)
        self.brand_new_tokens = True


    def token_fresh(self):
        logging.info("Verifying Token Freshness")
        url = 'https://api.mercadolibre.com/sites/MLA/search?category=MLA1459&PROPERTY_TYPE=242062&OPERATION=242075&state=TUxBUENBUGw3M2E1&offset=0&limit=0'
        headers = {"Authorization": "Bearer {}".format(self.access_token)}
        response = self.html_client.get(url, headers=headers)
        if "paging" in response.json().keys():
            logging.info("Token is fresh")
            return True
        else:
            logging.info("Token is not fresh")
            return False

    def refresh_access_token(self):
        refresh_url = "https://api.mercadolibre.com/oauth/token?grant_type=refresh_token&client_id=" \
                           "{}&client_secret={}&refresh_token={}".format(self.APP_ID,
                                                                         self.CLIENT_SECRET,
                                                                         self.refresh_token)
        response = self.html_client.post(refresh_url)
        self.persist_tokens(response)

    def get_access_token(self):
        return self.access_token
