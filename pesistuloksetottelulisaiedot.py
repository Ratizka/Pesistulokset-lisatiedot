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
        soup = BeautifulSoup(html_str,'html.parser')
        data = json.loads(soup.find('script', id='online-match-data').text)
        return(data)
    except AttributeError as e:
        print(f'Virhe: {e}')


def datan_tallennus(data, nimi):
    try:
        with open("C:/Users/Lenovo/Documents/Pesäpallo/" + nimi, "w", encoding="utf-8") as tiedosto:
            json.dump(data, tiedosto, ensure_ascii=False, indent=4)
        print("JSON-tiedosto tallennettu onnistuneesti!")
    except FileNotFoundError:
        print(f"Tiedostoa ei löydy: {nimi}")
        sys.exit(1)
    
    
def lue_json(polku):
    try:
        with open("C:/Users/Lenovo/Documents/Pesäpallo/" + polku, "r", encoding="utf-8") as tiedosto:
            tiedosto_sisältö = tiedosto.read()
            print("JSON-tiedosto luettu onnistuneesti!")
            return json.loads(tiedosto_sisältö)
    except FileNotFoundError:
        print(f"Tiedostoa ei löydy: {polku}")
        sys.exit(1)

def data_muokkaus(data):
    try:
        
        koti = pd.json_normalize(data['teams']['home'], record_path=['lineUp'], 
                            meta=['id', 'name', 'shorthand', 'icon', 'logo'])
        
        koti_pelinjohtajat = pd.json_normalize(data['teams']['home'], record_path=['managersLineUp'])
        
        koti_kaarten_väli = pd.json_normalize(data['details'], record_path=["innerCircle_home"], meta=['id'], record_prefix='sisäkaari_', errors='ignore')
        
        kotivalmennus = pd.json_normalize(data['details'], record_path=["OtherRoles:home"], record_prefix='valmennus', errors='ignore')
        
        kotivalmennus.columns = ['valmennuskoti']
        
        vieras = pd.json_normalize(data['teams']['away'], record_path=['lineUp'], 
                            meta=['id', 'name', 'shorthand', 'icon', 'logo'])
        
        vieras_pelinjohtajat = pd.json_normalize(data['teams']['away'], record_path=['managersLineUp'])

        vieras_kaarten_väli = pd.json_normalize(data['details'], record_path=["innerCircle_away"], meta=['id'], record_prefix='sisäkaari_', errors='ignore')
    
        vierasvalmennus = pd.json_normalize(data['details'], record_path=["OtherRoles:away"], record_prefix='valmennus' ,errors='ignore')

        vierasvalmennus.columns = ['valmennusvieras']
        
        kotijoukkue_pelinjohto = pd.merge(koti_pelinjohtajat, koti_kaarten_väli, left_on='manager.id', right_on='sisäkaari_id', how='outer')

        vierasjoukkue_pelinjohto = pd.merge(vieras_pelinjohtajat, vieras_kaarten_väli, left_on='manager.id', right_on='sisäkaari_id', how='outer')
        
        koti_kotiutuslyönti = pd.json_normalize(data['details']["scoringContestPlayers:0"], record_path=['home'], record_prefix='koti_')

        vieras_kotiutuslyönti = pd.json_normalize(data['details']["scoringContestPlayers:0"], record_path=['away'], record_prefix='vieras_')

        koti_kotiutuslyöntijatkot = pd.json_normalize(data['details']["scoringContestPlayers:1"], record_path=['home'], record_prefix='kotijatko_')

        vieras_kotiutuslyöntijatkot = pd.json_normalize(data['details']["scoringContestPlayers:1"], record_path=['away'],record_prefix='vierasjatko_')

        muut_tiedot = pd.json_normalize(data['details'], errors = 'ignore')

        kokoonpano = pd.concat([koti, vieras],  ignore_index=False)
        
        kotarit = pd.concat([koti_kotiutuslyönti,vieras_kotiutuslyönti, koti_kotiutuslyöntijatkot, vieras_kotiutuslyöntijatkot],  axis=1, ignore_index=False)
        
        pelinjohto = pd.concat([kotijoukkue_pelinjohto,vierasjoukkue_pelinjohto], ignore_index=False)

        valmennus = pd.concat([kotivalmennus,vierasvalmennus],  axis=1, join='outer', ignore_index=False)
        
        return(kokoonpano, kotarit, pelinjohto, valmennus, muut_tiedot)
    except TypeError as e:
        print(f'Virhe {e}')
        
def taulukon_teko(dataframe):
    try:
        taulukko = pd.DataFrame(dataframe)
        print('Taulukko muodostettu')
        return(taulukko)
    except (UnboundLocalError, KeyError, AttributeError, TypeError, ValueError) as e:
        print(f"Virhe Taulukon:n muodostamisessa: {e}")
 
def tallenna_csv(dataframe, polku):
    try:
        dataframe.to_csv(
            "C:/Users/Lenovo/Documents/Pesäpallo/" + polku + '.csv', index=False)
        print('CSV-tiedosto luotu onnistuneesti')
    except (FileNotFoundError, PermissionError, ValueError, AttributeError) as e:
        print(f"Virhe CSV:n tallentamisessa: {e}")
        sys.exit(1)

        
def main():
    
    ottelunId = input("Anna ottelun id: ")

    ottelunUrl = ('https://www.pesistulokset.fi/media/ottelu/' + ottelunId)

    hae_data = pyynto(ottelunUrl)
    
    tiedot = keitto(hae_data)
    
    ottelunJsonTiedosto = input(
        "Anna ottelun json-tiedoston nimi ilman .json-päätettä: ")

    ottelunCsvTiedosto = input(
        "Anna ottelun json-tiedostosta luotavan csv-tiedoston nimi ilman .csv päätettä: ")
    
    kokoonpano_nimi = ottelunCsvTiedosto + '_kokoonpano'
    
    kotari_nimi = ottelunCsvTiedosto + '_kotarit'
    
    pelinjohto_nimi = ottelunCsvTiedosto + '_pelinjohto'
    
    valmennus_nimi =  ottelunCsvTiedosto + '_valmennus'

    muut_nimi =  ottelunCsvTiedosto + '_tiedot'

    datan_tallennus(tiedot, ottelunJsonTiedosto + ".json")

    json_tiedostosta = lue_json(ottelunJsonTiedosto + ".json")
    
    kokoonpano, kotarit, pelinjohto, valmennus, muut_tiedot = data_muokkaus(json_tiedostosta)

    joukkue_kokoopanot = taulukon_teko(kokoonpano)
    
    tallenna_csv(joukkue_kokoopanot, kokoonpano_nimi)
    
    kotariparit = taulukon_teko(kotarit)
    
    tallenna_csv(kotariparit, kotari_nimi)
    
    pelinjohto_tiedot = taulukon_teko(pelinjohto)
    
    tallenna_csv(pelinjohto_tiedot, pelinjohto_nimi)
    
    valmennus_tiedot = taulukon_teko(valmennus)
    
    tallenna_csv(valmennus_tiedot, valmennus_nimi)

    tiedot = taulukon_teko(muut_tiedot)

    tallenna_csv(tiedot, muut_nimi)

    
main()
