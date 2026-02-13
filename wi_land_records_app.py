import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pyproj
import requests
import math
import pandas as pd
import io

# Dictionary of Wisconsin counties to their Register of Deeds portals
county_portals = {
    "Adams": "https://www.co.adams.wi.us/departments/register-of-deeds",
    "Ashland": "https://www.co.ashland.wi.us/departments/register-of-deeds",
    # ... (your full dictionary here – I've kept it abbreviated for brevity)
    "Wood": "https://www.woodcountywi.gov/departments/rod"
    # Add all others as in your original
}

sewrpc_counties = ["Milwaukee", "Kenosha", "Ozaukee", "Walworth", "Waukesha", "Racine"]

# Standard PLSS quarter codes → directions (common convention; confirm with sample response if needed)
quarter_map = {1: "NE", 2: "NW", 3: "SE", 4: "SW"}

st.title("Wisconsin Land Records & PLSS Finder")
st.write(
    "Enter a Wisconsin address to find the county's Register of Deeds portal, "
    "PLSS data (including quarter section), and links for CSSD/Survey Control."
)

address = st.text_input("Enter address (e.g., 123 Main St, Greenfield, WI)")

if address:
    try:
        geolocator = Nominatim(
            user_agent="wisconsin-land-plss-finder-app (bodemichael9@gmail.com)",
            timeout=30
        )
        location = geolocator.geocode(address + ", Wisconsin, USA", addressdetails=True)

        if not location:
            st.error("Could not geocode the address. Try adding more details (city, ZIP).")
            st.stop()

        # Extract county name safely
        county = None
        raw_addr = location.raw.get('address', {})
        for key in ['county', 'state_county', 'county_name']:
            if key in raw_addr:
                county = raw_addr[key].replace(" County", "").strip()
                break

        if not county and 'display_name' in location.raw:
            parts = location.raw['display_name'].split(',')
            for part in parts:
                part = part.strip()
                if 'County' in part:
                    county = part.replace(" County", "").strip()
                    break

        if not county:
            st.warning("Could not determine county from geocoded result.")
        else:
            st.success(f"Located in **{county} County** (Lat: {location.latitude:.6f}, Lon: {location.longitude:.6f})")

            # Show Register of Deeds portal
            if county in county_portals:
                portal_url = county_portals[county]
                st.markdown(f"**{county} County Register of Deeds:** [{portal_url}]({portal_url})")
                st.info("Search by address or parcel ID. Some sites may require payment/subscription.")
            else:
                st.warning(f"No portal listed for {county} County. Try https://www.wrdaonline.org/counties or Google search.")

            # ────────────────────────────────────────────────
            # PLSS Point Query (find section/quarter at point)
            # ────────────────────────────────────────────────
            plss_data = None
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

                resp = requests.get(url, params=params, timeout=15)
                resp.raise_for_status()
                poly_resp = resp.json()

                # Optional debug (comment out in production)
                # st.write("**Debug: Response keys**", list(poly_resp.keys()))
                # st.write("**Debug: Features count**", len(poly_resp.get('features', [])))

                if 'features' in poly_resp and poly_resp['features']:
                    plss_data = poly_resp['features'][0]['attributes']
                    # st.write("**Debug: Attributes**", plss_data)  # uncomment for dev

            except requests.exceptions.Timeout:
                st.warning("PLSS query timed out. Try again later.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network issue with PLSS service: {e}")
            except Exception as e:
                st.error(f"Error processing PLSS point query: {e}")

            # ────────────────────────────────────────────────
            # Display PLSS info if we have it
            # ────────────────────────────────────────────────
            if plss_data:
                twn = plss_data.get('PLSS_TWN_ID', 'N/A')
                rng = plss_data.get('PLSS_RNG_ID', 'N/A')
                rng_dir_code = plss_data.get('PLSS_RNG_DIR_NUM_CODE', 1)  # assume 1=E, 2=W
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
                st.write(f"**Quarter Section:** {quarter}")
                st.write(f"**Quarter-Quarter:** {qq} of the {quarter}")
                if desc:
                    st.write(f"**Full Description:** {desc}")

                st.subheader("Related Resources")
                scf_url = "https://maps.sco.wisc.edu/surveycontrolfinder/"
                st.markdown(f"Search T{twn}N R{rng}{rng_dir} S{sec} at [Survey Control Finder]({scf_url})")

                if county in sewrpc_counties:
                    sewrpc_url = "https://gis.sewrpc.org/portal/apps/webappviewer/index.html?id=9b49d9d04b294b8c8d1b667c9996b8ac"
                    st.markdown(f"For **{county} County**, view [SEWRPC PLSS Documents]({sewrpc_url})")

                # ────────────────────────────────────────────────
                # PNEZD Export: Get full quarter-quarter polygon → sort corners clockwise from NE
                # ────────────────────────────────────────────────
                try:
                    poly_params = {
                        'f': 'json',
                        'where': (
                            f"PLSS_TWN_ID = {twn} AND "
                            f"PLSS_RNG_ID = {rng} AND "
                            f"PLSS_RNG_DIR_NUM_CODE = {rng_dir_code} AND "
                            f"PLSS_SCTN_ID = {sec} AND "
                            f"PLSS_Q1_SCTN_NUM_CODE = {q1} AND "
                            f"PLSS_Q2_SCTN_NUM_CODE = {q2}"
                        ),
                        'returnGeometry': 'true',
                        'outFields': '*',
                        'outSR': '3071'
                    }

                    poly_resp = requests.get(url, params=poly_params, timeout=15).json()

                    if 'features' in poly_resp and poly_resp['features']:
                        geom = poly_resp['features'][0]['geometry']
                        rings = geom.get('rings', [])
                        if rings and len(rings[0]) >= 4:
                            exterior = rings[0]
                            points = [(coord[0], coord[1]) for coord in exterior if coord != exterior[-1]]  # close ring fix

                            if len(points) >= 4:
                                # Centroid for polar sort
                                cx = sum(x for x, y in points) / len(points)
                                cy = sum(y for x, y in points) / len(points)

                                def angle_key(p):
                                    return math.atan2(p[1] - cy, p[0] - cx)

                                sorted_pts = sorted(points, key=angle_key, reverse=True)  # clockwise

                                # Rotate so NE (highest y, then highest x) is first
                                ne_pt = max(sorted_pts, key=lambda p: (p[1], p[0]))
                                idx = sorted_pts.index(ne_pt)
                                rotated = sorted_pts[idx:] + sorted_pts[:idx]

                                corner_labels = ["NE", "NW", "SW", "SE"]
                                pnezd_rows = []
                                for i, (easting, northing) in enumerate(rotated[:4], start=1):
                                    label = corner_labels[i-1]
                                    desc = (
                                        f"{label} corner (P={i}) of {qq}{quarter} ¼ Sec {sec}, "
                                        f"T{twn}N R{rng}{rng_dir} | Addr: {address} | Co: {county} | Z=0"
                                    )
                                    pnezd_rows.append({
                                        "P": i,
                                        "N": round(northing, 3),
                                        "E": round(easting, 3),
                                        "Z": 0.000,
                                        "D": desc
                                    })

                                df = pd.DataFrame(pnezd_rows)
                                csv_buffer = io.StringIO()
                                df.to_csv(csv_buffer, index=False)
                                st.download_button(
                                    label="Download PNEZD CSV (1=NE → 4=SE clockwise)",
                                    data=csv_buffer.getvalue(),
                                    file_name=f"pnezd_{address.replace(' ', '_')[:20]}.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.info("Polygon has fewer than 4 valid points.")
                        else:
                            st.info("No usable polygon rings returned.")
                    else:
                        st.info("No matching quarter-quarter section polygon found for export.")

                except Exception as poly_e:
                    st.error(f"Failed to fetch/export polygon corners: {poly_e}")

            else:
                st.info("No PLSS quarter-quarter data found at this location (may be outside surveyed area or service issue).")

    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error("Geocoding service timed out or unavailable. Try again or check your internet.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

st.caption("Note: This app uses public APIs and links only. Official records may require manual search or fees. PLSS data for reference — not legal survey.")
