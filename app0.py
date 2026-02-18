import warnings
import logging
warnings.filterwarnings('ignore')
logging.getLogger('streamlit').setLevel(logging.ERROR)

import streamlit as st
import ee
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from branca.element import MacroElement
from jinja2 import Template

# Import legal mining sites database
from legal_mining_sites import LEGAL_MINING_AREAS


# ---------------------------------------------------------------------------
# DEFINITIVE FIX for folium >= 0.18 + streamlit-folium JSON serialization crash.
#
# Root cause: In folium >= 0.18, BOTH the base map tiles (tiles='OpenStreetMap')
# AND TileLayer objects store internal TileProvider/callable objects that cannot
# be JSON-serialized by streamlit-folium's st_folium().
#
# Solution: Use folium.Map(tiles=None) and inject ALL tile layers + LayerControl
# as a single MacroElement containing pure JavaScript. The MacroElement template
# outputs only strings — never Python callables — so serialization always works.
# ---------------------------------------------------------------------------

class AllTilesElement(MacroElement):
    """
    Injects ALL map tile layers and a Leaflet LayerControl as raw JavaScript.
    This completely bypasses folium's TileLayer / LayerControl serialization,
    which breaks in folium >= 0.18 with streamlit-folium.

    Parameters
    ----------
    true_color_url   : GEE tile URL string for True Color layer
    mineral_url      : GEE tile URL string for active mineral heatmap
    mineral_label    : Display name for the mineral heatmap layer
    false_color_url  : GEE tile URL string for False Color layer
    mineral_opacity  : Opacity for the mineral heatmap (default 0.7)
    """
    def __init__(self, true_color_url, mineral_url, mineral_label,
                 false_color_url, mineral_opacity=0.7):
        super().__init__()
        self._name = 'AllTilesElement'
        self.true_color_url   = true_color_url
        self.mineral_url      = mineral_url
        self.mineral_label    = mineral_label
        self.false_color_url  = false_color_url
        self.mineral_opacity  = mineral_opacity

        self._template = Template(u"""
{% macro script(this, kwargs) %}
// ── Base tile layers ─────────────────────────────────────────────────────────
var osmLayer = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {maxZoom: 19, attribution: "© OpenStreetMap contributors"}
);
var gSatLayer = L.tileLayer(
    "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    {maxZoom: 22, attribution: "Google Maps"}
);
var gHybridLayer = L.tileLayer(
    "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    {maxZoom: 22, attribution: "Google Maps"}
);

// ── GEE overlay layers ───────────────────────────────────────────────────────
var trueColorLayer = L.tileLayer(
    "{{ this.true_color_url }}",
    {opacity: 1.0, attribution: "ESA Sentinel-2 / Google Earth Engine"}
);
var mineralLayer = L.tileLayer(
    "{{ this.mineral_url }}",
    {opacity: {{ this.mineral_opacity }}, attribution: "ESA Sentinel-2 / Google Earth Engine"}
);
var falseColorLayer = L.tileLayer(
    "{{ this.false_color_url }}",
    {opacity: 1.0, attribution: "ESA Sentinel-2 / Google Earth Engine"}
);

// ── Add default visible layers ───────────────────────────────────────────────
osmLayer.addTo({{ this._parent.get_name() }});
trueColorLayer.addTo({{ this._parent.get_name() }});
mineralLayer.addTo({{ this._parent.get_name() }});

// ── Layer Control ─────────────────────────────────────────────────────────────
var baseLayers = {
    "OpenStreetMap": osmLayer,
    "Google Satellite": gSatLayer,
    "Google Hybrid": gHybridLayer
};
var overlayLayers = {
    "📷 True Color (Sentinel-2)": trueColorLayer,
    "{{ this.mineral_label }}": mineralLayer,
    "🌿 False Color NIR": falseColorLayer
};
L.control.layers(baseLayers, overlayLayers, {collapsed: false}).addTo(
    {{ this._parent.get_name() }}
);
{% endmacro %}
""")



# --- CONFIGURATION ---
MY_PROJECT_ID = "spectramining"
geolocator = Nominatim(user_agent="spectramining_ai_pro_v6")

def get_nearby_places(lat, lon, radius_km=5):
    """
    Get nearby points of interest (Google Maps style)
    """
    try:
        query = f"{lat},{lon}"
        results = geolocator.reverse(query, exactly_one=False, language='en', addressdetails=True)
        
        nearby_places = []
        if results:
            for result in results[:10]:
                if hasattr(result, 'raw') and 'address' in result.raw:
                    address = result.raw['address']
                    place_name = None
                    place_type = None
                    
                    if 'mall' in address or 'shopping' in address.get('amenity', '').lower():
                        place_name = address.get('mall', address.get('shop', address.get('amenity')))
                        place_type = "Shopping"
                    elif 'school' in address or 'college' in address or 'university' in address:
                        place_name = address.get('school', address.get('college', address.get('university')))
                        place_type = "Education"
                    elif 'hospital' in address or 'clinic' in address:
                        place_name = address.get('hospital', address.get('clinic'))
                        place_type = "Healthcare"
                    elif 'hotel' in address or 'restaurant' in address:
                        place_name = address.get('hotel', address.get('restaurant'))
                        place_type = "Hospitality"
                    elif 'building' in address:
                        place_name = address.get('building')
                        place_type = "Landmark"
                    
                    if place_name and place_name not in [p['name'] for p in nearby_places]:
                        nearby_places.append({
                            'name': place_name,
                            'type': place_type,
                            'lat': result.latitude,
                            'lon': result.longitude
                        })
        
        return nearby_places[:5]
    except:
        return []


def get_mineral_index_at_point(mineral_index_ee, lat, lon, mineral_name='iron'):
    """
    Get mineral index value at a specific point
    """
    try:
        point = ee.Geometry.Point([lon, lat])
        sample = mineral_index_ee.sample(region=point, scale=10, geometries=True).first()
        if sample:
            mineral_value = sample.get(f'{mineral_name}_index').getInfo()
            return mineral_value
        return None
    except:
        return None


