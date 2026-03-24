import logging
import os
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
import requests


BASE_URL = "https://api.helldivers2.dev/api"
HISTORY_FILE = Path(__file__).resolve().parent / "planet_history.csv"

DEFAULT_CLIENT = "helldivers-machine_learning-project"
DEFAULT_CONTACT = "replace-with-email@example.com"


def load_history() -> pd.DataFrame:
    if HISTORY_FILE.exists():
        return pd.read_csv(HISTORY_FILE, parse_dates=["timestamp"])
    return pd.DataFrame()


def save_history(df: pd.DataFrame) -> None:
    df.to_csv(HISTORY_FILE, index=False)


def get_headers() -> dict[str, str]:
    return {
        "X-Super-Client": os.getenv("HD2_CLIENT_NAME", DEFAULT_CLIENT),
        "X-Super-Contact": os.getenv("HD2_CONTACT_EMAIL", DEFAULT_CONTACT),
    }


def fetch_json(
    url: str,
    headers: dict[str, str],
    timeout: int = 30,
    max_retries: int = 5,
    backoff_seconds: float = 2.0,
) -> Any:
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
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


def shortest_path_with_major_order_rules(
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    major_order_planets: set[int],
    target: int,
) -> list[int] | None:
    def is_frontline(planet: int) -> bool:
        if owner_by_index.get(planet) == "Humans":
            return False
        for neighbor in graph.neighbors(planet):
            if owner_by_index.get(neighbor) == "Humans":
                return True
        return False

    start_planets = [planet for planet, owner in owner_by_index.items() if owner == "Humans"]
    if not start_planets:
        return None

    queue = deque((start, [start]) for start in start_planets)
    visited = set(start_planets)

    while queue:
        current, path = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue

            allowed = False
            if owner_by_index.get(neighbor) == "Humans":
                allowed = True
            elif neighbor in major_order_planets:
                allowed = True
            elif is_frontline(neighbor):
                allowed = True

            if not allowed:
                continue

            visited.add(neighbor)
            next_path = path + [neighbor]
            if neighbor == target:
                return next_path
            queue.append((neighbor, next_path))

    return None


def recompute_major_order_flags(
    df: pd.DataFrame,
    graph: nx.Graph,
    owner_by_index: dict[int, str],
    major_order_planets: list[int],
) -> None:
    major_targets = set(major_order_planets)
    df["in_major_order"] = "F"
    df["major_order_completed"] = "F"

    for planet in major_targets:
        if owner_by_index.get(planet) == "Humans":
            df.loc[df["planet_index"] == planet, "major_order_completed"] = "T"

    for target in major_targets:
        if owner_by_index.get(target) == "Humans":
            continue
        path = shortest_path_with_major_order_rules(graph, owner_by_index, major_targets, target)
        if path is None:
            continue
        for planet in path[1:]:
            df.loc[df["planet_index"] == planet, "in_major_order"] = "T"


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


def get_major_order_planet_indexes(major_order_payload: list[dict[str, Any]]) -> list[int]:
    if not major_order_payload:
        return []

    tasks = major_order_payload[0].get("setting", {}).get("tasks", [])
    indexes: list[int] = []
    for task in tasks:
        values = task.get("values", [])
        if len(values) > 2 and isinstance(values[2], int):
            indexes.append(values[2])
    return indexes


def build_graph(planets: list[dict[str, Any]], owner_by_index: dict[int, str]) -> nx.Graph:
    graph = nx.Graph()
    for planet in planets:
        planet_index = planet["index"]
        graph.add_node(planet_index, name=planet.get("name"), owner=planet.get("currentOwner"))

    for planet in planets:
        src = planet["index"]
        for dst in planet.get("waypoints", []):
            if dst in owner_by_index:
                graph.add_edge(src, dst)

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
        available = bool(planet.get("isAvailableToPlay", False))

        planet_rows.append(
            {
                "planet_index": planet["index"],
                "name": planet.get("name"),
                "sector": planet.get("sector"),
                "biome": planet.get("biome", {}).get("name"),
                "planet_environ_hazards": hazard_name,
                "player_on_planet": stats.get("playerCount", 0),
                "isAvailableToPlay": "T" if available else "F",
                "in_major_order": "T" if planet["index"] in major_order_planet_indexes else "F",
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

    recompute_major_order_flags(df, graph, owner_by_index, major_order_planet_indexes)
    df[["enemy_attacking_planet", "enemy_attacking_owner"]] = df["planet_index"].apply(
        lambda x: pd.Series(get_enemy_attacking_planet_and_owner(graph, int(x), owner_by_index))
    )

    df["is_humans_defending"] = (
        (df["currentOwner"] == "Humans") & (df["enemy_attacking_planet"].notna())
    ).map({True: "T", False: "F"})

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

    df_history = load_history()
    df_history = pd.concat([df_history, df], ignore_index=True)
    save_history(df_history)

    logging.info("Saved %s new rows. Total rows now: %s", len(df), len(df_history))
    return df_history


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    run_collection_once()


if __name__ == "__main__":
    main()
