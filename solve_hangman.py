# -*- coding: utf-8 -*-
from collections import Counter
import csv
import os
import difflib
import sys

# Alfabetul românesc complet pentru a ne asigura că încercăm toate literele posibile
ROMANIAN_FULL_ALPHABET = (
    list('AEIOUĂÂÎ') +  # Vocale și vocale cu diacritice
    list('RTNLSCMDPBVGFH') +  # Consoane frecvente și medii
    list('ȘȚZJXYWKQ')  # Consoane rare și foarte rare
)

# Ordine optimizată de ghicire (ROMÂNĂ) - bazată pe frecvența în dicționar
ORDINE_LITERE = {
    'vocale_frecvente': ['A', 'E', 'I'],
    'consoane_foarte_frecvente': ['R', 'T', 'N', 'S', 'L'],
    'vocale_medii': ['O', 'U'],
    'consoane_frecvente': ['C', 'M', 'P', 'D'],
    'diacritice_frecvente': ['Ă', 'Î'],
    'consoane_medii': ['B', 'V', 'G', 'F'],
    'diacritice_rare': ['Ș', 'Ț', 'Â'],
    'consoane_rare': ['H', 'Z', 'J'],
    'extrem_rare': ['X', 'Y', 'Q', 'W']
}

# Lista optimizată pentru primele încercări - reorganizată pentru eficiență maximă
ORDINE_INIȚIALĂ = ['A', 'E', 'I', 'R', 'T', 'S', 'N', 'L', 'O', 'C', 'M', 'P']

def normalize(s: str) -> str:
    """Normalizează string: uppercase și strip"""
    if s is None:
        return ''
    return s.strip().upper()

def read_input_csv(path: str):
    """Citește CSV-ul de intrare și validează rândurile."""
    valid = []
    errors = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for lineno, row in enumerate(reader, start=1):
            if not row:
                errors.append((lineno, 'linie goală'))
                continue
            if len(row) < 3:
                errors.append((lineno, f'campuri insuficiente: {len(row)}'))
                continue
            game_id = normalize(row[0])
            pattern_initial = normalize(row[1])
            cuvant_tinta = normalize(row[2])
            
            if not all([game_id, pattern_initial, cuvant_tinta]):
                errors.append((lineno, 'câmp gol'))
                continue
                
            if len(pattern_initial) != len(cuvant_tinta):
                errors.append((lineno, 'lungimi pattern_initial și cuvant_tinta neconcordante'))
                continue
                
            valid.append((game_id, pattern_initial, cuvant_tinta))
    return valid, errors

def load_dictionary(path: str = None):
    """Încarcă dicționarul de cuvinte."""
    dict_words = []
    if path and os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for ln in f:
                w = ln.strip()
                if w:
                    dict_words.append(normalize(w))
    return dict_words

def pattern_matches(word: str, pattern: str) -> bool:
    """Verifică dacă un cuvânt se potrivește cu un pattern."""
    if len(word) != len(pattern):
        return False
    return all(p == '*' or p == w for w, p in zip(word, pattern))

def find_matching_words(pattern: str, dictionary: list) -> set:
    """Găsește toate cuvintele din dicționar care se potrivesc cu pattern-ul."""
    matches = set()
    known_positions = {i: c for i, c in enumerate(pattern) if c != '*'}
    
    for word in dictionary:
        if len(word) != len(pattern):
            continue
            
        # Verifică mai întâi pozițiile cunoscute pentru eficiență
        valid = True
        for pos, char in known_positions.items():
            if word[pos] != char:
                valid = False
                break
                
        if valid:
            matches.add(word)
            
    return matches

