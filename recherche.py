"""Partie 2 : recherches dans la Médina. Toutes renvoient
(chemin, cout, nb_explores) ; nb_explores = cases retirées de la frontière.
Le paramètre optionnel `trace` (liste) collecte les cases développées."""
import heapq
import itertools
import math

from structures import File, Pile


def _reconstruire(parent, arrivee):
    chemin = []
    c = arrivee
    while c is not None:
        chemin.append(c)
        c = parent[c]
    return chemin[::-1]


def _resultat(medina, parent, arrivee, nb):
    if arrivee not in parent:
        return None, float("inf"), nb
    ch = _reconstruire(parent, arrivee)
    return ch, medina.cout_chemin(ch), nb


# ---------------------------------------------------------------- BFS / DFS
def bfs(medina, depart, arrivee, trace=None):
    f = File()
    f.enfiler(depart)
    parent = {depart: None}
    nb = 0
    while not f.est_vide():
        c = f.defiler()
        nb += 1
        if trace is not None:
            trace.append(c)
        if c == arrivee:
            break
        for v in medina.voisins(c):
            if v not in parent:
                parent[v] = c
                f.enfiler(v)
    return _resultat(medina, parent, arrivee, nb)


def dfs(medina, depart, arrivee, trace=None):
    p = Pile()
    p.empiler(depart)
    parent = {depart: None}
    nb = 0
    while not p.est_vide():
        c = p.depiler()
        nb += 1
        if trace is not None:
            trace.append(c)
        if c == arrivee:
            break
        # on empile dans l'ordre inverse pour développer N avant S, E, O
        for v in reversed(medina.voisins(c)):
            if v not in parent:
                parent[v] = c
                p.empiler(v)
    return _resultat(medina, parent, arrivee, nb)


# --------------------------------------------------- Dijkstra / A* / glouton
def a_star(medina, depart, arrivee, h, w=1, trace=None):
    """f = g + w*h. Avec w=1 et h admissible : chemin de coût minimal."""
    cpt = itertools.count()
    g = {depart: 0}
    parent = {depart: None}
    tas = [(w * h(depart, arrivee), next(cpt), depart, 0)]
    nb = 0
    while tas:
        _, _, c, gc = heapq.heappop(tas)
        if gc > g[c]:            # entrée périmée (un meilleur g existe)
            continue
        nb += 1
        if trace is not None:
            trace.append(c)
        if c == arrivee:
            break
        for v in medina.voisins(c):
            gv = gc + medina.cout(v)
            if v not in g or gv < g[v]:
                g[v] = gv
                parent[v] = c
                heapq.heappush(tas, (gv + w * h(v, arrivee), next(cpt), v, gv))
    return _resultat(medina, parent, arrivee, nb)


def cout_uniforme(medina, depart, arrivee, trace=None):
    """Dijkstra = A* avec h = 0."""
    return a_star(medina, depart, arrivee, h_nulle, 1, trace)


def glouton(medina, depart, arrivee, h, trace=None):
    """Recherche gloutonne : priorité f = h seule."""
    cpt = itertools.count()
    parent = {depart: None}
    tas = [(h(depart, arrivee), next(cpt), depart)]
    nb = 0
    while tas:
        _, _, c = heapq.heappop(tas)
        nb += 1
        if trace is not None:
            trace.append(c)
        if c == arrivee:
            break
        for v in medina.voisins(c):
            if v not in parent:
                parent[v] = c
                heapq.heappush(tas, (h(v, arrivee), next(cpt), v))
    return _resultat(medina, parent, arrivee, nb)


# -------------------------------------------------------------- heuristiques
def h_nulle(case, arrivee):
    return 0


def h_manhattan(case, arrivee):
    return abs(case[0] - arrivee[0]) + abs(case[1] - arrivee[1])


def h_euclide(case, arrivee):
    return math.hypot(case[0] - arrivee[0], case[1] - arrivee[1])


def h_tchebychev(case, arrivee):
    return max(abs(case[0] - arrivee[0]), abs(case[1] - arrivee[1]))
