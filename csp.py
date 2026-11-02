"""Partie 4 : le souk réaménagé (CSP)."""
import time
from collections import deque


class CSP:
    """variables : liste de noms ; domaines : {var: liste de valeurs} ;
    contraintes : liste de (X, fonction) unaires (réduisent le domaine tout
    de suite) ou de (X, Y, fonction(x, y)) binaires."""

    def __init__(self, variables, domaines, contraintes):
        self.variables = list(variables)
        self.domaines = {v: list(domaines[v]) for v in variables}
        self.voisins = {v: set() for v in variables}
        self.contr = {}                      # (X, Y) -> [f(x, y), ...]
        for c in contraintes:
            if len(c) == 2:
                self.ajouter_unaire(*c)
            else:
                self.ajouter_binaire(*c)

    def ajouter_unaire(self, X, f):
        self.domaines[X] = [x for x in self.domaines[X] if f(x)]

    def ajouter_binaire(self, X, Y, f):
        self.contr.setdefault((X, Y), []).append(f)
        self.contr.setdefault((Y, X), []).append(lambda y, x, f=f: f(x, y))
        self.voisins[X].add(Y)
        self.voisins[Y].add(X)

    def consistant(self, X, x, Y, y):
        return all(f(x, y) for f in self.contr[(X, Y)])

    def copie(self):
        c = CSP.__new__(CSP)
        c.variables = list(self.variables)
        c.domaines = {v: list(d) for v, d in self.domaines.items()}
        c.voisins, c.contr = self.voisins, self.contr
        return c


def creer_csp_souk(lumiere=False):
    """Encode le problème du souk. lumiere=True ajoute BI, TI, CH in {4, 5} (Q23)."""
    V = ["PA", "PB", "CH", "DI", "BI", "TI", "LI", "PT"]
    dom = {v: list(range(1, 11)) for v in V}
    c = []
    for i, X in enumerate(V):                                   # 1. tous différents
        for Y in V[i + 1:]:
            c.append((X, Y, lambda x, y: x != y))
    c += [("PA", lambda x: x <= 3), ("PB", lambda x: x <= 3),   # 2. près de la mosquée
          ("PA", "PB", lambda a, b: abs(a - b) >= 2),           # 3. pas voisins
          ("DI", "PA", lambda d, p: abs(d - p) >= 4),           # 4. cuivre loin
          ("DI", "PB", lambda d, p: abs(d - p) >= 4),
          ("DI", lambda d: d <= 7),                             # 5. calme
          ("LI", lambda l: l >= 8),                             # 6. livres
          ("BI", "TI", lambda b, t: abs(b - t) == 1),           # 7. trousseau
          ("CH", "TI", lambda h, t: abs(h - t) <= 2),           # 8. laine
          ("PT", "DI", lambda p, d: abs(p - d) >= 2)]           # 9. gâteaux
    if lumiere:
        c += [(v, lambda x: x in (4, 5)) for v in ("BI", "TI", "CH")]
    return CSP(V, dom, c)


def backtracking(csp, mrv=False, fc=False, toutes=False):
    """Retour arrière. Renvoie un dict :
       solution (1re) / solutions (toutes si toutes=True), nb_solutions,
       noeuds   = nombre d'états (affectations partielles) visités, racine
                  comprise = nombre d'appels récursifs,
       retours  = nombre d'affectations défaites sans solution dessous
                  (y compris celles rejetées par un domaine vidé en FC),
       temps_ms."""
    t0 = time.perf_counter()
    stats = {"noeuds": 0, "retours": 0}
    solutions, affect = [], {}
    n = len(csp.variables)

    def legales(v, dom):
        return [x for x in dom[v]
                if all(csp.consistant(v, x, y, affect[y])
                       for y in csp.voisins[v] if y in affect)]

    def choisir(dom):
        libres = [v for v in csp.variables if v not in affect]
        if not mrv:
            return libres[0]
        return min(libres, key=lambda v: (
            len(legales(v, dom)),                                  # MRV
            -sum(len(csp.contr[(v, y)])                            # degré
                 for y in csp.voisins[v] if y not in affect)))

    def propager(dom, v, x):
        """Forward checking : filtre les voisins non affectés de v."""
        nd = dict(dom)
        nd[v] = [x]
        for y in csp.voisins[v]:
            if y not in affect:
                nd[y] = [b for b in nd[y] if csp.consistant(v, x, y, b)]
                if not nd[y]:
                    return nd, False
        return nd, True

    def rec(dom):
        stats["noeuds"] += 1
        if len(affect) == n:
            solutions.append(dict(affect))
            return True
        v = choisir(dom)
        trouve = False
        for x in legales(v, dom):
            affect[v] = x
            ok, nd = True, dom
            if fc:
                nd, ok = propager(dom, v, x)
            sous = rec(nd) if ok else False
            del affect[v]
            if sous:
                trouve = True
                if not toutes:
                    return True
            else:
                stats["retours"] += 1
        return trouve

    rec({v: list(d) for v, d in csp.domaines.items()})
    stats["temps_ms"] = (time.perf_counter() - t0) * 1000
    stats["nb_solutions"] = len(solutions)
    stats["solution"] = solutions[0] if solutions else None
    if toutes:
        stats["solutions"] = solutions
    return stats


def ac3(csp):
    """Rend tous les arcs cohérents (modifie csp.domaines). False si domaine vide."""
    file = deque((X, Y) for X in csp.variables for Y in csp.voisins[X])
    while file:
        X, Y = file.popleft()
        revise = False
        for x in list(csp.domaines[X]):
            if not any(csp.consistant(X, x, Y, y) for y in csp.domaines[Y]):
                csp.domaines[X].remove(x)
                revise = True
        if revise:
            if not csp.domaines[X]:
                return False
            for Z in csp.voisins[X]:
                if Z != Y:
                    file.append((Z, X))
    return True