def calculate_letter_score(letter: str, pattern: str, matching_words: set, position: int) -> int:
    """Calculează un scor pentru o literă bazat pe frecvență și poziție."""
    score = 0
    word_length = len(pattern)
    asterisks = pattern.count('*')
    
    # Scor bazat pe frecvența în cuvintele potrivite și poziție
    pos_count = 0
    total_count = 0
    positions_freq = Counter()
    
    for word in matching_words:
        if letter in word:
            letter_positions = [i for i, c in enumerate(word) if c == letter]
            total_count += len(letter_positions)
            for pos in letter_positions:
                positions_freq[pos] += 1
            if position < len(word) and word[position] == letter:
                pos_count += 1
    
    if total_count > 0:
        # Scor bazat pe frecvența totală ajustată
        score += total_count * (1 + (pos_count / (total_count + 1)))
        # Bonus pentru frecvența în poziția specifică
        if pos_count > 0:
            score += pos_count * 4
        # Bonus pentru distribuția pozițională
        if len(positions_freq) > 1:
            score += len(positions_freq) * 2
    
    # Ajustări bazate pe progres și context
    progress = 1 - (asterisks / word_length)
    
    # Strategii bazate pe stadiul jocului
    if progress < 0.25:  # Început de joc
        if letter in 'AEI':
            score += 5
        elif letter in 'RTNS':
            score += 4
        elif letter in 'LCMP':
            score += 3
    elif progress < 0.5:  # Mijloc timpuriu
        if letter in 'RTNLSCMDP':
            score += 4
        elif letter in 'OU':
            score += 3
    elif progress < 0.75:  # Mijloc târziu
        if letter in 'ĂÎÂȘȚ':
            score += 4
        elif letter in 'BVGF':
            score += 3
    else:  # Final de joc
        if letter in 'ĂÎÂȘȚHJZ':
            score += 5
            
    # Ajustări pentru lungimea cuvântului
    if word_length <= 5:
        if letter in 'AEIOU':
            score += 3
    elif word_length >= 8:
        if letter in 'RTNLSCMD':
            score += 3
            
    # Penalizări pentru litere rare
    if letter in 'XYQ':
        score -= 5
    elif letter in 'WK':
        score -= 4
    
    return score

def get_next_guess(pattern: str, matching_words: set, used_letters: set) -> str:
    """Alege următoarea literă folosind o strategie inteligentă."""
    # Primele 10 ghiciri: folosește ordinea predefinită
    if len(used_letters) < 10:
        for letter in ORDINE_INIȚIALĂ:
            if letter not in used_letters and letter not in pattern:
                return letter
    
    # După 10 ghiciri sau dacă toate literele inițiale au fost folosite
    # Calculează scoruri pentru fiecare poziție cu '*'
    position_scores = {}
    asterisk_positions = [i for i, c in enumerate(pattern) if c == '*']
    
    if matching_words:
        # Pentru fiecare poziție cu '*', găsește cea mai bună literă
        for pos in asterisk_positions:
            letter_scores = {}
            for word in matching_words:
                if pos < len(word):
                    letter = word[pos]
                    if letter not in used_letters and letter not in pattern:
                        score = calculate_letter_score(letter, pattern, matching_words, pos)
                        letter_scores[letter] = letter_scores.get(letter, 0) + score
            if letter_scores:
                best_letter = max(letter_scores.items(), key=lambda x: x[1])
                position_scores[pos] = best_letter

        # Alege perechea poziție-literă cu cel mai mare scor
        if position_scores:
            best_position = max(position_scores.items(), key=lambda x: x[1][1])[0]
            return position_scores[best_position][0]

    # Fallback: folosește frecvențele literelor în cuvintele rămase
    if matching_words:
        letter_freqs = Counter()
        for word in matching_words:
            for i, c in enumerate(word):
                if pattern[i] == '*' and c not in used_letters:
                    letter_freqs[c] += 1
        
        if letter_freqs:
            return max(letter_freqs.items(), key=lambda x: x[1])[0]

    # Fallback mai agresiv: încearcă toate literele rămase din alfabetul românesc
    remaining_letters = [l for l in ROMANIAN_FULL_ALPHABET 
                        if l not in used_letters and l not in pattern]
    
    if remaining_letters:
        # Sortează literele rămase după frecvența generală în limba română
        letter_scores = {
            l: (4 if l in 'AEI' else
                3 if l in 'RTNLS' else
                2 if l in 'OUĂÂÎCMDP' else
                1)
            for l in remaining_letters
        }
        return max(remaining_letters, key=lambda l: letter_scores[l])
            
    return None

