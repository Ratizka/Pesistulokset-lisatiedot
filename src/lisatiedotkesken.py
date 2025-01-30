import json
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup


def pyynto(url):
    try:
        vastaus = requests.get(url, timeout=1000)
        vastaus.raise_for_status()
        return vastaus.content
    except requests.RequestException as e:
        print(f"Virhe datan haussa: {e}")
        sys.exit(1)


def keitto(html):
    try:
        html_str = html.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        data = json.loads(soup.find('script', id='online-match-data').text)
        return (data)
    except AttributeError as e:
        print(f'Virhe: {e}')
        sys.exit(1)


def kokoonpano(data):

    kotikokoopano = pd.json_normalize(data['teams']['home']["lineUp"])

    vieraskokoopano = pd.json_normalize(data['teams']['away']["lineUp"])

    kotipj = pd.json_normalize(
        data['teams']['home']["managersLineUp"])

    vieraspj = pd.json_normalize(
        data['teams']['away']["managersLineUp"])

    kokoonpano = pd.concat(
        [kotikokoopano, vieraskokoopano],  ignore_index=False)
    
    pj = pd.concat(
        [kotipj, vieraspj],  ignore_index=False)
    
    vaihtopenkki = {"koti": data["details"]["OtherRoles:home"],
                    "vieras": data["details"]["OtherRoles:away"]}
    
    vaihtopenkki_norm = pd.json_normalize(vaihtopenkki)
    
def kotarit(data):
    
    kotikokoopano = pd.json_normalize(data['teams']['home']["lineUp"])
    
    kotikokoopano["joukkue"] = data['teams']['home']["shorthand"]
    
    vieraskokoopano = pd.json_normalize(data['teams']['away']["lineUp"])
    
    kotikokoopano["joukkue"] = data['teams']['away']["shorthand"]
    
    kotikokoopano["etenijänimi"] = kotikokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]
        
    kotikokoopano["lyöjänimi"] = kotikokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]
        
    vieraskokoopano["etenijänimi"] = vieraskokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]

    vieraskokoopano["lyöjänimi"] = vieraskokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]

    
    kotieka = data["details"]["scoringContestPlayers:0"]["home"]
    
    vieraseka = data["details"]["scoringContestPlayers:0"]["away"]
    
    kotijatko = data["details"]["scoringContestPlayers:1"]["koti"]
    
    vierasjatko = data["details"]["scoringContestPlayers:1"]["away"]
    
    kotikotari = pd.concat([pd.json_normalize(kotieka), pd.json_normalize(
        kotijatko)])
    
    vieraskotari = pd.concat([pd.json_normalize(vieraseka), pd.json_normalize(
        vierasjatko)])
     
    kotietenijakotari = kotikotari.merge(kotikokoopano[[
        "etenijänimi", "joukkue","originalNumber"]], left_on="runner", right_on="originalNumber")
    
    kotikotarilopullinen = kotietenijakotari.merge(kotikokoopano[[
        "lyöjänimi", "joukkue", "originalNumber"]], left_on="batter", right_on="originalNumber", suffixes=("_etenijä", "_lyöja"))
    
    vierasetenijakotari = vieraskotari.merge(vieraskokoopano[[
        "etenijänimi", "joukkue", "originalNumber"]], left_on="runner", right_on="originalNumber")

    vieraskotarilopullinen = vierasetenijakotari.merge(vieraskokoopano[[
        "lyöjänimi", "joukkue", "originalNumber"]], left_on="batter", right_on="originalNumber", suffixes=("_etenijä", "_lyöja"))
    
    print(pd.concat([kotikotarilopullinen, vieraskotarilopullinen]))
    
    