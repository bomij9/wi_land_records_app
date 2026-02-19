import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from pyproj import Transformer
import requests
import math
import pandas as pd
import io
import time

# Dictionary of Wisconsin counties to their Register of Deeds portals
# (Fill this out completely – here's a starter; add the rest)
county_portals = {
    
    "Adams": "https://www.co.adams.wi.us/departments/register-of-deeds",
    "Ashland": "https://www.co.ashland.wi.us/departments/register-of-deeds",
    "Barron": "https://www.barroncountywi.gov/156/Register-of-Deeds",
    "Bayfield": "https://www.bayfieldcounty.wi.gov/156/Register-of-Deeds",
    "Brown": "https://www.browncountywi.gov/departments/register-of-deeds",
    "Buffalo": "https://www.buffalocountywi.gov/190/Register-of-Deeds",
    "Burnett": "https://www.burnettcountywi.gov/100/Register-of-Deeds",
    "Calumet": "https://www.co.calumet.wi.us/156/Register-of-Deeds",
    "Chippewa": "https://www.co.chippewa.wi.us/departments/register_of_deeds/index.php",
    "Clark": "https://www.clarkcountywi.gov/departments/register-of-deeds",
    "Columbia": "https://www.columbiacountywi.gov/departments/register-of-deeds",
    "Crawford": "https://www.crawfordcountywi.org/departments/register-of-deeds",
    "Dane": "https://www.danecounty.gov/registerofdeeds",
    "Dodge": "https://www.co.dodge.wi.gov/departments/register-of-deeds",
    "Door": "https://www.co.door.wi.gov/departments/register-of-deeds",
    "Douglas": "https://www.douglascountywi.gov/379/Register-of-Deeds",
    "Dunn": "https://www.co.dunn.wi.us/departments/register-of-deeds",
    "Eau Claire": "https://www.eauclairecounty.gov/departments/register-of-deeds",
    "Florence": "https://www.florencecountywi.com/departments/register-of-deeds",
    "Fond du Lac": "https://www.fdlco.wi.gov/departments/departments-n-z/register-of-deeds",
    "Forest": "https://www.co.forest.wi.gov/departments/register-of-deeds",
    "Grant": "https://www.grantcountywi.gov/departments/register-of-deeds",
    "Green": "https://www.greencountywi.org/195/Register-of-Deeds",
    "Green Lake": "https://www.co.green-lake.wi.us/departments/register-of-deeds",
    "Iowa": "https://www.iowacounty.org/departments/register-of-deeds",
    "Iron": "https://www.co.iron.wi.gov/departments/register-of-deeds",
    "Jackson": "https://www.co.jackson.wi.us/departments/register-of-deeds",
    "Jefferson": "https://www.jeffersoncountywi.gov/departments/register-of-deeds",
    "Juneau": "https://www.co.juneau.wi.gov/departments/register-of-deeds",
    "Kenosha": "https://www.kenoshacounty.org/156/Register-of-Deeds",
    "Kewaunee": "https://www.kewauneeco.org/departments/register-of-deeds",
    "La Crosse": "https://www.lacrossecounty.org/departments/register-of-deeds",
    "Lafayette": "https://www.co.lafayette.wi.gov/departments/register-of-deeds",
    "Langlade": "https://www.co.langlade.wi.us/departments/register-of-deeds",
    "Lincoln": "https://www.co.lincoln.wi.gov/departments/register-of-deeds",
    "Manitowoc": "https://www.manitowoccountywi.gov/156/Register-of-Deeds",
    "Marathon": "https://www.co.marathon.wi.us/departments/register-of-deeds",
    "Marinette": "https://www.marinettecounty.com/departments/register-of-deeds",
    "Marquette": "https://www.co.marquette.wi.gov/departments/register-of-deeds",
    "Menominee": "https://www.co.menominee.wi.gov/departments/register-of-deeds",
    "Milwaukee": "https://county.milwaukee.gov/EN/Register-of-Deeds",
    "Monroe": "https://www.co.monroe.wi.us/departments/register-of-deeds",
    "Oconto": "https://www.co.oconto.wi.us/departments/register-of-deeds",
    "Oneida": "https://www.oneidacountywi.gov/departments/register-of-deeds",
    "Outagamie": "https://www.outagamie.org/government/departments-n-z/register-of-deeds",
    "Ozaukee": "https://www.ozaukeecounty.gov/199/Register-of-Deeds",
    "Pepin": "https://www.co.pepin.wi.gov/departments/register-of-deeds",
    "Pierce": "https://www.co.pierce.wi.us/departments/register-of-deeds",
    "Polk": "https://www.polkcountywi.gov/government/divisions_and_departments/environmental_services_division/land_information_office/register_of_deeds.php",
    "Portage": "https://www.co.portage.wi.gov/departments/register-of-deeds",
    "Price": "https://www.co.price.wi.gov/departments/register-of-deeds",
    "Racine": "https://www.racinecounty.gov/departments/register-of-deeds",
    "Richland": "https://www.co.richland.wi.us/departments/register-of-deeds",
    "Rock": "https://www.co.rock.wi.us/departments/register-of-deeds",
    "Rusk": "https://www.ruskcountywi.gov/departments/register-of-deeds",
    "Sauk": "https://www.co.sauk.wi.us/departments/register-of-deeds",
    "Sawyer": "https://www.co.sawyer.wi.gov/departments/register-of-deeds",
    "Shawano": "https://www.co.shawano.wi.gov/departments/register-of-deeds",
    "Sheboygan": "https://www.sheboygancounty.com/departments/register-of-deeds",
    "St. Croix": "https://www.sccwi.gov/departments/register-of-deeds",
    "Taylor": "https://www.co.taylor.wi.us/departments/register-of-deeds",
    "Trempealeau": "https://www.tremplocounty.com/departments/register-of-deeds",
    "Vernon": "https://www.vernoncountywi.gov/departments/register_of_deeds/index.php",
    "Vilas": "https://www.co.vilas.wi.gov/departments/register-of-deeds",
    "Walworth": "https://www.co.walworth.wi.us/departments/register-of-deeds",
    "Washburn": "https://www.co.washburn.wi.gov/departments/register-of-deeds",
    "Washington": "https://www.washcowisco.gov/departments/register-of-deeds",
    "Waukesha": "https://www.waukeshacounty.gov/registerofdeeds",
    "Waupaca": "https://www.co.waupaca.wi.gov/departments/register-of-deeds",
    "Waushara": "https://www.co.waushara.wi.gov/departments/register-of-deeds",
    "Winnebago": "https://www.co.winnebago.wi.gov/departments/register-of-deeds",
    "Wood": "https://www.woodcountywi.gov/departments/rod"
}
}

