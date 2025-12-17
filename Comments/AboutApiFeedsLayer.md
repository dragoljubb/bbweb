------------------Flask Api feed sloj
jedno pitanje


ja uzimam podatke iz baze i prikazujem na sajtu

Vidim da evroliga , kao da uzima podatke sa nekog linka tipa:

feeds.incrowdsports.com/putanja-kao-da-je-api-neki-ovde


Pitanje , ako su meni organizovani podaci u tabeli u bazi, kaako su njima?

Kratko:
👉 I oni imaju bazu.
👉 Taj link koji vidiš je API / feed sloj iznad baze, ne “zamena za bazu”.

Kako je to tipično organizovano (kao kod EuroLeague)
1️⃣ Baza (isto kao kod tebe)

relacione tabele / DWH

game, teams, standings, stats

sve normalizovano / optimizovano

👉 ništa se ne servira direktno iz baze

2️⃣ API / Feed servis (to vidiš kao link)

Npr:

feeds.incrowdsports.com/...


To je:

REST / GraphQL / custom feed

često read-only

vraća JSON

keširan (CDN)

Primer toka:

DB → API Service → CDN → Browser

3️⃣ Zašto ne čitaju direktno iz baze

❌ bezbednost

❌ skaliranje (hiljade zahteva)

❌ format (DB ≠ frontend-friendly)

❌ kontrola verzija

Kako to izgleda kod njih u praksi

Backend endpoint:

GET /games?round=15&season=2025


Backend:

SELECT ... FROM games WHERE round = 15;


Frontend:

fetch("https://feeds.incrowdsports.com/...")

Kako TI treba da radiš (isti model)

Ti već imaš:

STG → live / current

DWH → istorija

Dodaj:

4️⃣ Tvoj API sloj

Flask / FastAPI / ASP.NET

Endpoint npr:

/api/games/live
/api/games/upcoming


Frontend:

fetch("/api/games/live")

Bitna razlika

Frontend nikad ne zna da baza postoji

Zna samo za JSON feed

Jedna rečenica za pamćenje

EuroLeague ne “uzima podatke sa linka” –
taj link JE njihov backend iznad baze.

Ako hoćeš, mogu ti:

nacrtati tačnu arhitekturu za tvoj projekat

ili predložiti API endpoint strukturu 1:1 kao EuroLeague feeds

Flask / FastAPI / ASP.NET

Zar mora sd ASP.net, ne moze Flask?

Kratko:
👉 Ne mora ASP.NET. Flask je sasvim OK. ✅

----------------------------