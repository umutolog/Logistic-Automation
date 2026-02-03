import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import random
import re

# ==========================================
# 1. DİL AYARLARI (TRANSLATION)
# ==========================================
TEXTS = {
    "TR": {
        "sidebar_title": "LogiMatch v3.2 (Fix)",
        "menu_label": "Menü",
        "menu_options": ["🚛 Nakliyeci (İlan Ver)", "📦 Yük Sahibi (Yük Ekle)", "🤖 AI Rota Planlayıcı", "📊 Canlı Pazar & Harita"],
        "system_status": "Sistem: 🟢 Online\n\nArayüz: ✅ Renkler Düzeltildi",
        "btn_demo": "🎲 Test Verisi Yükle (AI Eğitimi)",
        "demo_success": "✅ AI için test verileri (Zincirleme Rotalar) yüklendi.",
        
        # AI Sayfası
        "ai_title": "🤖 Yapay Zeka Rota Optimizasyonu",
        "ai_subtitle": "Sadece gidişi değil, dönüşü ve sonraki işi de planlayın.",
        "lbl_ai_origin": "Mevcut Konumun",
        "lbl_ai_dest": "Gitmek İstediğin Yön",
        "btn_ai_search": "🚀 Maksimum Verimlilik İçin Rota Oluştur",
        "res_direct": "Tek Yön Kazanç",
        "res_chain": "⚡ ZİNCİRLEME KAZANÇ (Gidiş + Dönüş)",
        "chain_expl": "Yapay zeka, varış noktanızdaki yükleri taradı ve size 2. işi ayarladı.",
        "btn_complete": "✅ Yükü Teslim Ettim (Konumu Güncelle)",
        "success_complete": "Konumunuz güncellendi! Artık yeni şehirde 'Müsait' durumdasınız.",

        # Genel
        "err_phone": "⚠️ Geçersiz Telefon! (Min 10 hane)",
        "err_same_city": "⚠️ Çıkış ve Varış aynı olamaz!",
        "warn_fill_all": "⚠️ Tüm alanları doldurun.",
        "header_post": "📝 İlan Oluştur",
        "btn_submit": "Yayınla",
        "success_post": "✅ Kayıt Başarılı!",
        "info_no_data": "Veri yok."
    },
    
    "EN": {
        "sidebar_title": "LogiMatch v3.2 (Fix)",
        "menu_label": "Menu",
        "menu_options": ["🚛 Transporter", "📦 Shipper", "🤖 AI Route Planner", "📊 Market & Map"],
        "system_status": "System: 🟢 Online\n\nUI: ✅ Colors Fixed",
        "btn_demo": "🎲 Load Test Data",
        "demo_success": "✅ Data loaded for AI simulation.",
        
        "ai_title": "🤖 AI Route Optimization",
        "ai_subtitle": "Plan not just the trip, but the return load.",
        "lbl_ai_origin": "Current Location",
        "lbl_ai_dest": "Target Direction",
        "btn_ai_search": "🚀 Optimize Route Efficiency",
        "res_direct": "Single Leg Profit",
        "res_chain": "⚡ CHAIN PROFIT (Trip + Return)",
        "chain_expl": "AI found a second job starting at your destination.",
        "btn_complete": "✅ Delivered (Update Location)",
        "success_complete": "Location updated! You are now Available in the new city.",

        "err_phone": "⚠️ Invalid Phone!",
        "err_same_city": "⚠️ Origin/Dest error!",
        "warn_fill_all": "⚠️ Fill all fields.",
        "header_post": "📝 Create Listing",
        "btn_submit": "Publish",
        "success_post": "✅ Success!",
        "info_no_data": "No data."
    }
}

