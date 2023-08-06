import datanalyse.dataelement.dataelement as dta
from datanalyse.dataelement import formate
from pathlib import Path

de = dta.Dataelement(pfad=Path("Ahlborn.xlsx"))
print(de.name)
print(de.elementtyp)
print(de.daten)

de.lese_daten_unformatiert_ein()
print(de.daten)

de.lese_daten_formatiert_ein(format_dict={"Ahlborn": formate.wincontrol_standard})
print(de.daten)

print("Monat:", de.daten.index[0].month)