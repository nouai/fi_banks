# fi_banks.py

import os
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import html

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_URL = "https://www.fi.se"
LIST_PATH = "/sv/vara-register/foretagsregistret/index"

CATEGORIES = ["BANK", "MBANK", "SPAR"]

CATEGORY_LABELS = {
    "BANK": "Bankaktiebolag",
    "MBANK": "Medlemsbank",
    "SPAR": "Sparbank",
}

CATEGORY_CLASSES = {
    "Bankaktiebolag": "bank-row",
    "Medlemsbank": "mbank-row",
    "Sparbank": "spar-row",
}

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


# ---------------------------------------------------------
# Caching helpers
# ---------------------------------------------------------

def cache_path(url: str) -> str:
    h = hashlib.sha256(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.html")


def cached_file_for(url: str) -> str:
    # Use forward slashes so it works nicely in href
    return cache_path(url).replace("\\", "/")


# ---------------------------------------------------------
# Fetch + clean (dual mode: main list vs detail)
# ---------------------------------------------------------

def fetch(url: str, delay: int = 3) -> str:
    """
    Fetch URL, clean HTML, cache result.

    - Main list pages (…/foretagsregistret/index…):
        * keep only <table id="institut">
        * fix links to point to original FI site
    - Detail pages:
        * keep only <div class="page">
        * fix links to point to original FI site
        * replace breadcrumb 'Företagsregistret' with ../banks.html
    """
    path = cache_path(url)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"Fetching (live): {url}")
    time.sleep(delay)

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Remove scripts and styles globally
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    # ---------------------------------------------------------
    # MAIN LIST PAGE CLEANING
    # ---------------------------------------------------------
    if "foretagsregistret/index" in url:
        table = soup.find("table", id="institut")
        if table:
            # Fix links inside main list table to original FI site
            for tag in table.find_all("a", href=True):
                href = tag["href"]

                # Broken relative like "gransoverskridandehandel?id=22856"
                if not href.startswith("/") and not href.startswith("http"):
                    tag["href"] = (
                        BASE_URL
                        + "/sv/vara-register/foretagsregistret/"
                        + href
                    )
                    continue

                # Root-relative
                if href.startswith("/"):
                    tag["href"] = BASE_URL + href

            soup = table
        else:
            # Fallback: keep whole page if structure changes
            soup = BeautifulSoup(r.text, "html.parser")

    # ---------------------------------------------------------
    # DETAIL PAGE CLEANING
    # ---------------------------------------------------------
    else:
        content = soup.find("div", class_="page")
        if content:
            soup = content
        else:
            soup = BeautifulSoup(r.text, "html.parser")

        # Fix links in detail pages
        for tag in soup.find_all(href=True):
            href = tag["href"]

            # Broken relative like "gransoverskridandehandel?id=22856"
            if not href.startswith("/") and not href.startswith("http"):
                tag["href"] = (
                    BASE_URL
                    + "/sv/vara-register/foretagsregistret/"
                    + href
                )
                continue

            # Root-relative
            if href.startswith("/"):
                tag["href"] = BASE_URL + href

        for tag in soup.find_all(src=True):
            src = tag["src"]

            if not src.startswith("/") and not src.startswith("http"):
                tag["src"] = (
                    BASE_URL
                    + "/sv/vara-register/foretagsregistret/"
                    + src
                )
                continue

            if src.startswith("/"):
                tag["src"] = BASE_URL + src

        # Replace breadcrumb Företagsregistret → ../banks.html
        for bc in soup.find_all("a", class_="breadcrumb-item"):
            if "Företagsregistret" in bc.get_text(strip=True):
                bc["href"] = "../banks.html"

    cleaned_html = str(soup)

    with open(path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

    return cleaned_html


# ---------------------------------------------------------
# Scrape list pages
# ---------------------------------------------------------

def scrape_bank_list(cat_code: str):
    url = f"{BASE_URL}{LIST_PATH}?huvudkategori=Bank&cat={cat_code}&area=#results"
    html_text = fetch(url)
    soup = BeautifulSoup(html_text, "html.parser")

    table = soup.find("table", id="institut")
    if not table:
        print("No table found on:", url)
        return []

    rows = table.find("tbody").find_all("tr")

    banks = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) != 2:
            continue

        name_cell = cols[0]
        orgnr_cell = cols[1]

        link = name_cell.find("a")
        if not link or not link.get("href"):
            continue

        name = link.get_text(strip=True)
        details_url = urljoin(url, link["href"])
        orgnr = orgnr_cell.get_text(strip=True)

        banks.append(
            {
                "name": name,
                "orgnr": orgnr,
                "details_url": details_url,
                "category": CATEGORY_LABELS.get(cat_code, cat_code),
            }
        )

    return banks


# ---------------------------------------------------------
# Scrape details page
# ---------------------------------------------------------