def classify_location(lat, lon, mineral_coverage, mineral_name='iron'):
    """
    AI Classification based on proximity to legal mining areas and mineral detection.
    
    Returns
    -------
    classification      : str   — human-readable label
    classification_type : str   — one of 'mining', 'high_potential', 'moderate_potential', 'low_potential'
    nearby_mines        : list  — mines within 15 km that match the mineral type
    nearest_distance    : float — km to nearest matching mine (None if no matching mines at all)
    nearest_mine        : str   — name of nearest matching mine (None if no matching mines at all)
    """
    search_point = (lat, lon)
    nearby_mines = []
    min_distance = float('inf')
    nearest_mine = None

    mineral_type_map = {
        'iron':      ['Iron Ore', 'Metallic'],
        'aluminum':  ['Bauxite', 'Aluminum', 'Metallic'],
        'copper':    ['Copper', 'Metallic', 'Polymetallic'],
        'limestone': ['Limestone'],
        'manganese': ['Manganese'],
    }
    target_types = mineral_type_map.get(mineral_name, ['Iron Ore'])

    for mine_name, (mine_lat, mine_lon, country, mine_type) in LEGAL_MINING_AREAS.items():
        is_match = any(t.lower() in mine_type.lower() for t in target_types)
        if not is_match:
            continue

        mine_point = (mine_lat, mine_lon)
        distance = geodesic(search_point, mine_point).kilometers

        if distance <= 15:
            nearby_mines.append({
                'name':     mine_name,
                'distance': distance,
                'country':  country,
                'type':     mine_type
            })

        # Track nearest matching mine, but only show it when meaningfully close (< 200 km)
        if distance < min_distance:
            min_distance = distance
            nearest_mine = mine_name

    # If nearest matching mine is too far to be relevant, suppress it
    if min_distance > 200:
        nearest_mine = None
        nearest_distance = None
    else:
        nearest_distance = round(min_distance, 2)

    if nearby_mines:
        classification      = "Legal Mining Area"
        classification_type = "mining"
    else:
        mineral_display = mineral_name.capitalize()
        # Coverage thresholds calibrated per-mineral:
        # iron  : Red/Blue ratio readily saturates → use tighter bands
        # al/cu : indices noisier → slightly more lenient
        thresholds = {
            'iron':      (15.0, 5.0, 1.0),
            'aluminum':  (12.0, 3.0, 0.5),
            'copper':    (10.0, 2.0, 0.3),
            'limestone': (20.0, 8.0, 2.0),
            'manganese': (8.0,  2.5, 0.5),
        }
        high_t, mod_t, _ = thresholds.get(mineral_name, (15.0, 5.0, 1.0))

        if mineral_coverage >= high_t:
            classification      = f"High Potential {mineral_display} Deposits"
            classification_type = "high_potential"
        elif mineral_coverage >= mod_t:
            classification      = f"Moderate Potential {mineral_display} Deposits"
            classification_type = "moderate_potential"
        elif mineral_coverage >= 0.3:
            classification      = f"Low {mineral_display} Signature Detected"
            classification_type = "low_potential"
        else:
            classification      = f"No Significant {mineral_display} Signature"
            classification_type = "low_potential"

    return classification, classification_type, nearby_mines, nearest_distance, nearest_mine


@st.cache_resource
def init_gee():
    try:
        ee.Initialize(project=MY_PROJECT_ID)
        return True
    except Exception as e:
        st.error(f"⚠️ Earth Engine Initialization Failed: {e}")
        return False


# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'trigger_scan' not in st.session_state:
    st.session_state.trigger_scan = False
if 'selected_mineral' not in st.session_state:
    st.session_state.selected_mineral = 'iron'

