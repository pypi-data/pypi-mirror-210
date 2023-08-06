import pandas as pd
from datetime import datetime, timedelta

# from .dataelement import Dataelement - does not work in vsc
# from src.datanalyse.dataelement.dataelement import Dataelement - does not work in vsc
from .dataelement import Dataelement
from . import dfmanipulation as dfm


def wincontrol_standard(
    dataelement: Dataelement,
    dropna_spalten=True,
    dropna_zeilen=True,
    rolling_zeitschritt=None,
    resample_zeitschritt="1min",
    nur_ergebniszeile=False,
):
    """
    Standard-Einlese-Formatierung für xlsx-Daten aus einer WinControl-Tabelle
    :param dataelement: Dataelement
    :param dropna_spalten: drop alle leeren Spalten
    :param dropna_zeilen: drop alle Zeilen mit teilweise leerem Inhalt
    :param rolling_zeitschritt: Es wird über die Höhe des Zeitschritts der gleitende Mittelwert gebildet
    :param resample_zeitschritt: Resampling aller Daten dient der Umrechnung auf eine gemeinsame Zeitschrittweite, es werden alle zur Zeitschrittweite gehörenden Werte gemittelt
    :param nur_ergebniszeile:
    :return: formatiertes Dataelement
    """
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        parse_dates=[["Datum", "Zeit"]],
        # date_format=None,
    )

    # Zeitstempel wird als Index gesetzt
    df.set_index("Datum_Zeit", inplace=True)

    # drop alle Spalten, bei denen absolut nichts drin steht (beugt Fehlern vor, tritt vor allem bei Sollwerten auf)
    if dropna_spalten:
        df.dropna(how="all", axis=1, inplace=True)

    # drop alle Zeilen, bei denen zum Teil nichts drin steht (beugt Fehlern vor, tritt vor allem bei Sollwerten auf)
    if dropna_zeilen:
        df.dropna(inplace=True)

    # Schneide von den Spaltennamen die Messstelle ab und hänge die Einheit an, Achtung: tricky ;-)
    # für jede Spaltenbezeichnung im Dataframe...
    for Spalte in df.columns:
        # schaue, ob das erste Zeichen der Spalte eine Zahl ist (dann ist es eine Messstelle); wenn ja...
        if Spalte[0].isdigit():
            # "Spalte[(Spalte.find(" ")+1):]" entspricht dem Spaltennamen, aber durch "Spalte.find(" ")+1"
            # wird alles bis inklusive des Leerzeichens abgeschnitten
            # "df.iloc[1, df.columns.get_loc(Spalte)+1]" entspricht der Einheit in der ersten Zeile eine Spalte
            # daneben; beides zusammen soll den alten Spaltennamen ersetzen
            df.rename(
                columns={
                    Spalte: Spalte[(Spalte.find(" ") + 1) :]
                    + " ("
                    + df.iloc[0, df.columns.get_loc(Spalte) + 1]
                    + ")"
                },
                inplace=True,
            )

    # Einheiten-Spalten entfernen, indem nur Spalten übernommen werden, die nicht "Unnamed" enthalten (nicht => "~")
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]

    # Sortiere Spalten alphabetisch, damit bspw. die Temperaturlanzenwerte in geordneter Reihenfolge erscheinen
    df = df.loc[:, sorted(list(df.columns))]

    # auf Wunsch Datenmanipulation
    df = dfm.rolling_resample_ergebniszeile(
        df, rolling_zeitschritt, resample_zeitschritt, nur_ergebniszeile
    )

    # Übergebe das fertige Dataframe zurück
    return df


