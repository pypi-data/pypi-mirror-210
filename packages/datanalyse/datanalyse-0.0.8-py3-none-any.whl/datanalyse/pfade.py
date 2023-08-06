from pathlib import Path


def liste_der_ordner_im_pfad(pfad: Path):
    ordnerliste = [x for x in pfad.iterdir() if x.is_dir()]
    return ordnerliste


def liste_der_dateien_im_pfad(pfad: Path):
    dateiliste = [x for x in pfad.iterdir() if x.is_file()]
    return dateiliste


def filtern_nach(pfadliste: list, suchwort: str):
    """
    Filtert aus einer Pfadliste diejenigen Pfade, deren Name das Suchwort enthalten.
    :param pfadliste: Liste mit Path-Objekten
    :param suchwort: string, der im Path-Namen enthalten sein soll
    :return: gefilterte pfadliste
    """
    pfadliste_gefiltert = [x for x in pfadliste if suchwort in x.name]
    return pfadliste_gefiltert