sewrpc_counties = ["Milwaukee", "Kenosha", "Ozaukee", "Walworth", "Waukesha", "Racine"]

quarter_map = {1: "NE", 2: "NW", 3: "SE", 4: "SW"}

st.title("Wisconsin Land Records & PLSS Finder")
st.write(
    "Enter a Wisconsin address to find the county Register of Deeds portal, "
    "PLSS location (township/range/section/quarter), and links to higher-accuracy SCO Survey Control Finder."
)

address = st.text_input("Enter address (e.g., 123 Main St, Greenfield, WI)", "")

if address:
    try:
        with st.spinner("Geocoding address..."):
            geolocator = Nominatim(
                user_agent="wisconsin-land-plss-finder-app (bodemichael9@gmail.com)",
                timeout=45
            )
            location = geolocator.geocode(address + ", Wisconsin, USA", addressdetails=True)
            time.sleep(1)  # Respect Nominatim usage policy (1 req/sec)

        if not location:
            st.error("Could not geocode the address. Try adding city, ZIP, or more details.")
            st.stop()

        # ── County extraction ── robust version
        county = None
        if hasattr(location, 'raw') and isinstance(location.raw, dict):
            raw_addr = location.raw.get('address', {})
            for key in ['county', 'state_county', 'county_name', 'state_district']:
                if key in raw_addr and isinstance(raw_addr[key], str):
                    county = raw_addr[key].replace(" County", "").strip()
                    break

            if not county and 'display_name' in location.raw:
                parts = [p.strip() for p in location.raw['display_name'].split(',')]
                for part in parts:
                    if 'County' in part:
                        county = part.replace(" County", "").strip()
                        break

        if not county:
            st.warning("Could not reliably determine county. Some features may be limited.")
        else:
            st.success(f"Located in **{county} County** (Lat: {location.latitude:.6f}, Lon: {location.longitude:.6f})")

            # Register of Deeds link
            if county in county_portals:
                portal_url = county_portals[county]
                st.markdown(f"**{county} County Register of Deeds:** [{portal_url}]({portal_url})")
                st.info("Search by address or parcel ID. Some sites require payment/subscription.")
            else:
                st.warning(
                    f"No portal listed for {county} County. "
                    "Try https://www.wrdaonline.org/counties or Google search."
                )

        # ────────────────────────────────────────────────
        # PLSS Point Query
        # ────────────────────────────────────────────────
        plss_data = None
        try:
            with st.spinner("Querying Wisconsin DNR PLSS service..."):
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3071", always_xy=True)
                x, y = transformer.transform(location.longitude, location.latitude)

                url = "https://dnrmaps.wi.gov/arcgis/rest/services/DW_Map_Dynamic/FR_PLSS_Landnet_WTM_Ext/MapServer/2/query"
                params = {
                    'f': 'json',
                    'returnGeometry': 'false',
                    'spatialRel': 'esriSpatialRelWithin',
                    'geometry': f'{{"x":{x},"y":{y},"spatialReference":{{"wkid":3071}}}}',
                    'geometryType': 'esriGeometryPoint',
                    'inSR': '3071',
                    'outFields': '*',
                }
                resp = requests.get(url, params=params, timeout=20)
                resp.raise_for_status()
                result = resp.json()

                if 'features' in result and result['features']:
                    plss_data = result['features'][0]['attributes']

        except requests.exceptions.Timeout:
            st.warning("PLSS query timed out. Try again later.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network issue with PLSS service: {e}")
        except Exception as e:
            st.error(f"Error querying PLSS: {e}")

        # ────────────────────────────────────────────────
        # Display PLSS & SCO guidance
        # ────────────────────────────────────────────────
        if plss_data:
            twn = plss_data.get('PLSS_TWN_ID', 'N/A')
            rng = plss_data.get('PLSS_RNG_ID', 'N/A')
            rng_dir_code = plss_data.get('PLSS_RNG_DIR_NUM_CODE', 1)  # 1=E, 2=W
            rng_dir = "E" if rng_dir_code == 1 else "W" if rng_dir_code == 2 else "?"
            sec = plss_data.get('PLSS_SCTN_ID', 'N/A')
            q1 = plss_data.get('PLSS_Q1_SCTN_NUM_CODE')
            q2 = plss_data.get('PLSS_Q2_SCTN_NUM_CODE')
            desc = plss_data.get('PLSS_DESC', '')
            quarter = quarter_map.get(q1, 'N/A') if q1 else 'N/A'
            qq = quarter_map.get(q2, 'N/A') if q2 else 'N/A'

            st.subheader("PLSS Quarter-Quarter Section")
            cols = st.columns(3)
            cols[0].write(f"**Township:** {twn}N")
            cols[1].write(f"**Range:** {rng}{rng_dir}")
            cols[2].write(f"**Section:** {sec}")
            st.write(f"**Quarter Section:** {quarter} ¼")
            if qq != 'N/A':
                st.write(f"**Quarter-Quarter Section:** {qq} ¼ of the {quarter} ¼")
            if desc:
                st.write(f"**Full Description:** {desc}")

            # ── SCO Survey Control Finder guidance ──
            st.subheader("Higher-Accuracy Corner Coordinates & Tie Sheets")
            st.markdown(
                "The **SCO Survey Control Finder** provides precise surveyed corner coordinates "
                "(often cm-level in remonumented counties like Milwaukee), monument details, "
                "tie sheets/CSSD PDFs, and exports (CSV, Shapefile, KML, GeoJSON)."
            )

            search_terms = f"T{twn}N R{rng}{rng_dir} S{sec}"
            quarter_hint = ""
            if quarter != 'N/A':
                quarter_hint = f" — focus on the {quarter} quarter"
                if qq != 'N/A':
                    quarter_hint += f" ({qq} quarter-quarter)"

            st.info(f"""
            Quick steps:
            1
