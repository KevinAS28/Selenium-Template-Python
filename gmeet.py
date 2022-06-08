from pathlib import Path, PureWindowsPath
from selenium import webdriver, common
from browsermobproxy import Server
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TOE
from selenium.common.exceptions import NoSuchElementException as NSEE
from selenium.common.exceptions import ElementNotInteractableException as ENIE

from threading import Thread
import os
import time
import traceback
import requests
import json
import sys
import configparser


script_path = os.path.realpath(__file__)
script_dir = os.path.split(script_path)[0]
user_dir = os.path.join(script_dir, "gc")
log_file = os.path.join(script_dir, "ytb_music.log")

def log(*msg, print_msg=True, encode=False, end="\n"):    
    msg = " ".join([str(i) for i in msg])+"\n"
    
    if (encode):
        msg = msg.encode('utf-8')
        
    with open(log_file, "ba+" if encode else "a+") as logger:
        logger.write(msg)
        
    if print_msg:
        print(msg, end="")

driver = None
proxy = None
server = None

log("user_dir:", user_dir)

def on_max_try():
    return ""

fail_try = 0
def keep_try(function, args=[], exception=Exception, wait_sec=3, max_try=0, verbose=True, logged=True, on_max_try_func=on_max_try):
    global fail_try

    function_name = function.__name__

    loop = True
    while loop:
        try:
            to_return = function(*args)
            loop = False
            fail_try = 0
            return to_return
        except (exception) as error:
            if logged:
                log("{}(): error: {}".format(function_name, str(error)), print_msg=verbose)            
            
            if (max_try>0):
                if (fail_try == max_try):
                    if logged:
                        error_msg = f"function {function_name} has reached maximum try error ({str(max_try)})... raising an Execption!"
                        on_max_try_func()
                        log(error_msg, print_msg=verbose)
                        log(traceback.format_exc(), print_msg=verbose)
                    raise Exception(error_msg)
                fail_try+=1

            if logged:
                log(f"waiting for {str(wait_sec)} second(s) to try again...\n", print_msg=verbose)
            time.sleep(wait_sec)

        

def initialize_chrome():
    global driver
    global server
    global proxy
    dict={'port':8090}

    server = Server(path=os.path.join(script_dir, "binaries/browsermob-proxy-2.1.4/bin/browsermob-proxy"), options=dict)
    server.start()
    proxy = server.create_proxy()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={user_dir}")
    driver = webdriver.Chrome(str(Path(os.path.join(script_dir, "binaries/chromedriver83")).absolute()), options = chrome_options)
    log('initialized Chrome window!')


def main():
    #prepare the log file
    if os.path.isfile(log_file):
        os.remove(log_file)
    open(log_file, "w+").close()

    #read the configuration
    global config
    config = configparser.ConfigParser()
    config_file_name = "ytb_config.ini"
    try:    
        config.read(os.path.join(script_dir, config_file_name))

    except Exception as error:
        log(f"Error while reading configuration file ({config_file_name}): {str(error)}")
        log(traceback.format_exc())
        log("Exit!")
        sys.exit(1)
    
    # log("Configuration list: \n")
    # for space_config in list(config.keys())[1:]:
    #     log("[{}]".format(space_config))
    #     for config_key in list(config[space_config].keys()):
    #         log("{} = {}".format(config_key, str(config[space_config][config_key])))
    #     log("\n")
    

    #prepare the chrome

    initialize_chrome()

    url = "https://meet.google.com/hvv-sryj-nkb"

    driver.get(url)
    


if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("CTRL + C hitted. Hope you enjoy your media :)")
    except Exception as error:
        log(str(error))
        log(traceback.format_exc())
    
    driver.quit()