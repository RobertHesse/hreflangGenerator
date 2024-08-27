import csv
import requests
import xml.etree.ElementTree as ET

# Funktion zum Parsen der Sitemap und zum Extrahieren der URLs
def parse_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()  # Fehlerbehandlung
        root = ET.fromstring(response.content)
        urls = []
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            urls.append(url.text)
        return urls
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Sitemap {sitemap_url}: {e}")
        return []

# Laden der Sitemap-Übersicht aus der CSV-Datei
overview_csv_filename = 'data/sitemap_overview_dynamic.csv'
sitemaps_info = []

with open(overview_csv_filename, mode='r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        sitemaps_info.append({
            'shop_url': row['Shop URL'],
            'category_sitemap_url': row['Category Sitemap URL'],
            'country': row['Country'],
            'language': row['Language']
        })

# Sitemaps parsen und Kategorien extrahieren
categories = {}
for info in sitemaps_info:
    urls = parse_sitemap(info['category_sitemap_url'])
    key = f"{info['language']}_{info['country']}_{info['shop_url']}"
    categories[key] = {url.split('/')[-1]: url for url in urls}

# Alle Kategorien sammeln (Union der Kategorienamen)
all_categories = set()
for cat_dict in categories.values():
    all_categories.update(cat_dict.keys())

# CSV-Datei für hreflang-Tags erstellen
hreflang_csv_filename = 'data/hreflang_categories.csv'
with open(hreflang_csv_filename, mode='w', newline='') as csv_file:
    # Dynamische Spaltenüberschriften basierend auf den gefundenen Sprachen und Ländern
    sitemap_keys = list(categories.keys())
    fieldnames = ['Kategorie'] + [f'URL {key}' for key in sitemap_keys] + [f'hreflang {key}' for key in sitemap_keys]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    # Kategorien vergleichen und in die CSV schreiben
    for category in sorted(all_categories):
        row = {'Kategorie': category}
        for key in sitemap_keys:
            url = categories[key].get(category)
            row[f'URL {key}'] = url if url else ''
            hreflang_tag = f'<link rel="alternate" hreflang="{key.split("_")[0]}-{key.split("_")[1]}" href="{url}" />' if url else ''
            row[f'hreflang {key}'] = hreflang_tag
        writer.writerow(row)

print(f"CSV-Datei '{hreflang_csv_filename}' erfolgreich erstellt.")
