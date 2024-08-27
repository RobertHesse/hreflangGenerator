import requests
import xml.etree.ElementTree as ET
import re
import csv

# Liste der allgemeinen Sitemaps
general_sitemaps = [
    'https://stauff.com.br/sitemap.xml',
    'https://stauff.fr/sitemap.xml',
    'https://stauff.com/sitemap.xml',
    'https://www.stauffusa.com/sitemap.xml',
    'https://stauff.co.uk/sitemap.xml',
    'https://stauff.com.au/sitemap.xml',
    'https://stauff.co.nz/sitemap.xml',
    'https://stauffcanada.com/sitemap.xml',
    'https://stauff.ru/sitemap.xml',
    'https://stauff.it/sitemap.xml',
    'https://stauff.in/sitemap.xml'
]

# Funktion zum Parsen der Sitemap und zum Extrahieren der Kategorie-Sitemaps
def extract_category_sitemaps(general_sitemap_url):
    try:
        response = requests.get(general_sitemap_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        category_sitemaps = []
        for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
            loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            # Nur Kategorie-Sitemaps extrahieren
            if 'category' in loc:
                category_sitemaps.append(loc)
        
        return category_sitemaps
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Sitemap {general_sitemap_url}: {e}")
        return []

# Funktion zum Extrahieren von Länder- und Sprachinformationen aus der Sitemap-URL
def extract_country_language(sitemap_url):
    # Beispiel-URL: https://stauff.com.br/sitemap-category-en_US-1.xml
    match = re.search(r'sitemap-category-([a-z]{2})_([A-Z]{2})', sitemap_url)
    if match:
        language_code = match.group(1)
        country_code = match.group(2)
        return country_code, language_code
    else:
        # Fallback, falls das Muster nicht gefunden wird
        return 'Unknown', 'Unknown'

# CSV-Datei erstellen und Daten schreiben
csv_filename = 'data/sitemap_overview_dynamic.csv'
with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ['Shop URL', 'Category Sitemap URL', 'Country', 'Language']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for general_sitemap in general_sitemaps:
        category_sitemaps = extract_category_sitemaps(general_sitemap)
        for category_sitemap in category_sitemaps:
            country, language = extract_country_language(category_sitemap)
            writer.writerow({
                'Shop URL': general_sitemap,
                'Category Sitemap URL': category_sitemap,
                'Country': country,
                'Language': language
            })

print(f"CSV-Datei '{csv_filename}' erfolgreich erstellt.")
