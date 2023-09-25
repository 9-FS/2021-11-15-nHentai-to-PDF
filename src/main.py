# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import json
from KFSconfig import KFSconfig
from KFSfstr   import KFSfstr
from KFSlog    import KFSlog
import logging
import os
from get_hentai_ID_list import get_hentai_ID_list
from Hentai             import Hentai


@KFSlog.timeit
def main():
    cleanup_success: bool=True  #cleanup successful
    COOKIES_DEFAULT: str=json.dumps({
        "cf_clearance": "",
        "csrftoken": "",
    }, indent=4)
    cookies: dict[str, str]     # for requests.get to bypass cloudflare
    HEADERS_DEFAULT: str=json.dumps({
        "User-Agent": "",
    }, indent=4)
    headers: dict[str, str]
    hentai: Hentai              # individual hentai
    hentai_ID_list: list[int]   # hentai ID to download


    cookies=json.loads(KFSconfig.load_config("cookies.json", COOKIES_DEFAULT))
    headers=json.loads(KFSconfig.load_config("headers.json", HEADERS_DEFAULT))
    hentai_ID_list=get_hentai_ID_list()         # get desired hentai ID
    

    for i, hentai_ID in enumerate(hentai_ID_list):  # work through all desired hentai
        logging.info("--------------------------------------------------")
        logging.info(f"{KFSfstr.notation_abs(i+1, 0, round_static=True)}/{KFSfstr.notation_abs(len(hentai_ID_list), 0, round_static=True)} ({KFSfstr.notation_abs((i+1)/(len(hentai_ID_list)), 2, round_static=True)})")

        hentai=Hentai(hentai_ID, cookies, headers)  # create hentai object
        logging.info(hentai)

        hentai.download()   # download hentai
    logging.info("--------------------------------------------------")


    logging.info("Removing leftover image folders...")
    for hentai_ID in hentai_ID_list:                                                                # attempt final cleanup
        if os.path.isdir(f"./hentai/{hentai_ID}") and len(os.listdir(f"./hentai/{hentai_ID}"))==0:  # if cache folder still exists and is empty:
            try:
                os.rmdir(f"./hentai/{hentai_ID}")                                                   # try to clean up
            except PermissionError:                                                                 # may fail if another process is still using directory like dropbox
                logging.warning(f"Removing \"./hentai/{hentai_ID}\" failed with PermissionError.")
                cleanup_success=False                                                               # cleanup unsuccessful
    if cleanup_success==True:
        logging.info("\rRemoved leftover image folders.")

    return