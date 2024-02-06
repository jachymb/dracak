from dataclasses import dataclass
import random
import sys

FIRST_CHOICE = 'a'
MAX_HP = 10

class GameState:
    def __init__(self, current_page, coins):
        self.current_page = current_page
        self.coins = coins
        self.hp = MAX_HP
        self.completed_tasks = set()


@dataclass
class Choice:
    hint: str
    goto_page: str
    consequence_text: str = ""
    entry_cost: int = 0
    hp_gain: int = 0
    coins_gain: int = 0
    required_tasks: frozenset = frozenset()
    forbidden_tasks: frozenset = frozenset()
    completes_task: frozenset = frozenset()

    def execute(self):
        print()
        game_state.coins = max(0, game_state.coins + self.coins_gain - self.entry_cost)
        game_state.hp = min(MAX_HP, game_state.hp + self.hp_gain)
        game_state.current_page = self.goto_page
        game_state.completed_tasks.add(self.completes_task)

        if self.consequence_text: print(self.consequence_text)

    def format(self, i) -> str:
        s = f"{chr(ord(FIRST_CHOICE)+i)}) {self.hint}"
        if self.entry_cost > 0:
            s += f" [Cena: {self.entry_cost}]"
        return s

@dataclass
class Page:
    text: str
    choices: list[Choice]
    choice_random: bool = False

    def parseChoice(self) -> int:
        active_choices = [choice for choice in self.choices
                          if choice.required_tasks <= game_state.completed_tasks
                             and not choice.forbidden_tasks & game_state.completed_tasks]
        assert len(active_choices) > 0  # If this fails, it's a storytelling error and the book needs to be fixed
        print(" | ".join(c.format(i) for i, c in enumerate(active_choices)))
        try:
            s = input("Tvoje volba? ")
            i = ord(s) - ord('a')

            if not 0 <= i < len(active_choices):
                raise ValueError()

            return active_choices[i]
        except (TypeError, ValueError):
            print("Neplatná volba. Zkus to znovu!")
            return self.parseChoice()

    def play(self):
        print(f"Životy {"♥"*game_state.hp}{"♡"*(MAX_HP - game_state.hp)} | Peníze: {"①"*game_state.coins}")

        if game_state.hp <= 0:
            print("Zemřel jsi! Konec hry.")
            sys.exit()

        print(self.text)

        if not self.choices:  # Game over is indicated by no more choices available.
            print("Konec hry.")
            sys.exit()

        elif len(self.choices) == 1:  # When there is only thing to do, there is no choice.
            choice, = self.choices

        elif self.choice_random:
            choice = random.choice(self.choices)

        else:
            while (choice := self.parseChoice()).entry_cost > game_state.coins:
                print("Na to nemáš dost peněz! Vyber jinou možnost.")
        choice.execute()


print("Cílem hry je ukrást alchymistův kouzelný prsten!")

game_state = GameState("start", 5)

