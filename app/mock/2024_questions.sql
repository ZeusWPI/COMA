INSERT INTO question
(visible, number, title, max_score, max_score_display, solution, body)
VALUES
(true, 1, 'Met de Trein naar Πopia', 1.4142135623730951, '\sqrt{2}',
'129',
'Πopia wil een nieuw treinsysteem bouwen waarmee alle steden verbonden zijn met eventuele tussenverbindingen.
Ze hebben 6 steden, namelijk Cossius, Primus, Logania, Grafius, Somia, Integria.
Aangezien het een bergachtig land is, is er tussen volgende steden geen verbinding mogelijk:

<aside>![](https://pics.zeus.gent/psjqZWsTSEZKKdenFZUCp47C4B035tFbsiRWr329.png "Trein")</aside>

- Somia en Integria
- Cossius en Grafius
- Cossius en Integria
- Primus en Grafius

Spijtig genoeg kennen we niet alle afstanden.

We kennen de afstanden tussen enkele steden.

- Primus en Logania: 9 km
- Primus en Somia: 13 km
- Cossius en Primus: 41 km
- Primus en Integria: 27 km
- Logania en Integria: 31 km
- Logania en Somia: 60 km
- Grafius en Integria: 73 km

Spijtig genoeg kennen we niet alle afstanden.
We weten wel dat Cossius, Primus en Logania zich op een rechthoekige driehoek bevinden met Logania in de rechte hoek.
Bovendien weten we dat Cossius en Grafius allebei even ver zijn van Logania.
Daarnaast weten we ook dat Cossius, Somia, Grafius en Logania een parallellogram vormen.
Hoeveel km aan spoorweg zullen ze minstens moeten aanleggen?'),
(true, 2, 'Shuffle the numbers', 1.7320508075688772, '\sqrt{3}',
'684900085749',
'Op een spelletjesavond van PRIME, spelen we Rummikub met de cijfers 0, ..., 9.
Het getal $s$ is gelegd.
Iemand stelt zich de vraag of we uit het getal $s$, 3 nieuwe getallen $a$, $b$ en $c$ kunnen vormen.
Die elk even veel blokjes bevatten, en waarvoor er hoogstens één nieuw cijfertje eindigt met een 0.
Zij nu $S$ de verzameling van getallen s die bovenstaande eigenschap heeft.

Zoek dan:

$$
\sum_{s \in S \land ||s|| = 9} s
$$'),
(true, 3, 'Sine of Randomness', 2.23606797749979, '\sqrt{5}',
'4517257827071212713525532069616458209838542519110089994064253879499723112448',
'Soms heeft PRIME nood aan een willekeurig getal.
De manier waarop dit gebeurt, is echter interessant.
Eerst nemen we een sinusfunctie van de vorm $sin(tx)$, met $t$ een priemgetal dat vooraf bepaald is.
Deze functie kan altijd ontbonden worden als volgt:

$$
sin(tx) = \sum_{n \in \mathbb{N}} (a_n + b_n sin(x)) cos^n(x)
$$

Het willekeurige getal is dan de som van de coefficiënten $a_k + b_k$, waarbij $k$ het aantal jaar is dat PRIME bestaat.
Voor deze vraag wordt het 18181ste priemgetal gebruikt, namelijk 202409.
Welk willekeurig getal levert dit op als je weet dat PRIME 17 jaar bestaat?'),
(true, 4, 'Tempel van Recursia', 2.6457513110645907, '\sqrt{7}',
'0', -- FIXME can't input 6.647775891514982e+16
'description'),
(true, 5, 'Picknick van Euler', 3.3166247903554, '\sqrt{11}',
'0.33200864284009085',
'description'),
(true, 6, 'Cijfertelling', 3.605551275463989, '\sqrt{13}',
'89381917633561404099965310422218777763578501078967389485040680001239372408621094544659979116513865142102871118215543349638203320057389861701512200423970258862207853198392245807164843575591710312140827872332909850386707935218373601611165099835154674722213586771378176',
'description');
