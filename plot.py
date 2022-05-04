#!/usr/bin/env python3

import sys
import csv
import re
import datetime
from enum import Enum
import matplotlib.pyplot as plt

class NoValueEnum(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class Species(NoValueEnum):
    APRU = "Mountain beaver"
    CACA = "American beaver"
    CALA = "Coyote"
    CALUFA = "Dog"
    DIVI = "Virginia opossum"
    FECA = "Domestic cat"
    GLSP = "Flying squirrel"
    HOSA = "Human"
    LOCA = "River otter"
    LYRU = "Bobcat"
    MUFR = "Long-tailed weasel"
    ODHE = "Black-tailed deer"
    NETO = "Townsend’s chipmunk"
    PESP = "Deer mouse"
    PRLO = "Raccoon"
    RASP = "Rat"
    SCCA = "Eastern gray squirrel"
    SYFL = "Eastern cottontail"
    TADO = "Douglas tree squirrel"
    TUMI = "American robin"
    IXNA = "Varied thrush"
    CYST = "Steller’s jay"
    DRPI = "Pileated woodpecker"
    JUHY = "Dark-eyed junco"
    PIMA = "Spotted towhee"
    MEME = "Song sparrow"
    COAU = "Northern flicker"
    COBR = "American crow"


csv_file = sys.argv[1]

sightings = {}
sightings_time_of_day = {}
min_date = datetime.datetime(2100, 1, 1)
max_date = datetime.datetime(1970, 1, 1)

with open(csv_file, encoding="utf-8") as f:
    # sanitize headings
    headings = next(csv.reader(f))
    new_headings = []
    for heading in headings:
        if re.match(r'date', heading, re.IGNORECASE):
            heading = 'date'
        elif re.match(r'time', heading, re.IGNORECASE):
            heading = 'time'
        elif re.match(r'species', heading, re.IGNORECASE):
            heading = 'species'
        elif re.match(r'[\w\.\s]+individuals', heading, re.IGNORECASE):
            heading = 'count'
        new_headings.append(heading)

    # Collect animal sightings
    reader = csv.DictReader(f, new_headings)
    for row in reader:
        ts_str = row['date'] + " " + row['time']
        ts = datetime.datetime.strptime(ts_str, "%m/%d/%Y %H:%M")
        min_date = min(min_date, ts)
        max_date = max(max_date, ts)

        if row['count'] == "":
            count = 1
        else:
            count = int(row['count'])

        if row['species'] == "":
            continue
        species = Species[row['species']]

        for _ in range(count):
            if species not in sightings:
                sightings[species] = []
                sightings_time_of_day[species] = []
            sightings[species].append(ts)

            time = ts.time()
            hour_frac = time.hour + time.minute / 60
            sightings_time_of_day[species].append(hour_frac)


exclude_species = [
    Species.COBR,
    Species.COAU,
    Species.MEME,
    Species.PIMA,
    Species.JUHY,
    Species.DRPI,
    Species.CYST,
    Species.TUMI,
    Species.FECA,
    Species.HOSA,
    Species.TADO,
    Species.SCCA,
]

# 24 Hour Histogram
bins = 24

for species, events in sightings_time_of_day.items():
    if species in exclude_species:
       continue
    plt.hist(events, bins, alpha=0.5, label=species.value)
plt.legend(loc='upper right')
plt.show()


# calendar histogram
delta = max_date - min_date
bins = delta.days // 5
for species, events in sightings.items():
    if species in exclude_species:
        continue
    plt.hist(events, bins, alpha=0.5, label=species.value)
plt.legend(loc='upper right')
plt.show()
