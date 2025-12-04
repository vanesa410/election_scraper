import re
import csv
import sys
from bs4 import BeautifulSoup as bs
from requests import get


def create_link(path: str) -> str:
    """
    Build a full URL from a relative path.

    Args:
        path (str): Relative path such as "ps3?xjazyk=CZ".

    Returns:
        str: Full constructed URL.
    """
    return f"https://www.volby.cz/pls/ps2017nss/{path}"


def get_parsed_response(url: str) -> bs:
    """
    Takes an url and returns parsed HTML .

    Args:
        url (str): Page URL.

    Returns:
        BeautifulSoup: Parsed HTML.
    """
    html = bs(get(url).text, features="html.parser")
    return html


def parse_municipalities(html: bs) -> tuple[list[str], list[str]]:
    """
    Parses municipalities for a region.

    Args:
        html (BeautifulSoup): Parsed HTML.

    Returns:
        Tuple[list[str], list[str], list[str]]:
            - municipality hrefs
            - municipality IDs
            - municipality names
    """
    td_municipality_number = html.find_all("td", {"class": "cislo"})
    td_municipality_name = html.find_all("td", {"class": "overflow_name"})
    municipality_hrefs = [
        a["href"] for td in td_municipality_number for a in td.find_all("a")
    ]
    municipality_ids = [
        a.text for td in td_municipality_number for a in td.find_all("a")
    ]
    municipality_names = [td.text for td in td_municipality_name]
    return municipality_ids, municipality_names, municipality_hrefs


def parse_results(html: bs) -> tuple[list[str], list[str], list[str], dict[str, str], list[str]:
    """
    Parses election results for a municipality from html.

    Args:
        html (BeautifulSoup): Parsed HTML of a municipality page.

    Returns:
        Tuple[List[str], List[str], List[str], Dict[str, str], List[str]:
            - registered voters
            - envelopes
            - valid votes
            - dict {party: votes}
            - region_name
    """
    td_registered_voters = html.find_all("td", {"headers": "sa2"})
    td_envelopes = html.find_all("td", {"headers": "sa3"})
    td_valid_votes = html.find_all("td", {"headers": "sa6"})
    td_parties = html.find_all("td", {"class": "overflow_name"})
    td_votes = html.find_all("td", {"headers": re.compile(r"t[12]sa2\s+t[12]sb3")})
    registered_voters = [td.text for td in td_registered_voters]
    envelopes = [td.text for td in td_envelopes]
    valid_votes = [td.text for td in td_valid_votes]
    parties = [td.text for td in td_parties]
    votes = [td.text for td in td_votes]

    title_tags = html.find_all("h3")
    region_name = title_tags[1].text.strip() if len(title_tags) > 1 else "municipality"
    party_votes = {party: vote for party, vote in zip(parties, votes)}
    return (
        registered_voters,
        envelopes,
        valid_votes,
        party_votes,
        region_name,
    )


def write_municipality_csv(
    all_rows,
    filename: str,
) -> str:
    """
    Creates CSV for a region with all municipalities.

    Args:
        region_name (str): Region name.
        all_parties (list[str]): List of all parties in region.
        rows (list[list[str]]): Final data rows.

    Returns:
        str: Output filename.
    """
    all_parties = sorted(
        {party for row in all_rows for party in row["party_votes"].keys()}
    )
    header = [
        "id",
        "location",
        "registered voters",
        "envelopes",
        "valid votes",
    ] + all_parties

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        for row in all_rows:
            row_values = [
                row["id"],
                row["location"],
                row["registered"],
                row["envelopes"],
                row["valid"],
            ] + [row["party_votes"].get(party, "") for party in all_parties]
            csv_writer.writerow(row_values)


def main() -> None:
    """
    Main function that runs the code.
    """
    if len(sys.argv) != 3:
        print("Usage: python script.py <municipality_url> <output_file.csv>")
        sys.exit(1)

    municipality_url = sys.argv[1]
    filename = sys.argv[2]

    try:
        html = get_parsed_response(municipality_url)
    except Exception as e:
        print(f"Error loading {municipality_url}: {e}")
        sys.exit(1)
    municipality_ids, municipality_names, municipality_hrefs = parse_municipalities(
        html
    )

    all_rows = []
    for m_id, m_name, href in zip(
        municipality_ids, municipality_names, municipality_hrefs
    ):
        url = create_link(href)
        html_m = get_parsed_response(url)
        registered_voters, envelopes, valid_votes, party_votes, _ = parse_results(
            html_m
        )
        row = {
            "id": m_id,
            "location": m_name,
            "registered": registered_voters[0] if registered_voters else "",
            "envelopes": envelopes[0] if envelopes else "",
            "valid": valid_votes[0] if valid_votes else "",
            "party_votes": party_votes,
        }
        all_rows.append(row)

    write_municipality_csv(all_rows, filename)
    print(f"Saved {filename}")


if __name__ == "__main__":
    main()
