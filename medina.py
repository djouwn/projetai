
"""
Partie 1.2 : Carte de la Médina
Grille P x Q, murs, passages, coûts et affichage 2D.

Contraintes conservées :
- Génération DFS itérative avec Pile.
- Ordre des directions : Nord, Sud, Est, Ouest.
- Générateur aléatoire unique partagé entre DFS et passages.
- Deuxième générateur indépendant pour les escaliers.
- Coûts : normal = 1, escalier = 2, souk = 3.
- Carte reproductible à partir de la graine G.
"""

import random

from structures import Pile
from config import POINTS


# Ordre imposé : nord, sud, est, ouest
DIRS = [(-1, 0), (1, 0), (0, 1), (0, -1)]


class Medina:

    def __init__(self, P, Q, graine):

        if P <= 0 or Q <= 0:
            raise ValueError("P et Q doivent être positifs.")

        self.P = P
        self.Q = Q
        self.graine = graine

        # Générateur unique partagé entre DFS et passages
        self.rng = random.Random(graine)

        # Points d'intérêt définis dans config.py
        self.points = list(POINTS)

        # Vérification des coordonnées
        for point in self.points:
            if not self.dans_grille(*point):
                raise ValueError(
                    f"Point d'intérêt hors grille : {point}"
                )

        # Murs intérieurs
        self.mur_est = [[True] * Q for _ in range(P)]
        self.mur_sud = [[True] * Q for _ in range(P)]

        # Calcul des coûts
        self._couts = self._calculer_couts()

    # =====================================================
    # 1. GESTION DE LA GRILLE ET DES MURS
    # =====================================================

    def dans_grille(self, l, c):
        """Vérifie si une case appartient à la grille."""

        return 0 <= l < self.P and 0 <= c < self.Q

    def a_mur(self, a, b):
        """Vérifie la présence d'un mur entre deux cases adjacentes."""

        (l1, c1), (l2, c2) = a, b

        if abs(l1 - l2) + abs(c1 - c2) != 1:
            raise ValueError("Les cases doivent être adjacentes.")

        if l1 == l2:
            return self.mur_est[l1][min(c1, c2)]

        return self.mur_sud[min(l1, l2)][c1]

    def _abattre(self, a, b):
        """Supprime le mur entre deux cases adjacentes."""

        (l1, c1), (l2, c2) = a, b

        if abs(l1 - l2) + abs(c1 - c2) != 1:
            raise ValueError("Les cases doivent être adjacentes.")

        if l1 == l2:
            self.mur_est[l1][min(c1, c2)] = False
        else:
            self.mur_sud[min(l1, l2)][c1] = False

    def _murs_restants(self):
        """
        Retourne les murs intérieurs encore présents.

        Ordre imposé :
        ligne par ligne, puis colonne par colonne,
        mur est puis mur sud.
        """

        murs = []

        for l in range(self.P):
            for c in range(self.Q):

                if c < self.Q - 1 and self.mur_est[l][c]:
                    murs.append(((l, c), (l, c + 1)))

                if l < self.P - 1 and self.mur_sud[l][c]:
                    murs.append(((l, c), (l + 1, c)))

        return murs

    def nb_passages(self):
        """Nombre de murs intérieurs abattus."""

        total_int = (
            self.P * (self.Q - 1)
            + (self.P - 1) * self.Q
        )

        return total_int - len(self._murs_restants())

    # =====================================================
    # 2. GENERATION DU LABYRINTHE PAR DFS
    # =====================================================

    def generer_dfs(self):
        """
        Génère un labyrinthe parfait avec DFS itératif.

        Utilise la classe Pile et le générateur self.rng.
        """

        rng = self.rng

        # Réinitialisation des murs
        self.mur_est = [[True] * self.Q for _ in range(self.P)]
        self.mur_sud = [[True] * self.Q for _ in range(self.P)]

        visitee = [
            [False] * self.Q
            for _ in range(self.P)
        ]

        # Case de départ aléatoire
        depart = (
            rng.randrange(self.P),
            rng.randrange(self.Q)
        )

        visitee[depart[0]][depart[1]] = True

        pile = Pile()
        pile.empiler(depart)

        while not pile.est_vide():

            l, c = pile.sommet()

            # Recherche des voisins non visités
            non_visitees = [
                (l + dl, c + dc)
                for dl, dc in DIRS
                if self.dans_grille(l + dl, c + dc)
                and not visitee[l + dl][c + dc]
            ]

            if non_visitees:

                # Choix aléatoire d'un voisin
                v = rng.choice(non_visitees)

                # Suppression du mur
                self._abattre((l, c), v)

                # Marquage comme visité
                visitee[v[0]][v[1]] = True

                # Empilement
                pile.empiler(v)

            else:

                # Retour arrière
                pile.depiler()

    # =====================================================
    # 3. OUVERTURE DE PASSAGES SUPPLEMENTAIRES
    # =====================================================

    def ouvrir_passages(self, k):
        """
        Abat k murs intérieurs restants.

        Les murs sont sélectionnés avec rng.sample.
        """

        if k < 0:
            raise ValueError("Le nombre de passages doit être positif.")

        murs = self._murs_restants()

        if k > len(murs):
            raise ValueError("Pas assez de murs à abattre.")

        for a, b in self.rng.sample(murs, k):
            self._abattre(a, b)

    # =====================================================
    # 4. NAVIGATION
    # =====================================================

    def voisins(self, case):
        """
        Retourne les cases accessibles sans mur.

        Ordre : Nord, Sud, Est, Ouest.
        """

        l, c = case

        if not self.dans_grille(l, c):
            raise ValueError("Case hors grille.")

        res = []

        for dl, dc in DIRS:

            n = (l + dl, c + dc)

            if self.dans_grille(*n) and not self.a_mur(case, n):
                res.append(n)

        return res

    # =====================================================
    # 5. CALCUL DES COUTS
    # =====================================================

    def _est_souk(self, l, c):
        """
        Identifie les cases situées autour des deux souks.

        Indices 2 et 3 dans POINTS.
        """

        for i in (2, 3):

            if i >= len(self.points):
                continue

            pl, pc = self.points[i]

            if abs(l - pl) + abs(c - pc) <= 2:
                return True

        return False

    def _calculer_couts(self):
        """
        Coûts des déplacements :

        1 : case normale
        2 : escalier
        3 : souk

        Les escaliers sont sélectionnés avec un générateur
        indépendant du générateur principal.
        """

        couts = [
            [1] * self.Q
            for _ in range(self.P)
        ]

        souk = set()

        # Zones des souks
        for l in range(self.P):
            for c in range(self.Q):

                if self._est_souk(l, c):

                    couts[l][c] = 3
                    souk.add((l, c))

        # Les points d'intérêt sont exclus des escaliers
        poi = set(self.points)

        # Deuxième générateur indépendant
        rng2 = random.Random(self.graine)

        candidates = [
            (l, c)
            for l in range(self.P)
            for c in range(self.Q)
            if (l, c) not in souk
            and (l, c) not in poi
        ]

        nb_escaliers = round(0.05 * len(candidates))

        self.escaliers = set(
            rng2.sample(candidates, nb_escaliers)
        )

        # Affectation du coût 2
        for l, c in self.escaliers:
            couts[l][c] = 2

        return couts

    def cout(self, case):
        """Retourne le coût d'une case."""

        l, c = case

        if not self.dans_grille(l, c):
            raise ValueError("Case hors grille.")

        return self._couts[l][c]

    def cout_chemin(self, chemin):
        """
        Somme des coûts des cases où l'on entre.
        Le coût de la case de départ n'est pas comptabilisé.
        """

        return sum(
            self.cout(c)
            for c in chemin[1:]
        )

    def chemin_valide(self, chemin):
        """Vérifie que toutes les transitions sont accessibles."""

        return all(
            b in self.voisins(a)
            for a, b in zip(chemin, chemin[1:])
        )

    # =====================================================
    # 6. AFFICHAGE 2D AMELIORE
    # =====================================================

    def afficher(
        self,
        chemins=None,
        explores=None,
        titre=None,
        fichier=None,
        afficher_couts=False,
        noms_points=None
    ):
        """
        Affichage cartographique 2D.

        Beige  : zone normale
        Jaune  : escaliers
        Orange : souks
        Bleu   : points d'intérêt
        Traits : murs

        chemins :
            dict {nom: chemin} ou liste de chemins

        explores :
            dict {nom: cases explorées} ou liste de listes

        noms_points :
            dictionnaire {indice: nom}
            ou liste de noms dans l'ordre de POINTS

        fichier :
            chemin de sauvegarde PNG
        """

        import matplotlib.pyplot as plt

        from matplotlib.patches import Rectangle, Circle, Patch
        from matplotlib.lines import Line2D

        # Palette cartographique
        couleurs = {
            1: "#E9DCC3",
            2: "#E9BE67",
            3: "#D98262"
        }

        couleurs_algorithmes = [
            "#168AAD",
            "#E63946",
            "#6A4C93",
            "#2A9D8F",
            "#F77F00"
        ]

        fig, ax = plt.subplots(figsize=(17, 12))

        fig.patch.set_facecolor("#F4EFE5")
        ax.set_facecolor("#F4EFE5")

        # -------------------------------------------------
        # A. CASES
        # -------------------------------------------------

        for l in range(self.P):
            for c in range(self.Q):

                cout = self._couts[l][c]

                ax.add_patch(
                    Rectangle(
                        (c, l),
                        1,
                        1,
                        facecolor=couleurs[cout],
                        edgecolor="none",
                        zorder=1
                    )
                )

                if afficher_couts:

                    ax.text(
                        c + 0.5,
                        l + 0.5,
                        str(cout),
                        ha="center",
                        va="center",
                        fontsize=6,
                        color="#675D50",
                        zorder=2
                    )

        # -------------------------------------------------
        # B. MURS
        # -------------------------------------------------

        style_mur = {
            "color": "#554B40",
            "linewidth": 1.8,
            "solid_capstyle": "round",
            "zorder": 3
        }

        # Contour extérieur
        ax.plot(
            [0, self.Q, self.Q, 0, 0],
            [0, 0, self.P, self.P, 0],
            color="#40372E",
            linewidth=3,
            zorder=4
        )

        for l in range(self.P):
            for c in range(self.Q):

                # Mur Est
                if c < self.Q - 1 and self.mur_est[l][c]:

                    ax.plot(
                        [c + 1, c + 1],
                        [l, l + 1],
                        **style_mur
                    )

                # Mur Sud
                if l < self.P - 1 and self.mur_sud[l][c]:

                    ax.plot(
                        [c, c + 1],
                        [l + 1, l + 1],
                        **style_mur
                    )

        # -------------------------------------------------
        # C. CASES EXPLOREES
        # -------------------------------------------------

        if explores:

            items = (
                explores.items()
                if isinstance(explores, dict)
                else enumerate(explores)
            )

            for i, (nom, cases) in enumerate(items):

                if not cases:
                    continue

                xs = [c + 0.5 for l, c in cases]
                ys = [l + 0.5 for l, c in cases]

                couleur = couleurs_algorithmes[
                    i % len(couleurs_algorithmes)
                ]

                ax.scatter(
                    xs,
                    ys,
                    s=24,
                    color=couleur,
                    alpha=0.55,
                    edgecolors="none",
                    zorder=5,
                    label=(
                        f"Exploration : {nom}"
                        if isinstance(explores, dict)
                        else None
                    )
                )

        # -------------------------------------------------
        # D. CHEMINS
        # -------------------------------------------------

        if chemins:

            items = (
                chemins.items()
                if isinstance(chemins, dict)
                else enumerate(chemins)
            )

            for i, (nom, chemin) in enumerate(items):

                if not chemin:
                    continue

                xs = [c + 0.5 for l, c in chemin]
                ys = [l + 0.5 for l, c in chemin]

                couleur = couleurs_algorithmes[
                    i % len(couleurs_algorithmes)
                ]

                ax.plot(
                    xs,
                    ys,
                    color=couleur,
                    linewidth=3,
                    marker="o",
                    markersize=3,
                    solid_capstyle="round",
                    zorder=7,
                    label=f"Chemin : {nom}"
                )

        # -------------------------------------------------
        # E. POINTS D'INTERET
        # -------------------------------------------------

        for i, (l, c) in enumerate(self.points):

            ax.add_patch(
                Circle(
                    (c + 0.5, l + 0.5),
                    radius=0.27,
                    facecolor="#244C60",
                    edgecolor="#FFF9ED",
                    linewidth=2,
                    zorder=10
                )
            )

            ax.text(
                c + 0.5,
                l + 0.5,
                str(i),
                color="white",
                fontsize=8,
                fontweight="bold",
                ha="center",
                va="center",
                zorder=11
            )

            # Nom facultatif du point
            if noms_points is not None:

                if isinstance(noms_points, dict):
                    nom = noms_points.get(i, f"Point {i}")
                else:
                    nom = (
                        noms_points[i]
                        if i < len(noms_points)
                        else f"Point {i}"
                    )

                # Position des étiquettes
                if c >= self.Q - 4:
                    decalage = (-10, 8)
                    alignement = "right"

                elif c <= 4:
                    decalage = (10, 8)
                    alignement = "left"

                elif l >= self.P - 3:
                    decalage = (0, -13)
                    alignement = "center"

                else:
                    decalage = (0, 11)
                    alignement = "center"

                ax.annotate(
                    nom,
                    xy=(c + 0.5, l + 0.5),
                    xytext=decalage,
                    textcoords="offset points",
                    fontsize=8,
                    fontweight="bold",
                    color="#293D46",
                    ha=alignement,
                    va="bottom",
                    zorder=12,
                    bbox={
                        "boxstyle": "round,pad=0.3",
                        "facecolor": "#FFF9ED",
                        "edgecolor": "#C6B99F",
                        "alpha": 0.95
                    }
                )

        # -------------------------------------------------
        # F. LEGENDE
        # -------------------------------------------------

        legendes = [
            Patch(
                facecolor=couleurs[1],
                label="Zone normale - coût 1"
            ),
            Patch(
                facecolor=couleurs[2],
                label="Escaliers - coût 2"
            ),
            Patch(
                facecolor=couleurs[3],
                label="Souks - coût 3"
            ),
            Line2D(
                [0],
                [0],
                color="#554B40",
                linewidth=2,
                label="Mur"
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#244C60",
                markeredgecolor="white",
                markersize=9,
                label="Point d'intérêt"
            )
        ]

        handles, labels = ax.get_legend_handles_labels()

        legendes.extend(handles)

        ax.legend(
            handles=legendes,
            loc="upper left",
            bbox_to_anchor=(1.015, 1),
            fontsize=9,
            frameon=True,
            facecolor="#FFF9ED",
            edgecolor="#C6B99F"
        )

        # -------------------------------------------------
        # G. FINITIONS
        # -------------------------------------------------

        ax.set_xlim(-0.5, self.Q + 0.5)
        ax.set_ylim(self.P + 0.5, -0.5)

        ax.set_aspect("equal")

        ax.set_xticks([])
        ax.set_yticks([])

        ax.set_title(
            titre or (
                f"MÉDINA DE TUNIS — MÉDINA 2.0\n"
                f"Graine G = {self.graine} | "
                f"Grille {self.P} × {self.Q} | "
                f"Passages ouverts : {self.nb_passages()}"
            ),
            fontsize=16,
            fontweight="bold",
            color="#293D46",
            pad=20
        )

        for bord in ax.spines.values():
            bord.set_visible(False)

        fig.text(
            0.5,
            0.025,
            "MÉDINA 2.0 • Carte générée procéduralement • "
            "Déplacements Nord / Sud / Est / Ouest",
            ha="center",
            fontsize=9,
            color="#786B5B"
        )

        fig.tight_layout(
            rect=[0, 0.05, 0.84, 1]
        )

        if fichier:

            fig.savefig(
                fichier,
                dpi=220,
                bbox_inches="tight",
                facecolor=fig.get_facecolor()
            )

        return fig


# =========================================================
# 7. FONCTION DE GENERATION
# =========================================================

def creer_medina(P, Q, G, k=None):
    """
    Génère la Médina :

    1. Création de la grille.
    2. Génération DFS.
    3. Ouverture de k passages supplémentaires.
    """

    m = Medina(P, Q, G)

    m.generer_dfs()

    if k is not None:
        m.ouvrir_passages(k)

    return m


# =========================================================
# 8. EXECUTION DE TEST
# =========================================================

if __name__ == "__main__":

    import matplotlib.pyplot as plt

    P = 20
    Q = 30
    G = 1234

    K_PASSAGES = 60 + (G % 41)

    medina = creer_medina(
        P,
        Q,
        G,
        K_PASSAGES
    )

    print("===== MEDINA 2.0 =====")
    print("Dimensions :", P, "x", Q)
    print("Graine :", G)
    print("Passages supplémentaires :", K_PASSAGES)
    print("Nombre total de passages :", medina.nb_passages())
    print("Nombre d'escaliers :", len(medina.escaliers))

    medina.afficher(
        titre="Médina de Tunis - Carte 2D",
        fichier="medina_realiste.png"
    )

    plt.show()
