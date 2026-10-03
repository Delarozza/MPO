# Zadanie 1 – Analýza a experimentálne riešenie optimalizačnej úlohy

## Cieľ zadania

Cieľom zadania je analyzovať konkrétnu optimalizačnú úlohu opísanú v aktuálnom vedeckom článku a experimentálne overiť alebo rozšíriť riešenie navrhnuté jeho autormi.

Pri vypracovaní zadania si precvičíte:

- vyhľadávanie a čítanie vedeckej literatúry
- formálny opis optimalizačného problému
- analýzu vlastností problému
- návrh a realizáciu experimentov
- férové porovnávanie optimalizačných algoritmov
- interpretáciu a kritické hodnotenie výsledkov.

Zadanie sa vypracúva v trojiciach.

## Výber vedeckého článku

Vyberte si vedecký článok publikovaný najviac pred piatimi rokmi (rok vydania aspoň 2021). Článok musí opisovať riešenie konkrétnej optimalizačnej úlohy a obsahovať experimentálne výsledky, s ktorými je možné porovnať vaše riešenie.

Vybraný článok musí spĺňať tieto podmienky:

- článok bol publikovaný v recenzovanom časopise alebo na vedeckej konferencii
- riešený problém obsahuje jednoznačne identifikovateľnú optimalizačnú úlohu
- článok uvádza dostatok informácií na implementáciu alebo experimentálne overenie riešenia
- použité dáta alebo problémové inštancie sú dostupné, prípadne je možné vytvoriť ich porovnateľnú náhrad
- experimenty je možné uskutočniť s dostupnými výpočtovými prostriedkami
- článok obsahuje výsledky vhodné na kvantitatívne porovnanie.

Vhodnosť článku a plánovaný rozsah experimentov musí vopred schváliť vyučujúci.

## Analýza optimalizačnej úlohy

Najskôr opíšte optimalizačnú úlohu riešenú v článku. Analýza musí podľa charakteru problému identifikovať najmä:

- praktický význam a kontext problému
- typ problému, napríklad:
  - minimalizačný alebo maximalizačný
  - spojitý alebo diskrétny
  - jedno- alebo viackriteriálny
  - deterministický alebo stochastický
  - statický alebo dynamický
  - s obmedzeniami alebo bez nich
  - black-box alebo white-box
- rozhodovacie premenné
- priestor kandidátnych riešení a spôsob reprezentácie riešenia
- podmienky a obmedzenia prístupných riešení
- účelovú alebo fitness funkciu
- spôsob vyhodnocovania kvality riešení.

Ak článok neuvádza matematickú formuláciu explicitne, vytvorte ju na základe vlastného porozumenia problému.

## Spôsob riešenia

Vyberte si jednu z nasledujúcich možností.

### Variant A – Replikácia výsledkov

Implementujte metódu opísanú v článku a pokúste sa čo najvernejšie zopakovať vybrané experimenty autorov.

Podľa možností použite rovnaké dáta alebo problémové inštancie a rovnakú reprezentáciu riešenia. Nastavenie algoritmu a jeho parametrov môžete prispôsobiť možnostiam výpočtových zdrojov. Ponechajte použité metriky a spôsob vyhodnotenia riešenia.

Ak nie je možné presne zopakovať niektorú časť experimentu, zmenu jasne zdokumentujte a vysvetlite jej možné dôsledky.

Porovnajte svoje výsledky s výsledkami publikovanými v článku. Neočakáva sa, že výsledky budú vždy totožné. Zistené rozdiely však musíte identifikovať, diskutovať a podľa možností vysvetliť.

### Variant B – Návrh vlastného riešenia

Navrhnite a implementujte vlastný spôsob riešenia optimalizačnej úlohy. Môžete napríklad použiť iný optimalizačný algoritmus (netreba vytvoriť vedecky novú optimalizačnú metódu), alebo iba upraviť metódu navrhnutú autormi. Pri riešení tiež môžete zmeniť reprezentáciu kandidátnych riešení, v takom prípade ale nezabudnite za prípadnú transformáciu.

Vlastné riešenie porovnajte minimálne s hlavnou metódou alebo výsledkami uvedenými v článku. Zvolený spôsob porovnania musí umožňovať posúdiť, či a za akých podmienok je vaše riešenie lepšie alebo horšie. Dbajte na to, aby porovnávanie bolo férové (napríklad porovnanie populačného algoritmu s jednoduchým prehľadávaním).

