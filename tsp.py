"""Partie 3 : le circuit du guide (TSP asymétrique sur 12 points).
Une tournée = liste d'indices commençant par 0, sans répéter 0 à la fin."""
import itertools
import math
import random

from recherche import a_star, h_manhattan


# ----------------------------------------------------------- préparation
def matrice_couts(medina, points):
    """M[i][j] = coût du chemin A*(Manhattan) du point i au point j.
    Nombre d'appels à A* : n*(n-1) = 132 pour n = 12 (diagonale = 0)."""
    n = len(points)
    M = [[0] * n for _ in range(n)]
    appels = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                M[i][j] = a_star(medina, points[i], points[j], h_manhattan)[1]
                appels += 1
    matrice_couts.nb_appels = appels
    return M


def cout_tournee(tournee, M):
    """Coût du circuit fermé (retour à tournee[0] inclus)."""
    n = len(tournee)
    return sum(M[tournee[i]][tournee[(i + 1) % n]] for i in range(n))


def plus_proche_voisin(M):
    n = len(M)
    tournee, restants = [0], set(range(1, n))
    while restants:
        dernier = tournee[-1]
        suivant = min(restants, key=lambda j: (M[dernier][j], j))
        tournee.append(suivant)
        restants.remove(suivant)
    return tournee


def tournee_aleatoire(n, rng):
    return [0] + rng.sample(range(1, n), n - 1)


# -------------------------------------------------------------- Held-Karp
def held_karp(M):
    """Programmation dynamique exacte. Clés : (frozenset(visites), dernier).
    Nombre d'états pour n = 12 : (n-1) * 2^(n-2) = 11 * 1024 = 11 264."""
    n = len(M)
    C, parent = {}, {}
    for j in range(1, n):
        C[(frozenset([j]), j)] = M[0][j]
    for taille in range(2, n):
        for S in map(frozenset, itertools.combinations(range(1, n), taille)):
            for j in S:
                reste = S - {j}
                C[(S, j)], parent[(S, j)] = min(
                    (C[(reste, i)] + M[i][j], i) for i in reste)
    held_karp.nb_etats = len(C)
    complet = frozenset(range(1, n))
    opt, j = min((C[(complet, j)] + M[j][0], j) for j in complet)
    tournee, S = [], complet
    while j is not None:
        tournee.append(j)
        S, j = S - {j}, parent.get((S, j))
    tournee.append(0)
    return opt, tournee[::-1]


# ------------------------------------------------------- recherche locale
def _voisins_2opt(tournee):
    n = len(tournee)
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            yield tournee[:i] + tournee[i:j + 1][::-1] + tournee[j + 1:]


def descente_2opt(tournee, M):
    """Meilleure amélioration : tant qu'un voisin 2-opt est meilleur, s'y déplacer."""
    cur, cc = list(tournee), cout_tournee(tournee, M)
    while True:
        meilleur, mc = None, cc
        for v in _voisins_2opt(cur):
            c = cout_tournee(v, M)
            if c < mc:
                meilleur, mc = v, c
        if meilleur is None:
            return cur, cc
        cur, cc = meilleur, mc


# ------------------------------------------------------------ recuit simulé
def voisin_echange(tournee, rng):
    t = list(tournee)
    i, j = rng.sample(range(1, len(t)), 2)
    t[i], t[j] = t[j], t[i]
    return t


def voisin_2opt(tournee, rng):
    t = list(tournee)
    i, j = sorted(rng.sample(range(1, len(t)), 2))
    t[i:j + 1] = t[i:j + 1][::-1]
    return t


