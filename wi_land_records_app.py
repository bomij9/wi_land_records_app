import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pyproj
import requests

# Rest of your code (county_portals, etc.)...
# Dictionary of Wisconsin counties to their Register of Deeds portals (expanded).
county_portals = {
    "Adams": "https://www.co.adams.wi.us/departments/register-of-deeds",
    "Ashland": "https://www.co.ashland.wi.us/departments/register-of-deeds",
    "Barron": "https://barroncountywi.gov/register-of-deeds",
    "Bayfield": "https://www.bayfieldcounty.wi.gov/152/Register-of-Deeds",
    "Brown": "https://www.browncountywi.gov/departments/register-of-deeds",
    "Buffalo": "https://www.buffalocountywi.gov/151/Register-of-Deeds",
    "Burnett": "https://www.burnettcountywi.gov/100/Register-of-Deeds",
    "Calumet": "https://www.calumetcounty.org/156/Register-of-Deeds",
    "Chippewa": "https://www.chippewacountywi.gov/171/Register-of-Deeds",
    "Clark": "https://www.clarkcountywi.gov/departments/register-of-deeds",
    "Columbia": "https://www.co.columbia.wi.us/columbiacounty/registerofdeeds/RegisterofDeedsHome/tabid/106/Default.aspx",
    "Crawford": "https://crawfordcountywi.org/departments/register-of-deeds",
    "Dane": "https://rod.danecounty.gov/real-estate/online-record-search",
    "Dodge": "https://www.co.dodge.wi.gov/departments/departments-p-z/register-of-deeds",
    "Door": "https://www.co.door.wi.gov/187/Register-of-Deeds",
    "Douglas": "https://www.douglascountywi.gov/379/Register-of-Deeds",
    "Dunn": "https://dunncountywi.gov/departments/register-of-deeds",
    "Eau Claire": "https://www.eauclairecounty.gov/our-government/departments/register-of-deeds",
    "Florence": "https://www.florencecountywi.com/departments/?department=6d3f5a0c6a2a",
    "Fond du Lac": "https://www.fdlco.wi.gov/departments/departments-n-z/register-of-deeds",
    "Forest": "https://www.forestcountywi.gov/departments/register-of-deeds",
    "Grant": "https://www.co.grant.wi.gov/department/register-of-deeds",
    "Green": "https://www.greencountywi.org/195/Register-of-Deeds",
    "Green Lake": "https://www.co.green-lake.wi.us/departments/register-of-deeds",
    "Iowa": "https://www.iowacountywi.gov/departments/registerofdeeds/registerofdeeds.shtml",
    "Iron": "https://www.ironcountywi.gov/departments/register-of-deeds",
    "Jackson": "https://www.co.jackson.wi.us/index.asp?SEC=7B0A7E4A-4E4E-4E4E-8E4E-4E4E4E4E4E4E",
    "Jefferson": "https://www.jeffersoncountywi.gov/departments/register_of_deeds/index.php",
    "Juneau": "https://www.co.juneau.wi.gov/departments/register-of-deeds",
    "Kenosha": "https://www.kenoshacounty.org/169/Register-of-Deeds",
    "Kewaunee": "https://www.kewauneecounty.org/departments/register-of-deeds",
    "La Crosse": "https://www.lacrossecounty.org/departments/register-of-deeds",
    "Lafayette": "https://www.co.lafayette.wi.gov/departments/register-of-deeds",
    "Langlade": "https://www.co.langlade.wi.us/departments/register-of-deeds",
    "Lincoln": "https://www.co.lincoln.wi.us/departments/register-of-deeds",
    "Manitowoc": "https://manitowoccountywi.gov/departments/register-of-deeds",
    "Marathon": "https://www.marathoncounty.gov/services/online-records",
    "Marinette": "https://www.marinettecountywi.gov/departments/register_of_deeds",
    "Marquette": "https://webportal.co.marquette.wi.us/GCSWebPortal/Search.aspx",
    "Milwaukee": "https://county.milwaukee.gov/EN/Register-of-Deeds/Real-Estate-Records",
    "Monroe": "https://www.co.monroe.wi.us/departments/register-of-deeds",
    "Oconto": "https://www.co.oconto.wi.us/departments/register_of_deeds",
    "Oneida": "https://www.oneidacountywi.gov/departments/rd",
    "Outagamie": "https://www.outagamie.org/government/departments-a-e/development-and-land-services/gis-land-information",
    "Ozaukee": "https://www.ozaukeecounty.gov/165/Register-of-Deeds",
    "Pepin": "https://pepincountywi.gov/departments/register-of-deeds",
    "Pierce": "https://www.co.pierce.wi.us/departments/register_of_deeds/index.php",
    "Polk": "https://www.polkcountywi.gov/government/divisions_and_departments/environmental_services_division/land_information/land_resources_online.php",
    "Portage": "https://www.co.portage.wi.gov/department/register-of-deeds",
    "Price": "https://www.co.price.wi.us/151/Register-of-Deeds",
    "Racine": "https://www.racinecounty.com/departments/register-of-deeds",
    "Richland": "https://www.co.richland.wi.us/departments/registerofdeeds.shtml",
    "Rock": "https://www.co.rock.wi.us/departments/register-of-deeds/real-estate/online-search",
    "Rusk": "https://ruskcountywi.us/departments/register-of-deeds",
    "Sauk": "https://www.co.sauk.wi.us/registerofdeeds",
    "Sawyer": "https://www.sawyercountygov.org/164/Register-of-Deeds",
    "Shawano": "https://www.co.shawano.wi.us/departments/register_of_deeds",
    "Sheboygan": "https://www.sheboygancounty.com/departments/departments-r-z/register-of-deeds",
    "St. Croix": "https://www.sccwi.gov/177/Register-of-Deeds",
    "Taylor": "https://www.co.taylor.wi.us/departments/register-of-deeds",
    "Trempealeau": "https://tremplocounty.com/departments/register-of-deeds",
    "Vernon": "https://www.vernoncountywi.gov/departments/register_of_deeds/index.php",
    "Vilas": "https://www.vilascountywi.gov/departments/register_of_deeds/index.php",
    "Walworth": "https://www.co.walworth.wi.us/212/Register-of-Deeds",
    "Washburn": "https://www.co.washburn.wi.us/departments/register-of-deeds",
    "Washington": "https://www.washcowisco.gov/departments/register_of_deeds",
    "Waukesha": "https://www.waukeshacounty.gov/registerofdeeds",
    "Waupaca": "https://www.waupacacounty-wi.gov/departments/register_of_deeds.php",
    "Waushara": "https://www.co.waushara.wi.us/pView.aspx?id=12782&catid=636",
    "Winnebago": "https://www.winnebagocountywi.gov/491/Register-of-Deeds",
    "Wood": "https://www.woodcountywi.gov/departments/rod"
    # Note: This is now comprehensive; sourced from WRDA.
}

