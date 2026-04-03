import json
import os
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup


def pyynto(url):
    try:
        vastaus = requests.get(url, timeout=240)
        vastaus.raise_for_status()
        return vastaus.content
    except requests.RequestException as e:
        print(f"Virhe datan haussa: {e}")
        sys.exit(1)


def keitto(html):
    try:
        html_str = html.decode('utf-8')
        soup = BeautifulSoup(html_str, 'html.parser')
        return json.loads(soup.find('script', id='online-match-data').text)
    except AttributeError as e:
        print(f'Virhe: {e}')
        sys.exit(1)


def kokoonpano(data):

    kotikokoopano = pd.json_normalize(data['teams']['home']["lineUp"])

    vieraskokoopano = pd.json_normalize(data['teams']['away']["lineUp"])

    kokoonpano = pd.concat(
        [kotikokoopano, vieraskokoopano],  ignore_index=False)

    return kokoonpano


def johtotoimijat(data):
    kotipj = pd.json_normalize(
        data['teams']['home']["managersLineUp"])

    vieraspj = pd.json_normalize(
        data['teams']['away']["managersLineUp"])

    pj = pd.concat(
        [kotipj, vieraspj],  ignore_index=False)

    vaihtopenkki = {"koti": data["details"]["OtherRoles:home"],
                    "vieras": data["details"]["OtherRoles:away"]}

    vaihtopenkki_norm = pd.json_normalize(vaihtopenkki)

    print(data["details"]["OtherRoles:home"])

    print(data["details"]["OtherRoles:away"])


def kotarit(data):

    kotikokoopano = pd.json_normalize(data['teams']['home']["lineUp"])

    kotikokoopano["joukkue"] = data['teams']['home']["shorthand"]

    vieraskokoopano = pd.json_normalize(data['teams']['away']["lineUp"])

    vieraskokoopano["joukkue"] = data['teams']['away']["shorthand"]

    kotikokoopano["nimi"] = kotikokoopano["player.firstName"] + \
        " " + kotikokoopano["player.lastName"]

    vieraskokoopano["nimi"] = vieraskokoopano["player.firstName"] + \
        " " + vieraskokoopano["player.lastName"]

    kotieka = pd.json_normalize(
        data["details"]["scoringContestPlayers:0"]["home"])

    kotieka["kierros"] = 1

    vieraseka = pd.json_normalize(
        data["details"]["scoringContestPlayers:0"]["away"])

    vieraseka["kierros"] = 1

    kotijatko = pd.json_normalize(
        data["details"]["scoringContestPlayers:1"]["home"])

    kotijatko["kierros"] = 2

    vierasjatko = pd.json_normalize(
        data["details"]["scoringContestPlayers:1"]["away"])

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

    parit = pd.concat([kotikotarilopullinen, vieraskotarilopullinen])

    return parit


def tallennacsv(df, nimi):
    df.to_csv(f'{os.getcwd()}/data/{nimi}.csv', index=False)


def main():

    ottelunId = input("Anna ottelun id: ")

    url = (f'https://v1.pesistulokset.fi/media/ottelu/{ottelunId}')

    req = pyynto(url)

    data = keitto(req)

    lyontijarjestys = kokoonpano(data)

    johtotoimijat(data)

    parit = kotarit(data)

    tallennacsv(lyontijarjestys, ottelunId + "kokoonpano")

    tallennacsv(parit, ottelunId + "kotarit")
    
    while True:
        suoritaUudestaan = input(
            "Suorita ohjelma uudestaan kyllä/ei (k/e): ")
        if suoritaUudestaan.lower() == "k":
            main()
        if suoritaUudestaan.lower() == "e":
            print("Ohjelma suljetaan")
            sys.exit(1)
        else:
            print('Painoit väärää kirjainta')


if __name__ == '__main__':
    main()
