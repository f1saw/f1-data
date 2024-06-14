# f1-data
https://github.com/f1db/f1db


### TODO | MATTE
- [ ] DRIVERS | UI  | drivers / trend => visualizzare nel dropdown solo piloti che hanno vinto mondiali o che hanno dati
- [ ] DRIVERS | UI  | show total podiums count in absolute graph
- [ ] DRIVERS | UI  | absolute => show only min value ; trend => show only select driver
- [ ] DRIVERS | UI  | elencare nome piloti come teams (da mettere anche in seasons)

- [ ]         | FIX | Empty dataset warning
- [ ]         | UI  | add drivers' flag on the top of the bar chart

- [ ] how to put callbacks in different file


### ESPLOSIONI | MAURI
- [ ] mismatch data in teams absolute/trend
- [ ] graphic problem in teams radio button
- [ ] change the data view when hovering over graphs
- [ ] esplosione hovered nel grafico season


### GENERAL
- [ ] mettere valori di default x mostrare qualche grafico al caricamento (es. seasons => hamilton, verstapppen, leclerc)
- [ ] commentare cosa prendono, fanno e restituiscono le funzioni

==================================================================================

-> avendo principalmente variabili numeriche (e non tante categoriali)
  => suggerimento di implementare un grafico per implementare la correlazione (dashboard di esempio es.12-penguins) 
    | es. chi ha il maggior # vittorie in una stagione diventa campione del mondo ?
    | es. chi ha vinto le prime X gare diventa campione del mondo ?
    | es. la squadra che maggior # di 1-2 in una stagione diventa campione dei costruttori ?
    | es. il team del pilota campione del mondo vince anche i costruttori ?
    ( da fare potendo selezionare il range di anni da tenere in considerazioni )

-> x visualizzazione => utilizzare dizionario come in 12-penguins

controllare che non ci siano errori quando tolgo i valori da dropdown (plotly vuole stampare None)

### GOAL
Estrarre più informazioni in minor tempo possibile 

### DATA IDEAs
- Mappa del mondo con nazionalità dei piloti (vedere chi ha più piloti, / chi dovrebbe investire nel motorsport)
- Mappa del mondo per vedere la distribuzione della posizione delle gare (Continenti) al variare degli anni => vedere i paesi che stanno investendo recentemente in motorsport
- Andamento nel tempo della classifica piloti/costruttori di un singolo pilota/team
- Andamento nel tempo del tempo pole per un determinato circuito (colorare i punti in base a come erano le condizioni meteo (ottenute tramite api))
- Storia delle scuderie (minardi > toro rosso > alpha tauri > vcarb)
- Andamento # gare a stagione negli anni
- A partire dall'anno di un grafico (storico andamento pilota in campionato su più anni), clicco su un piazzamento e vedo le informazioni di quell'anno ("zoom sul punto")
- correlazione vincitore corsa e vincitore driver of the day 
- Età media dei piloti negli anni + pilota più giovane e più vecchio 
- [...]

### PPT
- Specificare chi ha fatto cosa (parte estetica, circuiti, piloti, ...)
- Struttura dei dati, come li abbiamo lavorati/uniti (NO grafici in presdentaxione ppt)
