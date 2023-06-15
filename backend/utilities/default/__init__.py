from .sets import InitialSetting
from datetime import datetime

from .sets import get_all_valores

# json
from utilities.default.sets.pathmanager import HasJson

# dates
from .sets import calc_date_compt_offset, get_compt, compt_to_date_obj

# drivers
from .webdriver_utilities import pgdas_driver, pgdas_driver_ua, ginfess_driver, default_qrcode_driver,jucesp_simple_driver, proffile_noqr_driver
# selenium shortcuts
from .webdriver_utilities import WDShorcuts
# selenium
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver import Remote
from selenium.webdriver.support.ui import Select

# Contimatic & G5 Utils
from pgdas_fiscal_oesk.contimatic import Contimatic
from pgdas_fiscal_oesk.relacao_nfs import NfCanceled
import pyautogui as pygui
import pyautogui
from .interact import ativa_janela, press_keys_b4, press_key_b4, all_keys, tk_msg, _contmatic_select_by_name, foritab

# email sender
from utilities.default.sets.init_email import EmailExecutor



# other utils
import os
import pandas as pd
from time import sleep
