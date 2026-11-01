"""Configuration commune du projet Médina 2.0."""

NUMEROS_INSCRIPTION = []

G = sum(NUMEROS_INSCRIPTION) % 10000 if NUMEROS_INSCRIPTION else 1234

P = 20
Q = 30              
K_PASSAGES = 60 + (G % 41) 


LIEUX = [
    ("Bab Bhar", (10, 29)),
    ("Mosquée Zitouna", (10, 15)),
    ("Souk el Attarine", (8, 15)),
    ("Souk ech-Chaouachia", (9, 9)),
    ("Médersa Slimania", (11, 17)),
    ("Dar Ben Abdallah", (15, 18)),
    ("Tourbet el Bey", (16, 13)),
    ("Dar Lasram", (5, 8)),
    ("Place de la Kasbah", (10, 1)),
    ("Bab Souika", (1, 14)),
    ("Zaouïa Sidi Mahrez", (3, 17)),
    ("Bab Jedid", (19, 12)),
]
NOMS = [n for n, _ in LIEUX]
POINTS = [c for _, c in LIEUX]
