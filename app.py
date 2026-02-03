import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import random

# ==========================================
# 1. DİL AYARLARI (TRANSLATION DICTIONARY)
# ==========================================
TEXTS = {
    "TR": {
        "sidebar_title": "LogiMatch v2.4",
        "menu_label": "Menü",
        "menu_options": ["🚛 Nakliyeci (Kamyonum Var)", "📦 Yük Sahibi (Yüküm Var)", "📊 Canlı Pazar & Harita"],
        "system_status": "Sistem: 🟢 Aktif\n\nVeri: ✅ Yük Tanımlı (v3)",
        "btn_demo": "🎲 Sisteme Test Verisi Yükle (Demo)",
        "demo_success": "✅ Gerçekçi yük tanımları ve araçlar sisteme eklendi!",
        
        # Nasıl Çalışır
        "how_title": "❓ Nasıl Çalışır?",
        "how_trans": "Rotanızı seçin, o yöne giden 'Paletli Yük', 'Ev Eşyası' veya 'Sebze' yüklerini bulun.",
        "how_ship": "Yükünüzün ne olduğunu (Örn: 10 Palet Karpuz) yazın, uygun aracı hemen bulun.",
        "how_market": "Kırmızı noktalar boş kamyonları gösterir. Listede yüklerin detaylarını görebilirsiniz.",

        # Nakliyeci Sayfası
        "trans_title": "🚛 Nakliyeci Paneli",
        "trans_subtitle": "Boş dönme! Aracına uygun yükü bul.",
        "header_post": "📝 İlan Ver",
        "lbl_name": "Ad Soyad / Firma",
        "lbl_phone": "Telefon Numarası",
        "lbl_vehicle": "Araç Tipi",
        "lbl_origin": "Nereden (Çıkış)",
        "lbl_dest": "Nereye (Varış)",
        "lbl_date": "Müsaitlik Tarihi",
        "btn_submit_truck": "İlanı Yayınla & Yük Ara",
        "vehicles": ["Tır (Tenteli)", "Kamyon (Açık)", "Kamyon (Kapalı)", "Kamyonet", "Panelvan", "Frigo (Soğutuculu)"],
        "warn_name": "⚠️ Lütfen isminizi girin.",
        "success_post": "✅ İlan Başarıyla Yayınlandı! Puanınız: 5.0 ⭐",
        "header_search": "🔍 Senin İçin Bulunan Yükler",
        "info_no_load": "Şu an bu rotada yük ilanı yok.",
        
        # Yük Sahibi Sayfası
        "ship_title": "📦 Yük Sahibi Paneli",
        "ship_subtitle": "Yükünü tanımla, taşıyıcılar seni bulsun.",
        "header_cargo": "📝 Yük Bildir",
        "lbl_company": "Firma Adı",
        "lbl_desc": "Yük Cinsi ve Miktarı",
        "ph_desc": "Örn: 20 Palet Domates, 3+1 Ev Eşyası, Demir Boru...",
        "btn_submit_cargo": "Yükü Yayınla & Araç Ara",
        "warn_company": "⚠️ Firma adı ve yük tanımı zorunludur.",
        "success_cargo": "✅ Yük İlanı Oluşturuldu!",
        "header_truck_search": "🔍 Uygun Araçlar",
        "info_no_truck": "Bu rotada şu an müsait araç yok.",
        
        # Harita Sayfası
        "map_title": "📊 Lojistik Pazarı",
        "header_map": "📍 Müsait Araçlar",
        "header_list_truck": "📋 Son Araç İlanları",
        "header_list_load": "📦 Son Yük İlanları",
        "warn_no_data": "Veri yok. Demo verisi yükleyebilirsiniz.",
        "info_empty": "Henüz ilan yok."
    },
    
    "EN": {
        "sidebar_title": "LogiMatch v2.4",
        "menu_label": "Menu",
        "menu_options": ["🚛 Transporter (I have a Truck)", "📦 Shipper (I have Cargo)", "📊 Live Market & Map"],
        "system_status": "System: 🟢 Online\n\nData: ✅ Cargo Description (v3)",
        "btn_demo": "🎲 Load Test Data (Demo Mode)",
        "demo_success": "✅ Realistic cargo & trucks injected!",

        "how_title": "❓ How does it work?",
        "how_trans": "Select route, find cargoes like 'Palletized Goods', 'Furniture' or 'Fresh Food'.",
        "how_ship": "Describe your cargo (e.g., 10 Pallets of Watermelon), find the right truck.",
        "how_market": "Red dots are empty trucks. Check the lists for cargo details.",
        
        "trans_title": "🚛 Transporter Hub",
        "trans_subtitle": "Don't return empty! Find cargo fits your truck.",
        "header_post": "📝 Post Truck",
        "lbl_name": "Name / Company",
        "lbl_phone": "Phone Number",
        "lbl_vehicle": "Vehicle Type",
        "lbl_origin": "Origin City",
        "lbl_dest": "Destination City",
        "lbl_date": "Available Date",
        "btn_submit_truck": "Post & Search Cargo",
        "vehicles": ["Semi-Trailer", "Truck (Open)", "Truck (Box)", "Van", "Minivan", "Refrigerated"],
        "warn_name": "⚠️ Please enter your name.",
        "success_post": "✅ Truck Posted Successfully! Score: 5.0 ⭐",
        "header_search": "🔍 Cargo Matches",
        "info_no_load": "No cargo found for this route yet.",
        
        "ship_title": "📦 Shipper Hub",
        "ship_subtitle": "Describe cargo, find reliable trucks.",
        "header_cargo": "📝 Post Cargo",
        "lbl_company": "Company Name",
        "lbl_desc": "Cargo Description & Quantity",
        "ph_desc": "Ex: 20 Pallets Tomatoes, Household Goods, Steel Pipes...",
        "btn_submit_cargo": "Post & Search Trucks",
        "warn_company": "⚠️ Company name and description required.",
        "success_cargo": "✅ Cargo Posted Successfully!",
        "header_truck_search": "🔍 Available Trucks",
        "info_no_truck": "No trucks available for this route yet.",
        
        "map_title": "📊 Logistics Market",
        "header_map": "📍 Live Truck Locations",
        "header_list_truck": "📋 Latest Trucks",
        "header_list_load": "📦 Latest Loads",
        "warn_no_data": "No data. Try 'Load Test Data'.",
        "info_empty": "No listings yet."
    }
}