def wincontrol_csv(
    dataelement: Dataelement,
    dropna_spalten=True,
    dropna_zeilen=True,
    rolling_zeitschritt=None,
    resample_zeitschritt="1min",
    nur_ergebniszeile=False,
):
    """
    Standard-Einlese-Formatierung für csv-Daten aus einer WinControl-Tabelle
    :param dataelement: Dataelement
    :param dropna_spalten: drop alle leeren Spalten
    :param dropna_zeilen: drop alle Zeilen mit teilweise leerem Inhalt
    :param rolling_zeitschritt: Es wird über die Höhe des Zeitschritts der gleitende Mittelwert gebildet
    :param resample_zeitschritt: Resampling aller Daten dient der Umrechnung auf eine gemeinsame Zeitschrittweite, es werden alle zur Zeitschrittweite gehörenden Werte gemittelt
    :param nur_ergebniszeile:
    :return: formatiertes Dataelement
    """
    df = pd.read_csv(
        dataelement.pfad,
        sep=";",
        decimal=",",
        encoding="ANSI",
        index_col=0,
        header=2,
        skiprows=[3, 4, 5, 6],
        parse_dates=[[0, 1]],
        dayfirst=True,  # Verhindert Verwechslung von Tag und Monat beim Einlesen des Datums
    )

    # Indexspalte einen ordentlichen Namen geben (heißt aktuell etwa "Kommentar_Unnamed: 1")
    df.index.names = ["Datum_Zeit"]

    # drop alle Spalten, bei denen absolut nichts drin steht (beugt Fehlern vor, tritt vor allem bei Sollwerten auf)
    if dropna_spalten:
        df.dropna(how="all", axis=1, inplace=True)

    # drop alle Zeilen, bei denen zum Teil nichts drin steht (beugt Fehlern vor, tritt vor allem bei Sollwerten auf)
    if dropna_zeilen:
        df.dropna(inplace=True)

    # Sortiere Spalten alphabetisch, damit bspw. die Temperaturlanzenwerte in geordneter Reihenfolge erscheinen
    df = df.loc[:, sorted(list(df.columns))]

    # auf Wunsch Datenmanipulation
    df = dfm.rolling_resample_ergebniszeile(
        df, rolling_zeitschritt, resample_zeitschritt, nur_ergebniszeile
    )

    # Übergebe das fertige Dataframe zurück
    return df


def mothership(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=4,
        index_col=0,
    )

    # Überspring die ersten beiden Zeilen, da leer bzw. 0
    df = df.iloc[2:]

    # Konvertiere Zeitstempel-String im Index zu echtem Zeitstempel
    df.index = pd.to_datetime(df.index)

    # Das Datum der Messung wird aus dem Dateinamen entnommen
    messdatum = pd.to_datetime(str(dataelement.pfad.name)[37:47], format="%d_%m_%Y")
    # ersetze Datum im Zeitstempel durch das Datum der Speicherzeit
    df.index = df.index.map(
        lambda x: x.replace(
            year=messdatum.year, month=messdatum.month, day=messdatum.day
        )
    )

    # Resampling der Daten
    df = df.resample("1min").mean()

    # Letzter Schliff:
    # Lösche Sollwerte, da keine sinnvollen Werte enthalten
    df.drop(labels="Sollwert aller Wände", axis=1, inplace=True)

    # Übergebe das fertige Dataframe zurück
    return df


def klimaanlage(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=9,
        index_col="Name",  # Die Zeitstempel stehen in Excel unter der Spalte "Name"
    )

    # Überspring die ersten 4 Zeilen, da leer bzw. 0
    df = df.iloc[4:]

    # Konvertiere Zeitstempel-String zu echtem Zeitstempel; Formatvorgabe nötig, da sonst Vertauschen von Tag/Monat
    df.index = pd.to_datetime(df.index, format="%d.%m.%Y %H:%M:%S.%f")

    # Konvertiere alle restlichen Daten zum Typ float (Gleitkommazahl),
    # da sonst Strings, mit denen kein Resample möglich (keine Mittelwertbildung)
    df = df.astype(float)

    # Letzter Schliff:
    # Übernehme zur besseren Übersicht nur die nützlichen Daten
    df = df.loc[
        :,
        [
            "Außenluft Temperatur (TV6)",
            "Abluft (TV5)",
            "Zuluft (TV3)",
            "Status Kühlen",
            "Status Heizen",
        ],
    ]

    # Benenne Spalten
    df.rename(
        columns={
            "Außenluft Temperatur (TV6)": "Hallentemperatur",
            "Abluft (TV5)": "Ablufttemperatur",
            "Zuluft (TV3)": "Zulufttemperatur",
            "Status Kühlen": "Regler Kühlen",
            "Status Heizen": "Regler Heizen",
        },
        inplace=True,
    )

    # Resampling der Daten
    df = df.resample("1min").mean()

    # Übergebe das fertige Dataframe zurück
    return df


def umbuzoo_standard(dataelement: Dataelement):
    pass