def solve_hangman(target_word: str, pattern: str, dictionary: list):
    """Rezolvă o instanță de spânzurătoarea."""
    remaining_pattern = pattern
    used_letters = set()
    attempts = []
    found = False
    
    # Extrage literele deja cunoscute din pattern
    known_letters = {c for c in pattern if c != '*'}
    used_letters.update(known_letters)

    matching_words = find_matching_words(pattern, dictionary)
    word_length = len(pattern)
    
    # Strategia super-agresivă pentru cuvinte foarte scurte (≤3)
    if word_length <= 3 and matching_words:
        # Pentru cuvinte foarte scurte, încearcă toate cuvintele posibile în ordine
        sorted_candidates = sorted(matching_words, 
            key=lambda w: (sum(3 if c in 'AEI' else 2 if c in 'RTNLS' else 1 for c in w), w))
        for guess in sorted_candidates:
            if guess == target_word:
                found = True
                remaining_pattern = target_word
                return found, attempts, remaining_pattern
    
    # Strategia agresivă pentru cuvinte scurte (4-5)
    elif word_length <= 5 and matching_words:
        if len(matching_words) <= 3:
            # Folosește similaritatea pentru a ghici cuvântul cel mai probabil
            guess = max(matching_words, 
                key=lambda w: (sum(3 if c in 'AEIOU' else 2 if c in 'RTNLS' else 1 for c in w),
                              sum(1 for c in w if c in known_letters)))
            if guess == target_word:
                found = True
                remaining_pattern = target_word
                return found, attempts, remaining_pattern
                
    # Strategia moderată pentru cuvinte medii (6-7)
    elif word_length <= 7 and matching_words:
        if len(matching_words) <= 2:
            # Încearcă cuvintele candidate în ordine de probabilitate
            for guess in sorted(matching_words,
                key=lambda w: (sum(1 for c in w if c in known_letters), 
                             sum(2 if c in 'AEIOURTNLS' else 1 for c in w))):
                if guess == target_word:
                    found = True
                    remaining_pattern = target_word
                    return found, attempts, remaining_pattern

    # Bucla principală de ghicire cu strategie îmbunătățită
    while True:
        # Recalculează cuvintele potrivite la fiecare iterație pentru precizie maximă
        matching_words = find_matching_words(remaining_pattern, dictionary)
        
        # Strategii de ghicire pentru diferite scenarii
        if matching_words:
            if len(matching_words) <= 3:
                # Sortăm candidații după probabilitate și încercăm pe rând
                sorted_candidates = sorted(matching_words,
                    key=lambda w: (
                        sum(1 for c in w if c in known_letters),  # Mai întâi după literele cunoscute
                        sum(3 if c in 'AEIOU' else 2 if c in 'RTNLS' else 1 for c in w),  # Apoi după frecvența literelor
                        len(set(w) & set('ĂÂÎȘȚ')),  # Bonus pentru diacritice
                        -len(set(w) & set('XYWQ'))  # Penalizare pentru litere rare
                    ),
                    reverse=True
                )
                
                # Încercăm fiecare candidat în ordinea probabilității
                for guess in sorted_candidates:
                    if guess == target_word:
                        found = True
                        remaining_pattern = target_word
                        break
                if found:
                    break

        next_letter = get_next_guess(remaining_pattern, matching_words, used_letters)
        if next_letter is None:
            break

        attempts.append(next_letter)
        used_letters.add(next_letter)

        if next_letter in target_word:
            # Actualizează pattern-ul cu litera ghicită corect
            new_pattern = ''
            for i, (p, t) in enumerate(zip(remaining_pattern, target_word)):
                if p != '*':
                    new_pattern += p
                elif t == next_letter:
                    new_pattern += t
                else:
                    new_pattern += '*'
            remaining_pattern = new_pattern

            if remaining_pattern == target_word:
                found = True
                break

        # Actualizează cuvintele potrivite bazat pe noul pattern
        matching_words = find_matching_words(remaining_pattern, matching_words if matching_words else dictionary)

        # Strategii de ghicire mai agresive pe măsură ce avansăm
        asterisks = remaining_pattern.count('*')
        known_count = len(remaining_pattern) - asterisks
        
        # Cu cât avem mai multe litere cunoscute, cu atât suntem mai agresivi în încercări
        if known_count >= len(remaining_pattern) * 0.4:  # 40% sau mai mult cunoscut
            if matching_words:
                # Sortăm candidații după similitudinea cu pattern-ul și frecvența literelor
                candidates = sorted(matching_words,
                    key=lambda w: (
                        sum(1 for c in w if c in known_letters),  # Prioritate la cuvinte cu litere cunoscute
                        -sum(1 for c in w if c not in used_letters),  # Preferăm cuvinte cu mai puține litere necunoscute
                        sum(3 if c in 'AEIOU' else 2 if c in 'RTNLS' else 1 for c in w)  # Scor pe frecvența literelor
                    ),
                    reverse=True
                )
                
                # Încercăm toate cuvintele candidate până găsim unul corect
                for guess in candidates:
                    if guess == target_word:
                        found = True
                        remaining_pattern = target_word
                        break
                
        # Dacă nu mai sunt candidați sau am rămas cu puține litere de încercat
        if not matching_words or len(used_letters) >= 25:  # Aproape tot alfabetul încercat
            # Reîncarcă dicționarul și încearcă din nou
            matching_words = find_matching_words(remaining_pattern, dictionary)
            # Încearcă să ghicești direct din cuvintele rămase
            if matching_words:
                # Sortează după probabilitate și încearcă fiecare
                candidates = sorted(matching_words,
                    key=lambda w: sum(3 if c in 'AEIOU' else 2 if c in 'RTNLS' else 1 for c in w),
                    reverse=True
                )
                for guess in candidates:
                    if guess == target_word:
                        found = True
                        remaining_pattern = target_word
                        break

    return found, attempts, remaining_pattern