# --- PAGE CONFIG ---
st.set_page_config(
    layout="wide",
    page_title="SpectraMining AI",
    page_icon="🛰️",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
# FIX 3: Heading CSS — use a more specific selector so the gradient is not
#         overridden by the broad `h1 { color: #FFE66D !important }` rule.
#         Adding `!important` to the background properties and using both
#         prefixed and unprefixed background-clip ensures gradient text renders.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    /* Sidebar Toggle Button */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%) !important;
        border-radius: 0 10px 10px 0 !important;
        color: white !important;
        padding: 10px !important;
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    /* Fix header visibility */
    header[data-testid="stHeader"] {
        visibility: hidden;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b3d 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 2px solid rgba(230, 57, 70, 0.3);
        box-shadow: 0 8px 32px rgba(230, 57, 70, 0.2);
    }

    /* FIX 3: More specific selector beats the broad h1 rule below.
       Also adding both webkit and standard background-clip for max compat. */
    .main-header .main-title {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 50%, #FFE66D 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        margin: 0 !important;
        letter-spacing: 2px !important;
        display: inline-block !important;
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        color: #A8DADC;
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 1px;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #2d1b3d 100%);
        border-right: 2px solid rgba(230, 57, 70, 0.3);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFE66D !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(230, 57, 70, 0.3) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        padding: 0.75rem !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%) !important;
        color: white !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 0.8rem 2rem !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(230, 57, 70, 0.4);
        transition: all 0.3s ease;
        letter-spacing: 2px;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(230, 57, 70, 0.6);
    }
    
    [data-testid="stMetric"] {
        background: rgba(230, 57, 70, 0.1);
        padding: 1rem;
        border-radius: 15px;
        border: 2px solid rgba(230, 57, 70, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stMetric"] label {
        color: #A8DADC !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.9rem !important;
        font-weight: 600;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFE66D !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #E63946 0%, #FF6B6B 50%, #FFE66D 100%);
        border-radius: 10px;
    }
    
    /* Keep generic h1/h2/h3 for sidebar and other sections */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #FFE66D !important;
    }
    
    .stats-card {
        background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid rgba(230, 57, 70, 0.3);
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .stats-title {
        font-family: 'Orbitron', sans-serif;
        color: #FFE66D;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    iframe {
        display: block;
        margin: 0;
        padding: 0;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛰️ SPECTRAMINING AI</h1>
    <p class="subtitle">Advanced Satellite-Based Multi-Mineral Detection & Geological Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.8rem 0; background: linear-gradient(135deg, rgba(230, 57, 70, 0.15) 0%, rgba(69, 123, 157, 0.15) 100%); border-radius: 12px; margin-bottom: 1rem; border: 2px solid rgba(230, 57, 70, 0.3);">
        <div style="font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 900; background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🛰️ CONTROL PANEL
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Location Search
    st.markdown("#### 📍 Location")
    search_query = st.text_input(
        "Search Site or Region",
        value="Bailadila, India",
        placeholder="e.g., Chuquicamata, Chile",
        help="Enter mine name, city, or coordinates",
        label_visibility="visible"
    )
    
    if 'last_search_query' not in st.session_state:
        st.session_state.last_search_query = ""
    
    # New Analysis button - RIGHT AFTER search, before divider
    if st.session_state.analysis_complete:
        if st.button("🔄 New Analysis", use_container_width=True, key="new_analysis"):
            if search_query != st.session_state.last_search_query:
                st.session_state.analysis_complete = False
                st.session_state.results = None
                st.session_state.trigger_scan = True
                st.rerun()
            else:
                st.warning("⚠️ Enter a new location first")
    
    st.markdown("---")
    
    # MINERAL SELECTOR — 5 clean text buttons, no emojis
    st.markdown("#### 🧪 Active Mineral")

    _MINERALS = [
        ('iron',      'Fe · Iron'),
        ('aluminum',  'Al · Aluminum'),
        ('copper',    'Cu · Copper'),
        ('limestone', 'Ls · Limestone'),
        ('manganese', 'Mn · Manganese'),
    ]
    for key, label in _MINERALS:
        is_active = st.session_state.selected_mineral == key
        if st.button(label, use_container_width=True,
                     type="primary" if is_active else "secondary",
                     key=f"btn_{key}"):
            if not is_active:
                st.session_state.selected_mineral = key
                if st.session_state.analysis_complete:
                    st.rerun()

    mineral_names = {
        'iron':      'Iron (Fe)',
        'aluminum':  'Aluminum (Al)',
        'copper':    'Copper (Cu)',
        'limestone': 'Limestone (Ls)',
        'manganese': 'Manganese (Mn)',
    }
    st.info(f"**Active:** {mineral_names[st.session_state.selected_mineral]}")

    selected_mineral_key = st.session_state.selected_mineral

    # Fixed High-sensitivity thresholds — no slider needed
    FIXED_THRESHOLDS = {
        'iron': 1.3, 'aluminum': 1.2, 'copper': 1.5,
        'limestone': 1.2, 'manganese': 0.5,
    }
    mineral_threshold = FIXED_THRESHOLDS[selected_mineral_key]
    st.caption(f"⚙️ Sensitivity: **High** · Threshold: **{mineral_threshold}** · Radius: **10 km**")
    
    st.markdown("---")
    
    # Time Range Selection
    st.markdown("#### 📅 Imagery Period")
    date_range = st.selectbox(
        "Time Range",
        ["Last Year", "Last 2 Years", "Last 3 Years", "All Available (2020+)"],
        index=2,
        help="Longer periods = more cloud-free images",
        label_visibility="collapsed"
    )
    
    date_map = {
        "Last Year": "2025-02-15",
        "Last 2 Years": "2024-02-15",
        "Last 3 Years": "2023-02-15",
        "All Available (2020+)": "2020-01-01"
    }
    start_date = date_map[date_range]
    
    # Fixed cloud threshold (NO SLIDER)
    cloud_threshold = 40
    st.caption("☁️ **Cloud Filter:** Fixed at < 40% (Optimal Quality)")
    
    st.markdown("---")
    
    if st.session_state.analysis_complete:
        st.success("✅ **Analysis Ready**")
        st.caption("Adjust settings for real-time updates")
    
    st.markdown("---")
    
    mineral_display = mineral_names[selected_mineral_key]
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%); padding: 1rem; border-radius: 12px; border: 2px solid rgba(230, 57, 70, 0.3);">
        <div style="font-family: 'Orbitron', sans-serif; color: #FFE66D; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem;">⚡ SYSTEM</div>
        <div style="color: #4CAF50; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem;">● ONLINE</div>
        <div style="color: #A8DADC; font-size: 0.75rem; line-height: 1.4;">
            <b>Satellite:</b> Sentinel-2 SR<br>
            <b>Engine:</b> Google Earth<br>
            <b>Active:</b> {mineral_display}<br>
            <b>Project:</b> {MY_PROJECT_ID}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN APPLICATION ---
scan_button = st.button("🚀 INITIATE SCAN", use_container_width=True, disabled=st.session_state.analysis_complete)

should_scan = (scan_button or st.session_state.trigger_scan) and not st.session_state.analysis_complete

if should_scan:
    
    st.session_state.trigger_scan = False
    
    if not init_gee():
        st.stop()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.markdown("**📍 Geocoding location...**")
        progress_bar.progress(10)
        
        location = geolocator.geocode(search_query)
        if not location:
            st.error(f"❌ Location not found: '{search_query}'")
            st.stop()
        
        st.session_state.last_search_query = search_query
        
        st.success(f"✓ Location Found: **{location.address}**")
        progress_bar.progress(20)
        
        status_text.markdown("**🌍 Defining analysis region...**")
        poi = ee.Geometry.Point([location.longitude, location.latitude])
        region = poi.buffer(10000).bounds()
        progress_bar.progress(30)
        
        status_text.markdown("**🛰️ Fetching Sentinel-2 SR Harmonized imagery...**")
        
        s2_col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterBounds(region)
                  .filterDate(start_date, '2026-02-15')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
                  .sort('CLOUDY_PIXEL_PERCENTAGE'))
        
        num_images = s2_col.size().getInfo()
        
        if num_images == 0:
            st.error(f"⚠️ No imagery found with <{cloud_threshold}% clouds.")
            st.warning("Try expanding time range to 'All Available (2020+)'")
            st.stop()
        
        st.info(f"📡 Retrieved **{num_images}** Sentinel-2 SR images")
        progress_bar.progress(50)
        
        s2_img = s2_col.median().divide(10000).clip(region)
        
        status_text.markdown("**🧪 Computing multi-mineral spectral signatures...**")
        progress_bar.progress(60)
        
        status_text.markdown("**🧪 Computing spectral indices...**")
        progress_bar.progress(60)

        # Build all 5 spectral indices (pure EE graph — no network yet)
        red_band   = s2_img.select('B4')
        blue_band  = s2_img.select('B2')
        green_band = s2_img.select('B3')
        nir_band   = s2_img.select('B8')
        swir1_band = s2_img.select('B11')
        swir2_band = s2_img.select('B12')

        iron_index      = red_band.divide(blue_band).rename('iron_index')
        aluminum_index  = swir1_band.divide(swir2_band).rename('aluminum_index')
        copper_index    = red_band.divide(green_band).multiply(
                              nir_band.divide(red_band)).rename('copper_index')
        limestone_index = swir1_band.divide(swir2_band.add(1e-6)).rename('limestone_index')
        manganese_index = red_band.divide(swir1_band.add(1e-6)).rename('manganese_index')

        # Fixed High-sensitivity thresholds
        iron_threshold_value      = 1.3
        aluminum_threshold_value  = 1.2
        copper_threshold_value    = 1.5
        limestone_threshold_value = 1.2
        manganese_threshold_value = 0.5

        # ── BATCH 1: stats for all 5 minerals in ONE getInfo() ───────────────
        # Previously 5 separate round-trips; now a single call → ~5× faster.
        status_text.markdown("**📊 Fetching statistics (batched)...**")
        all_indices = ee.Image.cat([
            iron_index, aluminum_index, copper_index,
            limestone_index, manganese_index
        ])
        raw_stats = all_indices.reduceRegion(
            reducer=(ee.Reducer.percentile([10, 90])
                     .combine(ee.Reducer.mean(), '', True)),
            geometry=region,
            scale=60,        # 60 m: 4× fewer pixels than 30 m, negligible loss
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()

        def _s(name, key):
            return raw_stats.get(f'{name}_index_{key}', None)

        iron_stats      = {'iron_index_p10':      _s('iron','p10'),      'iron_index_p90':      _s('iron','p90')}
        aluminum_stats  = {'aluminum_index_p10':  _s('aluminum','p10'),  'aluminum_index_p90':  _s('aluminum','p90')}
        copper_stats    = {'copper_index_p10':     _s('copper','p10'),    'copper_index_p90':    _s('copper','p90')}
        limestone_stats = {'limestone_index_p10':  _s('limestone','p10'), 'limestone_index_p90': _s('limestone','p90')}
        manganese_stats = {'manganese_index_p10':  _s('manganese','p10'), 'manganese_index_p90': _s('manganese','p90')}

        progress_bar.progress(70)

        # ── BATCH 2: coverage for all 5 minerals in ONE getInfo() ────────────
        status_text.markdown("**🗺️ Computing coverage (batched)...**")
        cov_img = ee.Image.cat([
            iron_index.gt(iron_threshold_value).rename('iron_cov'),
            aluminum_index.gt(aluminum_threshold_value).rename('aluminum_cov'),
            copper_index.gt(copper_threshold_value).rename('copper_cov'),
            limestone_index.gt(limestone_threshold_value).rename('limestone_cov'),
            manganese_index.gt(manganese_threshold_value).rename('manganese_cov'),
        ])
        cov = cov_img.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=60,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()

        iron_coverage      = (cov.get('iron_cov',      0) or 0) * 100
        aluminum_coverage  = (cov.get('aluminum_cov',  0) or 0) * 100
        copper_coverage    = (cov.get('copper_cov',    0) or 0) * 100
        limestone_coverage = (cov.get('limestone_cov', 0) or 0) * 100
        manganese_coverage = (cov.get('manganese_cov', 0) or 0) * 100
        
        progress_bar.progress(80)
        status_text.markdown("**🗺️ Generating map tiles...**")

        def _rng(stats, key, thr, lo_cap, hi_cap):
            p10 = stats.get(f'{key}_index_p10') or thr
            p90 = stats.get(f'{key}_index_p90') or hi_cap
            return max(thr, p10), min(p90, hi_cap)

        iron_min,      iron_max      = _rng(iron_stats,      'iron',      iron_threshold_value,      iron_threshold_value,      3.5)
        aluminum_min,  aluminum_max  = _rng(aluminum_stats,  'aluminum',  aluminum_threshold_value,  aluminum_threshold_value,  2.5)
        copper_min,    copper_max    = _rng(copper_stats,     'copper',    copper_threshold_value,    copper_threshold_value,    3.0)
        limestone_min, limestone_max = _rng(limestone_stats,  'limestone', limestone_threshold_value, limestone_threshold_value, 3.0)
        manganese_min, manganese_max = _rng(manganese_stats,  'manganese', manganese_threshold_value, manganese_threshold_value, 1.5)

        true_color_tile  = s2_img.getMapId({'bands': ['B4','B3','B2'], 'min': 0.0, 'max': 0.3, 'gamma': 1.3})
        false_color_tile = s2_img.getMapId({'bands': ['B8','B4','B3'], 'min': 0.0, 'max': 0.4, 'gamma': 1.2})

        iron_tile = iron_index.updateMask(
            iron_index.gt(iron_threshold_value)).getMapId(
            {'min': iron_min, 'max': iron_max,
             'palette': ['#FFA500','#FF6347','#FF4500','#DC143C','#8B0000','#4A0000']})

        aluminum_tile = aluminum_index.updateMask(
            aluminum_index.gt(aluminum_threshold_value)).getMapId(
            {'min': aluminum_min, 'max': aluminum_max,
             'palette': ['#E0F7FA','#4DD0E1','#00BCD4','#0097A7','#00838F','#006064']})

        copper_tile = copper_index.updateMask(
            copper_index.gt(copper_threshold_value)).getMapId(
            {'min': copper_min, 'max': copper_max,
             'palette': ['#FFEB3B','#FFC107','#FF9800','#FF5722','#8D6E63','#5D4037']})

        limestone_tile = limestone_index.updateMask(
            limestone_index.gt(limestone_threshold_value)).getMapId(
            {'min': limestone_min, 'max': limestone_max,
             'palette': ['#F5F5DC','#E8DCC8','#D4C5A9','#C0AA87','#A08060','#705030']})

        manganese_tile = manganese_index.updateMask(
            manganese_index.gt(manganese_threshold_value)).getMapId(
            {'min': manganese_min, 'max': manganese_max,
             'palette': ['#E8C880','#C89040','#985010','#6B2D00','#3D1500','#1A0500']})
        
        progress_bar.progress(90)
        
        # Store EE objects in session state for point queries
        st.session_state.iron_index_ee      = iron_index
        st.session_state.aluminum_index_ee  = aluminum_index
        st.session_state.copper_index_ee    = copper_index
        st.session_state.limestone_index_ee = limestone_index
        st.session_state.manganese_index_ee = manganese_index
        st.session_state.s2_img_ee          = s2_img

        # AI Classification for the currently selected mineral
        mineral_coverage_for_classification = {
            'iron':      iron_coverage,
            'aluminum':  aluminum_coverage,
            'copper':    copper_coverage,
            'limestone': limestone_coverage,
            'manganese': manganese_coverage,
        }[selected_mineral_key]

        classification, class_type, nearby_mines, nearest_distance, nearest_mine = classify_location(
            location.latitude,
            location.longitude,
            mineral_coverage_for_classification,
            selected_mineral_key
        )

        # Store results — tile URLs stored as strings (url_format), NOT raw dicts
        st.session_state.results = {
            'location':   location,
            'num_images': num_images,
            # coverages
            'iron_coverage':       iron_coverage,
            'aluminum_coverage':   aluminum_coverage,
            'copper_coverage':     copper_coverage,
            'limestone_coverage':  limestone_coverage,
            'manganese_coverage':  manganese_coverage,
            # stats
            'iron_stats':      iron_stats,
            'aluminum_stats':  aluminum_stats,
            'copper_stats':    copper_stats,
            'limestone_stats': limestone_stats,
            'manganese_stats': manganese_stats,
            # thresholds
            'iron_threshold':      iron_threshold_value,
            'aluminum_threshold':  aluminum_threshold_value,
            'copper_threshold':    copper_threshold_value,
            'limestone_threshold': limestone_threshold_value,
            'manganese_threshold': manganese_threshold_value,
            # tile URLs
            'true_color_tile':  true_color_tile['tile_fetcher'].url_format,
            'false_color_tile': false_color_tile['tile_fetcher'].url_format,
            'iron_tile':        iron_tile['tile_fetcher'].url_format,
            'aluminum_tile':    aluminum_tile['tile_fetcher'].url_format,
            'copper_tile':      copper_tile['tile_fetcher'].url_format,
            'limestone_tile':   limestone_tile['tile_fetcher'].url_format,
            'manganese_tile':   manganese_tile['tile_fetcher'].url_format,
            # viz ranges
            'iron_min': iron_min,           'iron_max': iron_max,
            'aluminum_min': aluminum_min,   'aluminum_max': aluminum_max,
            'copper_min': copper_min,       'copper_max': copper_max,
            'limestone_min': limestone_min, 'limestone_max': limestone_max,
            'manganese_min': manganese_min, 'manganese_max': manganese_max,
            # misc
            'start_date':      start_date,
            'cloud_threshold': cloud_threshold,
            'region':          region,
            # classification
            'classification':         classification,
            'classification_type':    class_type,
            'nearby_mines':           nearby_mines,
            'nearest_distance':       nearest_distance,
            'nearest_mine':           nearest_mine,
            'classified_for_mineral': selected_mineral_key,
        }
        
        st.session_state.analysis_complete = True
        st.session_state.last_search_query = search_query
        
        progress_bar.progress(100)
        status_text.markdown("**✅ Analysis Complete!**")
        
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

# --- DISPLAY RESULTS ---
if st.session_state.analysis_complete and st.session_state.results:
    
    results = st.session_state.results
    location = results['location']
    
    current_mineral = st.session_state.selected_mineral
    
    mineral_config = {
        'iron':      {'symbol': '●', 'name': 'Iron',      'abbr': 'Fe', 'color': '#E63946', 'emoji': '🔴'},
        'aluminum':  {'symbol': '●', 'name': 'Aluminum',  'abbr': 'Al', 'color': '#00BCD4', 'emoji': '⚪'},
        'copper':    {'symbol': '●', 'name': 'Copper',    'abbr': 'Cu', 'color': '#FF9800', 'emoji': '🟠'},
        'limestone': {'symbol': '●', 'name': 'Limestone', 'abbr': 'Ls', 'color': '#C0A060', 'emoji': '🪨'},
        'manganese': {'symbol': '●', 'name': 'Manganese', 'abbr': 'Mn', 'color': '#795548', 'emoji': '🟤'},
    }

    config = mineral_config[current_mineral]
    current_coverage = results[f'{current_mineral}_coverage']

    # ── Re-classify if the active mineral changed since last classification ──────
    # The initial scan classifies for `selected_mineral_key` at scan time.
    # When the user switches Fe → Al → Cu the stored classification becomes stale.
    if results.get('classified_for_mineral') != current_mineral:
        classification, class_type, nearby_mines, nearest_distance, nearest_mine = classify_location(
            location.latitude,
            location.longitude,
            results[f'{current_mineral}_coverage'],
            current_mineral
        )
        st.session_state.results['classification']        = classification
        st.session_state.results['classification_type']   = class_type
        st.session_state.results['nearby_mines']          = nearby_mines
        st.session_state.results['nearest_distance']      = nearest_distance
        st.session_state.results['nearest_mine']          = nearest_mine
        st.session_state.results['classified_for_mineral'] = current_mineral
        results = st.session_state.results

    col1, col2 = st.columns([7, 3])
    
    with col2:
        st.markdown(f"### 📊 {config['symbol']} {config['name'].upper()} ANALYSIS")
        
        class_type = results.get('classification_type', 'unknown')
        classification = results.get('classification', 'Unknown')
        
        if class_type == 'mining':
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(56, 142, 60, 0.2) 100%);
                padding: 1.2rem;
                border-radius: 12px;
                border: 3px solid #4CAF50;
                margin-bottom: 1rem;
                box-shadow: 0 6px 24px rgba(76, 175, 80, 0.4);
            ">
                <div style="font-family: 'Orbitron', sans-serif; color: #4CAF50; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.3rem;">🤖 AI CLASSIFICATION</div>
                <div style="font-family: 'Orbitron', sans-serif; color: #66BB6A; font-size: 1.1rem; font-weight: 900;">⚖️ LEGAL MINING</div>
            </div>
            """, unsafe_allow_html=True)
            
            if results.get('nearby_mines'):
                st.success(f"✅ {len(results['nearby_mines'])} mine(s) in 15km")
                with st.expander("📍 Nearby Mines"):
                    for mine in results['nearby_mines']:
                        st.write(f"**{mine['name']}**")
                        st.caption(f"{mine['distance']:.2f} km | {mine['country']}")
        else:
            if class_type == 'high_potential':
                color, icon = "#FF9800", "🌟"
            elif class_type == 'moderate_potential':
                color, icon = "#2196F3", "💎"
            else:
                color, icon = "#9E9E9E", "🌍"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(25, 118, 210, 0.2) 100%);
                padding: 1.2rem;
                border-radius: 12px;
                border: 3px solid {color};
                margin-bottom: 1rem;
                box-shadow: 0 6px 24px rgba(33, 150, 243, 0.4);
            ">
                <div style="font-family: 'Orbitron', sans-serif; color: {color}; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.3rem;">🤖 AI CLASSIFICATION</div>
                <div style="font-family: 'Orbitron', sans-serif; color: {color}; font-size: 0.95rem; font-weight: 900; text-transform: uppercase;">{icon} {classification.replace('Natural - ', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if results.get('nearest_mine') and results.get('nearest_distance') is not None:
                nearest_name = results['nearest_mine']
                display_name = nearest_name[:30] + "..." if len(nearest_name) > 30 else nearest_name
                st.info(f"📌 Nearest {config['name']} mine: **{display_name}** ({results['nearest_distance']:.1f} km)")
        
        st.markdown("---")
        
        st.metric(
            label=f"{config['symbol']} {config['name']} Coverage Area",
            value=f"{current_coverage:.1f}%",
            delta=f"{config['abbr']} in 10km radius",
            help=f"Area showing {config['name']} mineral signature"
        )
        
        st.markdown(f"**{config['name']} Detection Confidence:**")
        confidence = min(current_coverage / 30, 1.0)
        st.progress(confidence)
        
        confidence_percent = confidence * 100
        if confidence_percent >= 75:
            st.success(f"🎯 **{confidence_percent:.0f}% Confidence** - Strong {config['name']} detection")
        elif confidence_percent >= 50:
            st.info(f"📊 **{confidence_percent:.0f}% Confidence** - Significant {config['name']} presence")
        elif confidence_percent >= 25:
            st.warning(f"⚠️ **{confidence_percent:.0f}% Confidence** - Weak {config['name']} signals")
        else:
            st.info(f"ℹ️ **{confidence_percent:.0f}% Confidence** - Limited {config['name']} content")
        
        st.markdown("---")
        
        if current_coverage > 20:
            st.success(f"{config['emoji']} **HIGH GRADE** - Major {config['name']} deposit")
        elif current_coverage > 10:
            st.warning(f"{config['emoji']} **MODERATE GRADE** - Significant {config['name']} presence")
        elif current_coverage > 3:
            st.info(f"{config['emoji']} **LOW GRADE** - Minor {config['name']} signatures")
        else:
            st.info(f"⚪ **TRACE AMOUNTS** - Limited {config['name']} content")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-title">📈 {config['symbol']} {config['name'].upper()} SPECTRAL DATA</div>
        </div>
        """, unsafe_allow_html=True)
        
        mineral_stats = results[f'{current_mineral}_stats']
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.metric("Min", f"{mineral_stats.get(f'{current_mineral}_index_min', 0):.2f}")
            st.metric("Mean", f"{mineral_stats.get(f'{current_mineral}_index_mean', 0):.2f}")
        with spec_col2:
            st.metric("Max", f"{mineral_stats.get(f'{current_mineral}_index_max', 0):.2f}")
            st.metric("90th %", f"{mineral_stats.get(f'{current_mineral}_index_p90', 0):.2f}")
        
        st.markdown("---")
    
    with col1:
        st.markdown(f"### 🗺️ {config['symbol']} {config['name'].upper()} SATELLITE VIEW - {location.address.split(',')[0]}")
        
        # tiles=None prevents folium from creating ANY internal TileProvider callable.
        # All tile layers are injected via AllTilesElement (pure JS, no Python callables).
        m = folium.Map(
            location=[location.latitude, location.longitude],
            zoom_start=13,
            tiles=None,
            control_scale=True
        )

        # Inject all tile layers + layer control as raw Leaflet JS — zero callables.
        mineral_label = f"🔬 {config['name']} ({config['abbr']}) Heatmap"
        mineral_tile_url = results[f'{current_mineral}_tile']
        AllTilesElement(
            true_color_url  = results['true_color_tile'],
            mineral_url     = mineral_tile_url,
            mineral_label   = mineral_label,
            false_color_url = results['false_color_tile'],
            mineral_opacity = 0.7
        ).add_to(m)
        
        with st.spinner("📍 Loading landmarks..."):
            nearby_places = get_nearby_places(location.latitude, location.longitude, radius_km=5)
        
        if nearby_places:
            for place in nearby_places:
                # FIX: Use Bootstrap icon names (no prefix='fa') — FontAwesome prefix
                # triggers an internal callable in folium >= 0.18 that breaks JSON serialization.
                icon_map = {
                    'Shopping': {'color': 'blue', 'icon': 'shopping-cart'},
                    'Education': {'color': 'purple', 'icon': 'book'},
                    'Healthcare': {'color': 'red', 'icon': 'plus-sign'},
                    'Hospitality': {'color': 'orange', 'icon': 'cutlery'},
                    'Landmark': {'color': 'lightgray', 'icon': 'home'}
                }
                
                icon_config = icon_map.get(place['type'], {'color': 'lightgray', 'icon': 'map-marker'})
                
                folium.Marker(
                    [place['lat'], place['lon']],
                    popup=folium.Popup(f"""
                    <div style='width: 180px; font-family: Arial;'>
                        <h4 style='color: #2196F3; margin-bottom: 5px;'>📍 {place['type']}</h4>
                        <p style='margin: 3px 0; font-weight: bold;'>{place['name']}</p>
                        <p style='margin: 5px 0 0 0; font-size: 0.85em; color: #666;'>Local landmark</p>
                    </div>
                    """, max_width=200),
                    tooltip=f"📍 {place['name']}",
                    icon=folium.Icon(color=icon_config['color'], icon=icon_config['icon'])
                ).add_to(m)
        
        # Tile layers are handled by AllTilesElement above — no separate calls needed.
        
        folium.Marker(
            [location.latitude, location.longitude],
            popup=folium.Popup(f"""
            <div style='width: 220px; font-family: Arial;'>
                <h4 style='color: {config["color"]}; margin-bottom: 5px;'>📍 Analysis Center</h4>
                <p style='margin: 3px 0;'><b>Location:</b> {location.address.split(',')[0]}</p>
                <p style='margin: 3px 0;'><b>Coordinates:</b><br>{location.latitude:.4f}°N<br>{location.longitude:.4f}°E</p>
                <p style='margin: 3px 0;'><b>Active:</b> {config["name"]} ({config["abbr"]})</p>
                <p style='margin: 3px 0;'><b>{config["name"]} Coverage:</b> {current_coverage:.1f}%</p>
                <p style='margin: 3px 0;'><b>Classification:</b> {results['classification']}</p>
            </div>
            """, max_width=250),
            tooltip="📍 Click for details",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        folium.Circle(
            location=[location.latitude, location.longitude],
            radius=10000,
            color=config['color'],
            fill=False,
            weight=2,
            opacity=0.5,
            popup=folium.Popup(f"""
            <div style='width: 180px; font-family: Arial;'>
                <h4 style='color: {config["color"]};'>⭕ Analysis Radius</h4>
                <p><b>Radius:</b> 10 kilometers</p>
                <p style='font-size: 0.9em;'>Area scanned for {config["name"]} deposits.</p>
            </div>
            """, max_width=200),
            tooltip="⭕ 10km Analysis Radius"
        ).add_to(m)
        
        if results.get('nearby_mines'):
            for mine in results['nearby_mines']:
                mine_coords = None
                for mine_name, (lat, lon, country, mine_type) in LEGAL_MINING_AREAS.items():
                    if mine_name == mine['name']:
                        mine_coords = (lat, lon)
                        break
                
                if mine_coords:
                    folium.Marker(
                        mine_coords,
                        popup=folium.Popup(f"""
                        <div style='width: 220px; font-family: Arial;'>
                            <h4 style='color: #4CAF50; margin-bottom: 5px;'>⚖️ Legal Mining Area</h4>
                            <p style='margin: 3px 0;'><b>Mine:</b> {mine['name']}</p>
                            <p style='margin: 3px 0;'><b>Country:</b> {mine['country']}</p>
                            <p style='margin: 3px 0;'><b>Type:</b> {mine['type']}</p>
                            <p style='margin: 3px 0;'><b>Distance:</b> {mine['distance']:.2f} km</p>
                            <p style='margin: 5px 0; padding: 5px; background: #E8F5E9; border-radius: 3px; font-size: 0.85em;'>✅ Registered legal operation</p>
                        </div>
                        """, max_width=250),
                        tooltip=f"⚖️ {mine['name']}",
                        icon=folium.Icon(color='green', icon='star')
                    ).add_to(m)
        
        # LayerControl is injected via AllTilesElement JS above — no folium.LayerControl needed.
        
        # FIX 1: st_folium is now properly inside `with col1:` (not in a broken container)
        map_data = st_folium(m, width=None, height=600, key="main_map", returned_objects=["last_clicked"])
        
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lng = map_data["last_clicked"]["lng"]
            
            center_point = (location.latitude, location.longitude)
            clicked_point = (clicked_lat, clicked_lng)
            distance_from_center = geodesic(center_point, clicked_point).kilometers
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(25, 118, 210, 0.15) 100%);
                padding: 1.2rem;
                border-radius: 12px;
                border: 2px solid {config['color']};
                margin-top: 1rem;
                box-shadow: 0 4px 16px rgba(33, 150, 243, 0.3);
            ">
                <div style="font-family: 'Orbitron', sans-serif; color: {config['color']}; font-size: 1rem; font-weight: 700; margin-bottom: 0.8rem;">
                    📍 {config['symbol']} {config['name'].upper()} AT SELECTED LOCATION
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_click1, col_click2, col_click3 = st.columns(3)
            
            with col_click1:
                st.metric("Latitude", f"{clicked_lat:.6f}°", delta="N")
            with col_click2:
                st.metric("Longitude", f"{clicked_lng:.6f}°", delta="E")
            with col_click3:
                st.metric("Distance", f"{distance_from_center:.2f} km", delta="from center")
            
            if distance_from_center <= 10:
                st.success("✅ **Within analysis radius (10km)**")
                
                if f'{current_mineral}_index_ee' in st.session_state:
                    with st.spinner(f"🔬 Analyzing {config['name']}..."):
                        mineral_value = get_mineral_index_at_point(
                            st.session_state[f'{current_mineral}_index_ee'],
                            clicked_lat,
                            clicked_lng,
                            current_mineral
                        )
                        
                        if mineral_value is not None:
                            current_threshold = results.get(f'{current_mineral}_threshold', 1.3)
                            
                            if mineral_value > current_threshold:
                                has_mineral = True
                                if mineral_value >= 2.5:
                                    point_class = "Very High"
                                elif mineral_value >= 2.0:
                                    point_class = "High"
                                elif mineral_value >= 1.6:
                                    point_class = "Medium"
                                else:
                                    point_class = "Medium-Low"
                                point_color = config['color']
                                point_emoji = config['emoji']
                            else:
                                has_mineral = False
                                point_class = "Below Threshold"
                                point_color = "#9E9E9E"
                                point_emoji = "⚪"
                            
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, rgba(230, 57, 70, 0.15) 0%, rgba(255, 107, 107, 0.15) 100%);
                                padding: 1.2rem;
                                border-radius: 12px;
                                border: 3px solid {point_color};
                                margin-top: 1rem;
                                box-shadow: 0 6px 20px rgba(230, 57, 70, 0.3);
                            ">
                                <div style="font-family: 'Orbitron', sans-serif; color: {point_color}; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem;">
                                    🔬 {config['name'].upper()} INDEX AT THIS POINT
                                </div>
                                <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                                    <div style="font-family: 'Orbitron', sans-serif; color: {point_color}; font-size: 2.5rem; font-weight: 900; margin-right: 1rem;">
                                        {mineral_value:.3f}
                                    </div>
                                    <div>
                                        <div style="font-family: 'Rajdhani', sans-serif; color: {point_color}; font-size: 1.2rem; font-weight: 700;">
                                            {point_emoji} {point_class} {config['name']}
                                        </div>
                                        <div style="font-family: 'Rajdhani', sans-serif; color: #A8DADC; font-size: 0.9rem;">
                                            Threshold: {current_threshold}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                if has_mineral:
                                    mineral_percent = ((mineral_value - current_threshold) / (3.5 - current_threshold)) * 100
                                    st.metric("Relative Strength", f"{min(mineral_percent, 100):.1f}%", delta="above threshold")
                                else:
                                    st.metric("Status", "No Detection", delta="below threshold")
                            
                            with col_info2:
                                area_mean = results.get(f'{current_mineral}_stats', {}).get(f'{current_mineral}_index_mean', 1.5)
                                diff = mineral_value - area_mean
                                if diff > 0:
                                    st.metric("vs Area Average", f"+{diff:.2f}", delta="above average")
                                else:
                                    st.metric("vs Area Average", f"{diff:.2f}", delta="below average")
                            
                            if mineral_value >= 2.5:
                                st.error(f"🎯 **Prime Target:** Extremely high {config['name']} concentration!")
                            elif mineral_value >= 2.0:
                                st.warning(f"🎯 **High Priority:** Strong {config['name']} signature!")
                            elif mineral_value >= 1.6:
                                st.info(f"💎 **Moderate Interest:** Significant {config['name']} presence.")
                            elif mineral_value >= current_threshold:
                                st.info(f"📊 **Detected:** {config['name']} signature above threshold.")
                            else:
                                st.info(f"🌍 **Natural:** {config['name']} content below detection threshold.")
                        
                        else:
                            st.warning(f"⚠️ Could not retrieve {config['name']} index. Try a different spot.")
            else:
                st.warning("⚠️ **Outside analysis radius**")
                st.info(f"{config['name']} index data only available within 10km.")
        
        legend_gradients = {
            'iron':      'linear-gradient(to right, #FFA500, #FF6347, #FF4500, #DC143C, #8B0000, #4a0000)',
            'aluminum':  'linear-gradient(to right, #E0F7FA, #4DD0E1, #00BCD4, #0097A7, #00838F, #006064)',
            'copper':    'linear-gradient(to right, #FFEB3B, #FFC107, #FF9800, #FF5722, #8D6E63, #5D4037)',
            'limestone': 'linear-gradient(to right, #F5F5DC, #E8DCC8, #D4C5A9, #C0AA87, #A08060, #705030)',
            'manganese': 'linear-gradient(to right, #E8C880, #C89040, #985010, #6B2D00, #3D1500, #1A0500)',
        }
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%); padding: 1rem; border-radius: 15px; border: 2px solid {config['color']}; margin-top: 1rem;">
            <div style="font-family: 'Orbitron', sans-serif; color: #FFE66D; font-size: 1rem; font-weight: 700; margin-bottom: 0.8rem;">🎨 {config['symbol']} {config['name'].upper()} HEATMAP LEGEND</div>
            <div style="width: 100%; height: 35px; background: {legend_gradients[current_mineral]}; border-radius: 5px; margin-bottom: 0.6rem; box-shadow: 0 3px 10px rgba(0,0,0,0.4);"></div>
            <div style="display: flex; justify-content: space-between; color: #A8DADC; font-size: 0.85rem; font-family: 'Rajdhani', sans-serif; font-weight: 600; padding: 0 10px;">
                <span>Low<br>{config['name']}</span>
                <span style="text-align: center;">Low-<br>Medium</span>
                <span style="text-align: center;">Medium<br>{config['name']}</span>
                <span style="text-align: center;">High<br>{config['name']}</span>
                <span style="text-align: right;">Very<br>High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"💡 Use layer panel to toggle True Color, {config['name']} Heatmap, and False Color.")
    
    st.markdown("### 📋 TECHNICAL DETAILS")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown(f"""
        **Satellite Data:**
        - Source: Sentinel-2 SR Harmonized
        - Images: {results['num_images']}
        - Date: {results['start_date']} to Feb 2026
        - Clouds: < 40%
        - Resolution: 10m/pixel
        """)
    
    with col_b:
        index_formulas = {
            'iron':      'Red/Blue (B4/B2)',
            'aluminum':  'SWIR1/SWIR2 (B11/B12)',
            'copper':    '(Red/Green)×(NIR/Red)',
            'limestone': 'Carbonate: SWIR1/SWIR2 (B11/B12)',
            'manganese': 'MnOx: Red/SWIR1 (B4/B11)',
        }
        
        st.markdown(f"""
        **Analysis Method:**
        - Mineral: {config['name']} ({config['abbr']})
        - Index: {index_formulas[current_mineral]}
        - Threshold: {results[f'{current_mineral}_threshold']:.2f}
        - Region: 10km radius
        - Processing: Median composite
        - Scale: 30m
        """)
    
    with col_c:
        st.markdown(f"""
        **Location:**
        - Lat: {location.latitude:.6f}°
        - Lon: {location.longitude:.6f}°
        - Place: {location.address.split(',')[0]}
        - Area: ~314 km²
        """)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; color: #6c757d; font-family: 'Rajdhani', sans-serif; padding: 1rem 0; margin-top: 2rem;">
    <p>🛰️ <strong>SpectraMining AI</strong> | Powered by Google Earth Engine & Sentinel-2 ESA</p>
    <p style="font-size: 0.9rem;">Advanced satellite-based multi-mineral exploration technology</p>
</div>
""", unsafe_allow_html=True)
#python -m streamlit run app.py