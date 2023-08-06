import pandas as pd
import numpy as np

""" Funktionen zur Manipulation von Dataframes """


def rolling_resample_ergebniszeile(
    df: pd.DataFrame,
    rolling_zeitschritt=None,
    resample_zeitschritt=None,
    nur_ergebniszeile=False,
):
    """
    Bündelung häufig wiederkehrender letzter Schritte in Verbindung mit Dataframes: Gleitende Mittelwertbildung
    (Rolling), Resample und Bildung einer Ergebniszeile mit Mittelwerten für jede Spalte.
    :param df: Dataframe
    :param rolling_zeitschritt: Zeitraum, über den gleitend gemittelt werden soll (z. B. "10min")
    :param resample_zeitschritt: Zeitschrittweite, auf welchen die Verlaufsdaten gebracht werden sollen (z. B. "1min")
    :param nur_ergebniszeile: wenn True, bilde die Mittelwerte aller Spalten und gebe das Ergebnis als eine Zeile aus
    """
    # Gleitende Mittelwertbildung
    if rolling_zeitschritt is not None:
        df = df.rolling(rolling_zeitschritt).mean()

    # Resampling der Daten
    if resample_zeitschritt is not None:
        df = df.resample(resample_zeitschritt).mean()

    # nur eine Zeile mit den Ergebnissen bilden
    if nur_ergebniszeile:
        # Mittelwertbildung der Daten (Ergebnis ist eine Series)
        df = df.mean()

        # Umwandlung der Series zurück in Dataframe und anschließende Transformation (Ergebnis in einer Zeile)
        df = df.to_frame().transpose()
    return df


def ersetze_spalten_werte(df: pd.DataFrame, spalten_liste, alt_liste, neu_liste):
    """
    Funktion, die Werte in (mehreren) Dataframe-Spalten anhand von Vorgaben umwandelt
    Angabe vom Dataframe, die Namen der relevanten Spalten, alte (zu ersetzende) und neue Werte nötig, Bsp.:
    Im "Dataframe" sollen in der Spalte "Geschlecht" die Werte ["männlich", "weiblich"] zu ["m", "w"] oder [0, 1] werden
    :param df: Dataframe
    :param spalten_liste: Namen der Spalten, deren Inhalte umgeschrieben werden sollen
    :param alt_liste: Werte, die überschrieben werden sollen
    :param neu_liste: Werte, die als Ersatz dienen sollen
    :return:
    """
    # Es wird geprüft, ob die Anzahl alter und neuer Werte gleich ist, sonst Fehlermeldung
    if len(alt_liste) == len(neu_liste):
        # In den angegebenen Spalten wird jeder alte Wert einzeln durch den dazugehörigen neuen ersetzt
        for i in range(0, len(alt_liste)):
            df.loc[:, spalten_liste] = df.loc[:, spalten_liste].replace(
                to_replace=alt_liste[i], value=neu_liste[i]
            )
    else:
        print(
            "ErsetzeSpaltenWerte: Anzahl der neuen und alten Werte ist nicht identisch."
        )
    # Noch vorhandene leere Strings ("") mit NaN (Not a Number) ersetzen, damit Spaltentyp ggf. float ("Zahl") wird
    df.loc[:, spalten_liste] = df.loc[:, spalten_liste].replace("", np.nan)
    return df


def filtern_nach(df: pd.DataFrame, suche_in, werte: list, wo="Spalte"):
    if wo == "Spalte":
        df = df.loc[df[suche_in].isin(werte), :]
    elif wo == "Reihe":
        df = df.loc[:, df.loc[:, suche_in].isin(werte)]
    return df


def gruppieren_nach(df: pd.DataFrame, spalten: list, art=None, **kwargs):
    df = df.groupby(by=spalten, **kwargs)
    if art == "Mittelung":
        df = df.mean()
    elif art == "Summe":
        df = df.sum()
    return df


def spaltenwerte_zaehlen(df: pd.DataFrame, spalte):
    df = df[spalte].count().unstack(spalte)
    return df