# ==========================================
# 2. AYARLAR & SABİTLER & CSS DÜZELTMESİ
# ==========================================
st.set_page_config(
    page_title="LogiMatch AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

TR_CITIES = {
    "ADANA": [37.0000, 35.3213], "ANKARA": [39.9334, 32.8597], "ANTALYA": [36.8969, 30.7133],
    "BURSA": [40.1885, 29.0610], "DIYARBAKIR": [37.9144, 40.2306], "EDIRNE": [41.6771, 26.5557],
    "ERZURUM": [39.9043, 41.2679], "ESKISEHIR": [39.7767, 30.5206], "GAZIANTEP": [37.0662, 37.3833],
    "HATAY": [36.4018, 36.3498], "ISTANBUL": [41.0082, 28.9784], "IZMIR": [38.4192, 27.1287],
    "KAYSERI": [38.7312, 35.4787], "KOCAELI": [40.8533, 29.8815], "KONYA": [37.8667, 32.4833],
    "MERSIN": [36.8000, 34.6333], "SAMSUN": [41.2867, 36.33], "TRABZON": [41.0015, 39.7178], 
    "VAN": [38.4891, 43.4089], "ZONGULDAK": [41.4564, 31.7987]
}
CITY_LIST = sorted(list(TR_CITIES.keys()))

# CSS DÜZELTMESİ: color: #000000 eklendi. (Yazıyı siyah olmaya zorluyoruz)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; }
    
    .metric-card { 
        background-color: #f8f9fa; 
        color: #000000; /* Yazı rengi Siyah */
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #FF4B4B; 
        margin-bottom: 10px; 
    }
    
    .ai-card { 
        background-color: #e8f4f8; 
        color: #000000; /* Yazı rengi Siyah (Görünürlük için) */
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00a8ff; 
        margin-bottom: 10px; 
    }
    
    .ai-card h4, .metric-card h4 {
        color: #000000 !important; /* Başlıklar kesin siyah */
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. VERİTABANI BAĞLANTISI (v4)
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
    CREATE TABLE IF NOT EXISTS transporters_v4 (
        id SERIAL PRIMARY KEY,
        contact_name TEXT NOT NULL,
        phone TEXT,
        vehicle_type TEXT,
        origin_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        date_available DATE,
        reputation_score INT DEFAULT 0,
        status TEXT DEFAULT 'Available',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    create_shippers = """
    CREATE TABLE IF NOT EXISTS shippers_v4 (
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

def is_valid_phone(phone_str):
    if not phone_str: return False
    clean_num = re.sub(r'\D', '', phone_str)
    return len(clean_num) >= 10

def save_to_db(table_name, data_dict):
    try:
        df = pd.DataFrame([data_dict])
        df.to_sql(table_name, engine, if_exists='append', index=False)
        return True
    except Exception as e:
        st.error(f"Save Error: {e}")
        return False

def update_driver_location(driver_phone, new_city):
    try:
        with engine.connect() as conn:
            stmt = text("""
                UPDATE transporters_v4 
                SET origin_city = :new_city, destination_city = '', status = 'Available', date_available = CURRENT_DATE
                WHERE phone = :phone
            """)
            conn.execute(stmt, {"new_city": new_city, "phone": driver_phone})
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Update Error: {e}")
        return False

def find_ai_routes(origin, dest):
    try:
        with engine.connect() as conn:
            query1 = text("SELECT * FROM shippers_v4 WHERE origin_city = :o AND destination_city = :d")
            leg1 = pd.read_sql(query1, conn, params={"o": origin, "d": dest})
            
            query2 = text("SELECT * FROM shippers_v4 WHERE origin_city = :d")
            potential_leg2 = pd.read_sql(query2, conn, params={"d": dest})
            
        return leg1, potential_leg2
    except Exception as e:
        st.error(f"AI Search Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def generate_demo_data():
    truck = {
        "contact_name": "AI Lojistik (Demo)", "phone": "05551112233", "vehicle_type": "Tır (Tenteli)",
        "origin_city": "IZMIR", "destination_city": "HATAY", "date_available": datetime.today().date(), "status": "Available"
    }
    load1 = {
        "company_name": "Ege Tarım", "phone": "02321112233", "cargo_description": "20 Palet Gübre",
        "origin_city": "IZMIR", "destination_city": "HATAY", "date_required": datetime.today().date()
    }
    load2 = {
        "company_name": "Hatay Demir Çelik", "phone": "03261112233", "cargo_description": "15 Ton Rulo Sac",
        "origin_city": "HATAY", "destination_city": "ISTANBUL", "date_required": datetime.today().date()
    }
    
    save_to_db("transporters_v4", truck)
    save_to_db("shippers_v4", load1)
    save_to_db("shippers_v4", load2)
    return True

# ==========================================
# 5. SAYFA YAPISI
# ==========================================
lang_choice = st.sidebar.selectbox("Dil / Language", ["TR", "EN"])
T = TEXTS[lang_choice] 

st.sidebar.title(T["sidebar_title"])
st.sidebar.markdown("---")
page_index = st.sidebar.radio(T["menu_label"], range(4), format_func=lambda x: T["menu_options"][x])

st.sidebar.markdown("---")
if st.sidebar.button(T["btn_demo"]):
    with st.spinner("Loading..."):
        if generate_demo_data():
            st.sidebar.success(T["demo_success"])

st.sidebar.success(T["system_status"])

# ==========================================
# SAYFA 1: NAKLİYECİ (İLAN VER)
# ==========================================
if page_index == 0:
    st.title("🚛 " + T["menu_options"][0])
    with st.form("trans_form"):
        name = st.text_input(T.get("lbl_name", "Ad / Firma"))
        phone = st.text_input(T.get("lbl_phone", "Telefon"))
        vehicle = st.selectbox("Araç", ["Tır", "Kamyon", "Kamyonet", "Frigo"])
        origin = st.selectbox("Çıkış", CITY_LIST)
        dest = st.selectbox("Varış", CITY_LIST)
        date = st.date_input("Tarih", min_value=datetime.today())
        if st.form_submit_button(T["btn_submit"]):
            if not is_valid_phone(phone): st.error(T["err_phone"])
            elif origin == dest: st.error(T["err_same_city"])
            else:
                save_to_db("transporters_v4", {
                    "contact_name": name, "phone": phone, "vehicle_type": vehicle,
                    "origin_city": origin, "destination_city": dest, "date_available": date,
                    "status": "Available"
                })
                st.success(T["success_post"])

# ==========================================
# SAYFA 2: YÜK SAHİBİ (YÜK EKLE)
# ==========================================
elif page_index == 1:
    st.title("📦 " + T["menu_options"][1])
    with st.form("ship_form"):
        comp = st.text_input("Firma Adı")
        phone = st.text_input("Telefon")
        desc = st.text_input("Yük Tanımı (Örn: 20 Palet)")
        origin = st.selectbox("Çıkış", CITY_LIST)
        dest = st.selectbox("Varış", CITY_LIST)
        date = st.date_input("Tarih", min_value=datetime.today())
        if st.form_submit_button(T["btn_submit"]):
            if not is_valid_phone(phone): st.error(T["err_phone"])
            elif origin == dest: st.error(T["err_same_city"])
            else:
                save_to_db("shippers_v4", {
                    "company_name": comp, "phone": phone, "cargo_description": desc,
                    "origin_city": origin, "destination_city": dest, "date_required": date
                })
                st.success(T["success_post"])

# ==========================================
# SAYFA 3: AI ROTA PLANLAYICI
# ==========================================
elif page_index == 2:
    st.title(T["ai_title"])
    st.markdown(T["ai_subtitle"])
    
    col1, col2 = st.columns(2)
    with col1:
        start_city = st.selectbox(T["lbl_ai_origin"], CITY_LIST, index=CITY_LIST.index("IZMIR") if "IZMIR" in CITY_LIST else 0)
    with col2:
        target_city = st.selectbox(T["lbl_ai_dest"], CITY_LIST, index=CITY_LIST.index("HATAY") if "HATAY" in CITY_LIST else 0)
        
    if st.button(T["btn_ai_search"]):
        leg1, leg2 = find_ai_routes(start_city, target_city)
        
        st.divider()
        
        # 1. ADIM
        st.subheader(f"1. {start_city} ➝ {target_city} ({T['res_direct']})")
        if not leg1.empty:
            for _, row in leg1.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📦 {row['cargo_description']}</h4>
                        <p>{row['company_name']} | 📞 {row['phone']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Bu rotada doğrudan yük yok.")

        # 2. ADIM (FIRSAT KARTI - DÜZELTİLDİ)
        st.subheader(f"2. {target_city} ➝ ? ({T['res_chain']})")
        
        if not leg1.empty and not leg2.empty:
            st.success(f"🤖 {T['chain_expl']}")
            for _, row in leg2.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="ai-card">
                        <h4>⚡ FIRSAT: {target_city} ➝ {row['destination_city']}</h4>
                        <p><b>📦 Yük:</b> {row['cargo_description']}</p>
                        <p>Bu yükü alırsan, hiç boş beklemeden yola devam edersin!</p>
                    </div>
                    """, unsafe_allow_html=True)
        elif leg1.empty:
            st.write("İlk bacakta yük olmadığı için zincir kurulamadı.")
        else:
            st.info(f"{target_city} şehrinden çıkan bir yük henüz yok. Dönüş yükü için beklemede kalın.")

# ==========================================
# SAYFA 4: PAZAR & OTOMATİK DURUM GÜNCELLEME
# ==========================================
elif page_index == 3:
    st.title("📊 Canlı Pazar & Takip")
    
    # OTOMATİK KONUM GÜNCELLEME SİMÜLASYONU
    with st.expander("📍 Sürücü Durum Simülasyonu (Otomatik Takip)"):
        st.write("Senaryo: Sürücü yükü indirdi. Sistem onu yeni şehirde 'Boş' olarak işaretlemeli.")
        
        with engine.connect() as conn:
            drivers = pd.read_sql("SELECT * FROM transporters_v4 WHERE destination_city != ''", conn)
        
        if not drivers.empty:
            driver_dict = {f"{row['contact_name']} ({row['origin_city']}->{row['destination_city']})": (row['phone'], row['destination_city']) for _, row in drivers.iterrows()}
            selected_driver_key = st.selectbox("Yükü Boşaltan Sürücü:", list(driver_dict.keys()))
            
            if st.button(T["btn_complete"]):
                phone_num, new_loc = driver_dict[selected_driver_key]
                if update_driver_location(phone_num, new_loc):
                    st.success(f"{T['success_complete']} Yeni Konum: {new_loc}")
                    st.rerun()
        else:
            st.info("Şu an yolda olan (varış yeri girilmiş) sürücü yok. 'İlan Ver' kısmından yeni bir iş başlatın.")
            
    # HARİTA
    try:
        with engine.connect() as conn:
            trucks_df = pd.read_sql("SELECT * FROM transporters_v4 ORDER BY created_at DESC", conn)
        
        if not trucks_df.empty:
            map_data = []
            for _, row in trucks_df.iterrows():
                city = row['origin_city']
                if city in TR_CITIES:
                    map_data.append({'lat': TR_CITIES[city][0], 'lon': TR_CITIES[city][1]})
            st.map(pd.DataFrame(map_data), zoom=5)
            st.dataframe(trucks_df[['contact_name', 'origin_city', 'destination_city', 'status', 'vehicle_type']], use_container_width=True)
    except Exception:
        st.error("Veri hatası.")