## Experimentálna metodológia

Experimenty musia byť navrhnuté tak, aby bolo porovnanie metód čo najviac férové. Porovnávané metódy preto majú používať rovnaké:

- problémové inštancie a vstupné dáta
- spôsob vyhodnocovania riešení
- výpočtové obmedzenie, napríklad počet vyhodnotení účelovej funkcie alebo časový limit
- kritériá ukončenia.

Pri stochastických algoritmoch vykonajte každý experiment opakovane s rôznymi počiatočnými stavmi generátora náhodných čísel. Uveďte počet behov a použité hodnoty `seed`. Výsledky prezentujte pomocou vhodných súhrnných štatistík, napríklad priemeru, mediánu, smerodajnej odchýlky, minima a maxima.

Samotná hodnota najlepšieho nájdeného riešenia nemusí byť postačujúca. Sledujte aj stabilitu výsledkov, konvergenciu algoritmu, čas výpočtu a úspešnosť nájdenia prípustného riešenia.

## Odovzdávka

Odovzdávka bude obsahovať nasledujúce časti.

### Zdrojový kód

- zdrojové súbory potrebné na vykonanie experimentov;
- skript alebo jednoznačný príkaz na spustenie experimentov;
- súbor so závislosťami (requirements) a ich verziami;
- konfiguračné súbory s použitými parametrami;
- súbor `README` s návodom na prípravu prostredia a spustenie riešenia.

### Záverečný report

Report musí obsahovať:

1. abstrakt;
2. opis a význam riešeného problému;
3. formuláciu optimalizačnej úlohy;
4. opis metódy autorov článku;
5. opis vašej implementácie alebo vlastného riešenia;
6. prehľad rozdielov oproti pôvodnému článku;
7. experimentálnu metodológiu;
8. dosiahnuté výsledky;
9. porovnanie s výsledkami autorov;
10. diskusiu výsledkov a možných zdrojov rozdielov;
11. obmedzenia vykonaných experimentov;
12. záver;
13. zoznam použitej literatúry.

Výsledky prezentujte pomocou vhodných tabuliek a grafov. Každá tabuľka a graf musia mať popis a musia byť interpretované v texte.

Rozsah záverečného reportu: 6–10 strán (A4) bez príloh.

## Používanie existujúcich implementácií a nástrojov

Použitie knižníc a verejne dostupného zdrojového kódu je dovolené, musí však byť riadne uvedené a citované. Z odovzdaného riešenia musí byť zrejmé, ktoré časti vytvorili autori článku, ktoré pochádzajú z externých zdrojov a ktoré ste vytvorili alebo upravili vy. Rovnaké zásady platia pri používaní nástrojov generatívnej umelej inteligencie.

**Použitie existujúcej implementácie nesmie nahradiť vlastnú analýzu problému, návrh experimentov a interpretáciu výsledkov.**

## Obhajoba
Každý člen tímu musí preukázať porozumenie celému riešeniu a vedieť vysvetliť zdrojový kód, nastavenie experimentov aj interpretáciu výsledkov.

Súčasťou obhajoby môže byť diskusia o tom, ako by zmena parametrov, výpočtového rozpočtu alebo vlastností problému ovplyvnila správanie algoritmu.

## Hodnotenie

Za zadanie je možné získať 10 bodov:

- analýza optimalizačného problému – 2 body;
- implementácia a reprodukovateľnosť riešenia – 2 body;
- kvalita experimentálnej metodológie – 2 body;
- vyhodnotenie a interpretácia výsledkov – 2 body;
- obhajoba a diskusia – 2 body.

Pri hodnotení sa nebude posudzovať iba to, či navrhnutá metóda dosiahla lepšie výsledky ako metóda z článku. Dôležitejšia je správnosť implementácie, kvalita experimentálneho porovnania, schopnosť kriticky interpretovať výsledky a reprodukovateľnosť riešenia.

Neúspešný pokus o replikáciu alebo vlastná metóda s horšími výsledkami môžu získať plný počet bodov, ak je postup metodologicky správny, výsledky sú dôkladne analyzované a závery zodpovedajú získaným dôkazom.