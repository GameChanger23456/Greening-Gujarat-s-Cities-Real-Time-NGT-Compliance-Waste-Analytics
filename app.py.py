"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       GUJARAT URBAN DEVELOPMENT MISSION                                      ║
║       NGT Compliance Monitoring Dashboard  v3.0                              ║
║       Original Application No. 606/2018 — National Green Tribunal            ║
║                                                                              ║
║  Developed by : Gundu Chaitanya Venkatesh                                    ║
║  Role         : Sustainability Project Analyst Intern                        ║
║  Education    : MSc Analytics, Tata Institute of Social Sciences (TISS),     ║
║                 Mumbai  |  Student ID: M2025ANL013                           ║
║                                                                              ║
║  Organisations: Urban Development & Urban Housing Dept. (UDD), Govt. of     ║
║                 Gujarat | Gujarat Urban Development Mission (GUDM)           ║
║                 Gujarat Urban Development Co. Ltd. (GUDC)                   ║
║                 Swachh Bharat Mission–Urban (SBM-U) | GPCB | AMRUT 2.0      ║
║                                                                              ║
║  Data Sources : UDD Gujarat (udd.gujarat.gov.in)                            ║
║                 GUDM (gudm.gujarat.gov.in)                                   ║
║                 GPCB (gpcb.gujarat.gov.in)                                   ║
║                 SBM-U (sbm.gov.in) | MoHUA (mohua.gov.in)                   ║
║                 NGT (ngt.gov.in) | AMRUT 2.0 | Smart City Mission           ║
║                 World Bank Gujarat Resilient Cities Project (P175728)        ║
║                                                                              ║
║  Version: 3.0  |  Last Updated: June 2026                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────── PAGE CONFIG ─────────────────────────────────────
st.set_page_config(
    page_title="Gujarat Urban NGT Compliance Dashboard | GUDM",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://udd.gujarat.gov.in',
        'About': "Gujarat Urban Development Mission — NGT Compliance Dashboard v4.0\nDeveloped by Gundu Chaitanya Venkatesh, MSc Analytics, TISS Mumbai"
    }
)

# ═══════════════════ CREDENTIALS ═════════════════════════════════════════════
VALID_USERS = {
    "10626": {"password": "gudm", "name": "Gundu Chaitanya Venkatesh",
              "role": "Sustainability Project Analyst Intern", "org": "GUDM / UDD, Govt. of Gujarat"}
}

# ═══════════════════ SESSION STATE INIT ══════════════════════════════════════
if "logged_in"    not in st.session_state: st.session_state.logged_in    = False
if "user_id"      not in st.session_state: st.session_state.user_id      = ""
if "login_error"  not in st.session_state: st.session_state.login_error  = ""
if "edit_mode"    not in st.session_state: st.session_state.edit_mode    = False
if "ulb_edits"    not in st.session_state: st.session_state.ulb_edits    = {}
if "save_msg"     not in st.session_state: st.session_state.save_msg     = ""
if "login_ts"     not in st.session_state: st.session_state.login_ts     = None

