# /// script
# dependencies = [
#   "httpx",
# ]
# ///
import itertools
import pathlib
import time

import httpx

FEMALE_GIVEN_NAME = "Q11879590"
SPARQL_URL = "https://query.wikidata.org/sparql"
API_URL = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "writober-first-names/0.1 (joachim@botify.com)"}
BATCH_SIZE = 50  # wbgetentities maximum


def fetch_ids(session: httpx.Client) -> list[str]:
    query = f"SELECT ?name WHERE {{ ?name wdt:P31 wd:{FEMALE_GIVEN_NAME} }}"
    response = session.get(
        SPARQL_URL,
        params={"query": query, "format": "json"},
        timeout=120,
    )
    response.raise_for_status()
    return [
        row["name"]["value"].rsplit("/", 1)[-1]
        for row in response.json()["results"]["bindings"]
    ]


def pick_label(labels: dict) -> str | None:
    for lang in ("mul", "en"):
        if lang in labels:
            return labels[lang]["value"]
    return next((label["value"] for label in labels.values()), None)


def fetch_labels(session: httpx.Client, ids: tuple[str, ...]) -> list[str]:
    while True:
        response = session.get(
            API_URL,
            params={
                "action": "wbgetentities",
                "ids": "|".join(ids),
                "props": "labels",
                "format": "json",
            },
            timeout=60,
        )
        if response.status_code != 429:
            break
        time.sleep(int(response.headers.get("Retry-After", 5)))
    response.raise_for_status()
    labels = (
        pick_label(entity.get("labels", {}))
        for entity in response.json()["entities"].values()
    )
    return [label for label in labels if label]


def main():
    with httpx.Client(headers=HEADERS) as session:
        ids = fetch_ids(session)
        batches = [
            fetch_labels(session, batch)
            for batch in itertools.batched(ids, BATCH_SIZE)
        ]

    names = sorted({name for batch in batches for name in batch})
    results = []
    for _, names_for_initial in itertools.groupby(names, lambda n: n[0]):
        results.append(", ".join(names_for_initial))

    pathlib.Path("first_names").write_text("\n".join(results))


if __name__ == "__main__":
    main()