def umbuzoo_person(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=None,
        index_col=None,
        skiprows=8,  # 8 Zeilen unnützer Informationen werden direkt beim Einlesen übersprungen
    )

    # Spalten entfernen, die komplett leer sind (Abstandsspalten des ursprünglichen Files)
    df.dropna(axis=1, how="all", inplace=True)

    # Überschriftenzeile 1 wird nach rechts aufgefüllt (Vorbereitung für Gruppierung)
    df.loc[0] = df.loc[0].fillna(method="ffill")

    # Überschriftenzeile 1 wird zu den Spaltenüberschriften des Dataframes
    df.columns = df.loc[0]

    # Ersetze alle "Kreuze" in Zeile 2 (nur hier sind die Antworten) durch den Antworttext in Überschriftenzeile 2
    for Spaltennummer in range(0, len(df.columns)):
        if df.iloc[2, Spaltennummer] == "X":
            df.iloc[2, Spaltennummer] = df.iloc[1, Spaltennummer]

    # Übernehme nur die letzte Zeile, übernehme nicht die ersten 2 und die letzten 3 Spalten (Müll abgeschnitten)
    df = df.iloc[-1:, 2:-3]

    # Startzeitpunkt als Index verwenden (Zeitstempel)
    df.set_index("Zusatzinformationen", inplace=True)

    # Es sind nun alle relevanten Daten vorhanden. Für den letzten Schritt müssen fehlende Werte (NaN) jedoch mit ""
    # gefüllt werden, da im Ergebnis des sum() unten sonst "0" herauskommen würde.
    df.fillna("", inplace=True)

    # Nun können die Spalten mit gleichem Namen aggregiert werden, um nur noch den Antworten-Text zu beinhalten
    df = df.groupby(by=df.columns, axis=1).sum()

    # Letzter Schliff:

    # Benenne Index-Spalte
    df.index.name = "Startzeitpunkt"

    # Benenne Spalten
    df.rename(
        columns={
            "Bitte geben Sie Ihr Alter (in Jahren) an.": "Alter (a)",
            "Bitte geben Sie Ihr Geschlecht an.": "Geschlecht",
            "Bitte geben Sie Ihr Gewicht (in kg) an.": "Gewicht (kg)",
            "Bitte geben Sie Ihre Körpergröße (in cm) an.": "Größe (cm)",
            "Was schätzen Sie, ist Ihre Wohlfühl-Raumtemperatur (in °C)?": "Wunschtemperatur (°C)",
            "Wie haben Sie den Weg bis hierher zurückgelegt?": "Weg",
        },
        inplace=True,
    )

    # Wandle Antworten in Zahlen um, da sich damit besser rechnen lässt bzw. Darstellung in Diagrammen einfacher:
    df = dfm.ersetze_spalten_werte(df, ["Geschlecht"], ["Männlich", "Weiblich"], [1, 0])
    df = dfm.ersetze_spalten_werte(
        df, ["Geschlecht"], ["männlich", "weiblich", "divers"], [1, 0, -1]
    )  # V2.0

    # Übergebe das fertige Dataframe zurück
    return df