# ═══════════════════ LOGIN PAGE ═══════════════════════════════════════════════
def show_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* hide sidebar on login */
    section[data-testid="stSidebar"] { display: none; }

    .login-bg {
        background: linear-gradient(135deg, #FF6B35 0%, #004E89 55%, #006B3C 100%);
        min-height: 100vh;
        display: flex; align-items: center; justify-content: center;
    }
    .login-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 44px 48px 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.28);
        max-width: 440px;
        width: 100%;
        margin: auto;
    }
    .login-logo {
        text-align: center;
        margin-bottom: 6px;
    }
    .login-logo .emoji { font-size: 2.8rem; }
    .login-logo .org-name {
        font-size: 1.05rem; font-weight: 700;
        color: #004E89; margin-top: 6px; line-height: 1.3;
    }
    .login-logo .sub {
        font-size: 0.78rem; color: #888; margin-top: 3px;
    }
    .login-divider {
        height: 2px;
        background: linear-gradient(90deg, #FF6B35, #004E89, #006B3C);
        border: none; border-radius: 2px;
        margin: 18px 0 26px;
    }
    .login-title {
        font-size: 1.22rem; font-weight: 600;
        color: #1a252f; margin-bottom: 22px; text-align: center;
    }
    .login-footer {
        font-size: 0.72rem; color: #aaa;
        text-align: center; margin-top: 20px; line-height: 1.6;
    }
    .error-box {
        background: #fde8e8; border-left: 4px solid #cb4335;
        border-radius: 8px; padding: 10px 14px;
        font-size: 0.84rem; color: #922b21; margin-bottom: 14px;
    }
    .success-box {
        background: #d5f5e3; border-left: 4px solid #1e8449;
        border-radius: 8px; padding: 10px 14px;
        font-size: 0.84rem; color: #1a6e3e; margin-bottom: 14px;
    }
    div[data-testid="stTextInput"] input {
        border: 1.5px solid #d0d7de !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 0.94rem !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #004E89 !important;
        box-shadow: 0 0 0 3px rgba(0,78,137,0.1) !important;
    }
    div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
    div[data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        background: linear-gradient(135deg, #004E89, #FF6B35) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        margin-top: 8px !important;
        transition: opacity 0.2s !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover { opacity: 0.9 !important; }
    </style>
    """, unsafe_allow_html=True)

    # Centred narrow column layout
    _, centre, _ = st.columns([1, 1.4, 1])
    with centre:
        st.markdown("""
        <div class="login-card">
          <div class="login-logo">
            <div class="emoji">🌿</div>
            <div class="org-name">Gujarat Urban Development Mission</div>
            <div class="sub">NGT Compliance Monitoring Dashboard</div>
          </div>
          <hr class="login-divider">
          <div class="login-title">🔒 Secure Login — Authorised Users Only</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.login_error:
            st.markdown(f'<div class="error-box">❌ {st.session_state.login_error}</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            uid  = st.text_input("🪪  User ID", placeholder="Enter your User ID", key="uid_input")
            pwd  = st.text_input("🔑  Password", type="password", placeholder="Enter your password", key="pwd_input")
            submitted = st.form_submit_button("Login to Dashboard →")

        if submitted:
            uid  = uid.strip()
            pwd  = pwd.strip()
            if uid in VALID_USERS and VALID_USERS[uid]["password"] == pwd:
                st.session_state.logged_in   = True
                st.session_state.user_id     = uid
                st.session_state.login_error = ""
                st.session_state.login_ts    = datetime.now()
                st.rerun()
            else:
                st.session_state.login_error = "Invalid User ID or Password. Please try again."
                st.rerun()

        st.markdown("""
        <div class="login-footer">
            Original Application No. 606/2018 · National Green Tribunal<br>
            UDD Gujarat · GUDM · GPCB · SBM-U · GUDC<br>
            Developed by Gundu Chaitanya Venkatesh · MSc Analytics, TISS Mumbai
        </div>
        """, unsafe_allow_html=True)

# ─── Gate: show login if not authenticated ───────────────────────────────────
if not st.session_state.logged_in:
    show_login()
    st.stop()

# ─── User info shortcut ───────────────────────────────────────────────────────
_uid = st.session_state.get("user_id", "")

print("UID =", repr(_uid))

_user = VALID_USERS.get(_uid)

if _user is None:
    print(f"Invalid user ID: {_uid}")

    _user = {
        "name": "Guest User",
        "org": "Guest Access",
        "role": "guest",
        "department": "N/A"
    }
# ─────────────────────────── CSS STYLING ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.main-header {
    background: linear-gradient(135deg, #FF6B35 0%, #004E89 60%, #006B3C 100%);
    padding: 22px 28px 18px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.18);
}
.main-header h1 { font-size: 1.9rem; margin: 0; font-weight: 700; letter-spacing: 0.3px; }
.main-header h2 { font-size: 1.05rem; margin: 4px 0 0; font-weight: 400; opacity: 0.9; }
.main-header p  { font-size: 0.82rem; margin: 6px 0 0; opacity: 0.85; }

/* ── Badge row ── */
.badge-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 0.5px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.74rem;
    color: #e8f4fd;
}
.badge.live { background: #1e8449; border-color: #27ae60; }

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff;
    border-left: 5px solid #004E89;
    border-radius: 10px;
    padding: 15px 18px 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    margin-bottom: 6px;
}
.kpi-card.green  { border-left-color: #1e8449; }
.kpi-card.amber  { border-left-color: #d4ac0d; }
.kpi-card.red    { border-left-color: #cb4335; }
.kpi-card.teal   { border-left-color: #117a65; }
.kpi-card.orange { border-left-color: #FF6B35; }
.kpi-val  { font-size: 1.75rem; font-weight: 700; color: #1a252f; line-height: 1.1; }
.kpi-lbl  { font-size: 0.75rem; color: #626567; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px; }
.kpi-sub  { font-size: 0.70rem; color: #95a5a6; margin-top: 4px; }

/* ── Section headers ── */
.sec-head {
    font-size: 1.15rem; font-weight: 600;
    color: #004E89; letter-spacing: 0.3px;
    border-bottom: 2.5px solid #FF6B35;
    padding-bottom: 5px; margin: 22px 0 14px;
}

/* ── Status pills ── */
.pill-compliant    { background: #d5f5e3; color: #1e8449; padding: 3px 11px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.pill-partial      { background: #fef9e7; color: #b7950b; padding: 3px 11px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
.pill-noncompliant { background: #fde8e8; color: #cb4335; padding: 3px 11px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }

/* ── Info box ── */
.info-box {
    background: #eaf4fd; border-left: 4px solid #2980b9;
    border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;
    font-size: 0.83rem; color: #1a3a4a;
}
.warn-box {
    background: #fef9e7; border-left: 4px solid #d4ac0d;
    border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;
    font-size: 0.83rem; color: #4a3500;
}

/* ── Timeline ── */
.timeline-item {
    border-left: 3px solid #FF6B35;
    padding: 8px 16px; margin: 8px 0;
    background: #fdf6f0; border-radius: 0 8px 8px 0;
}
.timeline-item .t-date { font-size: 0.73rem; color: #FF6B35; font-weight: 600; }
.timeline-item .t-text { font-size: 0.84rem; color: #1a252f; margin-top: 2px; }
.timeline-item .t-detail { font-size: 0.76rem; color: #666; margin-top: 3px; }

/* ── Phase boxes ── */
.phase-box {
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    color: white;
}
.phase-box .ph-n { font-size: 1.1rem; font-weight: 700; }
.phase-box .ph-t { font-size: 0.72rem; opacity: 0.85; margin: 3px 0; }
.phase-box .ph-d { font-size: 0.8rem; margin-top: 6px; line-height: 1.4; }

/* ── Data table ── */
.data-table-header {
    background: #004E89; color: white;
    font-size: 0.78rem; font-weight: 600;
    padding: 8px 10px; text-align: left;
}

/* ── Footer ── */
.footer {
    text-align: center; padding: 22px;
    color: #666; font-size: 0.88em;
    border-top: 2px solid #004E89;
    margin-top: 40px; background: #f8f9fa;
    border-radius: 8px;
}
.footer strong { color: #004E89; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #002D62; }
section[data-testid="stSidebar"] * { color: #d6eaf8 !important; }
section[data-testid="stSidebar"] .stSelectbox > label { color: #aed6f1 !important; }
section[data-testid="stSidebar"] a { color: #5dade2 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { font-size: 0.87rem; font-weight: 500; }
.stTabs [aria-selected="true"] { color: #FF6B35 !important; }

/* ── Divider ── */
hr { border-color: #e0e0e0; margin: 18px 0; }

/* ── Metric override ── */
div[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #1a252f !important; }
div[data-testid="stMetricLabel"] { font-size: 0.82rem !important; color: #626567 !important; }

/* ── Edit mode banner ── */
.edit-banner {
    background: linear-gradient(90deg, #d4ac0d, #b7950b);
    color: #fff; padding: 9px 18px;
    border-radius: 8px; margin-bottom: 14px;
    font-size: 0.86rem; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
    box-shadow: 0 2px 8px rgba(183,149,11,0.25);
}
.view-banner {
    background: linear-gradient(90deg, #1e8449, #117a65);
    color: #fff; padding: 9px 18px;
    border-radius: 8px; margin-bottom: 14px;
    font-size: 0.86rem; font-weight: 500;
    display: flex; align-items: center; gap: 10px;
}
.save-success {
    background: #d5f5e3; border-left: 4px solid #1e8449;
    border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;
    font-size: 0.84rem; color: #1a6e3e; font-weight: 500;
}
.edit-section {
    background: #fef9e7; border: 1.5px dashed #d4ac0d;
    border-radius: 10px; padding: 16px 18px; margin-bottom: 14px;
}
.user-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.18); border: 0.5px solid rgba(255,255,255,0.35);
    border-radius: 20px; padding: 4px 12px; font-size: 0.76rem; color: #e8f4fd;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════ MASTER DATA (Official Sources) ═════════════════════

# Real-world base data from UDD Gujarat, GUDM, World Bank GRCP P175728, AMRUT 2.0,
# SBM-U annual reports, GPCB records & NGT compliance filings OA 606/2018

ULB_BASE = {
    # Municipal Corporations (8 MCs)
    "Ahmedabad Municipal Corporation":  {
        "type": "Municipal Corporation", "region": "Central Gujarat",
        "pop_lakh": 80.0, "area_sqkm": 464,
        "sew_gen": 580, "stp_cap": 615, "stp_util": 78.5,
        "stp_nos": 5, "stp_status": "Operational",
        "hh_target": 180000, "hh_actual": 165000,
        "open_drains": 12, "drain_flow": 8.5,
        "ugd_status": "UGD Work Completed",
        "discharge": "Sabarmati River",
        "funded_by": "World Bank / AMRUT 2.0",
        "waste_gen": 780, "waste_coll": 94.5, "waste_proc": 72.0,
        "recycling": 28.5, "landfill": 3, "legacy": 35000,
        "wte_status": "250 TPD / 7.5 MW Operational (Jul 2022)",
        "swm_vehicles": 320, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": True, "amrut": True,
        "notes": "375 MLD Vasna STP upgrade underway (World Bank P175728); 240 MLD STP operational"
    },
    "Surat Municipal Corporation": {
        "type": "Municipal Corporation", "region": "South Gujarat",
        "pop_lakh": 70.0, "area_sqkm": 326,
        "sew_gen": 490, "stp_cap": 520, "stp_util": 84.0,
        "stp_nos": 4, "stp_status": "Operational",
        "hh_target": 160000, "hh_actual": 148000,
        "open_drains": 8, "drain_flow": 5.2,
        "ugd_status": "Under Expansion",
        "discharge": "Tapi River",
        "funded_by": "Smart City Mission / AMRUT 2.0",
        "waste_gen": 620, "waste_coll": 92.0, "waste_proc": 68.5,
        "recycling": 25.0, "landfill": 2, "legacy": 28000,
        "wte_status": "1200 TPD RDF–WtE Plant Approved (M/s Abellon)",
        "swm_vehicles": 280, "lw_status": "Compliant", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": True, "amrut": True,
        "notes": "Water+ certificate (2022); 2000 TPD centralised processing plant planning stage"
    },
    "Vadodara Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Central Gujarat",
        "pop_lakh": 22.0, "area_sqkm": 235,
        "sew_gen": 280, "stp_cap": 310, "stp_util": 87.0,
        "stp_nos": 3, "stp_status": "Operational",
        "hh_target": 90000, "hh_actual": 81000,
        "open_drains": 6, "drain_flow": 3.1,
        "ugd_status": "UGD Work Completed",
        "discharge": "Vishwamitri River",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 380, "waste_coll": 95.0, "waste_proc": 75.0,
        "recycling": 32.0, "landfill": 2, "legacy": 18000,
        "wte_status": "300 TPD Plant Operational",
        "swm_vehicles": 165, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": True, "amrut": True,
        "notes": "67 MLD additional STP capacity added under Smart City; 113.31 km new sewer lines"
    },
    "Rajkot Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Saurashtra",
        "pop_lakh": 18.0, "area_sqkm": 170,
        "sew_gen": 175, "stp_cap": 190, "stp_util": 91.6,
        "stp_nos": 3, "stp_status": "Operational",
        "hh_target": 65000, "hh_actual": 60000,
        "open_drains": 5, "drain_flow": 2.0,
        "ugd_status": "UGD Work Completed",
        "discharge": "Aji River / Treated Reuse",
        "funded_by": "AMRUT 2.0 / Smart City",
        "waste_gen": 250, "waste_coll": 96.0, "waste_proc": 78.0,
        "recycling": 35.5, "landfill": 2, "legacy": 12000,
        "wte_status": "200 TPD Processing – Active",
        "swm_vehicles": 120, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": True, "amrut": True,
        "notes": "Hirasar Greenfield Airport (Rs 1,405 Cr); 464 electric city buses inducted"
    },
    "Bhavnagar Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Saurashtra",
        "pop_lakh": 10.0, "area_sqkm": 107,
        "sew_gen": 80, "stp_cap": 90, "stp_util": 72.0,
        "stp_nos": 2, "stp_status": "Partial",
        "hh_target": 38000, "hh_actual": 30000,
        "open_drains": 7, "drain_flow": 5.8,
        "ugd_status": "Under Construction",
        "discharge": "Arabian Sea Outfall",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 145, "waste_coll": 88.0, "waste_proc": 62.0,
        "recycling": 18.0, "landfill": 2, "legacy": 7500,
        "wte_status": "DPR Stage",
        "swm_vehicles": 68, "lw_status": "Partial", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "UDAN scheme connectivity improvement; AMRUT Mitra SHG projects approved"
    },
    "Jamnagar Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Saurashtra",
        "pop_lakh": 9.5, "area_sqkm": 113,
        "sew_gen": 75, "stp_cap": 85, "stp_util": 68.0,
        "stp_nos": 2, "stp_status": "Under Expansion",
        "hh_target": 35000, "hh_actual": 26000,
        "open_drains": 9, "drain_flow": 7.2,
        "ugd_status": "Tender Floated",
        "discharge": "Drainage Network",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 130, "waste_coll": 85.0, "waste_proc": 58.0,
        "recycling": 15.0, "landfill": 2, "legacy": 6800,
        "wte_status": "Planning Stage",
        "swm_vehicles": 60, "lw_status": "Partial", "sw_status": "Non-Compliant",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "New city bus service started; UDAN scheme regional connectivity improved"
    },
    "Gandhinagar Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Central Gujarat",
        "pop_lakh": 3.5, "area_sqkm": 205,
        "sew_gen": 42, "stp_cap": 55, "stp_util": 95.0,
        "stp_nos": 2, "stp_status": "Operational",
        "hh_target": 22000, "hh_actual": 21500,
        "open_drains": 3, "drain_flow": 0.8,
        "ugd_status": "UGD Work Completed",
        "discharge": "Treated Water Reuse",
        "funded_by": "GUDM / AMRUT 2.0",
        "waste_gen": 68, "waste_coll": 97.0, "waste_proc": 88.0,
        "recycling": 42.0, "landfill": 1, "legacy": 3200,
        "wte_status": "Operational – Solar STP Integration",
        "swm_vehicles": 42, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": True, "amrut": True,
        "notes": "Smart city — 464 electric buses; Solar plants at STP; Dahod under Smart City Mission"
    },
    "Junagadh Municipal Corporation": {
        "type": "Municipal Corporation", "region": "Saurashtra",
        "pop_lakh": 6.0, "area_sqkm": 79,
        "sew_gen": 35, "stp_cap": 40, "stp_util": 74.0,
        "stp_nos": 1, "stp_status": "Partial",
        "hh_target": 18000, "hh_actual": 13500,
        "open_drains": 6, "drain_flow": 4.1,
        "ugd_status": "DPR Stage",
        "discharge": "Drainage Network",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 58, "waste_coll": 82.0, "waste_proc": 55.0,
        "recycling": 12.0, "landfill": 2, "legacy": 9000,
        "wte_status": "Bio-remediation: 2×300 TPD Trommel Machines",
        "swm_vehicles": 38, "lw_status": "Partial", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "Legacy waste bio-remediation with 300 TPD trommel machines; KESHOD airport UDAN"
    },
    # Municipalities (RCMs)
    "Anand Municipality": {
        "type": "Municipality (RCM)", "region": "Central Gujarat",
        "pop_lakh": 2.1, "area_sqkm": 35,
        "sew_gen": 18, "stp_cap": 22, "stp_util": 81.8,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 8000, "hh_actual": 6800,
        "open_drains": 4, "drain_flow": 2.1,
        "ugd_status": "Under Construction",
        "discharge": "Mahi River",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 35, "waste_coll": 91.0, "waste_proc": 65.0,
        "recycling": 20.0, "landfill": 1, "legacy": 4500,
        "wte_status": "Planned",
        "swm_vehicles": 18, "lw_status": "Compliant", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "AMRUT Mitra: Rs 303.62 Cr approved across 27 ULBs; SHG projects active"
    },
    "Mehsana Municipality": {
        "type": "Municipality (RCM)", "region": "North Gujarat",
        "pop_lakh": 1.8, "area_sqkm": 22,
        "sew_gen": 15, "stp_cap": 18, "stp_util": 77.8,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 7000, "hh_actual": 5800,
        "open_drains": 5, "drain_flow": 2.8,
        "ugd_status": "Under Construction",
        "discharge": "Drainage",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 28, "waste_coll": 88.0, "waste_proc": 60.0,
        "recycling": 17.0, "landfill": 1, "legacy": 3800,
        "wte_status": "Planned",
        "swm_vehicles": 15, "lw_status": "Partial", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "CNG bus service started (660 old replacement + 133 new buses approved)"
    },
    "Navsari Municipality": {
        "type": "Municipality (RCM)", "region": "South Gujarat",
        "pop_lakh": 1.7, "area_sqkm": 24,
        "sew_gen": 14, "stp_cap": 16, "stp_util": 86.3,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 6500, "hh_actual": 5900,
        "open_drains": 3, "drain_flow": 1.8,
        "ugd_status": "UGD Work Completed",
        "discharge": "Purna River",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 25, "waste_coll": 93.0, "waste_proc": 70.0,
        "recycling": 22.0, "landfill": 1, "legacy": 3100,
        "wte_status": "Composting Active",
        "swm_vehicles": 14, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": False, "amrut": True,
        "notes": "Navsari: Good ODF++ standing; new city bus service under CMUBS scheme"
    },
    "Morbi Municipality": {
        "type": "Municipality (RCM)", "region": "Saurashtra",
        "pop_lakh": 1.9, "area_sqkm": 28,
        "sew_gen": 16, "stp_cap": 18, "stp_util": 51.0,
        "stp_nos": 1, "stp_status": "Under Construction",
        "hh_target": 7500, "hh_actual": 4800,
        "open_drains": 6, "drain_flow": 4.5,
        "ugd_status": "DPR Stage",
        "discharge": "Drainage",
        "funded_by": "State Fund / AMRUT 2.0",
        "waste_gen": 30, "waste_coll": 79.0, "waste_proc": 48.0,
        "recycling": 10.0, "landfill": 2, "legacy": 5200,
        "wte_status": "Not Commissioned",
        "swm_vehicles": 14, "lw_status": "Non-Compliant", "sw_status": "Non-Compliant",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": False,
        "notes": "Priority focus — STP expansion critical; CNG bus service started"
    },
    "Surendranagar Municipality": {
        "type": "Municipality (RCM)", "region": "Saurashtra",
        "pop_lakh": 1.5, "area_sqkm": 20,
        "sew_gen": 13, "stp_cap": 15, "stp_util": 73.3,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 6000, "hh_actual": 4500,
        "open_drains": 5, "drain_flow": 3.2,
        "ugd_status": "Tender Floated",
        "discharge": "Drainage",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 22, "waste_coll": 84.0, "waste_proc": 58.0,
        "recycling": 14.0, "landfill": 1, "legacy": 3600,
        "wte_status": "Planned",
        "swm_vehicles": 12, "lw_status": "Partial", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "New city bus service started under CMUBS; Surendranagar–Dudhrej municipality"
    },
    "Bharuch Municipality": {
        "type": "Municipality (RCM)", "region": "South Gujarat",
        "pop_lakh": 1.6, "area_sqkm": 22,
        "sew_gen": 14, "stp_cap": 17, "stp_util": 82.4,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 6200, "hh_actual": 5500,
        "open_drains": 4, "drain_flow": 2.3,
        "ugd_status": "UGD Work Completed",
        "discharge": "Narmada River tributary",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 24, "waste_coll": 90.0, "waste_proc": 68.0,
        "recycling": 21.0, "landfill": 1, "legacy": 3400,
        "wte_status": "Composting Active",
        "swm_vehicles": 13, "lw_status": "Compliant", "sw_status": "Compliant",
        "odf_plus": True, "odf_plusplus": True,
        "smart_city": False, "amrut": True,
        "notes": "New city bus service; AMRUT Mitra SHG projects engaged"
    },
    "Valsad Municipality": {
        "type": "Municipality (RCM)", "region": "South Gujarat",
        "pop_lakh": 1.4, "area_sqkm": 20,
        "sew_gen": 12, "stp_cap": 14, "stp_util": 78.6,
        "stp_nos": 1, "stp_status": "Operational",
        "hh_target": 5500, "hh_actual": 4800,
        "open_drains": 4, "drain_flow": 2.0,
        "ugd_status": "Under Construction",
        "discharge": "Drainage",
        "funded_by": "AMRUT 2.0",
        "waste_gen": 20, "waste_coll": 89.0, "waste_proc": 64.0,
        "recycling": 19.0, "landfill": 1, "legacy": 2800,
        "wte_status": "Planned",
        "swm_vehicles": 11, "lw_status": "Compliant", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": True,
        "notes": "Vapi nearby CETP integration studies underway"
    },
    "Porbandar Municipality": {
        "type": "Municipality (RCM)", "region": "Saurashtra",
        "pop_lakh": 1.3, "area_sqkm": 18,
        "sew_gen": 11, "stp_cap": 13, "stp_util": 69.2,
        "stp_nos": 1, "stp_status": "Partial",
        "hh_target": 5000, "hh_actual": 3800,
        "open_drains": 5, "drain_flow": 3.5,
        "ugd_status": "DPR Stage",
        "discharge": "Arabian Sea",
        "funded_by": "State Fund",
        "waste_gen": 18, "waste_coll": 83.0, "waste_proc": 52.0,
        "recycling": 13.0, "landfill": 1, "legacy": 2500,
        "wte_status": "Not Commissioned",
        "swm_vehicles": 10, "lw_status": "Partial", "sw_status": "Partial",
        "odf_plus": True, "odf_plusplus": False,
        "smart_city": False, "amrut": False,
        "notes": "Porbandar airport UDAN connectivity; new bus service started"
    },
}

ULB_NAMES = list(ULB_BASE.keys())

# ─── Apply any user edits stored in session state ────────────────────────────
# When a logged-in user saves changes, values are written to st.session_state.ulb_edits
# {ulb_name: {field: new_value, ...}} — these override ULB_BASE for the session.
def get_ulb(name):
    """Return ULB dict with any session-state edits overlaid."""
    base = dict(ULB_BASE[name])
    if name in st.session_state.ulb_edits:
        base.update(st.session_state.ulb_edits[name])
    return base

def apply_edit(ulb_name, field, value):
    if ulb_name not in st.session_state.ulb_edits:
        st.session_state.ulb_edits[ulb_name] = {}
    st.session_state.ulb_edits[ulb_name][field] = value

# Build DataFrames
def build_lw_df():
    rows = []
    for name in ULB_BASE:
        d = get_ulb(name)
        hh_pct = round(d["hh_actual"] / d["hh_target"] * 100, 1)
        treated = round(d["stp_cap"] * d["stp_util"] / 100, 1)
        gap_treat = round(max(0, d["sew_gen"] - treated), 1)
        rows.append({
            "ULB Name": name,
            "Type": d["type"],
            "Region": d["region"],
            "Population (Lakh)": d["pop_lakh"],
            "Area (sq.km)": d["area_sqkm"],
            "Sewage Generation (MLD)": d["sew_gen"],
            "STPs (Nos.)": d["stp_nos"],
            "STP Installed Capacity (MLD)": d["stp_cap"],
            "STP Utilization (%)": d["stp_util"],
            "Treated Water (MLD)": treated,
            "Gap – Treatment (MLD)": gap_treat,
            "Targeted HH Connections": d["hh_target"],
            "Actual HH Connections": d["hh_actual"],
            "HH Connection (%)": hh_pct,
            "HH Gap": d["hh_target"] - d["hh_actual"],
            "Open Drains (Nos.)": d["open_drains"],
            "Flow in Open Drain (MLD)": d["drain_flow"],
            "UGD Status": d["ugd_status"],
            "STP Status": d["stp_status"],
            "Discharge Point": d["discharge"],
            "Funding Source": d["funded_by"],
            "Compliance Status": d["lw_status"],
        })
    return pd.DataFrame(rows)

def build_sw_df():
    rows = []
    for name in ULB_BASE:
        d = get_ulb(name)
        daily = d["waste_gen"]
        coll = round(daily * d["waste_coll"] / 100, 1)
        uncoll = round(daily - coll, 1)
        proc = round(daily * d["waste_proc"] / 100, 1)
        rows.append({
            "ULB Name": name,
            "Type": d["type"],
            "Region": d["region"],
            "Daily Waste Generation (TPD)": daily,
            "Waste Collected (TPD)": coll,
            "Waste Not Collected (TPD)": uncoll,
            "Waste Collection Rate (%)": d["waste_coll"],
            "Waste Processing Rate (%)": d["waste_proc"],
            "Waste Processed (TPD)": proc,
            "Recycling Rate (%)": d["recycling"],
            "Waste to Landfill (%)": round(100 - d["waste_proc"], 1),
            "Landfill Sites (Nos.)": d["landfill"],
            "Legacy Waste (MT)": d["legacy"],
            "SWM Vehicles": d["swm_vehicles"],
            "WtE Status": d["wte_status"],
            "ODF+ Certified": "Yes" if d["odf_plus"] else "No",
            "ODF++ Certified": "Yes" if d["odf_plusplus"] else "No",
            "Smart City": "Yes" if d["smart_city"] else "No",
            "AMRUT 2.0": "Yes" if d["amrut"] else "No",
            "Compliance Status": d["sw_status"],
        })
    return pd.DataFrame(rows)

lw_df = build_lw_df()
sw_df = build_sw_df()

# State aggregates (from official UDD/GUDM records)
STATE_STATS = {
    "total_ulbs": 159,
    "tracked_ulbs": 16,
    "sewage_total_mld": 2000,
    "odf_plus_cities": 159,
    "odf_plusplus_cities": 134,
    "water_plus_cities": 1,
    "smart_cities": 6,
    "amrut_cities": 31,
    "urban_budget_cr": 21067,
    "amrut_water_cr": 630.39,
    "amrut_sewerage_cr": 575.58,
    "new_stp_mld": 67,
    "new_sewer_km": 113.31,
    "hh_water_2025": 82328,
    "hh_sewerage_2025": 24206,
    "smart_city_projects": 357,
    "smart_city_value_cr": 11507,
    "dtod_coverage": 95.1,
    "swachh_ranking_stars": {"1 Star": 64, "3 Stars": 90, "5 Stars": 6, "7 Stars": 3},
}

# NGT Compliance submissions
NGT_SUBMISSIONS = [
    {
        "date": "22 Feb 2023",
        "title": "First Compliance Report under OA 606/2018",
        "detail": "Liquid & solid waste status across Gujarat ULBs submitted to Hon'ble NGT; initial gap of 17.26 MLD liquid waste treatment identified"
    },
    {
        "date": "22 Jul 2025",
        "title": "Mid-Term Review Submission",
        "detail": "Updated STP utilisation, HH connection data and SWM processing rates; project-wise progress on UGD works"
    },
    {
        "date": "01 Sep 2025",
        "title": "State-Level Compliance Status",
        "detail": "GUDM (liquid waste) and SBM-U (solid waste) consolidated compliance data submitted; GPCB verification complete"
    },
    {
        "date": "19 Mar 2026",
        "title": "Latest Affidavit Filed",
        "detail": "Q4 2025 compliance data, project progress, gap-closure action plans and digital mechanism rollout status"
    },
]

# Colour palette
CLR = {
    "compliant": "#1e8449", "partial": "#d4ac0d", "non": "#cb4335",
    "blue1": "#004E89", "blue2": "#2980b9", "orange": "#FF6B35",
    "teal": "#117a65", "light": "#aed6f1",
}

def c_status(s):
    m = {"Compliant": CLR["compliant"], "Partial": CLR["partial"], "Non-Compliant": CLR["non"]}
    return m.get(s, CLR["partial"])

def pill(s):
    cls = {"Compliant": "pill-compliant", "Partial": "pill-partial", "Non-Compliant": "pill-noncompliant"}
    return f'<span class="{cls.get(s, "pill-partial")}">{s}</span>'

def kpi(val, label, sub="", colour=""):
    return f"""<div class="kpi-card {colour}">
        <div class="kpi-val">{val}</div>
        <div class="kpi-lbl">{label}</div>
        {'<div class="kpi-sub">'+sub+'</div>' if sub else ''}
    </div>"""


# ════════════════════════════ SIDEBAR ════════════════════════════════════════

with st.sidebar:
    # ── User info chip ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:14px 0 4px">
        <div style="font-size:1.4rem;font-weight:700;color:#aed6f1;">🌿 GUDM</div>
        <div style="font-size:0.75rem;color:#7fb3d3;margin-top:2px;">NGT Compliance Dashboard</div>
        <div style="font-size:0.68rem;color:#5d8fa8;margin-top:3px;">OA No. 606/2018</div>
    </div>
    <div style="margin:10px 4px;background:rgba(255,255,255,0.08);border-radius:10px;padding:10px 12px;">
        <div style="font-size:0.70rem;color:#aed6f1;text-transform:uppercase;letter-spacing:.5px;">Logged In As</div>
        <div style="font-size:0.85rem;color:#fff;font-weight:600;margin-top:3px;">{_user['name']}</div>
        <div style="font-size:0.72rem;color:#7fb3d3;margin-top:2px;">{_user['role']}</div>
        <div style="font-size:0.70rem;color:#5d8fa8;margin-top:1px;">ID: {_uid} · {_user['org']}</div>
        <div style="font-size:0.68rem;color:#5d8fa8;margin-top:2px;">
            Session started: {st.session_state.login_ts.strftime('%d %b %Y, %H:%M') if st.session_state.login_ts else '—'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Edit Mode toggle ──────────────────────────────────────────────────────
    st.markdown("**✏️ Data Edit Mode**")
    edit_toggle = st.toggle(
        "Enable Data Editing",
        value=st.session_state.edit_mode,
        help="When ON, you can edit ULB data values directly in the ULB Deep Dive tab."
    )
    if edit_toggle != st.session_state.edit_mode:
        st.session_state.edit_mode = edit_toggle
        st.session_state.save_msg = ""
        st.rerun()

    if st.session_state.ulb_edits:
        total_edits = sum(len(v) for v in st.session_state.ulb_edits.values())
        st.markdown(f"<div style='font-size:0.74rem;color:#d4ac0d;margin-top:4px;'>⚠️ {total_edits} unsaved field(s) modified this session</div>", unsafe_allow_html=True)
        if st.button("🗑️ Reset All Edits", use_container_width=True):
            st.session_state.ulb_edits = {}
            st.session_state.save_msg  = "All edits reset to original values."
            st.rerun()

    st.divider()

    st.markdown("**📅 Quarter**")
    quarter = st.selectbox("Quarter", [
        "Q1 2026 (Jan–Mar)", "Q4 2025 (Oct–Dec)",
        "Q3 2025 (Jul–Sep)", "Q2 2025 (Apr–Jun)"
    ], label_visibility="collapsed")

    st.markdown("**🏙️ Urban Local Body**")
    ulb_type_filter = st.radio("Show", ["All ULBs", "Municipal Corporations", "Municipalities (RCMs)"],
                               label_visibility="collapsed")
    if ulb_type_filter == "Municipal Corporations":
        filtered_names = [n for n, d in ULB_BASE.items() if "Corporation" in d["type"]]
    elif ulb_type_filter == "Municipalities (RCMs)":
        filtered_names = [n for n, d in ULB_BASE.items() if "Municipality" in d["type"]]
    else:
        filtered_names = ULB_NAMES

    selected_ulb = st.selectbox("Select ULB", filtered_names, label_visibility="collapsed")

    st.markdown("**🗺️ Region**")
    regions = ["All"] + sorted({d["region"] for d in ULB_BASE.values()})
    selected_region = st.selectbox("Region", regions, label_visibility="collapsed")

    st.divider()
    st.markdown("**📤 Upload Data (Optional)**")
    up_lw = st.file_uploader("Liquid Waste Excel", type=["xlsx", "xls"], key="up_lw")
    up_sw = st.file_uploader("Solid Waste Excel",  type=["xlsx", "xls"], key="up_sw")
    if up_lw:
        try:
            lw_df = pd.read_excel(up_lw)
            st.success("✅ Liquid waste data loaded")
        except Exception as e:
            st.error(f"Error: {e}")
    if up_sw:
        try:
            sw_df = pd.read_excel(up_sw)
            st.success("✅ Solid waste data loaded")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem;color:#7fb3d3;line-height:2.0;">
    <b style="color:#aed6f1;">🔗 Official Portals</b><br>
    <a href="https://udd.gujarat.gov.in"    >UDD Gujarat</a><br>
    <a href="https://gudm.gujarat.gov.in"   >GUDM</a><br>
    <a href="https://gpcb.gujarat.gov.in"   >GPCB</a><br>
    <a href="https://sbm.gov.in"            >SBM-U</a><br>
    <a href="https://mohua.gov.in"          >MoHUA</a><br>
    <a href="https://www.ngt.gov.in"        >NGT Portal</a><br>
    <a href="https://amrut.gov.in"          >AMRUT 2.0</a><br>
    <a href="https://smartcities.gov.in"    >Smart City Mission</a>
    </div>""", unsafe_allow_html=True)

    st.divider()
    # ── Logout ────────────────────────────────────────────────────────────────
    if st.button("🚪 Logout", use_container_width=True):
        for key in ["logged_in","user_id","login_error","edit_mode","ulb_edits","save_msg","login_ts"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("""
    <div style="font-size:0.71rem;color:#7fb3d3;line-height:1.7;margin-top:6px;">
    <b style="color:#aed6f1;">👤 Developer</b><br>
    Gundu Chaitanya Venkatesh<br>
    MSc Analytics · TISS Mumbai<br>
    ID: M2025ANL013 · v4.0
    </div>""", unsafe_allow_html=True)


# ═════════════════════════ HEADER ════════════════════════════════════════════

st.markdown(f"""
<div class="main-header">
    <h1>🌿 Gujarat Urban Development Mission</h1>
    <h2>NGT Compliance Monitoring Dashboard — Liquid & Solid Waste Management</h2>
    <p>Original Application No. 606/2018 · National Green Tribunal · 159 Urban Local Bodies · Government of Gujarat</p>
    <div class="badge-row">
        <span class="badge live">● Q1 2026 Live</span>
        <span class="badge">UDD · GUDM · GPCB · SBM-U · GUDC</span>
        <span class="badge">Urban Development Year 2025</span>
        <span class="badge">AMRUT 2.0 · Smart City Mission</span>
        <span class="badge">Budget FY 2024–25: ₹21,067 Cr</span>
        <span class="badge">World Bank GRCP P175728</span>
        <span class="user-chip">👤 {_user['name']} · {_uid}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Edit / View mode banner ───────────────────────────────────────────────────
if st.session_state.edit_mode:
    st.markdown("""
    <div class="edit-banner">
        ✏️ <strong>EDIT MODE ACTIVE</strong> — You can now modify ULB data values in the ULB Deep Dive tab.
        Changes are highlighted and applied live across all charts. Use "Save Changes" to confirm.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="view-banner">
        👁️ <strong>VIEW MODE</strong> — Logged in as <strong>{_user['name']}</strong> ({_uid}).
        Enable <em>Data Editing</em> in the sidebar to modify ULB values.
    </div>""", unsafe_allow_html=True)

if st.session_state.save_msg:
    st.markdown(f'<div class="save-success">✅ {st.session_state.save_msg}</div>', unsafe_allow_html=True)

# ── State-level KPI row ───────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
lw_comp  = (lw_df["Compliance Status"]=="Compliant").sum()
lw_part  = (lw_df["Compliance Status"]=="Partial").sum()
lw_non   = (lw_df["Compliance Status"]=="Non-Compliant").sum()
avg_util = lw_df["STP Utilization (%)"].mean()
avg_coll = sw_df["Waste Collection Rate (%)"].mean()

with c1: st.markdown(kpi("159", "Total ULBs", "Gujarat State"), unsafe_allow_html=True)
with c2: st.markdown(kpi("2,000 MLD", "Total Sewage Gen.", "159 ULBs — UDD Gujarat", "teal"), unsafe_allow_html=True)
with c3: st.markdown(kpi(str(lw_comp), "LW Compliant", f"{lw_comp/len(lw_df)*100:.0f}% of tracked", "green"), unsafe_allow_html=True)
with c4: st.markdown(kpi(str(lw_part), "Partial", "Follow-up needed", "amber"), unsafe_allow_html=True)
with c5: st.markdown(kpi(str(lw_non), "Non-Compliant", "Immediate action", "red"), unsafe_allow_html=True)
with c6: st.markdown(kpi(f"{avg_util:.1f}%", "Avg STP Util.", "Tracked ULBs", ""), unsafe_allow_html=True)
with c7: st.markdown(kpi("₹575.58 Cr", "Sewerage Projects", "AMRUT 2.0 / 2025", "orange"), unsafe_allow_html=True)
with c8: st.markdown(kpi("67 MLD", "New STP Capacity", "Created in 2025", "teal"), unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>📢 Gujarat Urban Development Year 2025:</strong> 357+ projects worth ₹11,507 Cr completed under Smart City Mission (Ahmedabad, Surat, Vadodara, Rajkot, Gandhinagar, Dahod). 
    Under AMRUT 2.0 — water supply projects ₹630.39 Cr (82,328 HH), sewerage ₹575.58 Cr (24,206 HH), 67 MLD new STP capacity, 113.31 km new sewer lines. 
    159 cities ODF+ certified; 134 cities ODF++; Surat — India's only Water+ city (2022). Source: UDD Gujarat / CMO Gujarat, March 2026.
</div>
""", unsafe_allow_html=True)

st.divider()

# ════════════════════════ MAIN TABS ══════════════════════════════════════════

tab_home, tab_lw, tab_sw, tab_proj, tab_comp, tab_data, tab_timeline = st.tabs([
    "🏙️ ULB Deep Dive",
    "💧 Liquid Waste — All ULBs",
    "🗑️ Solid Waste — All ULBs",
    "🏗️ Projects & Schemes",
    "📊 Comparative Analysis",
    "📋 Data Tables & Export",
    "📅 NGT Timeline"
])

# ─────────────────────── TAB 1 : ULB DEEP DIVE ───────────────────────────────
with tab_home:
    d = get_ulb(selected_ulb)
    lw_row = lw_df[lw_df["ULB Name"]==selected_ulb].iloc[0]
    sw_row = sw_df[sw_df["ULB Name"]==selected_ulb].iloc[0]

    st.markdown(f'<div class="sec-head">📍 {selected_ulb} — {quarter}</div>', unsafe_allow_html=True)
    st.markdown(
        f"**Type:** {d['type']}  |  **Region:** {d['region']}  |  "
        f"**Population:** {d['pop_lakh']} lakh  |  **Area:** {d['area_sqkm']} sq.km  |  "
        f"**LW Status:** {pill(d['lw_status'])}  |  **SW Status:** {pill(d['sw_status'])}",
        unsafe_allow_html=True
    )
    if d["notes"]:
        st.markdown(f'<div class="info-box">📌 {d["notes"]}</div>', unsafe_allow_html=True)

    # ── EDIT FORM (only shown when edit_mode is True) ─────────────────────────
    if st.session_state.edit_mode:
        st.markdown('<div class="edit-section">', unsafe_allow_html=True)
        st.markdown(f"### ✏️ Edit Data — {selected_ulb}")
        st.caption("Modify the values below and click **Save Changes** to apply. Charts and KPIs update immediately.")

        with st.form(key=f"edit_form_{selected_ulb}"):
            st.markdown("**💧 Liquid Waste Parameters**")
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1:
                e_sew_gen  = st.number_input("Sewage Generation (MLD)", value=float(d["sew_gen"]),  min_value=0.0, step=0.5, format="%.1f")
                e_hh_target= st.number_input("Targeted HH Connections", value=int(d["hh_target"]),  min_value=0,   step=100)
            with ec2:
                e_stp_cap  = st.number_input("STP Installed Capacity (MLD)", value=float(d["stp_cap"]),  min_value=0.0, step=0.5, format="%.1f")
                e_hh_actual= st.number_input("Actual HH Connections",  value=int(d["hh_actual"]),  min_value=0,   step=100)
            with ec3:
                e_stp_util = st.number_input("STP Utilization (%)",    value=float(d["stp_util"]),  min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
                e_open_drains=st.number_input("Open Drains (Nos.)",    value=int(d["open_drains"]), min_value=0,   step=1)
            with ec4:
                e_stp_nos  = st.number_input("STPs (Nos.)",            value=int(d["stp_nos"]),     min_value=0,   step=1)
                e_drain_flow=st.number_input("Flow in Open Drain (MLD)",value=float(d["drain_flow"]),min_value=0.0,step=0.1, format="%.1f")

            ec5, ec6, ec7 = st.columns(3)
            with ec5:
                e_ugd_status = st.selectbox("UGD Project Status", [
                    "UGD Work Completed","Under Expansion","Under Construction",
                    "Tender Floated","DPR Stage","Survey Stage"
                ], index=["UGD Work Completed","Under Expansion","Under Construction",
                          "Tender Floated","DPR Stage","Survey Stage"].index(d["ugd_status"])
                    if d["ugd_status"] in ["UGD Work Completed","Under Expansion","Under Construction",
                                           "Tender Floated","DPR Stage","Survey Stage"] else 0)
            with ec6:
                e_stp_status = st.selectbox("STP Project Status", [
                    "Operational","Under Expansion","Under Construction","Partial","Planned"
                ], index=["Operational","Under Expansion","Under Construction","Partial","Planned"].index(d["stp_status"])
                    if d["stp_status"] in ["Operational","Under Expansion","Under Construction","Partial","Planned"] else 0)
            with ec7:
                e_lw_status  = st.selectbox("LW Compliance Status", ["Compliant","Partial","Non-Compliant"],
                    index=["Compliant","Partial","Non-Compliant"].index(d["lw_status"]))

            st.markdown("**🗑️ Solid Waste Parameters**")
            sw1, sw2, sw3, sw4 = st.columns(4)
            with sw1:
                e_waste_gen  = st.number_input("Daily Waste Gen. (TPD)",   value=float(d["waste_gen"]),  min_value=0.0, step=1.0,  format="%.1f")
                e_legacy     = st.number_input("Legacy Waste (MT)",         value=float(d["legacy"]),     min_value=0.0, step=100.0,format="%.0f")
            with sw2:
                e_waste_coll = st.number_input("Waste Collection (%)",     value=float(d["waste_coll"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
                e_swm_vehicles=st.number_input("SWM Vehicles",             value=int(d["swm_vehicles"]), min_value=0,   step=1)
            with sw3:
                e_waste_proc = st.number_input("Waste Processing (%)",     value=float(d["waste_proc"]), min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
                e_sw_status  = st.selectbox("SW Compliance Status", ["Compliant","Partial","Non-Compliant"],
                    index=["Compliant","Partial","Non-Compliant"].index(d["sw_status"]))
            with sw4:
                e_recycling  = st.number_input("Recycling Rate (%)",       value=float(d["recycling"]),  min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
                e_odf_plus   = st.checkbox("ODF+ Certified",   value=bool(d["odf_plus"]))
                e_odf_pp     = st.checkbox("ODF++ Certified",  value=bool(d["odf_plusplus"]))

            e_notes = st.text_area("Project Notes / Remarks", value=d["notes"], height=68)

            save_col, reset_col, _ = st.columns([1,1,3])
            with save_col:
                saved = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with reset_col:
                reset_one = st.form_submit_button("↺ Reset This ULB", use_container_width=True)

        if saved:
            apply_edit(selected_ulb, "sew_gen",     e_sew_gen)
            apply_edit(selected_ulb, "stp_cap",     e_stp_cap)
            apply_edit(selected_ulb, "stp_util",    e_stp_util)
            apply_edit(selected_ulb, "stp_nos",     e_stp_nos)
            apply_edit(selected_ulb, "hh_target",   e_hh_target)
            apply_edit(selected_ulb, "hh_actual",   e_hh_actual)
            apply_edit(selected_ulb, "open_drains", e_open_drains)
            apply_edit(selected_ulb, "drain_flow",  e_drain_flow)
            apply_edit(selected_ulb, "ugd_status",  e_ugd_status)
            apply_edit(selected_ulb, "stp_status",  e_stp_status)
            apply_edit(selected_ulb, "lw_status",   e_lw_status)
            apply_edit(selected_ulb, "waste_gen",   e_waste_gen)
            apply_edit(selected_ulb, "waste_coll",  e_waste_coll)
            apply_edit(selected_ulb, "waste_proc",  e_waste_proc)
            apply_edit(selected_ulb, "recycling",   e_recycling)
            apply_edit(selected_ulb, "legacy",      e_legacy)
            apply_edit(selected_ulb, "swm_vehicles",e_swm_vehicles)
            apply_edit(selected_ulb, "sw_status",   e_sw_status)
            apply_edit(selected_ulb, "odf_plus",    e_odf_plus)
            apply_edit(selected_ulb, "odf_plusplus", e_odf_pp)
            apply_edit(selected_ulb, "notes",       e_notes)
            st.session_state.save_msg = (
                f"Changes saved for {selected_ulb} by {_user['name']} ({_uid}) "
                f"at {datetime.now().strftime('%H:%M:%S, %d %b %Y')}. "
                "All charts and KPIs updated."
            )
            st.rerun()

        if reset_one:
            if selected_ulb in st.session_state.ulb_edits:
                del st.session_state.ulb_edits[selected_ulb]
            st.session_state.save_msg = f"Data for {selected_ulb} reset to original values."
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Reload after potential edit
        d = get_ulb(selected_ulb)
        lw_df = build_lw_df()
        sw_df = build_sw_df()
        lw_row = lw_df[lw_df["ULB Name"]==selected_ulb].iloc[0]
        sw_row = sw_df[sw_df["ULB Name"]==selected_ulb].iloc[0]

    # KPI row
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    hhpct = lw_row["HH Connection (%)"]
    with k1: st.markdown(kpi(f"{lw_row['Sewage Generation (MLD)']} MLD", "Sewage Generated", "Daily", "teal"), unsafe_allow_html=True)
    with k2: st.markdown(kpi(f"{lw_row['Treated Water (MLD)']} MLD", "Sewage Treated", "At STPs daily", "green"), unsafe_allow_html=True)
    with k3: st.markdown(kpi(f"{lw_row['STP Utilization (%)']}%", "STP Utilisation", f"Target ≥80%", "green" if lw_row['STP Utilization (%)']>=80 else "amber"), unsafe_allow_html=True)
    with k4: st.markdown(kpi(f"{hhpct}%", "HH Connection Rate", f"{lw_row['Actual HH Connections']:,} / {lw_row['Targeted HH Connections']:,}", "green" if hhpct>=85 else "amber"), unsafe_allow_html=True)
    with k5: st.markdown(kpi(f"{sw_row['Waste Collection Rate (%)']:.0f}%", "Waste Collection", "Door-to-door", "green" if sw_row['Waste Collection Rate (%)']>=90 else "amber"), unsafe_allow_html=True)
    with k6: st.markdown(kpi(f"{sw_row['Waste Processing Rate (%)']:.0f}%", "Waste Processing", "At facilities", "green" if sw_row['Waste Processing Rate (%)']>=70 else "amber"), unsafe_allow_html=True)

    st.markdown("")

    # Row 1 — Liquid charts
    st.markdown('<div class="sec-head">💧 Liquid Waste Analysis</div>', unsafe_allow_html=True)
    lc1,lc2,lc3 = st.columns(3)

    with lc1:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=lw_row["STP Utilization (%)"],
            number={"suffix":"%","font":{"size":36,"color":"#1a252f"}},
            delta={"reference":80,"valueformat":".1f","suffix":"%"},
            title={"text":"STP Utilisation Rate","font":{"size":13}},
            gauge={
                "axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#626567"},
                "bar":{"color":CLR["blue1"]},
                "steps":[
                    {"range":[0,50],"color":"#fde8e8"},
                    {"range":[50,75],"color":"#fef9e7"},
                    {"range":[75,100],"color":"#d5f5e3"}
                ],
                "threshold":{"line":{"color":"crimson","width":3},"thickness":0.75,"value":80}
            }
        ))
        fig_g.update_layout(height=270,margin=dict(t=30,b=10,l=20,r=20))
        st.plotly_chart(fig_g, use_container_width=True)

    with lc2:
        treated = lw_row["Treated Water (MLD)"]
        gap_t   = lw_row["Gap – Treatment (MLD)"]
        fig_p = go.Figure(go.Pie(
            labels=["Treated","Treatment Gap"],
            values=[treated, gap_t],
            marker_colors=[CLR["teal"],CLR["non"]],
            hole=0.45, textinfo="label+value",
            texttemplate="%{label}<br>%{value:.1f} MLD"
        ))
        fig_p.update_layout(title_text="Sewage Treatment Status (MLD)",
                             height=270,margin=dict(t=40,b=5,l=5,r=5),showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

    with lc3:
        cap  = lw_row["STP Installed Capacity (MLD)"]
        util = lw_row["Treated Water (MLD)"]
        fig_cap = go.Figure()
        fig_cap.add_trace(go.Bar(
            x=["Installed Capacity","Treated","Gap"],
            y=[cap, util, max(0,cap-util)],
            marker_color=[CLR["blue1"],CLR["teal"],CLR["partial"]],
            text=[f"{cap:.1f}",f"{util:.1f}",f"{max(0,cap-util):.1f}"],
            textposition="outside",textfont_size=10
        ))
        fig_cap.update_layout(title_text="STP Capacity vs Utilisation (MLD)",
                               height=270,showlegend=False,
                               yaxis_title="MLD",margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig_cap, use_container_width=True)

    # HH connections
    lc4,lc5,lc6 = st.columns(3)
    with lc4:
        fig_hh = go.Figure()
        fig_hh.add_trace(go.Bar(
            x=["Targeted","Achieved","Gap (STP)","Gap (UGD)"],
            y=[lw_row["Targeted HH Connections"], lw_row["Actual HH Connections"],
               lw_row["HH Gap"], int(lw_row["HH Gap"]*0.5)],
            marker_color=[CLR["blue1"],CLR["teal"],CLR["partial"],CLR["non"]],
            text=[f"{int(v):,}" for v in [lw_row["Targeted HH Connections"],
                                           lw_row["Actual HH Connections"],
                                           lw_row["HH Gap"],int(lw_row["HH Gap"]*0.5)]],
            textposition="outside",textfont_size=9
        ))
        fig_hh.update_layout(title_text="Household Connections", height=260,
                              showlegend=False,
                              yaxis_title="Connections",margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig_hh, use_container_width=True)

    with lc5:
        st.metric("🚰 Open Drains", f"{lw_row['Open Drains (Nos.)']} Nos.")
        st.metric("🌊 Flow in Open Drains", f"{lw_row['Flow in Open Drain (MLD)']} MLD",
                  delta="Action Needed" if lw_row['Flow in Open Drain (MLD)']>5 else "Manageable",
                  delta_color="inverse" if lw_row['Flow in Open Drain (MLD)']>5 else "normal")
        st.metric("🏭 STPs", f"{lw_row['STPs (Nos.)']} Nos.")
        st.metric("🔧 UGD Status", lw_row["UGD Status"])

    with lc6:
        st.info(f"**STP Status:** {lw_row['STP Status']}")
        st.info(f"**Discharge Point:** {lw_row['Discharge Point']}")
        st.info(f"**Funding Source:** {lw_row['Funding Source']}")
        st.success(f"**Installed Capacity:** {lw_row['STP Installed Capacity (MLD)']} MLD")

    # Solid waste section
    st.markdown('<div class="sec-head">🗑️ Solid Waste Analysis</div>', unsafe_allow_html=True)
    sc1,sc2,sc3 = st.columns(3)

    with sc1:
        fig_sw_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sw_row["Waste Collection Rate (%)"],
            number={"suffix":"%"},
            title={"text":"Waste Collection Rate (%)"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":CLR["teal"]},
                "steps":[
                    {"range":[0,70],"color":"#fde8e8"},
                    {"range":[70,85],"color":"#fef9e7"},
                    {"range":[85,100],"color":"#d5f5e3"}
                ]
            }
        ))
        fig_sw_g.update_layout(height=260,margin=dict(t=30,b=10,l=20,r=20))
        st.plotly_chart(fig_sw_g, use_container_width=True)

    with sc2:
        gen = sw_row["Daily Waste Generation (TPD)"]
        coll = sw_row["Waste Collected (TPD)"]
        proc = sw_row["Waste Processed (TPD)"]
        land = round(gen - proc, 1)
        fig_sw_p = go.Figure(go.Pie(
            labels=["Processed","Recycled","To Landfill/Queue"],
            values=[proc, round(gen*sw_row["Recycling Rate (%)"]/100,1), max(0,land)],
            marker_colors=[CLR["teal"],CLR["blue2"],CLR["partial"]],
            hole=0.42, textinfo="label+value",
            texttemplate="%{label}<br>%{value:.0f} TPD"
        ))
        fig_sw_p.update_layout(title_text="Waste Disposal Pipeline (TPD)",
                               height=260,margin=dict(t=40,b=5,l=5,r=5),showlegend=False)
        st.plotly_chart(fig_sw_p, use_container_width=True)

    with sc3:
        fig_sw_b = go.Figure()
        fig_sw_b.add_trace(go.Bar(
            x=["Generated","Collected","Not Collected"],
            y=[gen,coll,gen-coll],
            marker_color=[CLR["blue1"],CLR["teal"],CLR["non"]],
            text=[f"{v:.0f} TPD" for v in [gen,coll,gen-coll]],
            textposition="outside",textfont_size=9
        ))
        fig_sw_b.update_layout(title_text="Daily Waste Collection Status",
                               height=260,showlegend=False,
                               yaxis_title="TPD",margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig_sw_b, use_container_width=True)

    sc4,sc5,sc6 = st.columns(3)
    with sc4:
        st.metric("♻️ Recycling Rate", f"{sw_row['Recycling Rate (%)']:.1f}%",
                  delta="Above Target" if sw_row['Recycling Rate (%)']>=25 else "Below 25% Target",
                  delta_color="normal" if sw_row['Recycling Rate (%)']>=25 else "inverse")
    with sc5:
        st.metric("🏔️ Legacy Waste", f"{sw_row['Legacy Waste (MT)']:,.0f} MT",
                  delta="Needs remediation")
    with sc6:
        st.metric("🚛 SWM Vehicles", f"{sw_row['SWM Vehicles']}")
    st.info(f"**WtE / Processing Status:** {sw_row['WtE Status']}  |  "
            f"**ODF+:** {'✅' if d['odf_plus'] else '❌'}  |  "
            f"**ODF++:** {'✅' if d['odf_plusplus'] else '❌'}  |  "
            f"**Smart City:** {'✅' if d['smart_city'] else '❌'}  |  "
            f"**AMRUT 2.0:** {'✅' if d['amrut'] else '❌'}")


# ─────────────────────── TAB 2 : LIQUID WASTE ALL ULBs ───────────────────────
with tab_lw:
    st.markdown('<div class="sec-head">💧 Liquid Waste Management — All ULBs</div>', unsafe_allow_html=True)
    if selected_region != "All":
        lw_show = lw_df[lw_df["Region"]==selected_region]
    else:
        lw_show = lw_df.copy()

    fig_util = px.bar(
        lw_show.sort_values("STP Utilization (%)"),
        x="STP Utilization (%)", y="ULB Name",
        orientation="h",
        color="STP Utilization (%)",
        color_continuous_scale=["#fde8e8","#fef9e7","#d5f5e3"],
        text=lw_show.sort_values("STP Utilization (%)")["STP Utilization (%)"].apply(lambda x: f"{x:.1f}%"),
        title="STP Utilisation Rate by ULB (%) — Target ≥80%",
    )
    fig_util.add_vline(x=80, line_dash="dash", line_color="crimson",
                       annotation_text="80% Target", annotation_position="top right")
    fig_util.update_layout(height=440,coloraxis_showscale=False,
                           xaxis_range=[0,115],margin=dict(l=240,t=50,r=30,b=20))
    fig_util.update_traces(textposition="outside")
    st.plotly_chart(fig_util, use_container_width=True)

    r1c1,r1c2 = st.columns(2)
    with r1c1:
        fig_sv = go.Figure()
        fig_sv.add_trace(go.Bar(name="Sewage Generated",
            x=lw_show["ULB Name"], y=lw_show["Sewage Generation (MLD)"],
            marker_color=CLR["blue2"]))
        fig_sv.add_trace(go.Bar(name="Treated Water",
            x=lw_show["ULB Name"], y=lw_show["Treated Water (MLD)"],
            marker_color=CLR["teal"]))
        fig_sv.update_layout(title="Sewage Generated vs Treated (MLD)",
                              barmode="group",height=380,
                              xaxis_tickangle=-45,margin=dict(b=120,t=50))
        st.plotly_chart(fig_sv, use_container_width=True)

    with r1c2:
        lw_show2 = lw_show.copy()
        lw_show2["HH Ach. (%)"] = (lw_show2["Actual HH Connections"]/lw_show2["Targeted HH Connections"]*100).round(1)
        fig_hh2 = px.scatter(
            lw_show2, x="Sewage Generation (MLD)", y="HH Ach. (%)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            size="STP Installed Capacity (MLD)", hover_name="ULB Name",
            text="ULB Name",
            title="Sewage Generation vs HH Connection Achievement"
        )
        fig_hh2.update_traces(textposition="top center",textfont_size=8)
        fig_hh2.update_layout(height=380,margin=dict(t=50))
        st.plotly_chart(fig_hh2, use_container_width=True)

    r2c1,r2c2 = st.columns(2)
    with r2c1:
        fig_od = px.bar(
            lw_show.sort_values("Flow in Open Drain (MLD)",ascending=False),
            x="ULB Name", y="Flow in Open Drain (MLD)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            title="Flow in Open Drains (MLD) — Priority Closure Required"
        )
        fig_od.add_hline(y=5, line_dash="dash", line_color="orange",
                         annotation_text="5 MLD Concern Level")
        fig_od.update_layout(height=360,xaxis_tickangle=-45,margin=dict(b=120,t=50))
        st.plotly_chart(fig_od, use_container_width=True)

    with r2c2:
        ugd_cnt = lw_show["UGD Status"].value_counts().reset_index()
        ugd_cnt.columns = ["Status","Count"]
        stp_cnt = lw_show["STP Status"].value_counts().reset_index()
        stp_cnt.columns = ["Status","Count"]
        fig_ugd = make_subplots(rows=1,cols=2,specs=[[{"type":"pie"},{"type":"pie"}]],
                                subplot_titles=["UGD Status","STP Status"])
        fig_ugd.add_trace(go.Pie(labels=ugd_cnt["Status"],values=ugd_cnt["Count"],
                                  hole=0.4,name="UGD",showlegend=False,
                                  marker_colors=px.colors.qualitative.Safe),row=1,col=1)
        fig_ugd.add_trace(go.Pie(labels=stp_cnt["Status"],values=stp_cnt["Count"],
                                  hole=0.4,name="STP",showlegend=False,
                                  marker_colors=px.colors.qualitative.Pastel),row=1,col=2)
        fig_ugd.update_layout(title_text="UGD & STP Project Status",height=360,margin=dict(t=60))
        st.plotly_chart(fig_ugd, use_container_width=True)


# ─────────────────────── TAB 3 : SOLID WASTE ALL ULBs ────────────────────────
with tab_sw:
    st.markdown('<div class="sec-head">🗑️ Solid Waste Management — All ULBs</div>', unsafe_allow_html=True)
    if selected_region != "All":
        sw_show = sw_df[sw_df["Region"]==selected_region] if "Region" in sw_df.columns else sw_df
    else:
        sw_show = sw_df.copy()

    fig_coll = px.bar(
        sw_show.sort_values("Waste Collection Rate (%)"),
        x="Waste Collection Rate (%)", y="ULB Name",
        orientation="h",
        color="Waste Collection Rate (%)",
        color_continuous_scale=["#fde8e8","#fef9e7","#d5f5e3"],
        text=sw_show.sort_values("Waste Collection Rate (%)")["Waste Collection Rate (%)"].apply(lambda x: f"{x:.0f}%"),
        title="Waste Collection Rate by ULB (%) — Source: SBM-U / UDD Gujarat"
    )
    fig_coll.add_vline(x=90, line_dash="dash", line_color="green",
                       annotation_text="90% Target",annotation_position="top right")
    fig_coll.update_layout(height=440,coloraxis_showscale=False,
                           xaxis_range=[0,110],margin=dict(l=240,t=50,r=30,b=20))
    fig_coll.update_traces(textposition="outside")
    st.plotly_chart(fig_coll, use_container_width=True)

    sw_r1c1,sw_r1c2 = st.columns(2)
    with sw_r1c1:
        fig_proc = px.bar(
            sw_show.sort_values("Waste Processing Rate (%)",ascending=False),
            x="ULB Name", y="Waste Processing Rate (%)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            title="Waste Processing Rate by ULB (%)"
        )
        fig_proc.add_hline(y=70,line_dash="dash",line_color="crimson",
                           annotation_text="70% Target",annotation_position="top right")
        fig_proc.update_layout(height=370,xaxis_tickangle=-45,margin=dict(b=120,t=50))
        st.plotly_chart(fig_proc, use_container_width=True)

    with sw_r1c2:
        fig_rec = px.scatter(
            sw_show, x="Recycling Rate (%)", y="Waste Processing Rate (%)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            size="Daily Waste Generation (TPD)", hover_name="ULB Name",
            title="Recycling Rate vs Processing Rate"
        )
        fig_rec.update_layout(height=370,margin=dict(t=50))
        st.plotly_chart(fig_rec, use_container_width=True)

    sw_r2c1,sw_r2c2 = st.columns(2)
    with sw_r2c1:
        fig_leg = px.bar(
            sw_show.sort_values("Legacy Waste (MT)",ascending=False),
            x="ULB Name", y="Legacy Waste (MT)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            title="Legacy Waste Pending Remediation (MT)"
        )
        fig_leg.update_layout(height=360,xaxis_tickangle=-45,margin=dict(b=120,t=50))
        st.plotly_chart(fig_leg, use_container_width=True)

    with sw_r2c2:
        sw_comp = sw_show["Compliance Status"].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=sw_comp.index, values=sw_comp.values,
            marker_colors=[c_status(s) for s in sw_comp.index],
            hole=0.5, textinfo="label+value",
            hovertemplate="%{label}: %{value} ULBs (%{percent})<extra></extra>"
        ))
        fig_donut.update_layout(title="Solid Waste Compliance Status",height=360,margin=dict(t=50))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown('<div class="sec-head">🌟 SBM-U Certification Status — Gujarat</div>', unsafe_allow_html=True)
    cert_c1,cert_c2,cert_c3,cert_c4 = st.columns(4)
    with cert_c1: st.metric("🏙️ ODF+ Cities",    "159", delta="All 159 ULBs")
    with cert_c2: st.metric("🌟 ODF++ Cities",   "134", delta="134 of 159 ULBs")
    with cert_c3: st.metric("💧 Water+ Certified","1 (Surat)", delta="Water Plus — 2022")
    with cert_c4: st.metric("📋 D2D Collection", "95.1%", delta="State Average")

    st.markdown("**Swachh Survekshan 2023 — Gujarat ULB Star Ratings:**")
    ss_data = pd.DataFrame({
        "Star Rating": ["1 Star","3 Stars","5 Stars","7 Stars"],
        "ULBs Applied": [64, 90, 6, 3]
    })
    fig_ss = px.bar(ss_data, x="Star Rating", y="ULBs Applied",
                    color="Star Rating",
                    color_discrete_sequence=["#aed6f1","#2980b9","#1a5276","#0a3d62"],
                    title="Swachh Survekshan 2023 — Gujarat ULB Star Ratings (164 ULBs)")
    fig_ss.update_layout(height=300,showlegend=False,margin=dict(t=50,b=20))
    st.plotly_chart(fig_ss, use_container_width=True)


# ─────────────────────── TAB 4 : PROJECTS & SCHEMES ──────────────────────────
with tab_proj:
    st.markdown('<div class="sec-head">🏗️ Major Projects & Schemes — Gujarat Urban Development</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>Urban Budget Growth:</strong> Gujarat's urban budget has grown from ₹175 Cr (2003) to ₹21,067 Cr (FY 2024–25) — a 120× increase over two decades.
    Gujarat celebrates 2025 as the <strong>Urban Development Year</strong> marking 20 years since PM Modi declared 2005 as "Urban Year". Source: CMO Gujarat / eGov, March 2026.
    </div>""", unsafe_allow_html=True)

    proj_c1,proj_c2 = st.columns(2)
    with proj_c1:
        scheme_data = pd.DataFrame({
            "Scheme": ["Urban Budget", "Smart City Mission", "AMRUT 2.0 Sewerage",
                       "AMRUT 2.0 Water Supply", "AMRUT Mitra Projects","World Bank GRCP"],
            "Amount (₹ Cr)": [21067, 11507, 575.58, 630.39, 303.62, 3168]
        })
        fig_scheme = px.bar(scheme_data, x="Amount (₹ Cr)", y="Scheme",
                            orientation="h",
                            color="Amount (₹ Cr)",
                            color_continuous_scale=["#aed6f1","#004E89"],
                            title="Scheme-wise Investment in Gujarat Urban (₹ Crore)")
        fig_scheme.update_layout(height=380,coloraxis_showscale=False,
                                  margin=dict(l=200,t=50,r=40,b=20))
        st.plotly_chart(fig_scheme, use_container_width=True)

    with proj_c2:
        amrut_data = pd.DataFrame({
            "Category": ["HH Water Connections","HH Sewerage Connections",
                         "New STP Capacity (MLD)","New Sewer Lines (km)"],
            "Achieved": [82328, 24206, 67, 113.31]
        })
        fig_amrut = px.bar(amrut_data, x="Achieved", y="Category",
                           orientation="h",
                           color="Category",
                           color_discrete_sequence=["#2980b9","#117a65","#1e8449","#004E89"],
                           title="AMRUT 2.0 Outcomes — Gujarat (2025)")
        fig_amrut.update_layout(height=380,showlegend=False,
                                 margin=dict(l=240,t=50,r=40,b=20))
        st.plotly_chart(fig_amrut, use_container_width=True)

    st.markdown('<div class="sec-head">🏭 UGD & STP Project Status — 16 Tracked ULBs</div>', unsafe_allow_html=True)
    proj_tbl = pd.DataFrame([{
        "ULB": name,
        "UGD Status": d["ugd_status"],
        "STP Status": d["stp_status"],
        "STP Cap (MLD)": d["stp_cap"],
        "Discharge Point": d["discharge"],
        "Funding": d["funded_by"],
        "WtE / Processing": d["wte_status"],
        "Smart City": "✅" if d["smart_city"] else "❌",
        "AMRUT 2.0": "✅" if d["amrut"] else "❌",
    } for name, d in ULB_BASE.items()])
    st.dataframe(proj_tbl, use_container_width=True, height=380)

    st.markdown('<div class="sec-head">🚀 Digital Compliance Mechanism — Implementation Phases</div>', unsafe_allow_html=True)
    ph_c1,ph_c2,ph_c3,ph_c4 = st.columns(4)
    phases = [
        ("Phase 1","15 Working Days","Historical data upload — LW & SW by all ULBs in UPM Dashboard",CLR["blue1"]),
        ("Phase 2","5 Working Days","Verification of historical data by competent authorities (RCM / MC Commissioner)",CLR["teal"]),
        ("Phase 3","10 Working Days","Current quarter data entry by ULBs — mandatory first 3 working days",CLR["partial"]),
        ("Phase 4","5 Working Days","Final verification, approval, and workflow stabilisation for NGT submission",CLR["compliant"]),
    ]
    for col, (ph,tm,desc,clr) in zip([ph_c1,ph_c2,ph_c3,ph_c4], phases):
        with col:
            st.markdown(f"""
            <div class="phase-box" style="background:{clr};">
                <div class="ph-n">{ph}</div>
                <div class="ph-t">⏱ {tm}</div>
                <div class="ph-d">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-head">👥 Stakeholder Roles & Responsibilities</div>', unsafe_allow_html=True)
    stake_data = pd.DataFrame({
        "Stakeholder": [
            "MC Chief Engineer / Designated Officer",
            "Municipal Commissioner",
            "Municipality Chief Officer / Officer",
            "Regional Commissioner of Municipalities (RCM)",
            "Gujarat Urban Development Mission (GUDM)",
            "Swachh Bharat Mission – Urban (SBM-U)",
            "Gujarat Pollution Control Board (GPCB)",
            "Urban Development Department (UDD)",
        ],
        "Role": [
            "Entry of verified LW & SW data for Municipal Corporation in UPM Dashboard portal",
            "Review and approval of MC data before forwarding to GUDM/SBM-U",
            "Data entry for respective Municipality — LW & SW parameters",
            "Coordination, review, rectification follow-up and data consolidation for municipalities",
            "Coordination and monitoring of liquid waste management parameters across all ULBs",
            "Coordination and monitoring of solid waste management parameters across all ULBs",
            "Verification of STP operational data; GPCB consent monitoring; NGT compliance review",
            "Overall coordination, affidavit preparation, and submission to National Green Tribunal",
        ],
        "Frequency": [
            "Quarterly (Days 1–3)", "Quarterly (Days 4–5)",
            "Quarterly (Days 1–3)", "Quarterly (Days 4–5)",
            "Quarterly + Monthly review", "Quarterly + Monthly review",
            "As per NGT directions", "As per NGT schedule"
        ]
    })
    st.dataframe(stake_data, use_container_width=True)


# ─────────────────────── TAB 5 : COMPARATIVE ANALYSIS ────────────────────────
with tab_comp:
    st.markdown('<div class="sec-head">📊 Comparative Analysis — All ULBs</div>', unsafe_allow_html=True)

    comp_tab1, comp_tab2, comp_tab3 = st.tabs([
        "Liquid Waste Comparison", "Solid Waste Comparison", "Compliance Dashboard"
    ])

    with comp_tab1:
        fig_comp_stp = px.bar(
            lw_df, x="ULB Name", y="STP Utilization (%)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            title="STP Utilisation Across All 16 ULBs (%)",
            height=400
        )
        fig_comp_stp.add_hline(y=80, line_dash="dash", line_color="crimson",
                               annotation_text="80% Target")
        fig_comp_stp.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_comp_stp, use_container_width=True)

        fig_comp_hh = px.bar(
            lw_df, x="ULB Name", y="HH Connection (%)",
            color="Type",
            title="HH Connection Achievement Rate (%) — All ULBs",
            height=400
        )
        fig_comp_hh.add_hline(y=85, line_dash="dash", line_color="green",
                              annotation_text="85% Target")
        fig_comp_hh.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_comp_hh, use_container_width=True)

    with comp_tab2:
        fig_comp_coll = px.bar(
            sw_df, x="ULB Name", y="Waste Collection Rate (%)",
            color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            title="Waste Collection Efficiency — All ULBs (%)",
            height=400
        )
        fig_comp_coll.add_hline(y=90, line_dash="dash", line_color="crimson",
                                annotation_text="90% Target")
        fig_comp_coll.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_comp_coll, use_container_width=True)

        fig_comp_sc = px.scatter(
            sw_df, x="Daily Waste Generation (TPD)", y="Waste Processing Rate (%)",
            size="Recycling Rate (%)", color="Compliance Status",
            color_discrete_map={"Compliant":CLR["compliant"],"Partial":CLR["partial"],"Non-Compliant":CLR["non"]},
            hover_name="ULB Name",
            title="Waste Generation vs Processing Rate (size = Recycling Rate)",
            height=400
        )
        st.plotly_chart(fig_comp_sc, use_container_width=True)

    with comp_tab3:
        # Overall compliance
        all_c = pd.concat([
            lw_df[["ULB Name","Compliance Status"]].assign(Category="Liquid Waste"),
            sw_df[["ULB Name","Compliance Status"]].assign(Category="Solid Waste")
        ])
        cc = all_c["Compliance Status"].value_counts()
        fig_ov = go.Figure(go.Pie(
            labels=cc.index, values=cc.values,
            marker_colors=[c_status(s) for s in cc.index],
            hole=0.5, textinfo="label+value",
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"
        ))
        fig_ov.update_layout(title="Overall Compliance Distribution (LW + SW, all 16 ULBs)",height=400,margin=dict(t=50))
        st.plotly_chart(fig_ov, use_container_width=True)

        c_pct = cc.get("Compliant",0)/len(all_c)*100
        p_pct = cc.get("Partial",0)/len(all_c)*100
        n_pct = cc.get("Non-Compliant",0)/len(all_c)*100
        mc1,mc2,mc3 = st.columns(3)
        with mc1: st.metric("✅ Fully Compliant", f"{c_pct:.1f}%")
        with mc2: st.metric("⚠️ Partially Compliant", f"{p_pct:.1f}%")
        with mc3: st.metric("❌ Non-Compliant", f"{n_pct:.1f}%")

        # Budget growth chart
        st.markdown("**Gujarat Urban Budget Growth (₹ Crore):**")
        bud = pd.DataFrame({
            "Year": ["2003","2010","2015","2018","2021","2023","2024-25"],
            "Urban Budget (₹ Cr)": [175, 2200, 5000, 9500, 14000, 18500, 21067]
        })
        fig_bud = px.line(bud, x="Year", y="Urban Budget (₹ Cr)",
                          markers=True,
                          title="Gujarat Urban Budget Growth (2003–2025) — Source: UDD Gujarat",
                          height=320)
        fig_bud.update_traces(line_color=CLR["orange"],marker_color=CLR["blue1"],line_width=2.5)
        fig_bud.update_layout(margin=dict(t=50,b=20))
        st.plotly_chart(fig_bud, use_container_width=True)


# ─────────────────────── TAB 6 : DATA TABLES & EXPORT ────────────────────────
with tab_data:
    st.markdown('<div class="sec-head">📋 Data Tables — ' + quarter + '</div>', unsafe_allow_html=True)

    def style_status(val):
        c = {"Compliant":"background-color:#d5f5e3;color:#1e8449",
             "Partial":"background-color:#fef9e7;color:#b7950b",
             "Non-Compliant":"background-color:#fde8e8;color:#cb4335"}
        return c.get(val,"")

    view = st.radio("View:", ["Liquid Waste Data","Solid Waste Data","Project Data","Summary"], horizontal=True)

    if view == "Liquid Waste Data":
        cols = ["ULB Name","Type","Region","Sewage Generation (MLD)","STP Installed Capacity (MLD)",
                "STP Utilization (%)","Treated Water (MLD)","Gap – Treatment (MLD)",
                "Targeted HH Connections","Actual HH Connections","HH Connection (%)","HH Gap",
                "Open Drains (Nos.)","Flow in Open Drain (MLD)",
                "UGD Status","STP Status","Discharge Point","Compliance Status"]
        st.dataframe(
        lw_df[cols].style.map(
            style_status,
            subset=["Compliance Status"]
        ),
        use_container_width=True,
        height=420
        )

    elif view == "Solid Waste Data":
        cols = ["ULB Name","Type","Region","Daily Waste Generation (TPD)",
                "Waste Collection Rate (%)","Waste Processing Rate (%)","Recycling Rate (%)",
                "Waste to Landfill (%)","Legacy Waste (MT)","SWM Vehicles",
                "WtE Status","ODF+ Certified","ODF++ Certified","Smart City","AMRUT 2.0","Compliance Status"]
        st.dataframe(sw_df[cols].style.applymap(style_status, subset=["Compliance Status"]),
                     use_container_width=True, height=420)

    elif view == "Project Data":
        proj_df2 = pd.DataFrame([{
            "ULB": n, "Type": d["type"], "Region": d["region"],
            "STP Cap (MLD)": d["stp_cap"], "UGD Status": d["ugd_status"],
            "STP Status": d["stp_status"], "Discharge": d["discharge"],
            "Funding": d["funded_by"], "WtE": d["wte_status"],
            "Notes": d["notes"]
        } for n, d in ULB_BASE.items()])
        st.dataframe(proj_df2, use_container_width=True, height=420)

    else:
        summary = pd.DataFrame({
            "ULB Name": lw_df["ULB Name"],
            "Region": lw_df["Region"],
            "STP Util (%)": lw_df["STP Utilization (%)"],
            "Treated (MLD)": lw_df["Treated Water (MLD)"],
            "HH Conn (%)": lw_df["HH Connection (%)"],
            "Waste Coll (%)": sw_df["Waste Collection Rate (%)"].values,
            "Waste Proc (%)": sw_df["Waste Processing Rate (%)"].values,
            "Recycling (%)": sw_df["Recycling Rate (%)"].values,
            "Legacy Waste (MT)": sw_df["Legacy Waste (MT)"].values,
            "LW Compliance": lw_df["Compliance Status"],
            "SW Compliance": sw_df["Compliance Status"].values,
        })
        st.dataframe(summary.style.applymap(style_status,subset=["LW Compliance","SW Compliance"]),
                     use_container_width=True, height=420)

    # Excel download
    st.markdown("")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        lw_df.to_excel(writer, sheet_name="Liquid Waste", index=False)
        sw_df.to_excel(writer, sheet_name="Solid Waste",  index=False)
        pd.DataFrame([{
            "Field":f,"Value":v} for f,v in {
            "Dashboard": "Gujarat Urban Development Mission — NGT Compliance Dashboard v3.0",
            "Regulatory Reference": "NGT Original Application No. 606/2018",
            "Prepared By": "Gundu Chaitanya Venkatesh",
            "Role": "Sustainability Project Analyst Intern",
            "Institution": "GUDM / UDD, Govt. of Gujarat",
            "Education": "MSc Analytics, TISS Mumbai | M2025ANL013",
            "Quarter": quarter,
            "Date Generated": datetime.now().strftime("%d-%b-%Y"),
            "Data Sources": "UDD Gujarat, GUDM, GPCB, SBM-U, MoHUA, NGT, World Bank GRCP P175728",
        }.items()]).to_excel(writer, sheet_name="Metadata", index=False)
    st.download_button(
        label="⬇ Download Complete Excel Report",
        data=buf.getvalue(),
        file_name=f"Gujarat_NGT_Compliance_{quarter.replace(' ','_')}_{datetime.now().strftime('%d%b%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Pre-submission checklist
    st.markdown('<div class="sec-head">✅ Pre-NGT Submission Checklist</div>', unsafe_allow_html=True)
    checks = [
        "All mandatory fields filled for each ULB (LW & SW parameters)",
        "Sewage generation figures consistent with UDD Gujarat records & population data",
        "STP utilisation verified against GPCB operational logs and consent orders",
        "Household connection data cross-verified with UGD project completion records",
        "Open drain flow data supported by field monitoring reports",
        "Solid waste generation validated against SWM vehicle trip logs & weighbridge data",
        "Collection & processing rates verified by SBM-U state team",
        "Legacy waste status updated with bio-remediation progress (trommel/composting)",
        "WtE plant status confirmed with operating agency (TPD & MW as applicable)",
        "ODF+ / ODF++ / Water+ certification status confirmed",
        "Historical comparison completed with all previous 4 NGT submissions",
        "RCM approval obtained for all municipalities",
        "GUDM consolidation completed for all liquid waste parameters",
        "SBM-U review completed for all solid waste parameters",
        "GPCB sign-off on STP operational data and discharge quality",
        "Supporting documents attached: field photos, lab reports, project status certificates",
        "Final data reviewed and signed by UDD before filing affidavit with NGT",
    ]
    for i, chk in enumerate(checks):
        st.checkbox(chk, key=f"chk_{i}")


# ─────────────────────── TAB 7 : NGT TIMELINE ────────────────────────────────
with tab_timeline:
    st.markdown('<div class="sec-head">📅 NGT Compliance Timeline — OA No. 606/2018</div>', unsafe_allow_html=True)

    for item in NGT_SUBMISSIONS:
        st.markdown(f"""
        <div class="timeline-item">
            <div class="t-date">📁 {item['date']}</div>
            <div class="t-text"><strong>{item['title']}</strong></div>
            <div class="t-detail">{item['detail']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="sec-head">🏛️ Regulatory & Legal Framework</div>', unsafe_allow_html=True)

    reg_c1, reg_c2 = st.columns(2)
    with reg_c1:
        st.markdown("""
**National Regulatory Bodies:**
- 🏛️ **National Green Tribunal (NGT)** — OA No. 606/2018
- 🌍 **Ministry of Housing & Urban Affairs (MoHUA)**
- ♻️ **MoEFCC** — Solid Waste Management Rules, 2016
- 💧 **CPCB** — Standards for treated effluent discharge

**Compliance Requirements:**
- NGT Discharge Standards: BOD ≤10 mg/L, TSS ≤20 mg/L, TN ≤10 mg/L
- Quarterly Data Submission — first 3 working days of each quarter
- Verification timeline — next 2 working days (RCM / MC Commissioner)
- GPCB consent monitoring for all operational STPs
        """)
    with reg_c2:
        st.markdown("""
**Gujarat State Bodies:**
- 🏗️ **UDD** — Urban Development & Urban Housing Department, GoG
- 🌱 **GUDM** — Gujarat Urban Development Mission
- 🏢 **GUDC** — Gujarat Urban Development Company Ltd. (Nodal)
- 🔬 **GPCB** — Gujarat Pollution Control Board (STP consent)
- 🧹 **SBM-U** — Swachh Bharat Mission–Urban

**Key Missions / Schemes:**
- AMRUT 2.0 (2021–26) — Water & sewerage infrastructure
- Smart City Mission — 6 Gujarat cities; 357+ projects
- Nirmal Gujarat 2.0 — SWM vehicles, Safai grant, processing
- Waste-to-Energy Policy 2016 — Gujarat GoG
- CMUBS — Chief Minister Urban Bus Services Scheme
        """)

    st.markdown('<div class="sec-head">🎯 Gujarat Vision 2030 Urban Targets</div>', unsafe_allow_html=True)
    target_c1,target_c2,target_c3,target_c4 = st.columns(4)
    with target_c1:
        st.metric("💧 Piped Water Supply", "100%", delta="Target by 2030")
        st.metric("♻️ Wastewater Recycling", "100%", delta="Target by 2030")
    with target_c2:
        st.metric("🏙️ STP Utilisation", "≥80%", delta="NGT Mandate")
        st.metric("🗑️ Waste Processing", "≥70%", delta="SBM-U Target")
    with target_c3:
        st.metric("🔌 Renewable Energy", "250 MW + 150 MW", delta="MCs + Municipalities")
        st.metric("🚌 Urban Buses", "2,864 Buses", delta="CMUBS Target")
    with target_c4:
        st.metric("🌟 ODF++ Cities", "All 159", delta="Vision 2030")
        st.metric("⚡ Solar at STPs/WTPs", "Net-Zero Target", delta="Gujarat Commitment")


# ═══════════════════════ FOOTER ══════════════════════════════════════════════

st.markdown(f"""
<div class="footer">
    <h4>Gujarat Urban Development Mission — NGT Compliance Monitoring Dashboard v4.0</h4>
    <p>
        <strong>Regulatory Basis:</strong> Original Application No. 606/2018 · National Green Tribunal ·
        <strong>Data Parameters:</strong> Annexure I (Liquid Waste) & Annexure II (Solid Waste) ·
        <strong>Portal:</strong> UPM Dashboard — GUDC &nbsp;|&nbsp;
        Integration: GUDM · SBM-U · GPCB · RCM · UDD
    </p>
    <hr style="border:0.5px solid #ddd;margin:12px 0;">
    <p>
        <strong>Developed by:</strong> Gundu Chaitanya Venkatesh &nbsp;|&nbsp;
        <strong>Role:</strong> Sustainability Project Analyst Intern &nbsp;|&nbsp;
        <strong>Education:</strong> MSc Analytics, Tata Institute of Social Sciences (TISS), Mumbai &nbsp;|&nbsp;
        <strong>Student ID:</strong> M2025ANL013 &nbsp;|&nbsp;
        <strong>Last Updated:</strong> June 2026
    </p>
    <p>
        <strong>Current Session:</strong> {_user['name']} (ID: {_uid}) ·
        Login: {st.session_state.login_ts.strftime('%d %b %Y, %H:%M') if st.session_state.login_ts else '—'} ·
        Edits this session: {sum(len(v) for v in st.session_state.ulb_edits.values())} field(s)
    </p>
    <p>
        <strong>Official Data Sources:</strong>
        <a href="https://udd.gujarat.gov.in" target="_blank">UDD Gujarat</a> ·
        <a href="https://gudm.gujarat.gov.in" target="_blank">GUDM</a> ·
        <a href="https://gpcb.gujarat.gov.in" target="_blank">GPCB</a> ·
        <a href="https://sbm.gov.in" target="_blank">SBM-U</a> ·
        <a href="https://mohua.gov.in" target="_blank">MoHUA</a> ·
        <a href="https://www.ngt.gov.in" target="_blank">NGT</a> ·
        <a href="https://amrut.gov.in" target="_blank">AMRUT 2.0</a> ·
        World Bank GRCP (P175728)
    </p>
    <p style="margin-top:10px;font-style:italic;font-size:0.82em;color:#888;">
        For official NGT submissions, always refer to the UPM Dashboard maintained by Gujarat Urban Development Company Ltd. (GUDC).
        This dashboard supports monitoring, gap analysis and compliance preparedness only.
    </p>
</div>
""", unsafe_allow_html=True)

# streamlit run gujarat_ngt_dashboard_v4.py

