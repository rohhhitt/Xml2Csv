import requests
import pandas as pd
import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(filename='xml_import.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define URL for XML data source (Using ECB's public XML API)
XML_URL = "https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?detail=dataonly"  # Exchange rates dataset

def fetch_xml(url):
    """Fetch XML data from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to fetch XML: {e}")
        return None

def parse_xml(xml_data):
    """Parse XML and extract relevant data."""
    try:
        root = ET.fromstring(xml_data)
        ns = {'ns': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'}  # Namespace for ECB XML
        data = []
        
        for series in root.findall('.//ns:Series', ns):
            for obs in series.findall('.//ns:Obs', ns):
                time = obs.find('ns:ObsDimension', ns).get('value')
                rate = obs.find('ns:ObsValue', ns).get('value')
                record = {'Date': time, 'Exchange Rate': rate}
                data.append(record)
        return data
    except ET.ParseError as e:
        logging.error(f"XML Parsing error: {e}")
        return None

def save_to_csv(data, filename="exchange_rates.csv"):
    """Save extracted data to CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logging.info(f"Data saved to {filename}")

def main():
    xml_data = fetch_xml(XML_URL)
    if xml_data:
        parsed_data = parse_xml(xml_data)
        if parsed_data:
            save_to_csv(parsed_data)

if __name__ == "__main__":
    main()