def umbuzoo_abschluss_viessmann(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=None,
        index_col=None,
        skiprows=8,  # 8 Zeilen unnützer Informationen werden direkt beim Einlesen übersprungen
    )

    # Spalten entfernen, die komplett leer sind (Abstandsspalten des ursprünglichen Files)
    df.dropna(axis=1, how="all", inplace=True)

    # Überschriftenzeile 1 wird nach rechts aufgefüllt (Vorbereitung für Gruppierung)
    df.loc[0] = df.loc[0].fillna(method="ffill")

    # Überschriftenzeile 1 wird zu den Spaltenüberschriften des Dataframes
    df.columns = df.loc[0]

    # Ersetze alle "Kreuze" in Zeile 2 (nur hier sind die Antworten) durch den Antworttext in Überschriftenzeile 2
    for Spaltennummer in range(0, len(df.columns)):
        if df.iloc[2, Spaltennummer] == "X":
            df.iloc[2, Spaltennummer] = df.iloc[1, Spaltennummer]

    # Übernehme nur die letzte Zeile, übernehme nicht die ersten 2 und die letzten 3 Spalten (Müll abgeschnitten)
    df = df.iloc[-1:, 2:-3]

    # Startzeitpunkt als Index verwenden (Zeitstempel) und 95 min abziehen, damit der "merge backwards" funktioniert
    df["Zusatzinformationen"] = df["Zusatzinformationen"] - timedelta(minutes=95)
    df.set_index("Zusatzinformationen", inplace=True)

    # Es sind nun alle relevanten Daten vorhanden. Für den letzten Schritt müssen fehlende Werte (NaN) jedoch mit ""
    # gefüllt werden, da im Ergebnis des sum() unten sonst "0" herauskommen würde.
    df.fillna("", inplace=True)

    # Nun können die Spalten mit gleichem Namen aggregiert werden, um nur noch den Antworten-Text zu beinhalten
    df = df.groupby(by=df.columns, axis=1).sum()

    # Letzter Schliff:

    # Benenne Index-Spalte
    df.index.name = "Startzeitpunkt"

    # Benenne Spalten
    df.rename(
        columns={
            "(Bitte beurteilen Sie aus Ihrer Sicht die folgenden Punkte zum soeben genutzten Heizsystem.) "
            "Die Bedienung des Heizsystems über den Regler am PC war leicht verständlich.": "Reglerbewertung",
            "(Bitte beurteilen Sie aus Ihrer Sicht die folgenden Punkte zum soeben genutzten Heizsystem.) "
            "Das Heizsystem hat auf meine Änderungen schnell reagiert.": "Reakionsgeschwindigkeit",
            "(Bitte beurteilen Sie aus Ihrer Sicht die folgenden Punkte zum soeben genutzten Heizsystem.) "
            "Das Verhalten des Heizsystems war wie erwartet.": "Erwartung",
            "(Bitte beurteilen Sie aus Ihrer Sicht die folgenden Punkte zum soeben genutzten Heizsystem.) "
            "Die Positionierung des Heizsystems war genau richtig.": "Positionierung",
            "Falls Sie Aussagen der vorherigen Seite weniger oder nicht zugestimmt haben, "
            "teilen Sie uns bitte Ihre Verbesserungswünsche mit.": "Verbesserungswünsche",
        },
        inplace=True,
    )

    # Wandle Antworten in Zahlen um, da sich damit besser rechnen lässt bzw. Darstellung in Diagrammen einfacher:
    df = dfm.ersetze_spalten_werte(
        df,
        ["Reglerbewertung", "Reakionsgeschwindigkeit", "Erwartung", "Positionierung"],
        [
            "stimme voll zu",
            "stimme etwas zu",
            "weder noch",
            "stimme weniger zu",
            "stimme nicht zu",
        ],
        [2, 1, 0, -1, -2],
    )

    # Übergebe das fertige Dataframe zurück
    return df


