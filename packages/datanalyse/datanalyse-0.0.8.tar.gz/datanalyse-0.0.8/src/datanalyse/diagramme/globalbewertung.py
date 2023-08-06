import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from . import diagramm


class GlobalDiagramm(diagramm.Diagramm):
    def __init__(
        self,
        name,
        daten: pd.DataFrame,
        x_werte,
        xlabel="Versuchsvarianten",
        ylabel="Verteilung (%)",
        normieren=True,
        bewertungsskala=None,
        farben=None,
        beschriftung=False,
        legende=True,
        speichern=True,
        **kwargs,
    ):
        """
        Diagramm zur Darstellung von PMV/TSV-Werten (Globale Behaglichkeitskriterien)
        :param name: (Datei)name des Diagramms
        :param daten: Dataframe mit den darzustellenden Daten (siehe Test für die Formatierung)
        :param x_werte: Tick-Beschriftung an der x-Achse
        :param bewertungsskala: Antwortoptionen
        :param farben: optionale Balkenfarben, ansonsten PMV-Standardfarben
        :param beschriftung: wenn True, zugehörigen Zahlenwert mittig im Balken darstellen
        :param normieren: Normierung der Daten auf je 100 Prozent
        :param legende: Legende im Diagramm darstellen
        :param speichern: speichert Diagramm schon bei Instanzierung
        """
        super().__init__(name, **kwargs)

        self.daten = daten
        self.ersetze_leerzellen()
        self.x_werte = x_werte

        if normieren:
            self.daten = self.daten.transform(
                lambda row: row / row.sum() * 100, axis=1
            )  # axis=1 für Reihenbetrachtung

        if bewertungsskala is None:
            bewertungsskala = [
                -3,
                -2,
                -1,
                0,
                1,
                2,
                3,
            ]  # Notenbewertung für globale Behaglichkeit
        self.bewertungsskala = bewertungsskala

        # ergänze leere Spalten, falls eine der Bewertungen nicht in den Daten auftaucht (sonst Fehlermeldung)
        for i in bewertungsskala:
            if i in self.daten.columns:
                pass
            else:
                self.daten[i] = 0

        if farben is None:
            farben = [
                "royalblue",
                "dodgerblue",
                "lightskyblue",
                "limegreen",
                "gold",
                "orange",
                "red",
            ]  # Globalfarben
        self.farben = farben

        """Beginn Diagrammerzeugung"""
        self.gestapeltebalken(beschriftung=beschriftung)
        # self.set_axlabels(xlabel, ylabel)
        self.ax1.set(xlabel=xlabel, ylabel=ylabel)

        if legende:
            self.set_legend(bbox_to_anchor=(0.5, -0.1), loc="upper center", ncol=7)

        # plt.grid(None, axis="x")  # vertikale Gitterlinien entfernen
        plt.grid(None)  # Gitterlinien entfernen

        if speichern:
            self.speichern()

    def ersetze_leerzellen(self, ersetze=np.nan, durch=0):
        """
        vermeide Fehler bei Diagrammerzeugung, indem leere Zellen durch 0 ersetzt werdem
        :param ersetze: standardmäßig NaN
        :param durch: standardmäßig 0
        """
        self.daten = self.daten.replace(ersetze, durch)

    def gestapeltebalken(self, beschriftung=False):
        """
        Zeichnet aufeinander gestapelte Balken
        :param beschriftung: wenn True, zugehörigen Zahlenwert mittig im Balken darstellen
        """
        start = 0  # Startwert für die Plotbars ("untere Linie")
        anzahl_spalten = len(self.bewertungsskala)
        for i in range(anzahl_spalten):
            bewertung = self.bewertungsskala[i]
            farbe = self.farben[i]
            y_werte = self.daten[bewertung]
            self.ax1.bar(
                self.x_werte, y_werte, label=bewertung, color=farbe, bottom=start
            )
            # Beschriftung der Balken mit Werten (zentriert)
            if beschriftung:
                for xpos, ypos, yval in zip(self.x_werte, start + y_werte / 2, y_werte):
                    if yval > 0:
                        plt.text(xpos, ypos, "%.0f" % yval, ha="center", va="center")
            start += y_werte
