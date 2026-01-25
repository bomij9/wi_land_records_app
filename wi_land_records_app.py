import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pyproj
import requests
import math
import pandas as pd
import io

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
    "Walworth": "https://www.co.walworth.wi.us/243/Real-Estate-Records",
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
        geolocator = Nominatim(
    user_agent="wisconsin-land-plss-finder-app (bodemichael9@gmail.com)",  
            # <-- Replace with YOUR real email/name
    timeout=30  
            # Increase from 10 to 30 seconds to allow more time for slow responses
)
        location = geolocator.geocode(address + ", Wisconsin, USA", addressdetails=1)

        if location:
            # Extract county safely (no KeyError)
            county = None
            raw_address = location.raw.get('address', {})
            for key in ['county', 'state_county', 'county_name']:
                if key in raw_address:
                    county = raw_address[key].replace(" County", "").strip()
                    break

            # Fallback to display_name parsing
            if not county and 'display_name' in location.raw:
                parts = location.raw['display_name'].split(',')
                for part in parts:
                    part = part.strip()
                    if 'County' in part:
                        county = part.replace(" County", "").strip()
                        break

            if county:
                st.success(f"Address is in {county} County (Lat: {location.latitude:.6f}, Lon: {location.longitude:.6f}).")

                # Portal link
                if county in county_portals:
                    portal_url = county_portals[county]
                    st.write(f"Access records here: [{county} County Register of Deeds]({portal_url})")
                    st.info("Search by address/parcel. Some require subscriptions.")
                else:
                    st.warning(f"No portal for {county} County. Check https://www.wrdaonline.org/counties or search online.")

                # PLSS data (in a nested try to isolate network issues)
                try:
                    in_proj = pyproj.Proj(init='epsg:4326')
                    out_proj = pyproj.Proj(init='epsg:3071')
                    x, y = pyproj.transform(in_proj, out_proj, location.longitude, location.latitude)

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
                    response = requests.get(url, params=params, timeout=15).json()

                    # Debug prints - add these
                    st.write("**Debug: Polygon Query WHERE clause:**", polygon_params['where'])
                    st.write("**Debug: Polygon response keys:**", list(poly_resp.keys()))
                    st.write("**Debug: Features count:**", len(poly_resp.get('features', [])))
                if 'features' in poly_resp and poly_resp['features']:
                    st.write("**Debug: First feature attributes:**", poly_resp['features'][0]['attributes'])
                    st.write("**Debug: Geometry present?**", 'geometry' in poly_resp['features'][0])
                elif 'error' in poly_resp:
                    st.error("ArcGIS error:", poly_resp['error'])
                else:
                    st.info("No features or unexpected response format.")

                    if 'features' in response and response['features']:
                        attrs = response['features'][0]['attributes']
                        twn = attrs.get('PLSS_TWN_ID', 'N/A')
                        rng = attrs.get('PLSS_RNG_ID', 'N/A')
                        rng_dir = "E" if attrs.get('PLSS_RNG_DIR_NUM_CODE') == 1 else "W"
                        sec = attrs.get('PLSS_SCTN_ID', 'N/A')
                        q1 = attrs.get('PLSS_Q1_SCTN_NUM_CODE')
                        q2 = attrs.get('PLSS_Q2_SCTN_NUM_CODE')
                        desc = attrs.get('PLSS_DESC', '')

                        quarter = quarter_map.get(q1, str(q1) if q1 else 'N/A')
                        qq = quarter_map.get(q2, str(q2) if q2 else 'N/A')

                        st.subheader("PLSS Quarter Section Data")
                        st.write(f"Township: {twn}N")
                        st.write(f"Range: {rng}{rng_dir}")
                        st.write(f"Section: {sec}")
                        st.write(f"Quarter Section: {quarter}")
                        st.write(f"Quarter-Quarter Section: {qq} of the {quarter}")
                        if desc:
                            st.write(f"Full Description: {desc}")

                        st.subheader("Access CSSD")
                        scf_url = "https://maps.sco.wisc.edu/surveycontrolfinder/"
                        st.write(f"Search T{twn}N R{rng}{rng_dir} S{sec} at [Survey Control Finder]({scf_url})")
                        if county in sewrpc_counties:
                            sewrpc_url = "https://gis.sewrpc.org/portal/apps/webappviewer/index.html?id=9b49d9d04b294b8c8d1b667c9996b8ac"
                            st.write(f"For {county} County, check [SEWRPC PLSS Docs]({sewrpc_url})")
                            
                        # ────────────────────────────────────────────────────────────────
                        # PNEZD Export: 4 Corners (Clockwise: 1=NE → 2=NW → 3=SW → 4=SE)
                        # ────────────────────────────────────────────────────────────────
                        try:
                            polygon_url = "https://dnrmaps.wi.gov/arcgis/rest/services/DW_Map_Dynamic/FR_PLSS_Landnet_WTM_Ext/MapServer/2/query"
                            
                            # Use numeric comparison (no quotes around numbers)
                            dir_code = attrs.get('PLSS_RNG_DIR_NUM_CODE', 1 if rng_dir == 'E' else 2)
                            
                            where_clause = (
                                f"PLSS_TWN_ID = {twn} "
                                f"AND PLSS_RNG_ID = {rng} "
                                f"AND PLSS_RNG_DIR_NUM_CODE = {dir_code} "
                                f"AND PLSS_SCTN_ID = {sec} "
                                f"AND PLSS_Q1_SCTN_NUM_CODE = {q1} "
                                f"AND PLSS_Q2_SCTN_NUM_CODE = {q2}"
                            )
                            
                            polygon_params = {
                                'f': 'json',
                                'where': where_clause,
                                'returnGeometry': 'true',
                                'outFields': '*',
                                'outSR': '3071'
                            }

                            poly_resp = requests.get(polygon_url, params=polygon_params, timeout=15).json()

                            # If we got features, process them
                            if 'features' in poly_resp and poly_resp['features']:
                                geom = poly_resp['features'][0]['geometry']
                                rings = geom.get('rings', [])

                                if rings:
                                    exterior = rings[0]
                                    points = [(coord[0], coord[1]) for coord in exterior]

                                    if len(points) > 1 and points[0] == points[-1]:
                                        points = points[:-1]

                                    if len(points) >= 4:
                                        cx = sum(x for x, y in points) / len(points)
                                        cy = sum(y for x, y in points) / len(points)

                                        def angle_key(p):
                                            return math.atan2(p[1] - cy, p[0] - cx)

                                        sorted_pts = sorted(points, key=angle_key, reverse=True)

                                        ne_pt = max(sorted_pts, key=lambda p: (p[1], p[0]))
                                        idx = sorted_pts.index(ne_pt)
                                        rotated = sorted_pts[idx:] + sorted_pts[:idx]

                                        corner_labels = ["NE", "NW", "SW", "SE"]

                                        pnezd_rows = []
                                        for i, (easting, northing) in enumerate(rotated[:4], start=1):
                                            label = corner_labels[i-1]
                                            desc = f"{label} corner (P={i}) of {quarter_map.get(q1, '?')}{quarter_map.get(q2, '?')} ¼ Sec {sec}, T{twn}N R{rng}{rng_dir} | Addr: {address} | Co: {county} | Z=0"
                                            row = {
                                                "P": i,
                                                "N": round(northing, 3),
                                                "E": round(easting, 3),
                                                "Z": 0.000,
                                                "D": desc
                                            }
                                            pnezd_rows.append(row)

                                        df = pd.DataFrame(pnezd_rows)
                                        csv_buffer = io.StringIO()
                                        df.to_csv(csv_buffer, index=False, header=True)
                                        csv_str = csv_buffer.getvalue()

                                        st.download_button(
                                            label="Download PNEZD Corners (1=NE → 4=SE)",
                                            data=csv_str,
                                            file_name=f"pnezd_{address.replace(' ', '_')[:20]}.csv",
                                            mime="text/csv"
                                        )
                                    else:
                                        st.info("Polygon has fewer than 4 points.")
                                else:
                                    st.info("No polygon rings found.")
                            else:
                                st.info("No matching quarter-quarter polygon found.")
            except Exception as e:
                st.error(f"Polygon query / corner export failed: {str(e)}")
# Footer note
st.write("Note: Links to public resources only. Full records/CSMs/CSSD may require manual search or subscriptions.")