def umbuzoo_klimaraum(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=None,
        index_col=None,
        skiprows=8,  # 8 Zeilen unnützer Informationen werden direkt beim Einlesen übersprungen
    )

    # Spalten entfernen, die komplett leer sind (Abstandsspalten des ursprünglichen Files)
    df.dropna(axis=1, how="all", inplace=True)

    # Übergeordnete Spaltenüberschriftenzeile wird nach rechts aufgefüllt (Vorbereitung für nächsten Schritt)
    df.loc[0] = df.loc[0].fillna(method="ffill")

    # Überschriftenzeile 1 wird zu den Spaltenüberschriften des Dataframes
    df.columns = df.loc[0]

    # Ersetze alle "Kreuze" ab Zeile 3 (nur hier sind die Antworten) durch den Antworttext in Überschriftenzeile 2
    for Zeilennummer in range(2, len(df)):
        for Spaltennummer in range(0, len(df.columns)):
            if df.iloc[Zeilennummer, Spaltennummer] == "X":
                df.iloc[Zeilennummer, Spaltennummer] = df.iloc[1, Spaltennummer]

    # Kehrt die Reihenfolge um (Chronologie) und lässt die ersten beiden Zeilen aus (alte Überschriften)
    df = df.iloc[:1:-1, 2:-3]

    # Startzeitpunkt als Index verwenden (Zeitstempel)
    df.set_index("Zusatzinformationen", inplace=True)

    # Es sind nun alle relevanten Daten vorhanden. Für den letzten Schritt müssen fehlende Werte (NaN) jedoch mit ""
    # gefüllt werden, da im Ergebnis des sum() unten sonst "0" herauskommen würde.
    df.fillna("", inplace=True)

    # Nun können die Spalten mit gleichem Namen aggregiert werden, um nur noch den Antworten-Text zu beinhalten
    df = df.groupby(by=df.columns, axis=1).sum()

    # Letzter Schliff:
    # Benenne Index-Spalte
    df.index.name = "Startzeitpunkt"

    # Benenne Spalten um (wenn eine Spalte mal nicht existiert, wird kein Fehler ausgeworfen)
    df.rename(
        columns={
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Arme:": "Arme",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Beine:": "Beine",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Füße:": "Füße",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Hände:": "Hände",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Kopf:": "Kopf",
            "(Wie empfinden Sie die momentane Raumtemperatur?) Es ist...": "Global",
            "Empfinden Sie es irgendwo am Körper als kühl oder warm?": "lokal?",
            "Ist dies unangenehm?": "unangenehm?",  # Wortlaut der Frage beim Deckensystem
            "Empfinden Sie dies als unangenehm?": "unangenehm?",  # Wortlaut der Frage beim Halbraum
            "Haben Sie noch Anmerkungen?": "Anmerkungen",
            "Möchten Sie eine Änderung der Raumtemperatur?": "Änderung?",
            "Welche Änderung wünschen Sie sich?": "Wunsch",
            "Wie fühlt sich die Luft für Sie an?": "Luftqualität",
        },
        inplace=True,
    )

    # Wandle Antworten in Zahlen um, da sich damit besser rechnen lässt bzw. Darstellung in Diagrammen einfacher:
    # Liste der Zahlen wird mal explizit, mal mit "range" gebildet - einfach, weil es geht :)
    df = dfm.ersetze_spalten_werte(
        df,
        ["Arme", "Beine", "Füße", "Hände", "Kopf"],
        ["kühl", "neutral", "warm", ""],
        [-1, 0, 1, 0],
    )
    df = dfm.ersetze_spalten_werte(
        df,
        ["Global"],
        ["zu kühl", "kühl", "etwas kühl", "neutral", "etwas warm", "warm", "zu warm"],
        range(-3, 4),
    )
    df = dfm.ersetze_spalten_werte(
        df, ["lokal?", "unangenehm?", "Änderung?"], ["ja", "nein", ""], [1, 0, 0]
    )
    df = dfm.ersetze_spalten_werte(df, ["Wunsch"], ["wärmer", "kühler", ""], [1, -1, 0])
    df = dfm.ersetze_spalten_werte(
        df, ["Luftqualität"], ["1", "2", "3", "4", "5"], range(-2, 3)
    )

    # Übergebe das fertige Dataframe zurück
    return df


