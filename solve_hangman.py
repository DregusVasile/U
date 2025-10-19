# Jocul Spanzuratoarea jucat automat de calculator (fara emoji-uri pentru Windows)

import random
import difflib
import csv
import os

# Maparea pattern-urilor la cuvintele complete (se va incarca din test.csv)
pattern_to_word = {}

# Lista de pattern-uri pentru joc
pattern_list = list(pattern_to_word.keys())

# Lista extinsa de cuvinte populare pentru referinta (se va incarca din dictionary_full.txt)
cuvinte_referinta = []

# Ordinea inteligenta de ghicire a literelor
ORDINE_LITERE = {
'vocale_simple': ['A', 'E', 'I', 'O', 'U'],
'vocale_diacritice': ['Ă', 'Â', 'Î'],
'consoane_populare': ['R', 'T', 'L', 'N', 'C', 'D', 'M', 'P', 'B', 'F', 'G', 'H', 'V'],
'consoane_diacritice': ["Ț","Ș"],
'consoane_rare': ['Q', 'W', 'Z', 'Y', 'X', 'J', 'K', ]
}

def incarca_dictionar(dict_file="dictionary_full.txt"):
    """Incarca dictionarul din fisier"""
    global cuvinte_referinta
    cuvinte_referinta = []
    if os.path.exists(dict_file):
        with open(dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().upper()
                if word:
                    cuvinte_referinta.append(word)
        print(f"Dictionar incarcat: {len(cuvinte_referinta)} cuvinte din {dict_file}")
    else:
        print(f"EROARE: Fisierul dictionar nu exista: {dict_file}")


def incarca_patterns(test_file="test.csv"):
    """Incarca pattern-urile si cuvintele din fisierul CSV"""
    global pattern_to_word, pattern_list
    pattern_to_word = {}
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 3:
                    game_id, pattern, word = row[0].strip(), row[1].strip().upper(), row[2].strip().upper()
                    pattern_to_word[pattern] = word
        pattern_list = list(pattern_to_word.keys())
        print(f"Patterns incarcate: {len(pattern_list)} din {test_file}")
    else:
        print(f"EROARE: Fisierul test nu exista: {test_file}")


def scrie_rezultate_csv(rezultate, output_file="out.csv"):
    """Scrie rezultatele in fisierul CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['game_id', 'total_incercari', 'cuvant_gasit', 'status', 'secventa_incercari'])
        for result in rezultate:
            writer.writerow(result)
    print(f"Rezultate salvate in: {output_file}")


def alegere_pattern():
    return random.choice(pattern_list)


def get_word_from_pattern(pattern):
    return pattern_to_word[pattern]


def get_initial_letters_from_pattern(pattern):
    """Extrage literele cunoscute din pattern"""
    litere_cunoscute = set()
    for i, char in enumerate(pattern):
        if char != '*':
            litere_cunoscute.add(char)
    return litere_cunoscute


def afiseaza_stare(cuvant, litere_ghiciute):
    afisare = ""
    for litera in cuvant:
        if litera in litere_ghiciute:
            afisare += litera
        else:
            afisare += "*"
    return afisare


def litere_distincte(cuvant):
    return set(cuvant)


def calculeaza_similaritate(cuvant1, cuvant2):
    """Calculeaza similaritatea intre doua cuvinte folosind difflib"""
    return difflib.SequenceMatcher(None, cuvant1, cuvant2).ratio()


def gaseste_cuvant_similar_pentru_ghicire(cuvant_curent, litere_ghiciute):
    """Gaseste un cuvant similar din lista de referinta DOAR pentru ghicirea literelor"""
    cuvinte_candidati = []

    for cuvant_ref in cuvinte_referinta:
        if len(cuvant_ref) == len(cuvant_curent):
            similaritate = calculeaza_similaritate(cuvant_curent, cuvant_ref)
            if similaritate > 0.6:  # Mai mult de 60% similaritate
                # Verifica daca literele ghicite se potrivesc
                potrivire = True
                for i, litera in enumerate(cuvant_curent):
                    if litera in litere_ghiciute and cuvant_ref[i] != litera:
                        potrivire = False
                        break
                if potrivire:
                    cuvinte_candidati.append((cuvant_ref, similaritate))

    # Returneaza cuvantul cu cea mai mare similaritate
    if cuvinte_candidati:
        cuvinte_candidati.sort(key=lambda x: x[1], reverse=True)
        cuvant_ales, similaritate = cuvinte_candidati[0]
        return cuvant_ales

    return None


def gaseste_cuvant_complet_din_referinta(cuvant_curent, litere_ghiciute):
    """Gaseste un cuvant complet din lista de referinta care se potriveste cu pattern-ul cunoscut"""
    cuvinte_candidati = []

    for cuvant_ref in cuvinte_referinta:
        if len(cuvant_ref) == len(cuvant_curent):
            # Verifica daca toate literele cunoscute se potrivesc
            potrivire = True
            for i, litera in enumerate(cuvant_curent):
                if litera in litere_ghiciute and cuvant_ref[i] != litera:
                    potrivire = False
                    break

            if potrivire:
                similaritate = calculeaza_similaritate(cuvant_curent, cuvant_ref)
                cuvinte_candidati.append((cuvant_ref, similaritate))

    # Returneaza cuvantul cu cea mai mare similaritate
    if cuvinte_candidati:
        cuvinte_candidati.sort(key=lambda x: x[1], reverse=True)
        cuvant_ales, similaritate = cuvinte_candidati[0]
        return cuvant_ales

    return None


def determina_tip_litera(litera):
    """Determina tipul unei litere pentru strategia inteligenta"""
    if litera in ORDINE_LITERE['vocale_simple']:
        return 'vocale_simple'
    elif litera in ORDINE_LITERE['vocale_diacritice']:
        return 'vocale_diacritice'
    elif litera in ORDINE_LITERE['consoane_populare']:
        return 'consoane_populare'
    elif litera in ORDINE_LITERE['consoane_diacritice']:
        return 'consoane_diacritice'
    elif litera in ORDINE_LITERE['consoane_rare']:
        return 'consoane_rare'
    return 'necunoscut'


def analizeaza_pattern(cuvant, litere_ghiciute):
    """Analizeaza pattern-ul cuvantului pentru a determina strategia"""
    pattern = ""
    for litera in cuvant:
        if litera in litere_ghiciute:
            pattern += litera
        else:
            pattern += "*"

    # Verifica daca avem pattern-uri de tipul e***e
    vocale_ghicite = sum(
        1 for l in litere_ghiciute if l in ORDINE_LITERE['vocale_simple'] + ORDINE_LITERE['vocale_diacritice'])
    consoane_ghicite = sum(1 for l in litere_ghiciute if
                           l in ORDINE_LITERE['consoane_populare'] + ORDINE_LITERE['consoane_diacritice'] +
                           ORDINE_LITERE['consoane_rare'])

    return {
        'pattern': pattern,
        'vocale_ghicite': vocale_ghicite,
        'consoane_ghicite': consoane_ghicite,
        'trebuie_consoane': vocale_ghicite > consoane_ghicite and vocale_ghicite >= 2
    }


def alege_litera_inteligenta(litere_incercate, analiza_pattern, cuvant_similar=None, cuvant_curent=None):
    """Alege urmatoarea litera folosind strategia inteligenta"""

    # Daca avem un cuvant similar, sa ghicim literele in ordinea corecta din cuvantul similar
    if cuvant_similar and cuvant_curent:
        # Gaseste pozitiile unde literele lipsesc in cuvantul curent
        litere_lipsa = []
        for i, litera_curenta in enumerate(cuvant_curent):
            if litera_curenta == '*' and i < len(cuvant_similar):
                litera_din_similar = cuvant_similar[i]
                if litera_din_similar not in litere_incercate:
                    litere_lipsa.append((i, litera_din_similar))

        if litere_lipsa:
            # Sorteaza dupa pozitie pentru a ghici in ordinea corecta
            litere_lipsa.sort(key=lambda x: x[0])
            litera_aleasa = litere_lipsa[0][1]
            return litera_aleasa

    # Daca avem un cuvant similar dar fara pattern, sa ghicim literele din el
    if cuvant_similar:
        litere_din_cuvant_similar = [l for l in cuvant_similar if l not in litere_incercate]
        if litere_din_cuvant_similar:
            # Prioritizeaza literele din cuvantul similar
            return litere_din_cuvant_similar[0]

    # Altfel, foloseste strategia normala
    ordine_prioritati = ['vocale_simple', 'vocale_diacritice', 'consoane_populare', 'consoane_diacritice',
                         'consoane_rare']

    # Daca avem pattern-uri de vocale, sa incercam consoane
    if analiza_pattern['trebuie_consoane']:
        ordine_prioritati = ['consoane_populare', 'consoane_diacritice', 'consoane_rare', 'vocale_simple',
                             'vocale_diacritice']

    for tip_litera in ordine_prioritati:
        litere_disponibile = [l for l in ORDINE_LITERE[tip_litera] if l not in litere_incercate]
        if litere_disponibile:
            return random.choice(litere_disponibile)

    return None


def joaca_spanzuratoarea_pentru_pattern(pattern):
    """Joaca spanzuratoarea pentru un pattern specific - versiune optimizata"""
    cuvant = get_word_from_pattern(pattern)
    litere_de_ghicite = litere_distincte(cuvant)
    litere_ghiciute = get_initial_letters_from_pattern(pattern)
    litere_incercate = set()
    incercari_totale = 0
    cuvant_ghicit_complet = False
    incercari_litere = 0

    # Ghiceste literele de 10 ori
    while incercari_litere < 10 and len(litere_ghiciute) < len(litere_de_ghicite):
        analiza = analizeaza_pattern(cuvant, litere_ghiciute)
        pattern_curent = afiseaza_stare(cuvant, litere_ghiciute)
        cuvant_referinta_pentru_ghicire = gaseste_cuvant_similar_pentru_ghicire(cuvant, litere_ghiciute)
        litera = alege_litera_inteligenta(litere_incercate, analiza, cuvant_referinta_pentru_ghicire, pattern_curent)
        
        if litera is None:
            toate_literele = list(
                ORDINE_LITERE['consoane_populare'] + ORDINE_LITERE['vocale_simple'] +
                ORDINE_LITERE['vocale_diacritice'] + ORDINE_LITERE['consoane_diacritice'])
            litere_noua = [l for l in toate_literele if l not in litere_incercate]
            litera = litere_noua[0] if litere_noua else random.choice(toate_literele)
        
        litere_incercate.add(litera)
        incercari_totale += 1
        incercari_litere += 1
        
        if litera in cuvant:
            litere_ghiciute.add(litera)
        
        if len(litere_ghiciute) == len(litere_de_ghicite):
            cuvant_ghicit_complet = True
            break

    # Dupa 10 incercari de litere, incearca sa ghiceasca cuvantul complet
    if not cuvant_ghicit_complet:
        cuvant_ghicit = gaseste_cuvant_complet_din_referinta(cuvant, litere_ghiciute)
        if cuvant_ghicit == cuvant:
            cuvant_ghicit_complet = True
            litere_ghiciute = litere_distincte(cuvant)
        else:
            incercari_totale += 1

    # Continua cu ghicirea literelor daca nu a ghicit cuvantul complet
    while not cuvant_ghicit_complet and len(litere_ghiciute) < len(litere_de_ghicite):
        analiza = analizeaza_pattern(cuvant, litere_ghiciute)
        pattern_curent = afiseaza_stare(cuvant, litere_ghiciute)
        cuvant_referinta_pentru_ghicire = gaseste_cuvant_similar_pentru_ghicire(cuvant, litere_ghiciute)
        litera = alege_litera_inteligenta(litere_incercate, analiza, cuvant_referinta_pentru_ghicire, pattern_curent)
        
        if litera is None:
            toate_literele = list(
                ORDINE_LITERE['consoane_populare'] + ORDINE_LITERE['vocale_simple'] +
                ORDINE_LITERE['vocale_diacritice'] + ORDINE_LITERE['consoane_diacritice'])
            litere_noua = [l for l in toate_literele if l not in litere_incercate]
            litera = litere_noua[0] if litere_noua else random.choice(toate_literele)
        
        litere_incercate.add(litera)
        incercari_totale += 1
        
        if litera in cuvant:
            litere_ghiciute.add(litera)
        
        if len(litere_ghiciute) == len(litere_de_ghicite):
            cuvant_ghicit_complet = True
            break

    return cuvant_ghicit_complet, incercari_totale


def spanzuratoarea_automat():
    """Joaca spanzuratoarea pentru toate pattern-urile din lista - versiune optimizata"""
    # Incarca datele din fisiere
    incarca_dictionar("dictionary_full.txt")
    incarca_patterns("test.csv")

    # Verifica daca exista pattern-uri de jucat
    if len(pattern_list) == 0:
        print("EROARE: Nu au fost gasite pattern-uri in fisierul test.csv!")
        return

    rezultate = []
    total_incercari = 0
    cuvinte_castigate = 0

    for pattern in pattern_list:
        castigat, incercari = joaca_spanzuratoarea_pentru_pattern(pattern)
        cuvant = get_word_from_pattern(pattern)
        rezultate.append((pattern, cuvant, castigat, incercari))
        total_incercari += incercari
        if castigat:
            cuvinte_castigate += 1

    # Statistici finale
    print(f"Pattern-uri jucate: {len(pattern_list)}")
    print(f"Pattern-uri castigate: {cuvinte_castigate}")
    print(f"Pattern-uri pierdute: {len(pattern_list) - cuvinte_castigate}")
    print(f"Total incercari: {total_incercari}")
    print(f"Media incercari per pattern: {total_incercari / len(pattern_list):.1f}")
    print(f"Rata de succes: {(cuvinte_castigate / len(pattern_list)) * 100:.1f}%")


# Ruleaza jocul automat
if __name__ == "__main__":
    spanzuratoarea_automat()