book = {
    "start": Page("Stojíš na náměstí, kam se vydáš?", [
        Choice("Hospoda.", "hospoda", "Vydal ses do hospody.", forbidden_tasks={"hospodsky mrtvy"}),
        Choice("Kovárna.", "kovarna", "Vydal jsi se do kovárny."),
        Choice("Temná ulička.", "start", "Přepadli a okradli tě lupiči! Přesile se nedokážeš bránit. Raději ses vrátil na náměstí.", coins_gain=-5, hp_gain=-3),
        Choice("Nevěstinec.", "nevestinec", "Na vstupu jsi zaplatil hlídači, u kterého necháš všechny svoje nebezpečné předměty.", entry_cost=1),
        Choice("Alchymistova laboratoř.", "laborator", "Navštívil jsi alchymistu v jeho laboratoři. Místnost je zaplněná šťiplavým kouřem, až se rozkašleš.", hp_gain=-1, forbidden_tasks={"mrtvy alchymista"}),
        Choice("Statek za městem.", "statek", "Odešel jsi z města navštívit statkáře."),
        Choice("Hřbitov", "hrbitov", "Jdeš si prohlídnout hřbitov.", required_tasks={"mrtvy alchymista"})
    ]),
    "hospoda": Page("Sedíš v hospodě, přijde k tobě hospodský. Co si objednáš?", [
        Choice("Nic, raději odejdu.", "start", "Odešil jsi ven na náměstí."),
        Choice("Pivo.", "hospoda", "Vypil jsi pivo. ", entry_cost=1),
        Choice("Jídlo.", "hospoda:jidlo", "Snědl jsi jídlo a chutnalo ti.", entry_cost=2, hp_gain=2),
        Choice("Panáka.", "hospoda", "Opil jsi se!", entry_cost=3, hp_gain=-1),
        Choice("Zahraju si karty s cizincem.", "hospoda:gamble", entry_cost=1, forbidden_tasks={"cizinec mrtvy"}),
        Choice("Zabiju cizince s kartami!", "start", "Cizince jsi hněvivě zapíchl svojí dýkou. Zbytek hospody se na tebe ale seběhne, zbije tě a vyhodí.", required_tasks={"zbran"}, completes_task="cizinec mrtvy", forbidden_tasks={"cizinec mrtvy"}, hp_gain=-4),
        Choice("Zabiju hospodského!", "start", "Hospodského sis vzal stranou a nenápadně tiše podžízl svou dýkou. V kapsách měl nějaké peníze, které si vezmeš a raději rychle zmizíš. Hospoda nadále již není v provozu.", required_tasks={"zbran"}, completes_task="hospodsky mrtvy", coins_gain=3)
    ]),
    "hospoda:gamble": Page("Vložíš peníz do hry. Hrajete karty... Výsledek hry je, že...", [
        Choice("", "hospoda", "Vyhrál jsi!", coins_gain=2),
        Choice("", "hospoda", "Prohrál jsi svůj vklad!")
    ], choice_random=True),
    "hospoda:jidlo": Page("Chtěl bys dát hospodskému dýško?", [
        Choice("Ne", "hospoda", "Zaplatil jsi normální cenu. Hospodksý se nevrle zamračí, ale nic neřekne."),
        Choice("Ano", "hospoda", "Přihodil jsi peníz navíc. Hospodský se s tebou dá do řeči a poví ti drb, že alchymista má slabost pro slečnu Cecilii.", entry_cost=1, completes_task="dysko")
    ]
    ),
    "statek": Page("Statkář zrovna hledá pomocníka s prací na poli. Nabízí odměnu. Chceš mu pomoci?", [
        Choice("Ne", "start", "Jeho nabídku jsi odmítl. Raději se vrátíš na náměstí."),
        Choice("Ano", "statek", "Celý den jsi dřel na poli, jsi pořádně unavený, ale zaplaceno jsi nakonec dostal.", coins_gain=2, hp_gain=-1)
    ]),
    "kovarna": Page("Kovář prodává zbraně, nářadí i šperky. Chceš si něco koupit?", [
        Choice("Nic.", "start", "Odešel jsi z kovárny zpět na náměstí."),
        Choice("Náhrdelník.", "kovarna", "Koupil jsi krásný dámský náhrdelník.", entry_cost=10, completes_task="nahrdelnik"),
        Choice("Dýka.", "kovarna", "Koupil jsi pěkně ostrou a přitom nenápadnou zbraň.", entry_cost=7, completes_task="zbran"),
        Choice("Páčidlo.", "kovarna", "Dostal jsi páčidlo a uložíš si ho do batohu.", entry_cost=2, completes_task="pacidlo"),
        Choice("Zabiju kováře!", "kovarna", "Kovář ale sundá ze zdi meč a se zbraněmi to umí lépe, než ty!", required_tasks={"zbran"}, hp_gain=-MAX_HP)
    ]),
    "nevestinec": Page("Jsi uvnitř v nevěstinci. Kterou slečnu si vybereš.", [
        Choice("Alice.", "nevestinec:alice", "Dobře sis užil, cítíš se příjemně odreagovaný.", entry_cost=8,),
        Choice("Berta.", "nevestinec:berta", "Jdeš s Bertou do volného pokoje.", entry_cost=9,),
        Choice("Cecilie.", "nevestinec:cecilie", "Slečna je šikovná a milá. Je jasné, proč je nejdražší.", hp_gain=2, entry_cost=11),
        Choice("Žádnou, jdu pryč.", "start", "Opustíš dům, hlídač ti přitom vrátí tvoje věci.")
    ]),
    "nevestinec:alice": Page("Alice ti nabídne dát si ještě jedno kolo, tentokrát se slevou. Máš zájem?", [
        Choice("Ano", "nevestinec:alice", "Napodruhé jsi již neměl dost síly a za mnoho to nestálo.", entry_cost=7),
        Choice("Ne", "nevestinec")
    ]),
    "nevestinec:berta": Page("Jak to ale dopadne? S touto ženou jeden nikdy neví...", [
        Choice("", "nevestinec", "S prací krásné slečny jsi tentokrát velmi spokojen.", hp_gain=2),
        Choice("", "nevestinec", "Slečna se snažila, ale bylo vidět, že je již dnes dost unavená a tak to za moc nestálo."),
        Choice("", "start", "Od Berty jsi chytil nějakou infekci. Potom, co jsi z domu odešel jsi dlouho .", hp_gain=-4),
    ], choice_random=True),
    "nevestinec:cecilie": Page("Cecilie je upovídaná žena. Nabídne ti, že za 3 peníze ti bude vyprávět příběhy ze svého života. Zajímá tě to poslouchat?", [
        Choice("Zaplatím a poslechnu si to.", "nevestinec:cecilie", "Její řeči ti nepřijdou moc zajímavé. Ale když domluví, hezky se na tebe usměje, asi chtěla víc posluchače, než peníze.", completes_task="cecilie", entry_cost=3),
        Choice("Obdaruji ji náhrdelníkem.", "nevestinec", "Cecilie se zaraduje a vypráví sama dál, prořekne se, že za ní občas chodí alchymista, který svůj prsten schovává v truhle.", required_tasks={"dysko", "cecilie", "nahrdelnik"}, completes_task="truhla", forbidden_tasks={"truhla"}),
        Choice("Nemám zájem.", "nevestinec", "Opustíš její pokoj.")
    ]),
    "laborator": Page("Alchymista má vystavené různé podivné předměty. Zeptá se, jesli chceš něco koupit?", [
        Choice("Léčivý lektvar", "start", "Hodíš mu mince, popadneš lektvar a rychle vypadneš vypít ho ven.", hp_gain=MAX_HP, entry_cost=6),
        Choice("Neznámá směs bylin", "laborator", "Zaplatíš, dostaneš byliny, ale pak si uvědomíš, že nevíš co s tím. Alchymista je nevrlý a říká, že to je tvůj problém. Jsou to vyhozené peníze. Znovu se zakuckáš kouřem.", entry_cost=3, hp_gain=-1),
        Choice("Odejdu pryč", "start", "Laboratoř spěšně opustíš."),
        Choice("Zabiju alchymistu!", "laborator:mrtvy", "Alchymista se brání svými kouzly, utržíš četná zranění, ale nakonec ho svou dýkou udoláš.", required_tasks={"zbran"}, completes_task="mrtvy alchymista", hp_gain=-7)
    ]),
    "laborator:mrtvy": Page("Alchymista je mrtvý, ale v jedovatém kouři nemůžeš dlouho zůstat. Stihneš ještě něco udělat?", [
        Choice("Raději vypadnu hned ven.", "start", "Spěšně opustíš laboratoř."),
        Choice("Zkusím v rychlost ukrást co se kde válí.", "start", "Shrábneš nějaké mince pod pultem, ale dlouho nevydržíš.", hp_gain=-1, coins_gain=9),
        Choice("Vypáčím truhlu", "vyhra", "Chvíli kuckáš v kouři, ale nakonec v truhle najdeš kouzelný prsten.", hp_gain=-1, required_tasks={"truhla"})
    ]),
    "hrbitov": Page("Na hřbitově si všimneš nového hrobu: alchymistova. Jeho laboratoř již rozebrali. Uvědomíš si, že k jeho prstenu se již nikdy neodstaneš. Prohrál jsi.", []),
    "vyhra": Page("Získal jsi kouzelný prsten! Zvítězil jsi!", [])
}


if __name__ == "__main__":
    while True:
        book[game_state.current_page].play()