# ==========================================
# 2. AYARLAR & SABİTLER
# ==========================================
st.set_page_config(
    page_title="LogiMatch Pro",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

TR_CITIES = {
    "ADANA": [37.0000, 35.3213], "ADIYAMAN": [37.7648, 38.2786], "AFYONKARAHISAR": [38.7507, 30.5567],
    "AGRI": [39.7191, 43.0503], "AKSARAY": [38.3687, 34.0370], "AMASYA": [40.6499, 35.8353],
    "ANKARA": [39.9334, 32.8597], "ANTALYA": [36.8969, 30.7133], "ARDAHAN": [41.1105, 42.7022],
    "ARTVIN": [41.1828, 41.8183], "AYDIN": [37.8560, 27.8416], "BALIKESIR": [39.6484, 27.8826],
    "BARTIN": [41.6344, 32.3375], "BATMAN": [37.8812, 41.1351], "BAYBURT": [40.2552, 40.2249],
    "BILECIK": [40.1451, 29.9799], "BINGOL": [38.8855, 40.4980], "BITLIS": [38.4006, 42.1095],
    "BOLU": [40.7392, 31.6089], "BURDUR": [37.7204, 30.2908], "BURSA": [40.1885, 29.0610],
    "CANAKKALE": [40.1553, 26.4142], "CANKIRI": [40.6013, 33.6134], "CORUM": [40.5506, 34.9556],
    "DENIZLI": [37.7765, 29.0864], "DIYARBAKIR": [37.9144, 40.2306], "DUZCE": [40.8438, 31.1565],
    "EDIRNE": [41.6771, 26.5557], "ELAZIG": [38.6810, 39.2264], "ERZINCAN": [39.7500, 39.5000],
    "ERZURUM": [39.9043, 41.2679], "ESKISEHIR": [39.7767, 30.5206], "GAZIANTEP": [37.0662, 37.3833],
    "GIRESUN": [40.9128, 38.3895], "GUMUSHANE": [40.4600, 39.4814], "HAKKARI": [37.5833, 43.7333],
    "HATAY": [36.4018, 36.3498], "IGDIR": [39.9975, 44.0450], "ISPARTA": [37.7648, 30.5566],
    "ISTANBUL": [41.0082, 28.9784], "IZMIR": [38.4192, 27.1287], "KAHRAMANMARAS": [37.5858, 36.9371],
    "KARABUK": [41.2061, 32.6204], "KARAMAN": [37.1759, 33.2287], "KARS": [40.6172, 43.0974],
    "KASTAMONU": [41.3887, 33.7827], "KAYSERI": [38.7312, 35.4787], "KILIS": [36.7184, 37.1212],
    "KIRIKKALE": [39.8468, 33.5153], "KIRKLARELI": [41.7333, 27.2167], "KIRSEHIR": [39.1425, 34.1709],
    "KOCAELI": [40.8533, 29.8815], "KONYA": [37.8667, 32.4833], "KUTAHYA": [39.4167, 29.9833],
    "MALATYA": [38.3552, 38.3095], "MANISA": [38.6191, 27.4289], "MARDIN": [37.3212, 40.7245],
    "MERSIN": [36.8000, 34.6333], "MUGLA": [37.2153, 28.3636], "MUS": [38.9462, 41.7539],
    "NEVSEHIR": [38.6939, 34.6857], "NIGDE": [37.9667, 34.6833], "ORDU": [40.9839, 37.8764],
    "OSMANIYE": [37.0742, 36.2478], "RIZE": [41.0201, 40.5234], "SAKARYA": [40.7569, 30.3783],
    "SAMSUN": [41.2867, 36.33], "SANLIURFA": [37.1591, 38.7969], "SIIRT": [37.9333, 41.9500],
    "SINOP": [42.0231, 35.1531], "SIRNAK": [37.5164, 42.4611], "SIVAS": [39.7477, 37.0179],
    "TEKIRDAG": [40.9833, 27.5167], "TOKAT": [40.3167, 36.5500], "TRABZON": [41.0015, 39.7178],
    "TUNCELI": [39.1079, 39.5401], "USAK": [38.6823, 29.4082], "VAN": [38.4891, 43.4089],
    "YALOVA": [40.6500, 29.2667], "YOZGAT": [39.8181, 34.8147], "ZONGULDAK": [41.4564, 31.7987]
}

CITY_LIST = sorted(list(TR_CITIES.keys()))

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİTABANI BAĞLANTISI (v3 Versiyonu)
# ==========================================

@st.cache_resource
def get_db_engine():
    try:
        db_url = "postgresql://postgres.yzjzgkwwkinmtprqhudn:KzVzeHNAnoEoAetH@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"
        engine = create_engine(db_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"❌ DB Error: {e}")
        st.stop()

def init_db(engine):
    create_transporters = """
    CREATE TABLE IF NOT EXISTS transporters_v3 (
        id SERIAL PRIMARY KEY,
        contact_name TEXT NOT NULL,
        phone TEXT,
        vehicle_type TEXT,
        origin_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        date_available DATE,
        reputation_score INT DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # YENİ TABLO (Cargo weight YERİNE Cargo description)
    create_shippers = """
    CREATE TABLE IF NOT EXISTS shippers_v3 (
        id SERIAL PRIMARY KEY,
        company_name TEXT NOT NULL,
        phone TEXT,
        cargo_description TEXT NOT NULL,
        origin_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        date_required DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(create_transporters))
            conn.execute(text(create_shippers))
            conn.commit()
    except SQLAlchemyError as e:
        st.error(f"Table Error: {e}")

engine = get_db_engine()
init_db(engine)

# ==========================================
# 4. YARDIMCI FONKSİYONLAR
# ==========================================

def save_to_db(table_name, data_dict):
    try:
        df = pd.DataFrame([data_dict])
        df.to_sql(table_name, engine, if_exists='append', index=False)
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def find_matches(target_table, origin, destination):
    query = f"""
        SELECT * FROM {target_table} 
        WHERE origin_city = :origin 
        AND destination_city = :dest
        ORDER BY created_at DESC
    """
    try:
        with engine.connect() as conn:
            result = pd.read_sql(text(query), conn, params={"origin": origin, "dest": destination})
        return result
    except Exception as e:
        st.error(f"Match Error: {e}")
        return pd.DataFrame()

def generate_demo_data():
    """Rastgele Demo Verisi Oluşturur - GERÇEKÇİ YÜKLERLE"""
    fake_names = ["Yılmaz Lojistik", "Demir Nakliyat", "Ahmet Usta", "Kuzey Kargo", "Ege Taşımacılık"]
    fake_companies = ["Hal Komisyoncusu", "Tekstil Fabrikası", "İnşaat Ltd.", "Mobilya Dünyası", "Tarım Koop."]
    
    # Gerçekçi Yük Tanımları
    fake_loads = [
        "20 Palet Domates (Frigo Lazım)",
        "Ev Eşyası 3+1 (Asansörlü)",
        "15 Ton İnşaat Demiri (6 Metre)",
        "Tekstil Kolisi (500 Adet)",
        "Narenciye - Limon (Soğuk Zincir)",
        "Hırdavat Malzemesi (Paletli)",
        "Makine Parçası (Ağır Yük)",
        "Züccaciye (Kırılacak Eşya)"
    ]
    
    # 5 Kamyon Ekle
    for _ in range(5):
        origin = random.choice(CITY_LIST)
        dest = random.choice(CITY_LIST)
        save_to_db("transporters_v3", {
            "contact_name": random.choice(fake_names),
            "phone": f"05{random.randint(30,59)} 123 45 {random.randint(10,99)}",
            "vehicle_type": random.choice(["Frigo (Soğutuculu)", "Tır (Tenteli)", "Kamyon (Açık)"]),
            "origin_city": origin,
            "destination_city": dest,
            "date_available": datetime.today().date(),
            "reputation_score": random.randint(4, 5)
        })

    # 5 Yük Ekle (Sayı değil Tanım ile)
    for _ in range(5):
        origin = random.choice(CITY_LIST)
        dest = random.choice(CITY_LIST)
        save_to_db("shippers_v3", {
            "company_name": random.choice(fake_companies),
            "phone": f"0212 222 33 {random.randint(10,99)}",
            "cargo_description": random.choice(fake_loads),
            "origin_city": origin,
            "destination_city": dest,
            "date_required": datetime.today().date()
        })
    return True

# ==========================================
# 5. SAYFA YAPISI VE DİL SEÇİMİ
# ==========================================

lang_choice = st.sidebar.selectbox("Language / Dil", ["TR", "EN"])
T = TEXTS[lang_choice] 

st.sidebar.title(T["sidebar_title"])
st.sidebar.markdown("---")
page_index = st.sidebar.radio(
    T["menu_label"],
    range(len(T["menu_options"])),
    format_func=lambda x: T["menu_options"][x]
)

# DEMO BUTONU
st.sidebar.markdown("---")
if st.sidebar.button(T["btn_demo"]):
    with st.spinner("Generating Data..."):
        if generate_demo_data():
            st.sidebar.success(T["demo_success"])
            st.rerun()

st.sidebar.success(T["system_status"])

# ==========================================
# 6. SAYFA: NAKLİYECİ (TRANSPORTER)
# ==========================================
if page_index == 0:
    st.title(T["trans_title"])
    
    with st.expander(T["how_title"]):
        st.markdown(T["how_trans"])
        
    st.markdown(T["trans_subtitle"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(T["header_post"])
        with st.form("transporter_form"):
            name = st.text_input(T["lbl_name"])
            phone = st.text_input(T["lbl_phone"])
            vehicle = st.selectbox(T["lbl_vehicle"], T["vehicles"])
            origin = st.selectbox(T["lbl_origin"], CITY_LIST)
            dest = st.selectbox(T["lbl_dest"], CITY_LIST)
            date_avail = st.date_input(T["lbl_date"], min_value=datetime.today())
            
            submit_truck = st.form_submit_button(T["btn_submit_truck"])
            
    with col2:
        if submit_truck:
            if not name:
                st.warning(T["warn_name"])
            else:
                data = {
                    "contact_name": name,
                    "phone": phone,
                    "vehicle_type": vehicle,
                    "origin_city": origin,
                    "destination_city": dest,
                    "date_available": date_avail,
                    "reputation_score": 5
                }
                
                if save_to_db("transporters_v3", data):
                    st.success(T["success_post"])
                    
                    st.divider()
                    st.subheader(f"{T['header_search']}: '{origin}' -> '{dest}'")
                    matches = find_matches("shippers_v3", origin, dest)
                    
                    if not matches.empty:
                        for index, row in matches.iterrows():
                            with st.container():
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>🏢 {row['company_name']}</h4>
                                    <p><b>📦 {row['cargo_description']}</b></p>
                                    <p>📅 Tarih: {row['date_required']} | 📞 <b>{row['phone']}</b></p>
                                </div>
                                <br>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(T["info_no_load"])

# ==========================================
# 7. SAYFA: YÜK SAHİBİ (SHIPPER)
# ==========================================
elif page_index == 1:
    st.title(T["ship_title"])
    
    with st.expander(T["how_title"]):
        st.markdown(T["how_ship"])
        
    st.markdown(T["ship_subtitle"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(T["header_cargo"])
        with st.form("shipper_form"):
            company = st.text_input(T["lbl_company"])
            phone = st.text_input(T["lbl_phone"])
            # BURASI DEĞİŞTİ: Sayı yerine Metin
            desc = st.text_input(T["lbl_desc"], placeholder=T["ph_desc"])
            
            origin = st.selectbox(T["lbl_origin"], CITY_LIST)
            dest = st.selectbox(T["lbl_dest"], CITY_LIST)
            date_req = st.date_input(T["lbl_date"], min_value=datetime.today())
            
            submit_cargo = st.form_submit_button(T["btn_submit_cargo"])
            
    with col2:
        if submit_cargo:
            if not company or not desc:
                st.warning(T["warn_company"])
            else:
                data = {
                    "company_name": company,
                    "phone": phone,
                    "cargo_description": desc,
                    "origin_city": origin,
                    "destination_city": dest,
                    "date_required": date_req
                }
                
                if save_to_db("shippers_v3", data):
                    st.success(T["success_cargo"])
                    
                    st.divider()
                    st.subheader(f"{T['header_truck_search']}: '{origin}' -> '{dest}'")
                    matches = find_matches("transporters_v3", origin, dest)
                    
                    if not matches.empty:
                        for index, row in matches.iterrows():
                            stars = "⭐" * int(row.get('reputation_score', 3))
                            with st.container():
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4>🚛 {row['contact_name']} {stars}</h4>
                                    <p><b>Vehicle:</b> {row['vehicle_type']} | <b>Date:</b> {row['date_available']}</p>
                                    <p>📞 <b>Tel:</b> {row['phone']}</p>
                                </div>
                                <br>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(T["info_no_truck"])

# ==========================================
# 8. SAYFA: CANLI PAZAR (MARKET)
# ==========================================
elif page_index == 2:
    st.title(T["map_title"])
    
    with st.expander(T["how_title"]):
        st.markdown(T["how_market"])
    
    try:
        with engine.connect() as conn:
            trucks_df = pd.read_sql("SELECT * FROM transporters_v3 ORDER BY created_at DESC LIMIT 50", conn)
            loads_df = pd.read_sql("SELECT * FROM shippers_v3 ORDER BY created_at DESC LIMIT 50", conn)
            
        if not trucks_df.empty:
            map_data = []
            for _, row in trucks_df.iterrows():
                city = row['origin_city']
                if city in TR_CITIES:
                    map_data.append({
                        'lat': TR_CITIES[city][0],
                        'lon': TR_CITIES[city][1],
                        'type': 'Truck'
                    })
            
            map_df = pd.DataFrame(map_data)
            
            st.markdown(f"### {T['header_map']}")
            if not map_df.empty:
                st.map(map_df, zoom=5)
            else:
                st.warning(T["warn_no_data"])
            
            col_t, col_l = st.columns(2)
            
            with col_t:
                st.markdown(f"### {T['header_list_truck']}")
                st.dataframe(trucks_df[['contact_name', 'origin_city', 'destination_city', 'vehicle_type']], use_container_width=True, hide_index=True)
            
            with col_l:
                st.markdown(f"### {T['header_list_load']}")
                if not loads_df.empty:
                    st.dataframe(loads_df[['company_name', 'origin_city', 'destination_city', 'cargo_description']], use_container_width=True, hide_index=True)
                else:
                    st.info("No loads yet.")
            
        else:
            st.info(T["info_empty"])
            
    except Exception as e:
        st.error(f"Data Error: {e}")
