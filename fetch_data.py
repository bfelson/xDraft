import pandas as pd
import numpy as np
from typing import List
from pybaseball import statcast_batter_expected_stats, statcast_pitcher_expected_stats
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

position_eligiblity_link = "https://baseball.fantasysports.yahoo.com/b1/860/positioneligibility"
position_headers = ["C", "1B", "2B", "3B", "SS", "CI", "MI", "LF", "CF", "RF", "OF", "Util", "SP", "RP", "P"]

def get_position_eligibility_list(players):
    '''
    Drives get_position_eligibility function for a list of players
    Returns dictionary of players and their eligible positions
    '''
    players_positions = {}

    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get(position_eligiblity_link)

    for player in players:
        players_positions[player] = get_position_eligibility(player, driver)
    
    driver.quit()

    return players_positions


def get_position_eligibility(player_name: str, driver):
    '''
    Returns a list of eligible positions a player can play.
    Assumes that webdriver is already open

    Parameters:
    player_name: str - name of player in format: "First Last"
    driver: selenium webdriver to go on yahoo and get list
    '''
    # Establish list to return
    eligible_positions = []

    # Search for player in webpage search bar by locating search bar class
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".playersearch_ac.No-bdr.yui3-ysfplayersearch-input"))
        )
        search_bar.clear()
        search_bar.click()
        search_bar.send_keys(player_name)
        search_bar.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"Could not search for player:\t{e}")

    # Get eligibility table and parse for positions
    try:
        # Wait for rows in table to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody > tr"))
        )

        # Get table, rows of eligibility. Should be only one row.
        table = driver.find_element(By.CSS_SELECTOR, "table.Tst-table")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            for i, cell_index in enumerate(range(3,27,2)):
                if cells[cell_index].text.strip() == "E": # Eligible
                    eligible_positions.append(position_headers[i])
    except Exception as e:
        print(f"Could not get eligible positions list:\t{e}")

    return eligible_positions

def reverse_name(last_first: str):
    '''
    Function to convert name from format "last, first" to "First Last"
    '''
    last_name, first_name = last_first.split(",")
    return first_name.strip() + " " + last_name.strip()

def get_statcast_batters(year=2025, pa_threshold=25):
    '''
    Retrieves batter StatCast data and returns cleaned dataframe of expected stats
    '''
    xbats = statcast_batter_expected_stats(year=year, minPA=pa_threshold)
    xbats = xbats.drop(["player_id", 'bip', 'year'], axis=1)
    xbats.columns = ["Name", "PA", "BA", "xBA", "xBA-BA", "SLG", "xSLG", "xSLG-SLG", "wOBA", "xwOBA", "xwOBA-wOBA"]
    xbats["Name"] = xbats["Name"].apply(reverse_name)
    xbats = xbats.set_index("Name")
    xbats = xbats[xbats["PA"] > pa_threshold]
    xbats = xbats.sort_values(by=["xwOBA", "xwOBA-wOBA"], ascending=[False, False], axis=0)

    # Clean up floats
    for col in ["BA", "xBA", "xBA-BA", "SLG", "xSLG", "xSLG-SLG", "wOBA", "xwOBA", "xwOBA-wOBA", "ERA", "xERA", "ERA-xERA"]:
        if col in xbats:
            xbats[col] = np.round(xbats[col], 3)

    return xbats

def get_statcast_pitchers(year=2025, pa_threshold=25):
    '''
    Retrieves pitcher StatCast data and returns cleaned dataframe of expected stats
    '''
    xpits = statcast_pitcher_expected_stats(year=year, minPA=pa_threshold)
    xpits = xpits.drop(['player_id', 'year', 'bip'], axis=1)
    xpits.columns = ["Name", "PA", "BA", "xBA", "xBA-BA", "SLG", "xSLG", "xSLG-SLG", "wOBA", "xwOBA", "xwOBA-wOBA", "ERA", "xERA", "ERA-xERA"]
    xpits["Name"] = xpits["Name"].apply(reverse_name)
    xpits = xpits.set_index("Name")
    xpits = xpits[xpits["PA"] > pa_threshold]
    xpits = xpits.sort_values(by=["xwOBA", "xwOBA-wOBA"], ascending=[True, True], axis=0)

    # Clean up floats
    for col in ["BA", "xBA", "xBA-BA", "SLG", "xSLG", "xSLG-SLG", "wOBA", "xwOBA", "xwOBA-wOBA", "ERA", "xERA", "ERA-xERA"]:
        xpits[col] = np.round(xpits[col], 3)

    return xpits