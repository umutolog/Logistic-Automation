import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="LogiMatch B2B",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE MANAGEMENT (HARDCODED FIX)
# ==========================================

@st.cache_resource
def get_db_engine():
    """
    Creates the SQLAlchemy engine using the DIRECT LINK to bypass secrets issues.
    """
    try:
        # BURASI KRİTİK NOKTA: Şifreyi ve Linki direkt buraya yazdık.
        # Streamlit artık başka yere bakamaz.
        db_url = "postgresql://postgres.yzjzgkwwkinmtprqhudn:KzVzeHNAnoEoAetH@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"
        
        engine = create_engine(db_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"❌ Critical Error: Could not connect to database. {e}")
        st.stop()

def init_db(engine):
    """Creates tables if they don't exist."""
    create_transporters = """
    CREATE TABLE IF NOT EXISTS transporters (
        id SERIAL PRIMARY KEY,
        contact_name TEXT NOT NULL,
        phone TEXT,
        vehicle_type TEXT,
        origin_city TEXT NOT NULL,
        destination_city TEXT NOT NULL,
        date_available DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_shippers = """
    CREATE TABLE IF NOT EXISTS shippers (
        id SERIAL PRIMARY KEY,
        company_name TEXT NOT NULL,
        phone TEXT,
        cargo_weight INT,
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
        st.error(f"Database Initialization Failed: {e}")

# Initialize Database
engine = get_db_engine()
init_db(engine)

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def clean_input(text_input):
    return text_input.strip().upper() if text_input else ""

def save_to_db(table_name, data_dict):
    try:
        df = pd.DataFrame([data_dict])
        df.to_sql(table_name, engine, if_exists='append', index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {e}")
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
        st.error(f"Error finding matches: {e}")
        return pd.DataFrame()

# ==========================================
# 4. UI STRUCTURE
# ==========================================

st.sidebar.title("🚚 LogiMatch Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🚛 I am a Transporter", "📦 I am a Shipper", "📊 Live Market"]
)
st.sidebar.markdown("---")
st.sidebar.info("System Status: 🟢 Online\n\nDatabase: Supabase (Direct Link)")

# ==========================================
# 5. PAGE LOGIC: TRANSPORTER
# ==========================================
if page == "🚛 I am a Transporter":
    st.title("🚛 Transporter Operations")
    st.markdown("Post your empty truck location and find cargo instantly.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Post Truck")
        with st.form("transporter_form"):
            name = st.text_input("Driver/Company Name")
            phone = st.text_input("Phone Number")
            vehicle = st.selectbox("Vehicle Type", ["Van", "Box Truck", "Semi-Trailer", "Flatbed", "Refrigerated"])
            origin = st.text_input("Origin City (e.g. New York)")
            dest = st.text_input("Destination City (e.g. Boston)")
            date_avail = st.date_input("Available Date", min_value=datetime.today())
            
            submit_truck = st.form_submit_button("Post Availability & Search")
            
    with col2:
        if submit_truck:
            if not name or not origin or not dest:
                st.warning("⚠️ Please fill in Name, Origin, and Destination.")
            else:
                c_origin = clean_input(origin)
                c_dest = clean_input(dest)
                
                data = {
                    "contact_name": name,
                    "phone": phone,
                    "vehicle_type": vehicle,
                    "origin_city": c_origin,
                    "destination_city": c_dest,
                    "date_available": date_avail
                }
                
                if save_to_db("transporters", data):
                    st.success("✅ Truck Posted Successfully!")
                    
                    st.divider()
                    st.subheader(f"🔍 Cargo Matches: {c_origin} ➝ {c_dest}")
                    matches = find_matches("shippers", c_origin, c_dest)
                    
                    if not matches.empty:
                        st.dataframe(
                            matches[['company_name', 'cargo_weight', 'date_required', 'phone']], 
                            use_container_width=True,
                            hide_index=True
                        )
                        st.info(f"🎉 Found {len(matches)} active cargo loads for this route!")
                    else:
                        st.warning("No immediate matches found. We will notify you when a shipper posts this route.")

# ==========================================
# 6. PAGE LOGIC: SHIPPER
# ==========================================
elif page == "📦 I am a Shipper":
    st.title("📦 Shipper Operations")
    st.markdown("Post your cargo details and find available trucks instantly.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📝 Post Cargo")
        with st.form("shipper_form"):
            company = st.text_input("Company Name")
            phone = st.text_input("Contact Phone")
            weight = st.number_input("Cargo Weight (kg)", min_value=1, step=100)
            origin = st.text_input("Origin City")
            dest = st.text_input("Destination City")
            date_req = st.date_input("Required Date", min_value=datetime.today())
            
            submit_cargo = st.form_submit_button("Post Cargo & Search")
            
    with col2:
        if submit_cargo:
            if not company or not origin or not dest:
                st.warning("⚠️ Please fill in Company, Origin, and Destination.")
            else:
                c_origin = clean_input(origin)
                c_dest = clean_input(dest)
                
                data = {
                    "company_name": company,
                    "phone": phone,
                    "cargo_weight": weight,
                    "origin_city": c_origin,
                    "destination_city": c_dest,
                    "date_required": date_req
                }
                
                if save_to_db("shippers", data):
                    st.success("✅ Cargo Posted Successfully!")
                    
                    st.divider()
                    st.subheader(f"🔍 Truck Matches: {c_origin} ➝ {c_dest}")
                    matches = find_matches("transporters", c_origin, c_dest)
                    
                    if not matches.empty:
                        st.dataframe(
                            matches[['contact_name', 'vehicle_type', 'date_available', 'phone']],
                            use_container_width=True,
                            hide_index=True
                        )
                        st.info(f"🎉 Found {len(matches)} trucks available for this route!")
                    else:
                        st.warning("No immediate matches found. We will notify you when a transporter posts this route.")

# ==========================================
# 7. PAGE LOGIC: LIVE MARKET
# ==========================================
elif page == "📊 Live Market":
    st.title("📊 Live Market Overview")
    st.markdown("Real-time view of all active demands and capacities in the network.")
    
    try:
        with engine.connect() as conn:
            trucks_df = pd.read_sql("SELECT * FROM transporters ORDER BY created_at DESC LIMIT 50", conn)
            shippers_df = pd.read_sql("SELECT * FROM shippers ORDER BY created_at DESC LIMIT 50", conn)
            
        t_col, s_col = st.columns(2)
        
        with t_col:
            st.markdown(f"### 🚛 Available Trucks ({len(trucks_df)})")
            if not trucks_df.empty:
                st.dataframe(trucks_df[['origin_city', 'destination_city', 'vehicle_type', 'date_available']], use_container_width=True, hide_index=True)
            else:
                st.info("No trucks listed yet.")
            
        with s_col:
            st.markdown(f"### 📦 Cargo Loads ({len(shippers_df)})")
            if not shippers_df.empty:
                st.dataframe(shippers_df[['origin_city', 'destination_city', 'cargo_weight', 'date_required']], use_container_width=True, hide_index=True)
            else:
                st.info("No cargo listed yet.")
            
    except Exception as e:
        st.error(f"Could not load market data: {e}")