sewrpc_counties = ["Milwaukee", "Kenosha", "Ozaukee", "Walworth", "Waukesha", "Racine"]

# Function to map quarter codes (assumed standard PLSS: 1=NE, 2=NW, 3=SE, 4=SW)
quarter_map = {1: "NE", 2: "NW", 3: "SE", 4: "SW"}

# Streamlit app
st.title("Wisconsin Land Records & PLSS Finder")
st.write(
    "Enter a Wisconsin address to find the county's Register of Deeds portal, PLSS data (including quarter section), and links for CSSD.")

address = st.text_input("Enter address (e.g., 123 Main St, Greenfield, WI)")

if address:
    try:
        geolocator = Nominatim(user_agent="wi_land_records_app")
        location = geolocator.geocode(address + ", Wisconsin, USA", timeout=10)

if location:
    # Extract county safely
    county = None
    raw_address = location.raw.get('address', {})  # .get() returns {} if no 'address' key
    # Try common county keys (Nominatim varies: 'county', '_county', etc.)
    for key in ['county', 'state_county', 'county_name']:
        if key in raw_address:
            county = raw_address[key].replace(" County", "").strip()
            break

    # Fallback: parse from display_name if needed (less reliable but better than crash)
    if not county and 'display_name' in location.raw:
        parts = location.raw['display_name'].split(',')
        for part in parts:
            part = part.strip()
            if 'County' in part:
                county = part.replace(" County", "").strip()
                break

    if county:
        st.success(f"Address is in {county} County (Lat: {location.latitude:.6f}, Lon: {location.longitude:.6f}).")
        # ... rest of your portal lookup, PLSS query, etc.
    else:
        st.error("Could not extract county from geocoding result. Try a more specific address (include city/ZIP).")
        st.info("Raw place name: " + location.raw.get('display_name', 'N/A'))
else:
    st.error("Address not found. Try including city and ZIP code.")
                # Pull PLSS data
                try:
                    in_proj = pyproj.Proj(init='epsg:4326')
                    out_proj = pyproj.Proj(init='epsg:3071')
                    lon, lat = location.longitude, location.latitude
                    x, y = pyproj.transform(in_proj, out_proj, lon, lat)

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
                    response = requests.get(url, params=params).json()

                    if 'features' in response and response['features']:
                        attrs = response['features'][0]['attributes']
                        twn = attrs['PLSS_TWN_ID']
                        rng = attrs['PLSS_RNG_ID']
                        rng_dir = "E" if attrs['PLSS_RNG_DIR_NUM_CODE'] == 1 else "W"
                        sec = attrs['PLSS_SCTN_ID']
                        q1 = attrs['PLSS_Q1_SCTN_NUM_CODE']
                        q2 = attrs['PLSS_Q2_SCTN_NUM_CODE']
                        desc = attrs['PLSS_DESC']  # Fallback description

                        quarter = quarter_map.get(q1, str(q1))
                        qq = quarter_map.get(q2, str(q2))

                        st.subheader("PLSS Quarter Section Data")
                        st.write(f"Township: {twn}N")
                        st.write(f"Range: {rng}{rng_dir}")
                        st.write(f"Section: {sec}")
                        st.write(f"Quarter Section: {quarter}")
                        st.write(f"Quarter-Quarter Section: {qq} of the {quarter}")
                        if desc:
                            st.write(f"Full Description: {desc}")

                        # CSSD links
                        st.subheader("Access CSSD (Control Section Summary Diagram)")
                        scf_url = "https://maps.sco.wisc.edu/surveycontrolfinder/"
                        st.write(
                            f"Search by T{twn}N R{rng}{rng_dir} S{sec} at [Survey Control Finder]({scf_url}) for CSSD and dossier sheets.")

                        if county in sewrpc_counties:
                            sewrpc_url = "https://maps.sewrpc.org/plssapp/"
                            st.write(
                                f"For {county} County, also check [SEWRPC PLSS Document Search]({sewrpc_url}) using the same TRS.")
                    else:
                        st.error("No PLSS data found at this location.")
                except Exception as e:
                    st.error(f"Error fetching PLSS data: {e}")
            else:
                st.error("Could not determine county. Ensure the address is in Wisconsin.")
        else:
            st.error("Address not found. Try including city and ZIP code.")
    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error("Geocoding service timed out. Try again later.")

st.write(
    "Note: This app links to resources only—full data like CSSD may require manual search. For statewide parcels (with PLSS), see https://maps.sco.wisc.edu/Parcels. If you need automation for scraping portals or integrating more APIs, let me know!")
