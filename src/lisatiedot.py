import json
import os
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup


def pyynto(url):
    try:
        vastaus = requests.get(url, timeout = 240)
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
        
        return data
    except AttributeError as e:
        print(f'Virhe: {e}')
        sys.exit(1)


def data_muokkaus(data):
    try:

        koti = pd.json_normalize(data['teams']['home'], record_path=['lineUp'],
                                 meta=['id', 'name', 'shorthand', 'icon', 'logo'])

        koti_pelinjohtajat = pd.json_normalize(
            data['teams']['home'], record_path=['managersLineUp'])

        koti_kaarten_vali = pd.json_normalize(data['details'], record_path=[
                                              "innerCircle_home"], meta=['id'], record_prefix='sisäkaari_', errors='ignore')

        kotivalmennus = pd.json_normalize(data['details'], record_path=[
                                          "OtherRoles:home"], record_prefix='valmennus', errors='ignore')

        kotivalmennus.columns = ['valmennuskoti']

        vieras = pd.json_normalize(data['teams']['away'], record_path=['lineUp'],
                                   meta=['id', 'name', 'shorthand', 'icon', 'logo'])

        vieras_pelinjohtajat = pd.json_normalize(
            data['teams']['away'], record_path=['managersLineUp'])

        vieras_kaarten_vali = pd.json_normalize(data['details'], record_path=[
                                                "innerCircle_away"], meta=['id'], record_prefix='sisäkaari_', errors='ignore')

        vierasvalmennus = pd.json_normalize(data['details'], record_path=[
                                            "OtherRoles:away"], record_prefix='valmennus', errors='ignore')

        vierasvalmennus.columns = ['valmennusvieras']

        kotijoukkue_pelinjohto = pd.merge(
            koti_pelinjohtajat, koti_kaarten_vali, left_on='manager.id', right_on='sisäkaari_id', how='outer')

        vierasjoukkue_pelinjohto = pd.merge(
            vieras_pelinjohtajat, vieras_kaarten_vali, left_on='manager.id', right_on='sisäkaari_id', how='outer')

        koti_kotiutuslyönti = pd.json_normalize(
            data['details']["scoringContestPlayers:0"], record_path=['home'], record_prefix='koti_')

        vieras_kotiutuslyönti = pd.json_normalize(
            data['details']["scoringContestPlayers:0"], record_path=['away'], record_prefix='vieras_')

        koti_kotiutuslyöntijatkot = pd.json_normalize(
            data['details']["scoringContestPlayers:1"], record_path=['home'], record_prefix='kotijatko_')

        vieras_kotiutuslyöntijatkot = pd.json_normalize(
            data['details']["scoringContestPlayers:1"], record_path=['away'], record_prefix='vierasjatko_')

        muut_tiedot = pd.json_normalize(data['details'], errors='ignore')

        kokoonpano = pd.concat([koti, vieras],  ignore_index=False)

        kotarit = pd.concat([koti_kotiutuslyönti, vieras_kotiutuslyönti, koti_kotiutuslyöntijatkot,
                            vieras_kotiutuslyöntijatkot],  axis=1, ignore_index=False)

        pelinjohto = pd.concat(
            [kotijoukkue_pelinjohto, vierasjoukkue_pelinjohto], ignore_index=False)

        valmennus = pd.concat([kotivalmennus, vierasvalmennus],
                              axis=1, join='outer', ignore_index=False)

        return (kokoonpano, kotarit, pelinjohto, valmennus, muut_tiedot)
    except (TypeError, KeyError) as e:
        print(f'Virhe {e}')


def kotarit(data):

    kotikokoopano = pd.json_normalize(data['teams']['home']["lineUp"])

    kotikokoopano["joukkue"] = data['teams']['home']["shorthand"]

    kotikokoopano["joukkueid"] = data['teams']['home']["id"]

    vieraskokoopano = pd.json_normalize(data['teams']['away']["lineUp"])

    vieraskokoopano["joukkue"] = data['teams']['away']["shorthand"]

    vieraskokoopano["joukkueid"] = data['teams']['away']["id"]

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

    kotikotarieka = kotikotari.merge(kotikokoopano[["joukkueid", "originalNumber", "player.id", "nimi"]], left_on="batter",
                                     right_on = "originalNumber", how = "inner", validate = "many_to_many")

    kotikotarilopullinen = kotikotarieka.merge(kotikokoopano[["originalNumber", "player.id", "nimi"]],
                                               left_on = "runner", right_on = "originalNumber",
                                               suffixes = ("_lyoja", "_etenija"), how = "inner", validate = "many_to_many")

    vieraskotarieka = vieraskotari.merge(vieraskokoopano[["joukkueid", "originalNumber", "player.id", "nimi"]],
                                         left_on = "batter", right_on = "originalNumber", how = "inner", validate = "many_to_many")

    vieraskotarilopullinen = vieraskotarieka.merge(vieraskokoopano[["originalNumber", "player.id", "nimi"]],
                                                   left_on = "runner", right_on = "originalNumber",
                                                   suffixes = ("_lyoja", "_etenija"), how = "inner", validate = "many_to_many")

    return pd.concat([kotikotarilopullinen, vieraskotarilopullinen])


def taulukon_teko(dataframe):
    try:
        taulukko = pd.DataFrame(dataframe)
        return taulukko
    except (UnboundLocalError, KeyError, AttributeError, TypeError, ValueError) as e:
        print(f"Virhe Taulukon:n muodostamisessa: {e}")


def tallenna_csv(dataframe, tiedostonimi):
    try:
        dataframe.to_csv(f'{os.getcwd()}/data/{tiedostonimi}.csv', index=False)
        print('CSV-tiedosto luotu onnistuneesti')
    except (FileNotFoundError, PermissionError, ValueError, AttributeError) as e:
        print(f"Virhe CSV:n tallentamisessa: {e}")


def main():

    ottelunId = input("Anna ottelun id: ")

    ottelunUrl = (f'https://v1.pesistulokset.fi/media/ottelu/{ottelunId}')

    hae_data = pyynto(ottelunUrl)

    hae_tiedot = keitto(hae_data)
    
    kotiutuskilpailu = kotarit(hae_tiedot)
    
    tallenna_csv(kotiutuskilpailu, f'{ottelunId}kotarit')
    

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


main()
