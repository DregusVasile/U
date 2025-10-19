# Solver Spânzurătoarea (automat)

Proiect minimal pentru tema de laborator: solver offline pentru jocul Hangman (Spânzurătoarea) în limba română.

Structură:
- src/solve_hangman.py - script principal (Python)
- data/test.csv - fișier CSV exemplu (game_id,pattern_initial,cuvant_tinta)
- results/ - output recomandat
- docs/ - loc pentru prezentarea PPTX

Cerinte de rulare:
- Python 3.8+
- Fără dependențe externe

Exemplu rulare:

```pwsh
python .\src\solve_hangman.py --input .\data\test.csv --output .\results\out.csv
```

Ieșire:
- CSV cu coloanele: game_id,total_incercari,cuvant_gasit,status,secventa_incercari

Limitări & Observații:
- Soluția folosește un dicționar simplu (dacă nu se oferă unul) construit din coloana `cuvant_tinta` a input-ului.
- Strategia: dacă există candidați din dicționar, se prioritizează literele cele mai frecvente în pozițiile necunoscute.
- Respectăm constrângerea de a nu folosi `cuvant_tinta` pentru a decide încercările (folosit doar pentru evaluare în output).

Pentru evaluare pe setul oficial de test, pune fișierul în `data/test.csv` și rulează comanda de mai sus.
