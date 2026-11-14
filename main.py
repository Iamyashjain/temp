import requests
from bs4 import BeautifulSoup


# Set this to a URL to use a fixed link instead of being prompted.
STATIC_URL = "https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"


def print_secret_message(url: str) -> None:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    characters: dict[tuple[int, int], str] = {}
    min_x = min_y = None
    max_x = max_y = None

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        headers = [
            cell.get_text(strip=True).lower()
            for cell in rows[0].find_all(["td", "th"])
        ]
        x_column = next(
            (i for i, header in enumerate(headers)
             if "x" in header and "coordinate" in header),
            None,
        )
        y_column = next(
            (i for i, header in enumerate(headers)
             if "y" in header and "coordinate" in header),
            None,
        )
        character_column = next(
            (i for i, header in enumerate(headers) if "character" in header),
            None,
        )

        if x_column is None or y_column is None or character_column is None:
            continue

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) <= max(x_column, y_column, character_column):
                continue

            try:
                x = int(cells[x_column].get_text(strip=True))
                y = int(cells[y_column].get_text(strip=True))
            except ValueError:
                continue

            character = cells[character_column].get_text(strip=True)
            if not character:
                continue

            characters[(x, y)] = character
            min_x = x if min_x is None else min(min_x, x)
            max_x = x if max_x is None else max(max_x, x)
            min_y = y if min_y is None else min(min_y, y)
            max_y = y if max_y is None else max(max_y, y)

    if not characters:
        raise ValueError(
            "No coordinate data found. Check that the page contains a table "
            "with x-coordinate, y-coordinate, and character columns."
        )

    for y in range(max_y, min_y - 1, -1):
        print("".join(
            characters.get((x, y), " ")
            for x in range(min_x, max_x + 1)
        ))


def main() -> None:
    url = STATIC_URL.strip() or input("Enter the page URL: ").strip()
    if not url:
        raise ValueError("A URL is required.")

    print_secret_message(url)


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError) as error:
        print(f"Error: {error}")
