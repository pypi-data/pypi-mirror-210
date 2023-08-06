import pandas as pd  # Öffnen, Einlesen, Bearbeiten von Exceldaten in Form von Dataframes
import pathlib  # Pfade zu Versuchsordnern und Dateien
from datetime import datetime  # Erstellen und Bearbeiten von Zeitstempeln


class Dataelement:
    def __init__(
        self,
        pfad: pathlib.Path,
        daten: pd.DataFrame = pd.DataFrame(),
        name=None,
        oberelement=None,
        unterelemente: list = [],
    ):
        """
        Objekt, welches die Daten einer Datei / eines Versuchs / einer Versuchsreihe beinhaltet.
        Ein Dataelement kann wiederum aus mehreren Unterelementen bestehen und/oder zu einem Oberelement dazugehören.
        :param pfad: Pfad zur Datei / zum Versuch(sreihen)ordner (als pathlib-Objekt)
        :param daten: Daten (als Dataframe-Objekt, optional)
        :param name: Name des Dataelements (optional), entspricht falls nicht angegeben dem Datei-/Ordnernamen
        :param oberelement: Zuweisung des Objekts zu einem übergeordneten Dataelement (optional)
        :param unterelemente: Liste mit allen zum Objekt gehörenden untergeordneten Dataelementen (optional)
        """

        # übergebene statische Attribute:
        self.pfad = pfad
        self.daten = daten

        """ abgeleitete Attribute: """
        # letzter Teil des Pfades wird als Name genutzt (kann Datei oder Ordner sein), wenn nicht angegeben
        if name is None:
            self.name = pfad.name
        else:
            self.name = name

        # legt Typ des Elements anhand des Pfades fest
        try:
            if pfad.is_dir():
                self.elementtyp = "ordner"
            elif pfad.is_file():
                self.elementtyp = "datei"
        except AttributeError:
            self.elementtyp = None

        """ dynamische Attribute zur Strukturierung (können zur Laufzeit angepasst werden): """

        # Oberelement festlegen, wenn eines angegeben ist (kann auch später erfolgen)
        if oberelement is None:
            self.oberelement = None
        else:
            self.ist_unterelement_von(oberelement)

        # Liste der Unterelement(e) festlegen, wenn welche angegeben sind (kann auch später erfolgen)
        self.unterelemente = list()
        for unterelement in unterelemente:
            self.unterelemente.append(unterelement)

    def ist_unterelement_von(self, oberelement):
        """
        weist das Dataelement einem übergeordneten Dataelement zu
        :param oberelement: muss selbst ein Dataelement sein
        """
        if type(oberelement) == Dataelement:
            self.oberelement = oberelement
            oberelement.unterelemente.append(self)
        else:
            print(
                datetime.now(),
                "Fehler in",
                self.name + ":",
                "Oberelement muss vom Typ Dataelement sein.",
            )

    def lese_daten_unformatiert_ein(self):
        """
        Einlesen der Datei einer Datei ohne weitere Formatierung für einen "ersten Blick"
        Aktuell funktioniert dies nur mit Excel-Dateien, da csv nicht standardisiert ist
        """
        if self.elementtyp != "datei":
            print(
                datetime.now(),
                "Fehler in",
                self.name + ":",
                "Nur Typ Datei kann Rohdaten einlesen.",
            )
            exit()

        dateityp = self.pfad.suffix

        try:
            if dateityp == ".xlsx":
                self.daten = pd.read_excel(self.pfad)
            else:
                print(
                    datetime.now(),
                    "Fehler in",
                    self.name + ":",
                    "Dateityp nicht unterstützt.",
                )
        except AttributeError:
            print(
                datetime.now(),
                "AttributeError in der Funktion lese_daten_unformatiert_ein",
            )

    def lese_daten_formatiert_ein(self, format_dict: dict):
        if self.elementtyp == "datei":
            for key in format_dict.keys():
                if key in self.name:
                    self.daten = format_dict[key](dataelement=self)
                    break
        else:
            print(
                datetime.now(),
                "Fehler in",
                self.name + ":",
                "Typ Ordner kann keine Rohdaten einlesen.",
            )

    def mergeasof_unterelemente(self, abfolge_liste: list):
        """
        Reiht die Daten aller Unterlemente nebeneinander an (anhand Zeitstempel) in der Reihenfolge der Listenelemente.
        Bestehende Daten des Dataelements werden NICHT überschrieben.
        :param abfolge_liste: Reihenfolge, in der Unterelemente aufgereiht werden (Listen-Item muss im Namen auftauchen)
        """
        for item in abfolge_liste:
            for element in self.unterelemente:
                if item in element.name:
                    daten_aktuell = self.daten
                    if daten_aktuell.empty:
                        daten_neu = element.daten
                    else:
                        daten_neu = pd.merge_asof(
                            daten_aktuell,
                            element.daten,
                            left_index=True,
                            right_index=True,
                            direction="backward",
                        )
                    self.daten = daten_neu

    def concat_unterelemente(self):
        """
        Reiht die Daten aller Unterelemente aneinander. Bestehende Daten des Dataelements werden NICHT überschrieben.
        """
        for element in self.unterelemente:
            daten_aktuell = self.daten
            if daten_aktuell.empty:
                daten_neu = element.daten
            else:
                daten_neu = pd.concat([daten_aktuell, element.daten])
            self.daten = daten_neu

    def daten_speichern(self, dateipfad="standard", dateityp="xlsx"):
        if dateipfad == "standard":
            if self.elementtyp == "datei":
                pfad = (
                    str(self.pfad.parent) + "_" + str(self.pfad.stem) + "." + dateityp
                )
            else:
                pfad = str(self.pfad) + "." + dateityp
        else:
            pfad = str(dateipfad) + "." + dateityp

        if dateityp == "xlsx":
            with pd.ExcelWriter(pfad) as Writer:
                self.daten.to_excel(Writer)
                print(datetime.now(), "Speichere", self.name, "unter", pfad + ".")
        elif dateityp == "csv":
            self.daten.to_csv(pfad, sep=";", decimal=",")
            print(datetime.now(), "Speichere", self.name, "unter", pfad + ".")
        else:
            print(
                datetime.now(),
                "Fehler in",
                self.name + ":",
                "Kann aktuell nur xlsx- und csv-Dateien abspeichern.",
            )

    def daten_aller_unterelemente_speichern(self, dateipfad="standard"):
        if self.elementtyp == "datei":
            print(
                datetime.now(),
                "Fehler in",
                self.name + ":",
                "Typ Datei dürfte keine Unterelemente haben.",
            )
        else:
            if dateipfad == "standard":
                pfad = str(self.pfad) + ".xlsx"
            else:
                pfad = str(dateipfad) + ".xlsx"

            with pd.ExcelWriter(pfad) as Writer:
                for unterelement in self.unterelemente:
                    unterelement.daten.to_excel(Writer, sheet_name=unterelement.name)

    """ Testfunktionen: """

    def dein_name(self):
        print(
            datetime.now(),
            "Testfunktion ausgelöst von",
            self.name + ":",
            "Dein Name?",
            self.name,
        )

    def dein_typ(self):
        print(
            datetime.now(),
            "Testfunktion ausgelöst von",
            self.name + ":",
            "Dein Typ?",
            self.elementtyp,
        )

    def deine_unterlemente(self):
        liste_der_unterelementnamen = []
        anzahl_der_unterelemente = 0
        for unterelement in self.unterelemente:
            liste_der_unterelementnamen.append(unterelement.name)
            anzahl_der_unterelemente += 1

        print(
            datetime.now(),
            "Testfunktion ausgelöst von",
            self.name + ":",
            "\nAnzahl Unterelemente?",
            anzahl_der_unterelemente,
            "\nNamen der Unterelemente?",
            liste_der_unterelementnamen,
        )


if __name__ == "__main__":
    pass
