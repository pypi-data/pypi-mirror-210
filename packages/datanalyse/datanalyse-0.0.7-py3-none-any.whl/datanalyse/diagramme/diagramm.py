import matplotlib.pyplot as plt


class Diagramm:
    def __init__(
        self,
        name,
        figsize=(5.5, 3.5),
        pfad="diagramme/",
        y2=False,
        colors: list = "standard",
        linestyles: list = "standard",
    ):
        """
        Superklasse für Diagramme
        :param name: Name des Diagramms (entspricht gewünschtem Dateinamen)
        :param figsize: Größe des Diagramms (Bildfläche, Angabe in Zoll)
        :param pfad: Pfad für die zu speichernde Datei
        :param y2: True aktiviert die 2. y-Achse
        """
        self.name = name
        self.figsize = figsize
        self.pfad = pfad

        self.fig, self.ax1 = self.neues_diagramm()

        # Erstellung 2. y-Achse wenn True
        if y2:
            self.ax2 = self.ax1.twinx()

        # generelle Festlegungen zu Plot-Farben
        if colors == "standard":
            prop_cycle = plt.rcParams["axes.prop_cycle"]
            self.colors = prop_cycle.by_key()["color"]
        else:
            self.colors = colors
        # generelle Festlegungen zu Plot-Linienarten
        if linestyles == "standard":
            self.linestyles = ["-"] * len(
                self.colors
            )  # so viele durchgezogene Linien in Liste wie es Farben gibt
        else:
            self.linestyles = linestyles

    def neues_diagramm(self, layout="constrained"):
        """
        Erstellung eines neuen Diagramms mit einer y-Achse
        :param layout: Layout des Diagramms
        :return: fig (Diagramm), ax1 (y-Achse)
        """
        fig, ax1 = plt.subplots(figsize=self.figsize, layout=layout)
        return fig, ax1

    def set_axformat(self, x_label=None, y_label=None, title=None, ax="ax1", **kwargs):
        """
        Anpassung von Achsenbeschriftung, Titel etc.
        :param ax: Angabe der Achsen (standardmäßig Achsenpaar 1)
        :param x_label:
        :param y_label:
        :param title:
        :param kwargs:
        """
        if ax == "ax1":
            self.ax1.set(xlabel=x_label, ylabel=y_label, title=title, **kwargs)
        elif ax == "ax2":
            self.ax2.set(xlabel=x_label, ylabel=y_label, title=title, **kwargs)
        else:
            print("Fehler, mehr als zwei Achsen werden aktuell nicht unterstützt.")

    def set_legend(self, **kwargs):
        self.ax1.legend(**kwargs)

    def speichern(self, bbox_inches="tight", **kwargs):
        """
        Speichern des Diagramms unter dem gegebenen Pfad+Namen
        :param bbox_inches: Bestimmt Umgang mit weißem Rand um Diagramm, 'tight' entfernt diesen
        """
        speicherpfad = self.pfad + self.name
        self.fig.savefig(speicherpfad, bbox_inches=bbox_inches, **kwargs)
        print(self.__class__, "gespeichert unter", speicherpfad)
