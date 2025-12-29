# Pesistulokset-lisatiedot

Hakee kotariparit ja vaihtopenkillä olevat henkilöt. Tarvittaessa hakee sataako, tuleeko, kokoonpanot ja muut tiedot ottelusta. Ovat näkyvissä tulospalvelussa ja osa on saatavilla rajapinnan kautta, joten suosittelen käyttävän niitä.

## Vaatimukset

Asenna Python osoitteesta <https://www.python.org/downloads/>

Asenna requests, pandas, beautiful soup kirjastot käyttäen komentokehotetta:

`pip install requests`

`pip install pandas`

`pip install bs4`

## Käyttö

Haku toimii vain, kun ottelu on livetilassa tai päättynyt. Käyttöliittymä on komentokehoitteinen ja kysyy ottelun id, joka löytyy osoitteesta 'https://www.pesistulokset.fi/ottelut/*128172*' kursivoituna. Tiedot tallennetaan hakemiston data-kansioon ottelun id mukaan. Esimerkkidata kotiutuskilpailusta löytyy data-kansiosta.

Sen jälkeen tulee kysely, haluaako suorittaa uudestaan. Paimalla k-kirjainta suorittaa uudelleen ja e-kirjaimella lopettaa. Jos painaa väärää, kysyy uudestaan uutta kirjainta.

Jos kyseisessä sarjassa ei ilmoiteta jatkopareja ennakkoon tai on kaudelta 2023 tai aiemmin, käyttäkää ilmanjatkoa versiota.

## Ongelmia

Jos median puoli ei toimi, vaihtakaa url = 'https://v1.pesistulokset.fi/ottelut/'.
