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
    
    vieraskokoopano["joukkue"] = data['teams']['away']["shorthand"]
    
    kotikokoopano["nimi"] = kotikokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]
        
        
    vieraskokoopano["nimi"] = vieraskokoopano["player.firstName"] + \
        " " + vieraskokoopano["player.lastName"]
    
    kotieka = pd.json_normalize(data["details"]["scoringContestPlayers:0"]["home"])
    
    kotieka["kierros"] = 1
    
    vieraseka = pd.json_normalize(data["details"]["scoringContestPlayers:0"]["away"])
    
    vieraseka["kierros"] = 1
    
    kotijatko = pd.json_normalize(data["details"]["scoringContestPlayers:1"]["home"])
    
    kotijatko["kierros"] = 2
    
    vierasjatko = pd.json_normalize(data["details"]["scoringContestPlayers:1"]["away"])
    
    vierasjatko["kierros"] = 2
    
    kotikotari = pd.concat([kotieka, kotijatko])
    
    vieraskotari = pd.concat([vieraseka, vierasjatko])
     
    kotikotarieka = kotikotari.merge(kotikokoopano[[
        "nimi", "originalNumber"]], left_on="batter", right_on="originalNumber", how="inner", validate="many_to_many")


    kotikotarilopullinen = kotikotarieka.merge(kotikokoopano[[
    "nimi", "originalNumber", "joukkue"]], left_on="runner", right_on="originalNumber", suffixes=("_lyöjä", "_etenijä"), how="inner", validate="many_to_many")

    vieraskotarieka = vieraskotari.merge(vieraskokoopano[[
    "nimi", "originalNumber"]], left_on="batter", right_on="originalNumber", how="inner", validate="many_to_many")

    vieraskotarilopullinen = vieraskotarieka.merge(vieraskokoopano[[
    "nimi", "originalNumber", "joukkue"]], left_on="runner", right_on="originalNumber", suffixes=("_lyöjä", "_etenijä"), how="inner", validate="many_to_many")

    pd.concat([kotikotarilopullinen, vieraskotarilopullinen])

