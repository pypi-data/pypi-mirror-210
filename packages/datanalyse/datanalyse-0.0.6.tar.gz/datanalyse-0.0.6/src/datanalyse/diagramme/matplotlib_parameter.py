import matplotlib.pyplot as plt

# für Komma statt Punkt als Dezimalzeichen
import locale

locale.setlocale(locale.LC_ALL, "deu_deu")

"""Globale Einstellungen für Diagramme 
siehe auch https://matplotlib.org/3.2.1/tutorials/introductory/customizing.html """

# Dateiformat (pdf, png, ...)
plt.rcParams["savefig.format"] = "png"

# Bild automtisch vergrößern, wenn Elemente über den Rand ragen
plt.rcParams["figure.autolayout"] = True

# Schriftart
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Open Sans"

# Schriftgröße
plt.rcParams["font.size"] = 11

# relative Legendenschriftgröße
plt.rcParams["legend.fontsize"] = "smaller"

# Gitterlinien eingeschaltet
plt.rcParams["axes.grid"] = True

# Linienart des Gitters
plt.rcParams["grid.linestyle"] = "-"

# Transparenz des Gitters
plt.rcParams["grid.alpha"] = 0.5

# Linienstärke des Gitters
plt.rcParams["grid.linewidth"] = 1.0

# Linienstärke der Graphen
plt.rcParams["lines.linewidth"] = 1.0

# Komma statt Punkt
plt.rcParams["axes.formatter.use_locale"] = True
