from . import diagramm

class ZeitreihenDiagramm(diagramm.Diagramm):
    def __init__(
        self,
        name,
        zeit,
        daten_ax1: list,
        daten_ax2: list = None,
        titel=None,
        x_label=None,
        y1_label=None,
        y2_label=None,
        plot_labels: list = "auto",
        **kwargs,
    ):
        """
        Erstellung eines Zeitreihendiagramms auf Basis von Dataframe-Serien
        :param name: Name des Diagramms
        :param zeit: Serie mit Zeitdaten/Zeitstempeln - muss aktuell für alle dargestellten Daten gültig sein!
        :param daten_ax1: Liste an Dataframe-Spalten, die auf der linken y-Achse dargestellt werden sollen
        :param daten_ax2: Liste an Dataframe-Spalten, die auf der rechten y-Achse dargestellt werden sollen
        :param titel: Titel über dem Diagramm, falls gewünscht
        :param x_label: Titel der x-Achse
        :param y1_label: Titel der 1. y-Achse
        :param y2_label: Titel der 2. y-Achse
        :param plot_labels: Titel der Datenreihen für die Legende
        :param kwargs:
        """
        # Entscheidung, ob 2. y-Achse nötig ist
        if daten_ax2 is None:
            y2 = False
        else:
            y2 = True

        # Initialisierung Diagramm-Mutterklasse
        super().__init__(name, y2=y2, **kwargs)

        if plot_labels == "auto":
            self.plot_labels = [daten.name for daten in daten_ax1]
        else:
            self.plot_labels = plot_labels

        # Zeichne Graphen für 1. y-Achse
        for daten in daten_ax1:
            self.ax1.plot(
                zeit,
                daten,
                label=self.plot_labels.pop(0),
                color=self.colors.pop(0),
                linestyle=self.linestyles.pop(0),
            )

        # grundsätzliche Diagrammformatierung
        self.ax1.set(xlabel=x_label, ylabel=y1_label, title=titel)
        self.handles, self.labels = self.ax1.get_legend_handles_labels()
        self.ncol = len(daten_ax1)  # Anzahl Spalten für Legende - ggf. nicht sauber

        # Wiederholung des Ganzens, sofern 2. y-Achse vorhanden
        if y2:
            if plot_labels == "auto":
                self.plot_labels = [daten.name for daten in daten_ax2]
            for daten in daten_ax2:
                self.ax2.plot(
                    zeit,
                    daten,
                    label=self.plot_labels.pop(0),
                    color=self.colors.pop(0),
                    linestyle=self.linestyles.pop(0),
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