def umbuzoo_klimaraum_hybrid(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=None,
        index_col=None,
        skiprows=8,  # 8 Zeilen unnützer Informationen werden direkt beim Einlesen übersprungen
    )

    # Spalten entfernen, die komplett leer sind (Abstandsspalten des ursprünglichen Files)
    df.dropna(axis=1, how="all", inplace=True)

    # Übergeordnete Spaltenüberschriftenzeile wird nach rechts aufgefüllt (Vorbereitung für nächsten Schritt)
    df.loc[0] = df.loc[0].fillna(method="ffill")

    # Überschriftenzeile 1 wird zu den Spaltenüberschriften des Dataframes
    df.columns = df.loc[0]

    # Frage nach lokaler Zuglufterscheinung und unangenehm benötigt Ergänzung, da andernfalls keine Unterscheidung
    search_Zugluft = "Bitte geben Sie die jeweiligen Körperbereiche an, an denen Sie Zuglufterscheinungen empfinden."
    parts_Zugluft = ["Kopf", "Nacken", "Rücken", "Arme", "Hände", "Beine", "Füße"]
    search_unangenehm = "Ist dies unangenehm?"
    parts_unangenehm = ["lokal", "lokal", "Zugluft", "Zugluft"]
    new_columns = []
    for column in df.columns:
        if column == search_Zugluft:
            new_columns.append("Zugluft_" + parts_Zugluft.pop(0))
        elif column == search_unangenehm:
            new_columns.append(parts_unangenehm.pop(0) + "_unangenehm?")
        else:
            new_columns.append(column)
    df.columns = new_columns

    # Ersetze alle "Kreuze" ab Zeile 3 (nur hier sind die Antworten) durch den Antworttext in Überschriftenzeile 2
    for Zeilennummer in range(2, len(df)):
        for Spaltennummer in range(0, len(df.columns)):
            if df.iloc[Zeilennummer, Spaltennummer] == "X":
                df.iloc[Zeilennummer, Spaltennummer] = df.iloc[1, Spaltennummer]

    # Kehrt die Reihenfolge um (Chronologie) und lässt die ersten beiden Zeilen aus (alte Überschriften)
    df = df.iloc[:1:-1, 2:-3]

    # Startzeitpunkt als Index verwenden (Zeitstempel)
    df.set_index("Zusatzinformationen", inplace=True)

    # Es sind nun alle relevanten Daten vorhanden. Für den letzten Schritt müssen fehlende Werte (NaN) jedoch mit ""
    # gefüllt werden, da im Ergebnis des sum() unten sonst "0" herauskommen würde.
    df.fillna("", inplace=True)

    # Nun können die Spalten mit gleichem Namen aggregiert werden, um nur noch den Antworten-Text zu beinhalten
    df = df.groupby(by=df.columns, axis=1).sum()

    # Letzter Schliff:
    # Benenne Index-Spalte
    df.index.name = "Startzeitpunkt"

    # Benenne Spalten um (wenn eine Spalte mal nicht existiert, wird kein Fehler ausgeworfen)
    df.rename(
        columns={
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Arme:": "Arme",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Beine:": "Beine",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Füße:": "Füße",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Hände:": "Hände",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Kopf:": "Kopf",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Nacken:": "Nacken",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Rücken:": "Rücken",
            "(Wie empfinden Sie die momentane Raumtemperatur?) Es ist...": "Global",
            "Empfinden Sie es irgendwo am Körper als kühl oder warm?": "lokal?",
            "Empfinden Sie irgendwo am Körper Zuglufterscheinungen?": "Zugluft?",
            "Ist dies unangenehm?": "lokal_unangenehm?",  # Wortlaut der Frage beim Deckensystem
            "Empfinden Sie dies als unangenehm?": "lokal_unangenehm?",  # Wortlaut der Frage beim Halbraum
            "Haben Sie noch Anmerkungen?": "Anmerkungen",
            "Möchten Sie eine Änderung der Raumtemperatur?": "Änderung?",
            "Welche Änderung wünschen Sie sich?": "Wunsch",
            "Wie fühlt sich die Luft für Sie an?": "Luftqualität",
            "Wie sehr nehmen Sie Störgeräusche der Lüftungsanlage wahr?": "Störgeräusche",
        },
        inplace=True,
    )

    # Wandle Antworten in Zahlen um, da sich damit besser rechnen lässt bzw. Darstellung in Diagrammen einfacher:
    # Liste der Zahlen wird mal explizit, mal mit "range" gebildet - einfach, weil es geht :)
    df = dfm.ersetze_spalten_werte(
        df,
        ["Arme", "Beine", "Füße", "Hände", "Kopf", "Nacken", "Rücken"],
        ["kühl", "neutral", "warm", ""],
        [-1, 0, 1, 0],
    )
    df = dfm.ersetze_spalten_werte(
        df,
        ["Global"],
        ["zu kühl", "kühl", "etwas kühl", "neutral", "etwas warm", "warm", "zu warm"],
        range(-3, 4),
    )
    df = dfm.ersetze_spalten_werte(
        df,
        ["lokal?", "lokal_unangenehm?", "Änderung?", "Zugluft?", "Zugluft_unangenehm?"],
        ["ja", "nein", ""],
        [1, 0, 0],
    )
    df = dfm.ersetze_spalten_werte(df, ["Wunsch"], ["wärmer", "kühler", ""], [1, -1, 0])
    df = dfm.ersetze_spalten_werte(
        df,
        [
            "Zugluft_Arme",
            "Zugluft_Beine",
            "Zugluft_Füße",
            "Zugluft_Hände",
            "Zugluft_Kopf",
            "Zugluft_Nacken",
            "Zugluft_Rücken",
        ],
        ["Arme", "Beine", "Füße", "Hände", "Kopf", "Nacken", "Rücken", ""],
        [1, 1, 1, 1, 1, 1, 1, 0],
    )
    df = dfm.ersetze_spalten_werte(
        df, ["Luftqualität", "Störgeräusche"], ["1", "2", "3", "4", "5"], range(1, 6)
    )

    # Übergebe das fertige Dataframe zurück
    return df