def scrape_details(url: str):
    html_text = fetch(url)
    soup = BeautifulSoup(html_text, "html.parser")

    data = {"details_url": url}

    # FI Institutnummer
    funky = soup.find("dl", class_="funky")
    if funky:
        dt = funky.find(
            "dt",
            string=lambda s: s and "institutnummer" in s.lower(),
        )
        if dt:
            dd = dt.find_next("dd")
            if dd:
                data["fi_institutnummer"] = dd.get_text(strip=True)

    # Authorizations
    auth_ul = soup.find("ul", class_="tillstand")
    if auth_ul:
        items = []
        for li in auth_ul.find_all("li"):
            text = " ".join(li.stripped_strings)
            if text:
                items.append(text)
        data["authorizations"] = items

    return data


# ---------------------------------------------------------
# Scrape all banks
# ---------------------------------------------------------

def scrape_all_banks():
    all_banks = []

    for cat in CATEGORIES:
        banks = scrape_bank_list(cat)
        all_banks.extend(banks)

    for bank in all_banks:
        details = scrape_details(bank["details_url"])
        bank.update(details)

    return all_banks


# ---------------------------------------------------------
# HTML output
# ---------------------------------------------------------

def generate_html(banks, filename: str = "banks.html"):
    js = r"""
<script>
function sortTable(n, numeric=false) {
  var table = document.getElementById("banksTable");
  var rows = Array.from(table.rows).slice(1);
  var dir = table.getAttribute("data-sort-dir-" + n) === "asc" ? "desc" : "asc";
  rows.sort(function(a, b) {
    var x = a.cells[n].innerText.trim();
    var y = b.cells[n].innerText.trim();
    if (numeric) {
      x = x.replace(/\D/g, "") || "0";
      y = y.replace(/\D/g, "") || "0";
      x = parseInt(x, 10);
      y = parseInt(y, 10);
    }
    if (x < y) return dir === "asc" ? -1 : 1;
    if (x > y) return dir === "asc" ? 1 : -1;
    return 0;
  });
  var tbody = table.tBodies[0];
  rows.forEach(function(r) { tbody.appendChild(r); });
  table.setAttribute("data-sort-dir-" + n, dir);
}
</script>
"""

    html_rows = []
    for b in banks:
        name = html.escape(b["name"])
        orgnr = html.escape(b["orgnr"])
        category = b.get("category", "")
        category_escaped = html.escape(category)
        fi_inst = html.escape(b.get("fi_institutnummer", ""))

        css_class = CATEGORY_CLASSES.get(category, "")

        # Cascade: ensure cached detail file exists; if missing, fetch & cache
        local = cached_file_for(b["details_url"])
        if not os.path.exists(local):
            fetch(b["details_url"])
        url = html.escape(local)

        auth_list = b.get("authorizations", [])
        if auth_list:
            auth_html = (
                "<details><summary>Show</summary><ul>"
                + "".join(
                    f"<li>{html.escape(item)}</li>" for item in auth_list
                )
                + "</ul></details>"
            )
        else:
            auth_html = ""

        html_rows.append(
            f"<tr class=\"{css_class}\">"
            f"<td><a href=\"{url}\" target=\"_blank\">{name}</a></td>"
            f"<td>{orgnr}</td>"
            f"<td>{category_escaped}</td>"
            f"<td>{fi_inst}</td>"
            f"<td>{auth_html}</td>"
            f"</tr>"
        )

    html_doc = f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8">
<title>FI Banks</title>
<style>
table {{
  border-collapse: collapse;
  width: 100%;
  font-family: sans-serif;
  font-size: 14px;
}}
th, td {{
  border: 1px solid #ccc;
  padding: 4px 8px;
}}
th {{
  background: #f0f0f0;
  cursor: pointer;
}}
tr:has(details[open]) {{
  background: #fafafa;
}}
details summary {{
  cursor: pointer;
  color: #0074d9;
}}
.bank-row {{
  background-color: #d9f2d9;
}}
.mbank-row {{
  background-color: #fff7cc;
}}
.spar-row {{
  background-color: #ffe0cc;
}}
/* Highlight row when details are open */
tr:has(details[open]) {{
  background: #fafafa !important;
}}
</style>
{js}
</head>
<body>
<h1>Swedish Banks (FI Företagsregistret)</h1>
<p>Total banks: {len(banks)}</p>
<table id="banksTable" data-sort-dir-0="asc" data-sort-dir-1="asc" data-sort-dir-2="asc" data-sort-dir-3="asc" data-sort-dir-4="asc">
<thead>
<tr>
  <th onclick="sortTable(0, false)">Name</th>
  <th onclick="sortTable(1, true)">Organisationsnummer</th>
  <th onclick="sortTable(2, false)">Category</th>
  <th onclick="sortTable(3, true)">FI Institutnummer</th>
  <th onclick="sortTable(4, false)">Authorizations</th>
</tr>
</thead>
<tbody>
{''.join(html_rows)}
</tbody>
</table>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"HTML written to {filename}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    banks = scrape_all_banks()
    print(f"Total banks scraped: {len(banks)}")

    if "--html" in sys.argv:
        generate_html(banks)
    else:
        print(f"{'Name':<45}{'OrgNr':<15}{'Cat':<15}{'FI Inst':<10}")
        print("-" * 90)
        for b in banks:
            print(
                f"{b['name']:<45}"
                f"{b['orgnr']:<15}"
                f"{b.get('category',''):<15}"
                f"{b.get('fi_institutnummer',''):<10}"
            )
