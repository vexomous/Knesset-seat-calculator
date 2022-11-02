import matplotlib.pyplot as plt
import time
import numpy
import json

COLOR_DOC = 'colors.json'
RENAME_FILE = 'namereplace.json'


def absolute_value(pct):
    a = int(numpy.round(pct/100*240, 0))
    return a


def define_colors(party_names):
    with open(COLOR_DOC, 'r', encoding="utf8") as f:
        colors = json.load(f)
    j = 0
    for party in colors:
        if colors[party] == "":
            colors[party] = f"C{j}"
            j += 1
    ordered_colors = list()
    for party in party_names:
        try:
            ordered_colors.append(colors[party])
        except KeyError as e:
            j += 1
            ordered_colors.append(f"C{j}")
    ordered_colors.append("white")
    return ordered_colors


def create_chart(parties):
    fig = plt.figure(figsize=(13, 8), dpi=100)
    ax = fig.add_subplot(111)
    parties = [x for x in parties if x.seats > 0]
    party_names = [x.name for x in parties]
    party_seats = [x.seats for x in parties]
    ordered_colors = define_colors(party_names)
    with open(RENAME_FILE, 'r', encoding="utf8") as f:
        data = json.load(f)
        for i, name in enumerate(party_names):
            try:
                party_names[i] = data[name]
            except KeyError as e:
                continue
    # party_names.append("")
    # party_seats.append(120)
    # ax.pie(party_seats, labels=party_names, colors=ordered_colors,
    #        autopct=absolute_value, pctdistance=0.8, labeldistance=1.1)
    # ax.add_artist(plt.Circle((0, 0), 0.6, color='white'))
    plt.bar(party_names, party_seats, color=ordered_colors)
    rects = ax.patches
    for rect, label in zip(rects, party_seats):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height, label, ha="center", va="bottom"
        )
    plt.savefig(f'seats{time.time()}.png', bbox_inches='tight')