def umbuzoo_klimaraum_viessmann(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=None,
        index_col=None,
        skiprows=8,  # 8 Zeilen unnützer Informationen werden direkt beim Einlesen übersprungen
    )

    # Spalten entfernen, die komplett leer sind (Abstandsspalten des ursprünglichen Files)
    df.dropna(axis=1, how="all", inplace=True)

    # Übergeordnete Spaltenüberschriftenzeile wird nach rechts aufgefüllt (Vorbereitung für nächsten Schritt)
    df.loc[0] = df.loc[0].fillna(method="ffill")

    # Überschriftenzeile 1 wird zu den Spaltenüberschriften des Dataframes
    df.columns = df.loc[0]

    # Ersetze alle "Kreuze" ab Zeile 3 (nur hier sind die Antworten) durch den Antworttext in Überschriftenzeile 2
    for Zeilennummer in range(2, len(df)):
        for Spaltennummer in range(0, len(df.columns)):
            if df.iloc[Zeilennummer, Spaltennummer] == "X":
                df.iloc[Zeilennummer, Spaltennummer] = df.iloc[1, Spaltennummer]

    # Kehrt die Reihenfolge um (Chronologie) und lässt die ersten beiden Zeilen aus (alte Überschriften)
    df = df.iloc[:1:-1, 2:-3]

    # Startzeitpunkt als Index verwenden (Zeitstempel)
    df.set_index("Zusatzinformationen", inplace=True)

    # Es sind nun alle relevanten Daten vorhanden. Für den letzten Schritt müssen fehlende Werte (NaN) jedoch mit ""
    # gefüllt werden, da im Ergebnis des sum() unten sonst "0" herauskommen würde.
    df.fillna("", inplace=True)

    # Nun können die Spalten mit gleichem Namen aggregiert werden, um nur noch den Antworten-Text zu beinhalten
    df = df.groupby(by=df.columns, axis=1).sum()

    # Letzter Schliff:
    # Benenne Index-Spalte
    df.index.name = "Startzeitpunkt"

    # Benenne Spalten um (wenn eine Spalte mal nicht existiert, wird kein Fehler ausgeworfen)
    df.rename(
        columns={
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Arme:": "Arme",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Beine:": "Beine",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Füße:": "Füße",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Hände:": "Hände",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Kopf:": "Kopf",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Nacken:": "Nacken",
            "(Bitte geben Sie für den jeweiligen Körperbereich Ihre Empfindung an.) Rücken:": "Rücken",
            "(Wie empfinden Sie jetzt gerade die aktuelle Raumtemperatur?) Es ist...": "Global",
            "Empfinden Sie es irgendwo am Körper als kühl oder warm?": "lokal?",
            "Ist dies für Sie unangenehm?": "lokal_unangenehm?",  # Wortlaut der Frage bei Viessmann
            "Haben Sie noch Anmerkungen?": "Anmerkungen",
            "Haben Sie seit der letzten Umfrage eine Veränderung am Heizungsregler vorgenommen?": "Reglereingriff",
            "Möchten Sie eine Änderung der Raumtemperatur?": "Änderung?",
            "Sind Sie im Allgemeinen mit dem Raumklima zufrieden?": "Zufriedenheit",
            "Warum haben Sie diese Änderung vorgenommen?": "Reglerbegründung",
            "Wie fühlt sich die Luft für Sie an?": "Luftqualität",
        },
        inplace=True,
    )

    # Wandle Antworten in Zahlen um, da sich damit besser rechnen lässt bzw. Darstellung in Diagrammen einfacher:
    # Liste der Zahlen wird mal explizit, mal mit "range" gebildet - einfach, weil es geht :)
    df = dfm.ersetze_spalten_werte(
        df,
        ["Arme", "Beine", "Füße", "Hände", "Kopf", "Nacken", "Rücken"],
        ["kühl", "neutral", "warm", ""],
        [-1, 0, 1, 0],
    )
    df = dfm.ersetze_spalten_werte(
        df,
        ["Global"],
        ["kalt", "kühl", "etwas kühl", "neutral", "etwas warm", "warm", "heiß"],
        range(-3, 4),
    )
    df = dfm.ersetze_spalten_werte(
        df,
        ["lokal?", "lokal_unangenehm?", "Reglereingriff", "Zufriedenheit"],
        ["ja", "nein", ""],
        [1, 0, 0],
    )
    df = dfm.ersetze_spalten_werte(
        df, ["Änderung?"], ["wärmer", "keine Veränderung", "kühler"], [1, 0, -1]
    )
    df = dfm.ersetze_spalten_werte(
        df, ["Luftqualität"], ["1", "2", "3", "4", "5"], range(-2, 3)
    )

    # Übergebe das fertige Dataframe zurück
    return df