def recuit_simule(M, T0, alpha, n_palier, voisinage, rng=None, init=None, T_min=0.01):
    """Renvoie (meilleure tournée, historique des coûts courants)."""
    rng = rng or random.Random(0)
    n = len(M)
    cur = list(init) if init else tournee_aleatoire(n, rng)
    cc = cout_tournee(cur, M)
    best, bc = cur, cc
    hist = [cc]
    T = T0
    while T >= T_min:
        for _ in range(n_palier):
            cand = voisinage(cur, rng)
            dE = cout_tournee(cand, M) - cc
            if dE <= 0 or rng.random() < math.exp(-dE / T):   # Metropolis
                cur, cc = cand, cc + dE
                if cc < bc:
                    best, bc = cur, cc
            hist.append(cc)
        T *= alpha
    return best, hist


# --------------------------------------------------- algorithme génétique
def croisement_ox(p1, p2, rng=None, coupe=None):
    """Croisement ordonné : segment de p1 copié à la même place, le reste
    rempli avec les gènes de p2 dans l'ordre, sans doublon."""
    m = len(p1)
    i, j = coupe if coupe else sorted(rng.sample(range(m), 2))
    segment = p1[i:j + 1]
    present = set(segment)
    reste = iter(g for g in p2 if g not in present)
    return [p1[k] if i <= k <= j else next(reste) for k in range(m)]


def _tournoi(pop, couts, k, rng):
    idx = rng.sample(range(len(pop)), k)
    return pop[min(idx, key=lambda i: couts[i])]


def algo_genetique(M, taille_pop, n_gen, p_mut, k_tournoi, n_elite, rng=None):
    """Individu = permutation des monuments 1..n-1 (0 reste en tête).
    Renvoie (meilleure tournée, son coût, hist. meilleur coût, hist. diversité)."""
    rng = rng or random.Random(0)
    n = len(M)
    pop = [rng.sample(range(1, n), n - 1) for _ in range(taille_pop)]
    hist_cout, hist_div = [], []
    for _ in range(n_gen + 1):
        couts = [cout_tournee([0] + ind, M) for ind in pop]
        ordre = sorted(range(taille_pop), key=lambda i: couts[i])
        hist_cout.append(couts[ordre[0]])
        hist_div.append(len({tuple(ind) for ind in pop}))
        if len(hist_cout) == n_gen + 1:
            break
        nouvelle = [pop[i][:] for i in ordre[:n_elite]]          # élitisme
        while len(nouvelle) < taille_pop:
            e = croisement_ox(_tournoi(pop, couts, k_tournoi, rng),
                              _tournoi(pop, couts, k_tournoi, rng), rng)
            if rng.random() < p_mut:                              # mutation
                a, b = rng.sample(range(n - 1), 2)
                e[a], e[b] = e[b], e[a]
            nouvelle.append(e)
        pop = nouvelle
    return [0] + pop[ordre[0]], hist_cout[-1], hist_cout, hist_div


# ------------------------------------------------------- bonus : B&B
def branch_and_bound(M):
    """Séparation-évaluation. Borne inférieure du coût restant : chaque noeud
    encore à quitter (dernier + non visités) paie au moins sa plus petite
    arête sortante vers (non visités + 0). Initialisée par plus_proche_voisin."""
    n = len(M)
    nn = plus_proche_voisin(M)
    best = [cout_tournee(nn, M), nn]
    noeuds = [0]

    def borne(dernier, restants):
        cibles = restants | {0}
        total = 0
        for v in restants | {dernier}:
            total += min(M[v][w] for w in cibles if w != v)
        return total

    def rec(chemin, restants, cout):
        noeuds[0] += 1
        if not restants:
            total = cout + M[chemin[-1]][0]
            if total < best[0]:
                best[0], best[1] = total, chemin[:]
            return
        if cout + borne(chemin[-1], restants) >= best[0]:
            return
        for j in sorted(restants, key=lambda j: M[chemin[-1]][j]):
            chemin.append(j)
            rec(chemin, restants - {j}, cout + M[chemin[-2]][j])
            chemin.pop()

    rec([0], frozenset(range(1, n)), 0)
    branch_and_bound.nb_noeuds = noeuds[0]
    return best[0], best[1]