def process_file(input_csv: str, output_csv: str, dict_path: str = None) -> int:
    """Procesează fișierul de intrare și scrie rezultatele în output_csv."""
    if not os.path.exists(input_csv):
        print(f"Eroare: Fișierul de input nu există: {input_csv}")
        return 0
        
    records, errors = read_input_csv(input_csv)
    if errors:
        print("Erori la citirea input:")
        for lineno, msg in errors:
            print(f"  linia {lineno}: {msg}")
            
    if not records:
        print(f"Eroare: Nu am găsit înregistrări valide în {input_csv}")
        return 0

    # Încarcă dicționarul
    if dict_path:
        dictionary = load_dictionary(dict_path)
    else:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        default_full = os.path.join(data_dir, 'dictionary_full.txt')
        dictionary = load_dictionary(default_full)

    total_attempts = 0
    results = []

    print("\n=== REZULTATE PENTRU FIECARE CUVÂNT ===")
    print("=" * 60)
    
    for game_id, pattern_initial, target in records:
        print(f"\nCuvântul #{game_id}:")
        print(f"Pattern inițial: {pattern_initial}")
        print(f"Țintă: {target}")
        
        found, attempts, final_pattern = solve_hangman(target, pattern_initial, dictionary)
        
        status = 'OK' if found else 'FAIL'
        results.append((game_id, str(len(attempts)), final_pattern, status, ' '.join(attempts)))
        total_attempts += len(attempts)
        
        print(f"Status: {status}")
        print(f"Număr încercări: {len(attempts)}")
        if attempts:
            print(f"Secvența: {' '.join(attempts)}")
        print("-" * 60)

    # Statistici finale
    print("\n=== STATISTICI FINALE ===")
    print(f"Total cuvinte: {len(records)}")
    print(f"Total încercări: {total_attempts}")
    if records:
        print(f"Medie încercări/cuvânt: {total_attempts/len(records):.2f}")
        succes = sum(1 for r in results if r[3] == 'OK')
        print(f"Rata succes: {succes}/{len(records)} ({succes/len(records)*100:.1f}%)")
    print("=" * 60)

    # Scrie output
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['game_id', 'total_incercari', 'cuvant_gasit', 'status', 'secventa_incercari'])
        for row in results:
            writer.writerow(row)

    print(f"Scris output in: {output_csv}")
    return total_attempts