def versuchsleitung_normhybr(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=0,
        index_col=0,
        nrows=9,  # Verwende nur die ersten 9 Zeilen
        usecols="A:H",  # Verwende nur diese Spalten (G/H enthält ggf. Bemerkungen)
    )

    # Benenne letzte Spalten um, sodass diese "Kommentar" heißen
    df.rename(
        columns={"Unnamed: 6": "Kommentar", "Unnamed: 7": "Kommentar"}, inplace=True
    )

    # Entferne leere Spalten (es verbleibt nur die Kommentarspalte, in der auch etwas steht)
    df.dropna(how="all", axis=1, inplace=True)

    # Konvertiere Uhrzeit mit dem Messdatum (Erhalt aus dem Änderungsdatum der Datei) zu echtem Zeitstempel
    messdatum = datetime.utcfromtimestamp(dataelement.pfad.stat().st_mtime)
    df.index = df.index.map(lambda x: datetime.combine(messdatum, x))

    # Phasenspalte aufräumen, sodass nur noch Zeilen mit den Phasen-Startzeitpunkten enthalten sind
    df = df[df["Phase"].str.contains("Phase")]

    # Spalte mit Reihenfolge der Deckentemperaturen ergänzen durch Vergleich des letzten mit erstem Sollwert
    if df["Deckentemp. (°C)"][-1] > df["Deckentemp. (°C)"][0]:
        df = df.assign(Rang="aufsteigend")
    else:
        df = df.assign(Rang="absteigend")

    # Übergebe das fertige Dataframe zurück
    return df


def versuchsleitung_halbraum(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=9,
        index_col=1,
        nrows=7,  # Verwende nur die ersten 8 Zeilen
        usecols="B:G",  # Verwende nur diese 5 Spalten
    )
    df.drop(
        index=["hh:mm"], inplace=True
    )  # Löschen der ersten Zeile, da nur Einheiten enthalten

    # Konvertiere Uhrzeit mit dem Messdatum (Erhalt aus dem Änderungsdatum der Datei) zu echtem Zeitstempel
    messdatum = datetime.utcfromtimestamp(dataelement.pfad.stat().st_mtime)
    df.index = df.index.map(lambda x: datetime.combine(messdatum, x))

    # 1 Minuten addiert, da die erste Umfrage einer Phase genau die relevante für die Phase DAVOR ist
    df.index = df.index + pd.DateOffset(minutes=1)

    # Übergebe das fertige Dataframe zurück
    return df


def versuchsleitung_viessmann(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=0,
        index_col=0,
        nrows=6,  # Verwende nur die ersten 8 Zeilen
    )

    # Konvertiere Uhrzeit mit dem Messdatum (Erhalt aus dem Änderungsdatum der Datei) zu echtem Zeitstempel
    messdatum_raw = dataelement.name[:10].replace("_", "-")
    messdatum = pd.to_datetime(messdatum_raw)
    df.index = df.index.map(lambda x: datetime.combine(messdatum, x))

    # Übergebe das fertige Dataframe zurück
    return df


def versuchsleitung_standard(dataelement: Dataelement):
    df = pd.read_excel(
        dataelement.pfad,
        sheet_name=0,
        header=0,
        index_col=0,
        parse_dates=[["Datum", "Uhrzeit"]],
    )  # Verhindert Verwechslung von Tag und Monat beim Einlesen des Datums

    # Übergebe das fertige Dataframe zurück
    return df
