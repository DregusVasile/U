Rezolvare Joc Hangman
Prezentare a metodei inteligente de rezolvare automată a jocului Spânzurătoarea

Obiectivul programului

✔ Automatizarea rezolvării jocului Hangman (Spânzurătoarea).
✔ Utilizarea unui algoritm bazat pe frecvența și poziția literelor.
✔ Optimizarea numărului de încercări până la identificarea cuvântului corect.

Structura generală a codului

• Citirea și validarea datelor din fișierul CSV.
• Încărcarea dicționarului de cuvinte românești.
• Potrivirea pattern-urilor și calculul scorurilor literelor.
• Bucla principală de ghicire până la completarea cuvântului.

Citirea și validarea datelor

• Se citesc valorile game_id, pattern inițial și cuvânt țintă din CSV.
• Se normalizează textul (majuscule, eliminare spații).
• Se verifică erori de format și se elimină rândurile invalide.

Algoritmul de selecție a literelor

Citire pattern curent → Găsire cuvinte potrivite → Calcul scor litere → Selectare literă optimă → Actualizare pattern → Repetare până la soluție

Strategii inteligente de ghicire

• Primele încercări: ordine prestabilită de litere frecvente (A, E, I, R, T...).
• Ulterior: scoruri dinamice în funcție de progresul jocului.
• Adaptare automată la lungimea și dificultatea cuvântului.

Rezultate și concluzii

• Programul obține o rată ridicată de succes la identificarea cuvintelor.
• Reduce semnificativ numărul mediu de încercări per cuvânt.
• Poate fi extins pentru limbi diferite sau jocuri similare de ghicire.