if __name__ == '__main__':
    # Determină calea către directorul scriptului
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Determină calea către directorul rădăcină al proiectului (un nivel mai sus)
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if len(sys.argv) > 1:
        # Rulat din linia de comandă
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument('--input', '-i', required=True, help='fișier CSV input')
        p.add_argument('--output', '-o', required=True, help='fișier CSV output')
        p.add_argument('--dict', '-d', help='fișier dicționar (opțional)')
        args = p.parse_args()
        
        # Convert relative paths to absolute if needed
        input_csv = os.path.abspath(args.input) if os.path.isabs(args.input) else os.path.join(os.getcwd(), args.input)
        output_csv = os.path.abspath(args.output) if os.path.isabs(args.output) else os.path.join(os.getcwd(), args.output)
        dict_path = os.path.abspath(args.dict) if args.dict and os.path.isabs(args.dict) else os.path.join(os.getcwd(), args.dict) if args.dict else None
        
        total = process_file(input_csv, output_csv, dict_path)
    else:
        # Rulat direct
        # Încearcă mai multe locații posibile pentru fișierele necesare
        possible_paths = [
            # Project structure
            (os.path.join(project_dir, 'data', 'test.csv'),
             os.path.join(project_dir, 'results', 'out.csv'),
             os.path.join(project_dir, 'data', 'dictionary_full.txt')),
            # Next to script
            (os.path.join(script_dir, 'test.csv'),
             os.path.join(script_dir, 'out.csv'),
             os.path.join(script_dir, 'dictionary_full.txt')),
            # Current working directory
            (os.path.join(os.getcwd(), 'test.csv'),
             os.path.join(os.getcwd(), 'out.csv'),
             os.path.join(os.getcwd(), 'dictionary_full.txt')),
            # Data subdirectories
            (os.path.join(os.getcwd(), 'data', 'test.csv'),
             os.path.join(os.getcwd(), 'results', 'out.csv'),
             os.path.join(os.getcwd(), 'data', 'dictionary_full.txt'))
        ]
        
        # Găsește prima locație unde există test.csv
        found_paths = None
        for paths in possible_paths:
            if os.path.exists(paths[0]):  # Verifică dacă există test.csv
                found_paths = paths
                break
                
        if not found_paths:
            print("Eroare: Nu găsesc fișierul test.csv în niciuna din locațiile posibile:")
            for paths in possible_paths:
                print(f"  - {paths[0]}")
            sys.exit(1)
            
        input_csv, output_csv, dict_path = found_paths
        
        if not os.path.exists(input_csv):
            print(f"Eroare: Nu găsesc fișierul test.csv în {data_dir}")
            print("Căi verificate:")
            for d in possible_data_dirs:
                print(f"  - {os.path.join(d, 'test.csv')}")
            sys.exit(1)
            
        total = process_file(input_csv, output_csv, dict_path if os.path.exists(dict_path) else None)
    
    print(f"Done. Total attempts: {total}")
