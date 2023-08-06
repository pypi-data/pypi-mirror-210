import datanalyse.dataelement.dataelement as dta
from datanalyse.dataelement import formate
from pathlib import Path

versuchsreihe = dta.Dataelement(Path(), name="versuchsreihe")

versuchsreihe.deine_unterlemente()

versuch1 = dta.Dataelement(Path(), name="versuch1", oberelement=versuchsreihe)
versuch2 = dta.Dataelement(Path(), name="versuch2", oberelement=versuchsreihe)


versuchsreihe.deine_unterlemente()
versuch1.deine_unterlemente()
versuch2.deine_unterlemente()
