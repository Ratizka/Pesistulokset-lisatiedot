# Pesistulokset-lisatiedot

Hakee kotariparit, sataako ja tuleeko, kokoonpanot ja muut tiedot ottelusta.

## Vaatimukset

Asenna Python osoitteesta (https://www.python.org/downloads/)

Asenna requests, pandas, beautiful soup kirjastot käyttäen komentokehotetta:

`pip install requests`

`pip install pandas`

`pip install bs4`

## Käyttö

Toimii vain, kun ottelu on livetilassa tai päättynyt. Käyttöliittymä on komentokehoitteinen ja kysyy ottelun id, joka löytyy nettisivujen url:stä. Sen jälkeen kysyy tallennettavat tiedostojen nimet.

`"C:/Users/Lenovo/Documents/Pesäpallo/"`

Vaihtakaa kyseiset tiedostopolut haluamaanne paikkaan.

Sen jälkeen tulee kysely, haluaako suorittaa uudestaan. Paimalla k-kirjainta suorittaa uudelleen ja e-kirjaimella lopettaa. Jos painaa väärää, kysyy uudestaan uutta kirjainta.

Jos kyseisessä sarjassa ei ilmoiteta jatkopareja ennakkoo tai aiemmilta kausilta, käyttäkää ilmanjatkoa versiota.

## Tietoa

Kotariparit ovat merkitty alkuperäisien numeroiden mukaan. Ei pelaajien id:n mukaan.

Jos median puoli ei toimi, vaihtakaa url = ('https://www.pesistulokset.fi/ottelut/'). Ainoa puute on, ettei saa pelaajien syntymäaikaa.
