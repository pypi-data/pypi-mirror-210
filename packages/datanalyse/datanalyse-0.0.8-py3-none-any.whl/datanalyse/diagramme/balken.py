from . import diagramm
import numpy as np


class BalkenDiagramm(diagramm.Diagramm):
    def __init__(
        self,
        name,
        daten_ax1: list,
        daten_ax2: list = None,
        titel=None,
        x_label=None,
        y1_label=None,
        y2_label=None,
        plot_labels: list = "auto",
        xtick_labels: list = "auto",
        xtick_rotation=False,
        **kwargs,
    ):
        """
        Erstellung eines Zeitreihendiagramms auf Basis von Dataframe-Serien
        :param name: Name des Diagramms
        :param daten_ax1: Liste an Dataframe-Spalten, die auf der linken y-Achse dargestellt werden sollen
        :param daten_ax2: Liste an Dataframe-Spalten, die auf der rechten y-Achse dargestellt werden sollen
        :param titel: Titel über dem Diagramm, falls gewünscht
        :param x_label: Titel der x-Achse
        :param y1_label: Titel der 1. y-Achse
        :param y2_label: Titel der 2. y-Achse
        :param plot_labels: Titel der Datenreihen für die Legende
        :param xtick_labels: Beschriftung der x-Achse, "auto" für Benennung mit Index der ersten Datenreihe
        :param xtick_rotation: Beschriftung der x-Achse um 45° drehen (bei vielen Ticks)
        :param kwargs:
        """
        # Entscheidung, ob 2. y-Achse nötig ist
        if daten_ax2 is None:
            y2 = False
            self.daten = daten_ax1
        else:
            y2 = True
            self.daten = daten_ax1 + daten_ax2

        # Initialisierung Diagramm-Mutterklasse
        super().__init__(name, y2=y2, **kwargs)

        # Bestimmung der Anzahl, Breite, Abstand etc. der Balken
        anzahl_datenreihen = len(
            self.daten
        )  # Anzahl unterschiedlicher Balken nebeneinander in einer "Gruppe"
        width = (
            1 - 0.2
        ) / anzahl_datenreihen  # normierte Breite jedes Balkens (20 % Abstand zwischen Balkengruppen)
        x = np.arange(len(daten_ax1[0].index))  # grundsätzliche Anzahl xtick-Positionen

        # Beschriftung der x-Achsen-Werte
        if xtick_labels == "auto":
            labels = self.daten[0].index
        else:
            labels = xtick_labels

        if xtick_rotation:
            self.ax1.set_xticks(x, labels, rotation=45, horizontalalignment="right")
        else:
            self.ax1.set_xticks(x, labels)

        # Titel der Datenreihen
        if plot_labels == "auto":
            self.plot_labels = [daten.name for daten in daten_ax1]
        else:
            self.plot_labels = plot_labels

        # Positionslisten der jeweiligen nebeneinander stehenden Balken
        if anzahl_datenreihen == 1:
            xpos = [x]
        elif anzahl_datenreihen == 2:
            xpos = [x - 0.5 * width, x + 0.5 * width]
        elif anzahl_datenreihen == 3:
            xpos = [x - 1.0 * width, x, x + 1.0 * width]
        elif anzahl_datenreihen == 4:
            xpos = [x - 1.5 * width, x - 0.5 * width, x + 0.5 * width, x + 1.5 * width]
        else:
            xpos = None
            print("Fehler, Anzahl Datenreihen wird nicht unterstützt!")

        # Zeichne Graphen für 1. y-Achse
        for daten in daten_ax1:
            self.ax1.bar(
                xpos.pop(0),
                daten,
                width,
                label=self.plot_labels.pop(0),
                color=self.colors.pop(0),
            )

        # grundsätzliche Diagrammformatierung
        self.ax1.grid(axis="x", visible=None)
        self.ax1.set(xlabel=x_label, ylabel=y1_label, title=titel)
        self.handles, self.labels = self.ax1.get_legend_handles_labels()
        self.ncol = len(daten_ax1)  # Anzahl Spalten für Legende - ggf. nicht sauber

        # Wiederholung des Ganzens, sofern 2. y-Achse vorhanden
        if y2:
            if plot_labels == "auto":
                self.plot_labels = [daten.name for daten in daten_ax2]
            for daten in daten_ax2:
                self.ax2.bar(
                    xpos.pop(0),
                    daten,
                    width,
                    label=self.plot_labels.pop(0),
                    color=self.colors.pop(0),
                )
            self.ax2.set(ylabel=y2_label)
            self.ax2.grid(visible=None)
            handles2, labels2 = self.ax2.get_legend_handles_labels()
            self.handles += handles2
            self.labels += labels2
            self.ncol += len(daten_ax2)

        # Erstelle Legende
        self.set_legend(
            handles=self.handles,
            labels=self.labels,
            bbox_to_anchor=(0.5, -0.2),
            loc="upper center",
            ncol=self.ncol,
        )
