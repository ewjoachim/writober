# /// script
# dependencies = [
#   "httpx",
# ]
# ///
import asyncio
import itertools
import pathlib
import re

import httpx

CATEGORY = "Feminine_given_names"
URL = "https://en.wikipedia.org/w/api.php"

params = {
    "action": "query",
    "list": "categorymembers",
    "cmtitle": f"Category:{CATEGORY}",
    "cmlimit": "max",  # maximum allowed
    "format": "json",
}


async def main():
    session = httpx.AsyncClient()
    titles = []
    while True:
        response = (await session.get(URL, params=params)).json()

        for page in response["query"]["categorymembers"]:
            title = page["title"]
            if "Category" in title:
                continue

            title = title.split("(")[0].strip()
            titles.append(title)

        # Handle pagination
        if "continue" in response:
            params["cmcontinue"] = response["continue"]["cmcontinue"]
        else:
            break

    titles = sorted(titles)
    results = []
    for _, titles_for_initial in itertools.groupby(titles, lambda t: t[0]):
        results.append(", ".join(titles_for_initial))

    pathlib.Path("first_names").write_text("\n".join(results))


if __name__ == "__main__":
    asyncio.run(main())
