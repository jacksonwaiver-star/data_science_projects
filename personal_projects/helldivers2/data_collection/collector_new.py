from importlib.resources import path
import json
import logging
from os import path
import os
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
import requests
from pandas.errors import EmptyDataError

from sqlalchemy import create_engine
import os

#from asyncio import graph

DATABASE_URL = os.getenv("DATABASE_URL")
#make sure database url is set in environment variables, if not raise error
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

#print out whether database url exists for debugging purposes
print("DATABASE_URL exists:", DATABASE_URL is not None)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


BASE_URL = "https://api.helldivers2.dev/api"
#HISTORY_FILE = Path(__file__).resolve().parent / "planet_history.csv"

DEFAULT_CLIENT = "helldivers-machine_learning-project_jackson_weaver"
DEFAULT_CONTACT = "jacksonwaiver@gmail.com"


def apply_manual_edges(G: nx.Graph, name_to_index: dict[str, int]) -> int:
    skipped_edges = 0

    def add_edge_by_name(G: nx.Graph, name_a: str, name_b: str, name_to_index: dict[str, int]) -> None:
        nonlocal skipped_edges
        a = name_to_index.get(name_a)
        b = name_to_index.get(name_b)
        if a is None or b is None:
            skipped_edges += 1
            return
        G.add_edge(a, b)

    #already made edge from ESTANU TO CRIMSICA
    #DON'T CONNECT ABOVE PHACT BAY UP OR UPPER RIGHT OR UPPER LEFT WHEN ITS MENTIONED IN COMMENTS, WHEN MENTIONED IN COMMENT THAT IS CALLED THE HUB

    #WE ARE IN TERMINID TERRITORY ON MIDDLE RIGHT

    #now make rest of edges
    add_edge_by_name(G, "ESTANU", "CRIMSICA", name_to_index)

    #CONNECT EVERYTHING TO CRUCIBLE
    add_edge_by_name(G, "CRUCIBLE", "VOLTERRA", name_to_index)
    add_edge_by_name(G, "CRUCIBLE", "KRAKATWO", name_to_index)

    #CONNECT EVERYTHING TO KRAKATWO
    add_edge_by_name(G, "KRAKATWO", "SLIF", name_to_index)
    add_edge_by_name(G, "KRAKATWO", "NUBLARIA I", name_to_index)

    #CONNECT EVERYTHING TO SLIF
    add_edge_by_name(G,"SLIF", "VELD", name_to_index)

    #CONNECT EVERYTHING TO NUBLARIA I
    add_edge_by_name(G, "NUBLARIA I","SULFURA", name_to_index)
    add_edge_by_name(G, "NUBLARIA I","FORT UNION", name_to_index)

    #CONNECT EVERYTHING TO SULFURA
    add_edge_by_name(G,"SULFURA", "AZTERRA", name_to_index)

    #CONNECT EVERYTHING TO AZTERRA
    add_edge_by_name(G, "AZTERRA", "TERREK", name_to_index)
    add_edge_by_name(G, "AZTERRA", "CIRRUS", name_to_index)

    #CONNECT EVERYTHING TO FORT UNION
    add_edge_by_name(G, "FORT UNION", "CIRRUS", name_to_index)

    #CONNECT EVERYTHING TO CIRRUS
    add_edge_by_name(G, "CIRRUS", "TERREK", name_to_index)
    add_edge_by_name(G, "CIRRUS", "HEETH", name_to_index)

    #CONNECT EVERYTHING TO TERREK
    add_edge_by_name(G,"TERREK", "BORE ROCK", name_to_index)

    #CONNECT EVERYTHING TO VOLTERRA
    add_edge_by_name(G, "VOLTERRA", "CARAMOOR", name_to_index)
    add_edge_by_name(G, "VOLTERRA", "SLIF", name_to_index)
    add_edge_by_name(G, "VOLTERRA", "ALTA V", name_to_index)

    #CONNECT EVERYTHING TO HEETH
    add_edge_by_name(G, "HEETH", "FENRIR III", name_to_index)
    add_edge_by_name(G, "HEETH", "ERATA PRIME", name_to_index)

    #CONNECT EVERYTHING TO ERATA PRIME
    add_edge_by_name(G, "ERATA PRIME", "BORE ROCK", name_to_index)
    add_edge_by_name(G, "ERATA PRIME", "NIVEL 43", name_to_index)

    #CONNECT EVERYTHING TO ALTA V
    add_edge_by_name(G, "ALTA V", "INARI", name_to_index)
    add_edge_by_name(G, "ALTA V", "CARAMOOR", name_to_index)
    add_edge_by_name(G, "ALTA V", "SLIF", name_to_index)

    #CONNECT EVERYTHING TO INARI
    add_edge_by_name(G, "INARI", "VELD", name_to_index)
    add_edge_by_name(G, "INARI", "URSICA XI", name_to_index)

    #CONNECT EVERYTHING TO URSICA XI
    add_edge_by_name(G, "URSICA XI", "ACHIRD III", name_to_index)
    add_edge_by_name(G, "URSICA XI", "ACHERNAR SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO ACHERNAR SECUNDUS 
    add_edge_by_name(G, "ACHERNAR SECUNDUS", "GAR HAREN", name_to_index)
    add_edge_by_name(G,"ACHERNAR SECUNDUS", "DARIUS II", name_to_index)

    #CONNECT EVERYTHING TO GAR HAREN
    add_edge_by_name(G, "GAR HAREN", "GRAND ERRANT", name_to_index)
    add_edge_by_name(G, "GAR HAREN", "GATRIA", name_to_index)
    add_edge_by_name(G, "GAR HAREN", "PHACT BAY", name_to_index)

    #CONNECT EVERYTHING TO GRAND ERRANT
    add_edge_by_name(G, "GRAND ERRANT", "POLARIS PRIME", name_to_index)
    add_edge_by_name(G, "GRAND ERRANT", "PHERKAD SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO POLARIS PRIME
    add_edge_by_name(G,"POLARIS PRIME", "PHERKAD SECUNDUS", name_to_index)
    add_edge_by_name(G,"POLARIS PRIME", "POLLUX 31", name_to_index)

    #CONNECT EVERYTHING TO POLLUX 31
    add_edge_by_name(G, "POLLUX 31", "PRASA", name_to_index)

    #CONNECT EVERYTHING TO GATRIA 
    add_edge_by_name(G, "GATRIA", "TRANDOR", name_to_index)
    add_edge_by_name(G, "GATRIA", "PHACT BAY", name_to_index)
    add_edge_by_name(G, "GATRIA", "PHERKAD SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO TRANDOR
    add_edge_by_name(G, "TRANDOR", "PEACOCK", name_to_index)

    #CONNECT EVERYTHING TO PEACOCK
    add_edge_by_name(G, "PEACOCK", "PARTION", name_to_index)

    #CONNECT EVERYTHING TO PHACT BAY
    add_edge_by_name(G, "PHACT BAY", "GATRIA", name_to_index)
    add_edge_by_name(G, "PHACT BAY", "GAR HAREN", name_to_index)
    add_edge_by_name(G, "PHACT BAY", "DARIUS II", name_to_index)
    add_edge_by_name(G, "PHACT BAY", "PANDION-XXIV", name_to_index)
    add_edge_by_name(G, "PHACT BAY", "PARTION", name_to_index)

    #CONNECT EVERYTHING TO ACHIRD III
    add_edge_by_name(G, "ACHIRD III","URSICA XI", name_to_index)
    add_edge_by_name(G, "ACHIRD III","DARIUS II", name_to_index)
    #JUST ADDED BELOW
    add_edge_by_name(G, "ACHIRD III","TURING", name_to_index)

    #CONNECT EVERYTHING TO TURING
    add_edge_by_name(G, "TURING", "VELD", name_to_index)
    add_edge_by_name(G, "TURING", "ACAMAR IV", name_to_index)


    #DO ABOVE PANDION AND INCLUDE PANDION

    #CONNECT EVERYTHING TO PANDION-XXIV
    add_edge_by_name(G, "PANDION-XXIV", "PHACT BAY", name_to_index)
    add_edge_by_name(G, "PANDION-XXIV", "GACRUX", name_to_index)
    add_edge_by_name(G, "PANDION-XXIV", "ACAMAR IV", name_to_index)

    #CONNECT EVERYTHING TO PARTION
    add_edge_by_name(G, "PARTION", "PHACT BAY", name_to_index)
    add_edge_by_name(G, "PARTION", "PEACOCK", name_to_index)
    add_edge_by_name(G, "PARTION", "GACRUX", name_to_index)
    add_edge_by_name(G, "PARTION", "OVERGOE PRIME", name_to_index)

    #CONNECT EVERYTHING TO ACAMAR IV
    add_edge_by_name(G, "ACAMAR IV", "DARIUS II", name_to_index)
    add_edge_by_name(G, "ACAMAR IV", "PANDION-XXIV", name_to_index)
    add_edge_by_name(G, "ACAMAR IV", "TURING", name_to_index)
    add_edge_by_name(G, "ACAMAR IV", "CRIMSICA", name_to_index)
    add_edge_by_name(G, "ACAMAR IV", "GACRUX", name_to_index)

    #CONNECT EVERYTHING TO OVERGOE PRIME
    add_edge_by_name(G, "OVERGOE PRIME", "AZUR SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO CRIMSICA
    add_edge_by_name(G, "CRIMSICA", "FORI PRIME", name_to_index)
    add_edge_by_name(G, "CRIMSICA", "ESTANU", name_to_index)

    #CONNECT EVERYTHING TO ESTANU
    add_edge_by_name(G, "ESTANU", "FORI PRIME", name_to_index)
    add_edge_by_name(G, "ESTANU", "HELLMIRE", name_to_index)

    #CONNECT EVERYTHING TO FORI PRIME
    add_edge_by_name(G, "FORI PRIME", "GACRUX", name_to_index)
    add_edge_by_name(G, "FORI PRIME", "OSHAUNE", name_to_index)

    #CONNECT EVERYTHING TO NAVI VII
    add_edge_by_name(G, "NAVI VII", "NABATEA SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO OSHAUNE
    add_edge_by_name(G, "OSHAUNE", "HELLMIRE", name_to_index)
    add_edge_by_name(G, "OSHAUNE", "OMICRON", name_to_index)

    #CONNECT EVERYTHING TO HELLMIRE
    add_edge_by_name(G, "HELLMIRE", "ERATA PRIME", name_to_index)
    add_edge_by_name(G, "HELLMIRE", "FENRIR III", name_to_index)
    add_edge_by_name(G, "HELLMIRE", "NIVEL 43", name_to_index)
    add_edge_by_name(G, "HELLMIRE", "OSHAUNE", name_to_index)

    #CONNECT EVERYTHING TO NIVEL 43
    add_edge_by_name(G, "NIVEL 43", "HELLMIRE", name_to_index)
    add_edge_by_name(G, "NIVEL 43", "ERATA PRIME", name_to_index)
    add_edge_by_name(G, "NIVEL 43", "ZAGON PRIME", name_to_index)
    add_edge_by_name(G, "NIVEL 43", "ERSON SANDS", name_to_index)
    add_edge_by_name(G, "NIVEL 43", "ESKER", name_to_index)

    #CONNECT EVERYTHING TO ZAGON PRIME
    add_edge_by_name(G, "ZAGON PRIME", "OMICRON", name_to_index)


    #CONNECT EVERYTHING TO OMICRON
    add_edge_by_name(G, "OMICRON", "OSHAUNE", name_to_index)

    #CONNECT EVERYTHING TO NABATEA SECUNDUS
    add_edge_by_name(G, "NABATEA SECUNDUS", "GEMSTONE BLUFFS", name_to_index)

    #CONNECT EVERYTHING TO GEMSTONE BLUFFS
    add_edge_by_name(G, "GEMSTONE BLUFFS", "EPSILON PHOENCIS VI", name_to_index)
    add_edge_by_name(G, "GEMSTONE BLUFFS", "DIASPORA X", name_to_index)

    #CONNECT EVERYTHING TO ENULIAE
    add_edge_by_name(G, "ENULIALE", "DIASPORA X", name_to_index)
    add_edge_by_name(G, "ENULIALE", "EPSILON PHOENCIS VI", name_to_index)

    #CONNECT EVERYTHING TO ERSON SANDS
    add_edge_by_name(G, "ERSON SANDS", "ESKER", name_to_index)
    add_edge_by_name(G, "ERSON SANDS", "SOCORRO III", name_to_index)

    #CONNECT EVERYTHING TO ESKER
    add_edge_by_name(G,"ESKER","BORE ROCK", name_to_index)



    #START AT SHALLUS FOR AUTOMATONS AT TOP MIDDLE 


    #CONNECT EVERYTHING TO SHALLUS
    add_edge_by_name(G, "SHALLUS", "SHELT", name_to_index)
    add_edge_by_name(G, "SHALLUS", "MASTIA", name_to_index)

    #CONNECT EVERYTHING TO SHELT
    add_edge_by_name(G, "SHELT", "MASTIA", name_to_index)
    add_edge_by_name(G, "SHELT", "IMBER", name_to_index)

    #CONNECT EVERYTHING TO IMBER
    add_edge_by_name(G, "IMBER", "GAELLIVARE", name_to_index)
    add_edge_by_name(G, "IMBER", "CLAORELL", name_to_index)

    #CONNECT EVERYTHING TO CLAORELL
    add_edge_by_name(G, "CLAORELL", "VOG-SOJOTH", name_to_index)
    add_edge_by_name(G, "CLAORELL", "CLASA", name_to_index)

    #CONNECT EVERYTHING TO CLASA
    add_edge_by_name(G, "CLASA", "DEMIURG", name_to_index)
    add_edge_by_name(G, "CLASA", "ZEFIA", name_to_index)
    add_edge_by_name(G, "CLASA", "YED PRIOR", name_to_index)

    #CONNECT EVERYTHING TO ZEFIA
    add_edge_by_name(G, "ZEFIA", "MINTORIA", name_to_index)
    add_edge_by_name(G, "ZEFIA", "YED PRIOR", name_to_index)

    #CONNECT EVERYTHING TO YED PRIOR
    add_edge_by_name(G, "YED PRIOR", "BLISTICA", name_to_index)

    #CONNECT EVERYTHING TO BLISTICA
    add_edge_by_name(G,"BLISTICA", "MINTORIA", name_to_index)
    add_edge_by_name(G,"BLISTICA", "ZZANIAH PRIME", name_to_index)

    #CONNECT EVERYTHING TO ZZANIAH PRIME
    add_edge_by_name(G, "ZZANIAH PRIME", "ZOSMA", name_to_index)


    #CONNECT EVERYTHING TO MASTIA
    add_edge_by_name(G, "MASTIA", "GAELLIVARE", name_to_index)
    add_edge_by_name(G, "MASTIA", "FENMIRE", name_to_index)
    add_edge_by_name(G, "MASTIA", "TARSH", name_to_index)

    #CONNECT EVERYTHING TO GAELLIVARE
    add_edge_by_name(G, "GAELLIVARE", "LESATH", name_to_index)

    #CONNECT EVERYTHING TO LESATH
    add_edge_by_name(G, "LESATH", "VERNEN WELLS", name_to_index)
    add_edge_by_name(G, "LESATH", "MENKENT", name_to_index)
    add_edge_by_name(G, "LESATH", "CHORT BAY", name_to_index)
    add_edge_by_name(G, "LESATH", "PENTA", name_to_index)
    add_edge_by_name(G, "LESATH", "VOG-SOJOTH", name_to_index)

    #CONNECT EVERYTHING TO PENTA

    #COMMENTED OUT BECAUSE DARK FLUID BEAM VIA DSS DESTROYED PENTA

    # add_edge_by_name(G, "PENTA", "CHORT BAY", name_to_index)
    # add_edge_by_name(G, "PENTA", "MERAK", name_to_index)

    #CONNECT EVERYTHING TO CHORT BAY
    add_edge_by_name(G,"CHORT BAY", "MENKENT",  name_to_index)
    add_edge_by_name(G,"CHORT BAY", "CHOOHE",  name_to_index)

    #CONNECT EVERYTHING TO CHOOHE
    add_edge_by_name(G,"CHOOHE", "MENKENT",  name_to_index)
    add_edge_by_name(G,"CHOOHE", "AURORA BAY",  name_to_index)

    #CONNECT EVERYTHING TO MENKENT
    add_edge_by_name(G,"MENKENT", "VERNEN WELLS",  name_to_index)

    #CONNECT EVERYTHING TO VERNEN WELLS
    add_edge_by_name(G,"VERNEN WELLS", "TARSH",  name_to_index)
    add_edge_by_name(G,"VERNEN WELLS", "AESIR PASS",  name_to_index)

    #CONNECT EVERYTHING TO TARSH
    add_edge_by_name(G,"TARSH", "MASTIA",  name_to_index)
    add_edge_by_name(G,"TARSH", "CURIA",  name_to_index)

    #CONNECT EVERYTHING TO CURIA
    add_edge_by_name(G,"CURIA", "FENMIRE",  name_to_index)
    add_edge_by_name(G,"CURIA", "BOREA",  name_to_index)
    add_edge_by_name(G,"CURIA", "AESIR PASS",  name_to_index)

    #CONNECT EVERYTHING TO FENMIRE
    add_edge_by_name(G,"FENMIRE", "BARABOS",  name_to_index)

    #CONNECT EVERYTHING TO BARABOS
    add_edge_by_name(G,"BARABOS", "EMERIA",  name_to_index)

    #CONNECT EVERYTHING TO EMERIA
    add_edge_by_name(G,"EMERIA", "BOREA",  name_to_index)

    #CONNECT EVERYTHING TO AESIR PASS
    add_edge_by_name(G,"AESIR PASS", "MARFARK",  name_to_index)

    #CONNECT EVERYTHING TO MARFARK
    add_edge_by_name(G,"MARFARK", "BEKVAM III",  name_to_index)
    add_edge_by_name(G,"MARFARK", "MARTALE",  name_to_index)
    add_edge_by_name(G,"MARFARK", "MATAR BAY",  name_to_index)

    #CONNECT EVERYTHING TO MATAR BAY
    add_edge_by_name(G,"MATAR BAY", "MARTALE",  name_to_index)
    add_edge_by_name(G,"MATAR BAY", "MEISSA",  name_to_index)

    #CONNECT EVERYTHING TO MEISSA
    add_edge_by_name(G,"MEISSA", "WASAT",  name_to_index)
    add_edge_by_name(G,"MEISSA", "X-45",  name_to_index)

    #CONNECT EVERYTHING TO X-45
    add_edge_by_name(G,"X-45", "WASAT",  name_to_index)
    add_edge_by_name(G,"X-45", "VEGA BAY",  name_to_index)

    #CONNECT EVERYTHING TO VEGA BAY
    add_edge_by_name(G,"VEGA BAY", "WASAT",  name_to_index)
    add_edge_by_name(G,"VEGA BAY", "Mox",  name_to_index)
    add_edge_by_name(G,"VEGA BAY", "WEZEN",  name_to_index)

    #CONNECT EVERYTHING TO WEZEN
    add_edge_by_name(G,"WEZEN", "VARYLIA 5",  name_to_index)

    #CONNECT EVERYTHING TO MOX
    add_edge_by_name(G,"Mox", "VARYLIA 5",  name_to_index)

    #CONNECT EVERYTHING TO VARYLIA 5
    add_edge_by_name(G,"VARYLIA 5", "K",  name_to_index)
    add_edge_by_name(G,"VARYLIA 5", "CHOEPESSA IV",  name_to_index)
    add_edge_by_name(G,"VARYLIA 5", "USTOTU",  name_to_index)

    #CONNECT EVERYTHING TO CHOEPESSA IV
    add_edge_by_name(G,"CHOEPESSA IV", "K",  name_to_index)
    add_edge_by_name(G,"CHOEPESSA IV", "USTOTU",  name_to_index)
    add_edge_by_name(G,"CHOEPESSA IV", "FURY",  name_to_index)
    add_edge_by_name(G,"CHOEPESSA IV", "CHARON PRIME",  name_to_index)
    add_edge_by_name(G,"CHOEPESSA IV", "CHARBAL-VII",  name_to_index)

    #CONNECT EVERYTHING TO CHARON PRIME
    add_edge_by_name(G,"CHARON PRIME", "MARTALE",  name_to_index)
    add_edge_by_name(G,"CHARON PRIME", "CHARBAL-VII",  name_to_index)
    add_edge_by_name(G,"CHARON PRIME", "BEKVAM III",  name_to_index)

    #CONNECT EVERYTHING TO CHARBAL-VII
    add_edge_by_name(G,"CHARBAL-VII", "JULHEIM",  name_to_index)
    add_edge_by_name(G,"CHARBAL-VII", "MORT",  name_to_index)

    #CONNECT EVERYTHING TO USTOTU
    add_edge_by_name(G,"USTOTU", "TROOST",  name_to_index)
    add_edge_by_name(G,"USTOTU", "VANDALON IV",  name_to_index)
    add_edge_by_name(G,"USTOTU", "FURY",  name_to_index)

    #CONNECT EVERYTHING TO VANDALON IV
    add_edge_by_name(G,"VANDALON IV", "TROOST",  name_to_index)
    add_edge_by_name(G,"VANDALON IV", "INGMAR",  name_to_index)
    add_edge_by_name(G,"VANDALON IV", "MAIA",  name_to_index)
    add_edge_by_name(G,"VANDALON IV", "MANTES",  name_to_index)

    #CONNECT EVERYTHING TO VINDEMITARIX PRIME
    add_edge_by_name(G,"VINDEMITARIX PRIME", "MEKBUDA",  name_to_index)

    #CONNECT EVERYTHING TO MEKBUD
    add_edge_by_name(G,"MEKBUDA", "CYBERSTAN",  name_to_index)

    #CONNECT EVERYTHING TO CYBERSTAN
    add_edge_by_name(G,"CYBERSTAN", "MERGA IV",  name_to_index)



    #CONNECT EVERYTHING BELOW AUTOMATONS THAT ARE HELD BY HUMANS


    #CONNECT EVERYTHING TO BOREA
    add_edge_by_name(G,"BOREA", "GUNVALD",  name_to_index)
    add_edge_by_name(G,"BOREA", "DUMA TYR",  name_to_index)

    #CONNECT EVERYTHING TO DUMA TYR
    add_edge_by_name(G,"DUMA TYR", "BEKVAM III",  name_to_index)
    add_edge_by_name(G,"DUMA TYR", "OSLO STATION",  name_to_index)
    add_edge_by_name(G,"DUMA TYR", "JULHEIM",  name_to_index)

    #CONNECT EVERYTHING TO BEKVAM III
    add_edge_by_name(G,"BEKVAM III", "JULHEIM",  name_to_index)

    #CONNECT EVERYTHING TO JULHEIM
    add_edge_by_name(G,"JULHEIM", "DOLPH",  name_to_index)

    #CONNECT EVERYTHING TO DOLPH
    add_edge_by_name(G,"DOLPH", "OSLO STATION",  name_to_index)
    add_edge_by_name(G,"DOLPH", "CAPH",  name_to_index)

    #CONNECT EVERYTHING TO OSLO STATION
    add_edge_by_name(G,"OSLO STATION", "GUNVALD",  name_to_index)

    #CONNECT EVERYTHING TO PÖPLI IX
    add_edge_by_name(G,"PÖPLI IX", "MORT",  name_to_index)
    add_edge_by_name(G,"PÖPLI IX", "LASTOFE",  name_to_index)
    add_edge_by_name(G,"PÖPLI IX", "INGMAR",  name_to_index)
    add_edge_by_name(G,"PÖPLI IX", "MANTES",  name_to_index)

    #CONNECT EVERYTHING TO MORT
    add_edge_by_name(G,"MORT", "FURY",  name_to_index)
    add_edge_by_name(G,"MORT", "INGMAR",  name_to_index)

    #CONNECT EVERYTHING TO CAPH
    add_edge_by_name(G,"CAPH", "LASTOFE",  name_to_index)
    add_edge_by_name(G,"CAPH", "CASTOR",  name_to_index)

    #CONNECT EVERYTHING TO CASTOR
    add_edge_by_name(G,"CASTOR", "TIEN KWAN",  name_to_index)

    #CONNECT EVERYTHING TO TIEN KWAN
    add_edge_by_name(G,"TIEN KWAN", "LASTOFE",  name_to_index)
    add_edge_by_name(G,"TIEN KWAN", "DRAUPNIR",  name_to_index)

    #CONNECT EVERYTHING TO DRAUPNIR
    add_edge_by_name(G,"DRAUPNIR", "MANTES",  name_to_index)
    add_edge_by_name(G,"DRAUPNIR", "UBANEA",  name_to_index)
    add_edge_by_name(G,"DRAUPNIR", "MALEVELON CREEK",  name_to_index)

    #CONNECT EVERYTHING TO UBANEA
    add_edge_by_name(G,"UBANEA", "TIBIT",  name_to_index)
    add_edge_by_name(G,"UBANEA", "DURGEN",  name_to_index)

    #CONNECT EVERYTHING TO DURGEN
    add_edge_by_name(G,"DURGEN", "MALEVELON CREEK",  name_to_index)

    #CONNECT EVERYTHING TO MALEVELON CREEK
    add_edge_by_name(G,"MALEVELON CREEK", "MAIA",  name_to_index)
    add_edge_by_name(G,"MALEVELON CREEK", "MANTES",  name_to_index)


    #DO ILLUMINATE SECTORS


    #CONNECT EVERYTHING TO OBARI
    add_edge_by_name(G,"OBARI", "BALDRICK PRIME",  name_to_index)
    add_edge_by_name(G,"OBARI", "VIRIDIA PRIME",  name_to_index)

    #CONNECT EVERYTHING TO BALDRICK PRIME
    add_edge_by_name(G,"BALDRICK PRIME", "ILDUNA PRIME",  name_to_index)
    add_edge_by_name(G,"BALDRICK PRIME", "LIBERTY RIDGE",  name_to_index)

    #CONNECT EVERYTHING TO VIRIDIA PRIME
    add_edge_by_name(G,"VIRIDIA PRIME", "EMORATH",  name_to_index)
    add_edge_by_name(G,"VIRIDIA PRIME", "DILUVIA",  name_to_index)

    #CONNECT EVERYTHING TO EMORATH
    add_edge_by_name(G,"EMORATH", "ILDUNA PRIME",  name_to_index)
    add_edge_by_name(G,"EMORATH", "LIBERTY RIDGE",  name_to_index)
    add_edge_by_name(G,"EMORATH", "EAST IRIDIUM TRADING BAY",  name_to_index)

    #CONNECT EVERYTHING TO LIBERTY RIDGE
    add_edge_by_name(G,"LIBERTY RIDGE", "CANOPUS",  name_to_index)

    #CONNECT EVERYTHING TO CANOPUS
    add_edge_by_name(G,"CANOPUS", "OSUPSAM",  name_to_index)
    add_edge_by_name(G,"CANOPUS", "BUNDA SECUNDUS",  name_to_index)

    #CONNECT EVERYTHING TO BUNDA SECUNDUS
    add_edge_by_name(G,"BUNDA SECUNDUS", "KRAZ",  name_to_index)

    #CONNECT EVERYTHING TO KRAZ
    add_edge_by_name(G,"KRAZ", "LENG SECUNDUS",  name_to_index)

    #CONNECT EVERYTHING TO LENG SCUNDUS
    add_edge_by_name(G,"LENG SECUNDUS", "KLAKA 5",  name_to_index)
    add_edge_by_name(G,"LENG SECUNDUS", "STOUT",  name_to_index)

    #CONNECT EVERYTHING TO STOUT
    add_edge_by_name(G,"STOUT", "STOR THA PRIME",  name_to_index)

    #CONNECT EVERYTHING TO STOR THA PRIME
    add_edge_by_name(G,"STOR THA PRIME", "TERMADON",  name_to_index)
    add_edge_by_name(G,"STOR THA PRIME", "SPHERION",  name_to_index)

    #CONNECT EVERYTHING TO SPHERION
    add_edge_by_name(G,"SPHERION", "SIRIUS",  name_to_index)
    add_edge_by_name(G,"SPHERION", "KNETH PORT",  name_to_index)

    #CONNECT EVERYTHING TO KNETH PORT
    add_edge_by_name(G,"KNETH PORT", "KLAKA 5",  name_to_index)
    add_edge_by_name(G,"KNETH PORT", "BOTEIN",  name_to_index)
    add_edge_by_name(G,"KNETH PORT", "BRINK-2",  name_to_index)

    #CONNECT EVERYTHING TO KLAKA 5
    add_edge_by_name(G, "KLAKA 5", "OSUPSAM",  name_to_index)

    #CONNECT EVERYTHING TO BRINK-2
    add_edge_by_name(G,"BRINK-2", "OSUPSAM",  name_to_index)
    add_edge_by_name(G,"BRINK-2", "EAST IRIDIUM TRADING BAY",  name_to_index)

    #CONNECT EVERYTHING TO EAST IRIDIUM TRADING BAY
    add_edge_by_name(G,"EAST IRIDIUM TRADING BAY", "ELYSIAN MEADOWS",  name_to_index)


    #CONNECT EVERYTHING TO DILUVIA 
    add_edge_by_name(G,"DILUVIA", "SOLGHAST",  name_to_index)
    add_edge_by_name(G,"DILUVIA", "IRULTA",  name_to_index)

    #CONNECT EVERYTHING TO SOLGHAST
    add_edge_by_name(G,"SOLGHAST", "REAF",  name_to_index)
    add_edge_by_name(G,"SOLGHAST", "EFFLUVIA",  name_to_index)

    #CONNECT EVERYTHING TO EFFLUVIA
    add_edge_by_name(G,"EFFLUVIA", "PARSH",  name_to_index)
    add_edge_by_name(G,"EFFLUVIA", "SEYSHEL BEACH",  name_to_index)

    #CONNECT EVERYTHING TO SEYSHEL BEACH
    add_edge_by_name(G,"SEYSHEL BEACH", "FORT SANCTUARY",  name_to_index)
    add_edge_by_name(G,"SEYSHEL BEACH", "KERTH SECUNDUS",  name_to_index)
    add_edge_by_name(G,"SEYSHEL BEACH", "MYRIUM",  name_to_index)

    #CONNECT EVERYTHING TO FORT SANCTUARY
    add_edge_by_name(G,"FORT SANCTUARY", "EUKORIA",  name_to_index)

    #CONNECT EVERTYHING TO IRULTA
    add_edge_by_name(G,"IRULTA", "ELYSIAN MEADOWS",  name_to_index)
    add_edge_by_name(G,"IRULTA", "REAF",  name_to_index)

    #CONNECT EVERYTHING TO ELYSIAN MEADOWS
    add_edge_by_name(G,"ELYSIAN MEADOWS", "CALYPSO",  name_to_index)

    #CONNECT EVERYTHING TO CALYPSO
    add_edge_by_name(G,"CALYPSO", "ALDERIDGE COVE",  name_to_index)
    add_edge_by_name(G,"CALYPSO", "OUTPOST 32",  name_to_index)
    add_edge_by_name(G,"CALYPSO", "ANDAR",  name_to_index)

    #CONNECT EVERYTHING TO ALDERIDGE COVE
    add_edge_by_name(G,"ALDERIDGE COVE", "BELLATRIX",  name_to_index)
    add_edge_by_name(G,"ALDERIDGE COVE", "BOTEIN",  name_to_index)

    #CONNECT EVERYTHING TO BELLATRIX
    add_edge_by_name(G,"BELLATRIX", "KHANDARK",  name_to_index)

    #CONNECT EVERYTHING TO BOTEIN
    add_edge_by_name(G,"BOTEIN", "KHANDARK",  name_to_index)

    #CONNECT EVERYTHING TO KHANDARK
    add_edge_by_name(G,"KHANDARK", "SKAT BAY",  name_to_index)
    add_edge_by_name(G,"KHANDARK", "ASPEROTH PRIME",  name_to_index)

    #CONNECT EVERYTHINGN TO SKAT BAY
    add_edge_by_name(G,"SKAT BAY", "SIRIUS",  name_to_index)
    add_edge_by_name(G,"SKAT BAY", "SIEMNOT",  name_to_index)

    #CONNECT EVERYTHING TO REAF
    add_edge_by_name(G,"REAF", "IRULTA",  name_to_index)
    add_edge_by_name(G,"REAF", "OUTPOST 32",  name_to_index)
    add_edge_by_name(G,"REAF", "PARSH",  name_to_index)

    #CONNECT EVERYTHING TO ANDAR
    add_edge_by_name(G,"ANDAR", "ASPEROTH PRIME",  name_to_index)
    add_edge_by_name(G,"ANDAR", "ALATHFAR XI",  name_to_index)

    #CONNECT EVERYTHING TO ASPEROTH PRIME
    add_edge_by_name(G,"ASPEROTH PRIME", "KEID",  name_to_index)

    #CONNECT EVERYTHING TO KEID
    add_edge_by_name(G,"KEID", "KARLIA",  name_to_index)
    add_edge_by_name(G,"KEID", "SHETE",  name_to_index)

    #CONNECT EVERYTHING TO SHETE
    add_edge_by_name(G,"SHETE", "SETIA",  name_to_index)

    #CONNECT EVERYTHING TO PARSH
    add_edge_by_name(G,"PARSH", "REAF",  name_to_index)
    add_edge_by_name(G,"PARSH", "KERTH SECUNDUS",  name_to_index)
    add_edge_by_name(G,"PARSH", "GENESIS PRIME",  name_to_index)

    #CONNECT EVERYTHING TO GENESIS PRIME
    add_edge_by_name(G,"GENESIS PRIME", "OASIS",  name_to_index)
    add_edge_by_name(G,"GENESIS PRIME", "ALARAPH",  name_to_index)

    #CONNECT EVERYTHING TO ALARAPH
    add_edge_by_name(G,"ALARAPH", "ALATHFAR XI",  name_to_index)
    add_edge_by_name(G,"ALARAPH", "HYDROBIUS",  name_to_index)

    #CONNECT EVERYTHING TO ALATHFAR XI
    add_edge_by_name(G,"ALATHFAR XI", "KARLIA",   name_to_index)
    add_edge_by_name(G,"ALATHFAR XI", "ALARAPH",   name_to_index)

    #CONNECT EVERYTHING TO KARLIA
    add_edge_by_name(G,"KARLIA","KEID",   name_to_index)
    add_edge_by_name(G,"KARLIA","HYDROBIUS",   name_to_index)

    #CONNECT EVERYTHING TO HYDROBIUS
    add_edge_by_name(G,"HYDROBIUS", "HEZE BAY",   name_to_index)
    add_edge_by_name(G,"HYDROBIUS", "SENGE 23",   name_to_index)
    add_edge_by_name(G,"HYDROBIUS", "SETIA",   name_to_index)

    #CONNECT EVERYTHING TO KERTH SECUNDUS
    add_edge_by_name(G,"KERTH SECUNDUS", "GRAFMERE",   name_to_index)
    add_edge_by_name(G,"KERTH SECUNDUS", "MYRIUM",   name_to_index)

    #CONNECT EVERYTHING TO GRAFMERE
    add_edge_by_name(G,"GRAFMERE", "OASIS",   name_to_index)
    add_edge_by_name(G,"GRAFMERE", "IRO",   name_to_index)

    #CONNECT EVERYTHING TO OASIS
    add_edge_by_name(G,"OASIS", "ALAMAK VII",  name_to_index)
    add_edge_by_name(G,"OASIS", "ALARAPH",  name_to_index)

    #CONNECT EVERYTHING TO ALAMAK VII
    add_edge_by_name(G,"ALAMAK VII", "NEW STOCKHOLM",  name_to_index)
    add_edge_by_name(G,"ALAMAK VII", "ALAIRT III",  name_to_index)

    #CONNECT EVERYTHING TO ALAIRT III
    add_edge_by_name(G,"ALAIRT III", "NEW STOCKHOLM", name_to_index)
    add_edge_by_name(G,"ALAIRT III", "HEZE BAY", name_to_index)
    add_edge_by_name(G,"ALAIRT III", "HERTHON SECUNDUS", name_to_index)

    #CONNECT EVERYTHING TO HEZE BAY
    add_edge_by_name(G,"HEZE BAY", "HYDROBIUS", name_to_index)
    add_edge_by_name(G,"HEZE BAY", "RIRGA BAY", name_to_index)

    #CONNECT EVERYTHING TO RIRGA BAY
    add_edge_by_name(G,"RIRGA BAY", "HORT", name_to_index)
    add_edge_by_name(G,"RIRGA BAY", "SEASSE", name_to_index)

    #CONNECT EVERYTHING TO SEASSE
    add_edge_by_name(G,"SEASSE", "SENGE 23", name_to_index)
    add_edge_by_name(G,"SEASSE", "ROGUE 5", name_to_index)

    #CONNECT EVERYTHING TO SENGE 23
    add_edge_by_name(G,"SENGE 23", "SETIA", name_to_index)

    #CONNECT EVERYTHING TO ROGUE 5
    add_edge_by_name(G,"ROGUE 5", "RD-4", name_to_index)

    #CONNECT EVERYTHING TO RD-4
    add_edge_by_name(G,"RD-4", "HESOE PRIME", name_to_index)
    add_edge_by_name(G,"RD-4", "HORT", name_to_index)

    #CONNECT EVERYTHING TO HORT 
    add_edge_by_name(G,"HORT", "HERTHON SECUNDUS", name_to_index)
    add_edge_by_name(G,"HORT", "HESOE PRIME", name_to_index)

    #CONNECT EVERYTHING TO HERTHON SECUNDUS
    add_edge_by_name(G,"HERTHON SECUNDUS", "AIN-5", name_to_index)
    add_edge_by_name(G,"HERTHON SECUNDUS", "ZEA RUGOSIA", name_to_index)

    #CONNECT EVERYTHING TO ZEA RUGOSIA 
    add_edge_by_name(G,"ZEA RUGOSIA", "AFOYAY BAY", name_to_index)
    add_edge_by_name(G,"ZEA RUGOSIA", "HALDUS", name_to_index)

    #CONNECT EVERYTHING TO HALDUS
    add_edge_by_name(G,"HALDUS", "ADHARA", name_to_index)

    #CONNECT EVERYTHING TO ADHARA
    add_edge_by_name(G,"ADHARA", "AFOYAY BAY", name_to_index)
    add_edge_by_name(G,"ADHARA", "MOG", name_to_index)

    #CONNECT EVERYTHING TO AFOYAY BAY
    add_edge_by_name(G,"AFOYAY BAY", "AIN-5", name_to_index)
    add_edge_by_name(G,"AFOYAY BAY", "VALMOX", name_to_index)

    #CONNECT EVERYTHING TO VALMOX
    add_edge_by_name(G,"VALMOX", "IRO", name_to_index)
    add_edge_by_name(G,"VALMOX", "MOG", name_to_index)
    add_edge_by_name(G,"VALMOX", "MYRIUM", name_to_index)

    #CONNECT EVERYTHING TO MOG
    add_edge_by_name(G,"MOG", "REGNUS", name_to_index)

    #CONNECT EVERYTHING TO REGNUS
    add_edge_by_name(G,"REGNUS", "EUKORIA", name_to_index)

    #CONNECT EVERYTHING TO EUKORIA
    add_edge_by_name(G,"EUKORIA", "MYRIUM", name_to_index)

    #CONNECT EVERYTHING TO AIN-5
    add_edge_by_name(G,"AIN-5", "AFOYAY BAY", name_to_index)
    add_edge_by_name(G,"AIN-5", "HERTHON SECUNDUS", name_to_index)
    #CONNECT EVERYTHING TO MYRIUM
    #add_edge_by_name(G,"MYRIUM", "", name_to_index)

    #CONNECT EVERYTHING TO NEW STOCKHOLM
    add_edge_by_name(G,"NEW STOCKHOLM", "IRO", name_to_index)

    return skipped_edges



# def load_history() -> pd.DataFrame:
#     if not HISTORY_FILE.exists():
#         # create file with schema
#         df = pd.DataFrame(columns=["timestamp"])
#         df.to_csv(HISTORY_FILE, index=False)
#         return df

#     if HISTORY_FILE.stat().st_size == 0:
#         return pd.DataFrame(columns=["timestamp"])

#     try:
#         df = pd.read_csv(HISTORY_FILE)

#         # ensure timestamp column exists
#         if "timestamp" not in df.columns:
#             df["timestamp"] = pd.NaT
#         else:
#             df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

#         return df

#     except EmptyDataError:
#         return pd.DataFrame(columns=["timestamp"])

#     except Exception as e:
#         print(f"[load_history ERROR] {e}")
#         return pd.DataFrame(columns=["timestamp"])


# def save_history(df: pd.DataFrame) -> None:
#     df.to_csv(HISTORY_FILE, index=False)


def get_headers() -> dict[str, str]:
    return {
        "X-Super-Client": os.getenv("HD2_CLIENT_NAME", DEFAULT_CLIENT),
        "X-Super-Contact": os.getenv("HD2_CONTACT_EMAIL", DEFAULT_CONTACT),
    }


def fetch_json(
    url: str,
    headers: dict[str, str],
    timeout: int = 30,
    max_retries: int = 3,
    backoff_seconds: float = 30.0,
) -> Any:
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
            url,
            headers=headers,
            timeout=(10, 90)  # (connect timeout, read timeout)
            )
            status = response.status_code
            if status in (429, 500, 502, 503, 504):
                sleep_for = backoff_seconds * attempt
                logging.warning(
                    "Transient API status %s for %s (attempt %s/%s). Sleeping %.1fs",
                    status,
                    url,
                    attempt,
                    max_retries,
                    sleep_for,
                )
                
                time.sleep(sleep_for)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            if attempt == max_retries:
                raise RuntimeError(f"Failed API request after {max_retries} attempts: {url}") from exc
            sleep_for = backoff_seconds * attempt
            logging.warning(
                "API request failed for %s (attempt %s/%s): %s. Sleeping %.1fs",
                url,
                attempt,
                max_retries,
                exc,
                sleep_for,
            )
            time.sleep(sleep_for)

    raise RuntimeError(f"Unexpected API retry exit for {url}")



#below is the new attempt
from collections import deque

def get_planets_within_n_of_humans(
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    max_depth: int = 2,
):
    human_planets = [p for p, owner in owner_by_index.items() if owner == "Humans"]

    visited = set(human_planets)
    queue = deque((p, 0) for p in human_planets)

    within_range = set(human_planets)

    while queue:
        current, depth = queue.popleft()

        if depth == max_depth:
            continue

        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue

            visited.add(neighbor)
            within_range.add(neighbor)
            queue.append((neighbor, depth + 1))

    return within_range

from collections import deque

def shortest_path_with_major_order_rules(
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    major_order_planets: set[int],
    target: int,
    index_to_name,
) -> list[int] | None:
    DEBUG_BFS = False
    found_paths = []
    def pname(idx):
        return f"{index_to_name.get(idx, idx)} ({idx})"


    
    def is_frontline(planet: int) -> bool:
        # ❌ skip isolated planets
        if graph.degree(planet) == 0:
            return False
        if owner_by_index.get(planet) == "Humans":
            return False
        for neighbor in graph.neighbors(planet):
            if owner_by_index.get(neighbor) == "Humans":
                return True
        return False
    start_planets = [planet for planet, owner in owner_by_index.items() if owner == "Humans"]
    if not start_planets:
        if DEBUG_BFS:
            print(f"[BFS] No human start planets found for target {target}")
        return None

    if DEBUG_BFS:
        print(f"\n=== BFS DEBUG FOR TARGET {pname(target)} | Owner: {owner_by_index.get(target)} ===")
        print(f"Human start planet count: {len(start_planets)}")
        print(f"Target is major order: {target in major_order_planets}")
        print(f"Target is frontline: {is_frontline(target)}")

    queue = deque((start, [start]) for start in start_planets)
    #visited = set(start_planets)

    while queue:
        current, path = queue.popleft()

        if DEBUG_BFS:
            print(f"\n[CURRENT] {pname(current)} | Owner: {owner_by_index.get(current, 'Unknown')}")
            print(f"Path so far: {[pname(p) for p in path]}")

        for neighbor in graph.neighbors(current):
            if neighbor in path:
                if DEBUG_BFS:
                    print(f"  - Neighbor {pname(neighbor)} skipped: already in path")
                continue

            neighbor_owner = owner_by_index.get(neighbor, "Unknown")
            neighbor_is_human = neighbor_owner == "Humans"
            neighbor_is_major = neighbor in major_order_planets
            neighbor_is_frontline = is_frontline(neighbor)

            allowed = False
            reason = []

            if neighbor_is_human:
                allowed = True
                reason.append("human")
            if neighbor_is_major:
                allowed = True
                reason.append("major_order")
            if neighbor_is_frontline:
                allowed = True
                reason.append("frontline")

            if DEBUG_BFS:
                print(
                    f"  - Neighbor {pname(neighbor)} | Owner: {neighbor_owner} | "
                    f"human={neighbor_is_human}, "
                    f"major_order={neighbor_is_major}, "
                    f"frontline={neighbor_is_frontline} "
                    f"=> allowed={allowed}"
                )

            if not allowed:
                if DEBUG_BFS:
                    print(f"    ❌ Rejected {pname(neighbor)}")
                continue

            #visited.add(neighbor)
            next_path = path + [neighbor]

            if DEBUG_BFS:
                print(
                    f"    ✅ Accepted {pname(neighbor)} | "
                    f"path: {[pname(p) for p in next_path]}"
                )

            if neighbor == target:
                if DEBUG_BFS:
                    print(
                        f"*** TARGET REACHED: {pname(target)} via path "
                        f"{[pname(p) for p in next_path]}"
                    )
                found_paths.append(next_path)
                continue
                

            queue.append((neighbor, next_path))

    if DEBUG_BFS:
        print(f"*** TARGET NOT REACHABLE: {pname(target)}")

    return found_paths


def recompute_major_order_flags(
    df: pd.DataFrame,
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    major_order_planets: list[int],
    index_to_name,
) -> None:
    major_targets = set(major_order_planets)

    df["in_major_order"] = "F"
    df["major_order_completed"] = "F"
    df["possible_paths_to_major_order"] = "F"

    # ✅ Actual MO targets
    df.loc[df["planet_index"].isin(major_targets), "in_major_order"] = "T"

    # ✅ Completed
    for planet in major_targets:
        if owner_by_index.get(planet) == "Humans":
            df.loc[df["planet_index"] == planet, "major_order_completed"] = "T"

    # 🔥 PATH LOGIC
    all_planets_in_paths = set()

    for target in major_targets:
        paths = get_paths_to_target_limited(
            graph,
            owner_by_index,
            target,
            max_depth=2
        )

        

        for path in paths:
            for planet in path:
                all_planets_in_paths.add(planet)

    # ✅ APPLY ONCE (correct)
    #only allow non-human planets and non-major-order planets to be marked as possible paths to major order
    df.loc[
    (df["planet_index"].isin(all_planets_in_paths)) &
    (df["currentOwner"] != "Humans") &
    (~df["planet_index"].isin(major_targets)),
    "possible_paths_to_major_order"
    ] = "T"


from collections import deque

def get_paths_to_target_limited(
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    target: int,
    max_depth: int = 4,
):
    human_planets = [p for p, owner in owner_by_index.items() if owner == "Humans"]

    queue = deque((start, [start]) for start in human_planets)
    found_paths = []

    while queue:
        current, path = queue.popleft()

        if len(path) > max_depth:
            continue

        for neighbor in graph.neighbors(current):

            if neighbor in path:
                continue

            next_path = path + [neighbor]

            if neighbor == target:
                found_paths.append(next_path)
                continue

            queue.append((neighbor, next_path))

    return found_paths


def get_enemy_attacking_planet_and_owner(
    graph: nx.Graph,
    planet_index: int,
    owner_by_index: dict[int, str],
) -> tuple[int | None, str | None]:
    my_owner = owner_by_index.get(planet_index)
    if my_owner != "Humans":
        return None, None

    for neighbor in graph.neighbors(planet_index):
        neighbor_owner = owner_by_index.get(neighbor)
        if neighbor_owner != "Humans":
            return neighbor, neighbor_owner

    return None, None

#below is old way, might have to revert back to this incase new code doesn't work   
# def get_major_order_planet_indexes(major_order_payload: list[dict[str, Any]]) -> list[int]:
#     if not major_order_payload:
#         return []

#     tasks = major_order_payload[0].get("setting", {}).get("tasks", [])
#     indexes: list[int] = []
#     for task in tasks:
#         values = task.get("values", [])
#         if len(values) > 2 and isinstance(values[2], int):
#             indexes.append(values[2])
#     return indexes

def get_major_order_planet_indexes(major_order_payload: list[dict[str, Any]]) -> list[int]:
    if not major_order_payload:
        return []

    tasks = major_order_payload[0].get("setting", {}).get("tasks", [])
    indexes: list[int] = []

    for task in tasks:
        values = task.get("values", [])
        value_types = task.get("valueTypes", [])

        for v, t in zip(values, value_types):
            if t == 12:  # 12 = planet index
                indexes.append(v)

    return indexes


def build_graph(planets: list[dict[str, Any]], owner_by_index: dict[int, str]) -> nx.Graph:
    graph = nx.Graph()
    for planet in planets:
        planet_index = planet["index"]
        graph.add_node(planet_index, name=planet.get("name"), owner=planet.get("currentOwner"))

    name_to_index = {
        planet.get("name"): planet["index"]
        for planet in planets
        if planet.get("name")
    }

    skipped_edges = apply_manual_edges(graph, name_to_index)

    logging.info(
        "Applied hardcoded manual graph edges: %s added, %s skipped",
        graph.number_of_edges(),
        skipped_edges,
    )

    return graph


def run_collection_once() -> pd.DataFrame:
    headers = get_headers()
    logging.info("Starting Helldivers collection run")

    planets = fetch_json(f"{BASE_URL}/v1/planets", headers=headers)
    major_order_raw = fetch_json(
        "https://api.helldivers2.dev/raw/api/v2/Assignment/War/801",
        headers=headers,
    )
    assignments = fetch_json(f"{BASE_URL}/v1/assignments", headers=headers)
    dss = fetch_json(f"{BASE_URL}/v2/space-stations", headers=headers)


    major_order_planet_indexes = get_major_order_planet_indexes(major_order_raw)

    
    major_order_dispatch = (
            assignments[0].get("briefing", "NONE")
            if isinstance(assignments, list) and assignments
            else "NONE"
        )
    dss_planet_orbited = (
        dss[0].get("planet", {}).get("name")
        if isinstance(dss, list) and dss
        else None
    )

    planet_rows = []
    for planet in planets:
        hazards = planet.get("hazards", [])
        hazard_name = hazards[0]["name"] if hazards else ""
        stats = planet.get("statistics", {})
        #available = bool(planet.get("isAvailableToPlay", False))

        planet_rows.append(
            {
                "planet_index": planet["index"],
                "name": planet.get("name"),
                "sector": planet.get("sector"),
                "biome": planet.get("biome", {}).get("name"),
                "planet_environ_hazards": hazard_name,
                "player_on_planet": stats.get("playerCount", 0),
                "isAvailableToPlay": "F",
                "in_major_order": "F",
                "missions_won": stats.get("missionsWon", 0),
                "missions_lost": stats.get("missionsLost", 0),
                "is_humans_defending": "F",
                "helldiver_deaths_total": stats.get("deaths", 0),
                "helldiver_deaths_1hour_diff": "0",
                "bullets_fired": stats.get("bulletsFired", 0),
                "bullets_hit": stats.get("bulletsHit", 0),
                "illuminate_killed": stats.get("illuminateKills", 0),
                "terminids_killed": stats.get("terminidKills", 0),
                "automatons_killed": stats.get("automatonKills", 0),
                "currentOwner": planet.get("currentOwner"),
                "major_order_completed": "F",
                "planet_health": planet.get("health"),
                "max_planet_health": planet.get("maxHealth"),
            }
        )

    df = pd.DataFrame(planet_rows)
    df["major_order_dispatch"] = major_order_dispatch

    owner_by_index = {
        int(row["planet_index"]): str(row["currentOwner"])
        for _, row in df.iterrows()
    }
    graph = build_graph(planets, owner_by_index)
    # 🔥 COMPUTE PLAYABLE PLANETS (frontline logic)
    playable_planets = get_planets_within_n_of_humans(
    graph,
    owner_by_index,
    max_depth=1   # 👈 frontline (change to 2 if you want more reach)
)

    #recompute_major_order_flags(df, graph, owner_by_index, major_order_planet_indexes )
    index_to_name = dict(zip(df["planet_index"], df["name"]))

    recompute_major_order_flags(
        df,
        graph,
        owner_by_index,
        major_order_planet_indexes,
        index_to_name   # 👈 ADD THIS
    )
    
    df[["enemy_attacking_planet", "enemy_attacking_owner"]] = df["planet_index"].apply(
        lambda x: pd.Series(get_enemy_attacking_planet_and_owner(graph, int(x), owner_by_index))
    )
    #below doesn't work because a faction != human can be sitting beside the planet that humans are sitting on, will have to get later
    # df["is_humans_defending"] = (
    #     (df["currentOwner"] == "Humans") & (df["enemy_attacking_planet"].notna())
    # ).map({True: "T", False: "F"})

    df["major_order_planet_captured"] = (
        (df["currentOwner"] == "Humans") & (df["in_major_order"] == "T")
    ).map({True: "T", False: "F"})

    df["major_order_completed"] = (
        (df["currentOwner"] == "Humans")
        & (df["planet_index"].isin(major_order_planet_indexes))
    ).map({True: "T", False: "F"})

    df["DSS_present"] = (df["name"] == dss_planet_orbited).map({True: "T", False: "F"})

    now = datetime.now()
    df["Y-M-D"] = now.strftime("%Y-%m-%d")
    df["CST_H_M_S"] = now.strftime("%H:%M:%S")
    df["timestamp"] = now



    #BELOW IS FOR SAVING TO LOCAL CSV


    # df_history = load_history()
    # df_history = pd.concat([df_history, df], ignore_index=True)
    # save_history(df_history)

    # logging.info("Saved %s new rows. Total rows now: %s", len(df), len(df_history))


    #END OF CSV ADDING DATA

    #below is for saving to data postgres


    try:
        df.to_sql(
            "planet_history",
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )
        logging.info(f"Inserted {len(df)} rows into PostgreSQL")
    except Exception as e:
        logging.error(f"DB INSERT FAILED: {e}")

    # df.to_sql(
    # "planet_history",
    # engine,
    # if_exists="append",
    # index=False
    # )
    #print("LOCAL MODE: skipping database write")

    logging.info("Inserted %s rows into PostgreSQL", len(df))

    return df, graph, owner_by_index, major_order_planet_indexes, major_order_raw


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    run_collection_once()

    


#added debug code below


if __name__ == "__main__":
    main()
