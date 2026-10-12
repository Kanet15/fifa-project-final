import sys
import os
import base64
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

try:
    from src.models.pet import Pet
    from src.dal.json_storage import JSONStorageManager
    from src.bll.pet_service import PetService
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อระบบหลังบ้าน: {e}")

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="PawMatch — Pet Adoption Platform",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

pet_service = PetService()

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"
if "selected_pet_id" not in st.session_state:
    st.session_state.selected_pet_id = None
if "favorites" not in st.session_state:
    st.session_state.favorites = set()
if "home_species_filter" not in st.session_state:
    st.session_state.home_species_filter = "ทั้งหมด"

# ---------------------------------------------------------
# HELPER: GET HERO IMAGE
# ---------------------------------------------------------
def get_hero_image_src():
    local_path = "assets/pawmatch-hero.png"
    if os.path.exists(local_path):
        try:
            with open(local_path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            pass
    return "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=800&auto=format&fit=crop&q=80"

# ---------------------------------------------------------
# 2. CUSTOM CSS STYLING
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Prompt', sans-serif !important;
    }

    .stApp {
        background-color: #F8FAFC;
    }

    /* Hero Section */
    .hero-banner-card {
        background: linear-gradient(135deg, #581C87 0%, #3B0764 100%);
        border-radius: 24px;
        padding: 36px 40px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 16px 32px rgba(88, 28, 135, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 24px;
    }

    .hero-text-container {
        flex: 1.2;
        min-width: 300px;
    }

    .hero-badge {
        background: rgba(255, 255, 255, 0.15);
        color: #FDE047;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
    }

    .hero-main-title {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        color: #FFFFFF !important;
        margin-bottom: 10px;
    }

    .hero-sub-text {
        color: #F3E8FF;
        font-size: 1.02rem;
        font-weight: 300;
        line-height: 1.5;
    }

    .hero-avatar-frame {
        width: 210px;
        height: 210px;
        background-color: #FDE047;
        border-radius: 50%;
        overflow: hidden;
        border: 5px solid #FFFFFF;
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }

    .hero-avatar-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Category Image Cards */
    .cat-card-frame {
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid #E2E8F0;
        background: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 6px;
        height: 110px;
    }

    .cat-card-frame.active {
        border: 3px solid #8B5CF6 !important;
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3) !important;
    }

    .cat-card-frame img {
        width: 100% !important;
        height: 110px !important;
        object-fit: cover !important;
        display: block !important;
    }

    /* Pet Listing Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #F1F5F9 !important;
        border-radius: 20px !important;
        padding: 16px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.1) !important;
    }

    .tag-badge {
        background-color: #F3E8FF;
        color: #6B21A8;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 4px;
        display: inline-block;
    }

    .status-pending { color: #D97706; font-weight: 600; background: #FEF3C7; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; }
    .status-approved { color: #059669; font-weight: 600; background: #D1FAE5; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; }
    .status-rejected { color: #DC2626; font-weight: 600; background: #FEE2E2; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; }

    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. TOP NAVIGATION BAR
# ---------------------------------------------------------
nav_cols = st.columns([1.1, 1.2, 1.3, 1.4, 1.4, 1.1, 1.4])
pages = [
    ("🏠 Home", "🏠 Home"),
    ("🔎 Explore", "🔎 Explore Pets"),
    ("🔄 Compare", "🔄 Compare Pets"),
    ("🎯 Match Quiz", "🎯 Match Quiz"),
    ("💰 Budget Calc", "💰 Care Budget Calc"),
    ("❤️ Favorites", "❤ Favorites"),
    ("⚙️ Admin", "📊 Admin System")
]

for idx, (label, page_name) in enumerate(pages):
    with nav_cols[idx]:
        is_act = st.session_state.current_page == page_name
        if st.button(label, key=f"nav_{page_name}", type="primary" if is_act else "secondary", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()

st.write("")

# ---------------------------------------------------------
# HELPER: RENDER PET CARD
# ---------------------------------------------------------
def render_pet_card(pet: Pet, match_info: dict = None):
    with st.container(border=True):
        st.image(pet.image_url, use_container_width=True)
        if match_info:
            st.progress(match_info["score"] / 100)
            st.markdown(f"Match Score: `{match_info['score']}%`")
        
        st.markdown(f"### {pet.name}")
        st.caption(f"{pet.breed} • {pet.species}")
        
        tags_html = "".join([f'<span class="tag-badge">{t}</span>' for t in getattr(pet, 'tags', [])[:3]])
        st.markdown(tags_html, unsafe_allow_html=True)
        st.write("")
        
        st.markdown(f"อายุ: {pet.age} ปี | สถานที่: {pet.location}")
        st.markdown(f"ประมาณการค่าเลี้ยงดู: ~`{pet.cost_monthly:,}` บาท/เดือน")
        st.write("")

        c1, c2 = st.columns(2)
        with c1:
            is_fav = pet.pet_id in st.session_state.favorites
            if st.button("Saved" if is_fav else "Save", key=f"fav_{pet.pet_id}_{match_info['score'] if match_info else '0'}", use_container_width=True):
                if is_fav: st.session_state.favorites.remove(pet.pet_id)
                else: st.session_state.favorites.add(pet.pet_id)
                st.rerun()
        with c2:
            if st.button("รายละเอียด", key=f"det_{pet.pet_id}_{match_info['score'] if match_info else '0'}", type="primary", use_container_width=True):
                st.session_state.selected_pet_id = pet.pet_id
                st.session_state.current_page = "🐶 Pet Details"
                st.rerun()

# ==========================================
# 1. HOME PAGE
# ==========================================
if st.session_state.current_page == "🏠 Home":
    
    hero_img = get_hero_image_src()
    st.markdown(f"""
        <div class="hero-banner-card">
            <div class="hero-text-container">
                <div class="hero-badge">FIND YOUR PERFECT COMPANION</div>
                <div class="hero-main-title">A Loving Home With Your New Pet</div>
                <div class="hero-sub-text">
                    ศูนย์รวมสัตว์เลี้ยงตามหาบ้านใหม่ ค้นหาน้องๆ ที่เข้ากับไลฟ์สไตล์คุณ<br>
                    พร้อมระบบวิเคราะห์และคำนวณงบประมาณแบบครบวงจร
                </div>
            </div>
            <div>
                <div class="hero-avatar-frame">
                    <img src="{hero_img}" alt="Cute Pet Companion" />
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1E293B; margin-bottom:4px;'>หมวดหมู่สัตว์เลี้ยง (Categories)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748B; margin-bottom:18px;'>คลิกเลือกหมวดหมู่เพื่อกรองข้อมูลสัตว์เลี้ยง</p>", unsafe_allow_html=True)

    categories = [
        {"code": "ทั้งหมด", "name": "ALL PETS", "img": "https://images.unsplash.com/photo-1548767797-d8c844163c4c?w=500&auto=format&fit=crop&q=80"},
        {"code": "Dog", "name": "DOGS", "img": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=500&auto=format&fit=crop&q=80"},
        {"code": "Cat", "name": "CATS", "img": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=500&auto=format&fit=crop&q=80"},
        {"code": "Rabbit", "name": "RABBITS", "img": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=500&auto=format&fit=crop&q=80"},
        {"code": "Hamster", "name": "RODENTS", "img": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=500&auto=format&fit=crop&q=80"},
        {"code": "Bird", "name": "BIRDS", "img": "https://images.unsplash.com/photo-1522858547137-f1dcec554f55?w=500&auto=format&fit=crop&q=80"}
    ]

    cat_cols = st.columns(len(categories))

    for idx, cat in enumerate(categories):
        with cat_cols[idx]:
            is_active = (st.session_state.home_species_filter == cat["code"])
            active_class = "active" if is_active else ""

            st.markdown(f"""
                <div class="cat-card-frame {active_class}">
                    <img src="{cat['img']}" alt="{cat['name']}" />
                </div>
            """, unsafe_allow_html=True)

            if st.button(
                cat["name"],
                key=f"cat_btn_{idx}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                st.session_state.home_species_filter = cat["code"]
                st.rerun()

    st.write("")
    st.divider()

    all_pets = pet_service.get_all_pets()

    if all_pets:
        today_seed = int(datetime.now().strftime("%Y%m%d"))
        potd_index = today_seed % len(all_pets)
        potd = all_pets[potd_index]

        st.markdown("<h3 style='color:#6B21A8;'>Pet of the Day — สัตว์เลี้ยงโดดเด่นประจำวันนี้</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                st.image(potd.image_url, use_container_width=True)
            with p_col2:
                st.markdown(f"## {potd.name} ({potd.breed})")
                st.caption(f"สายพันธุ์: {potd.breed} | ประเภท: {potd.species} | สถานที่: {potd.location}")
                st.write(f"💬 *\"{potd.description}\"*")
                st.markdown(f"อายุ: {potd.age} ปี | ที่พักที่เหมาะ: {potd.living_space}")
                st.markdown(f"ประมาณการค่าเลี้ยงดู: `{potd.cost_monthly:,}` บาท/เดือน")
                st.write("")
                if st.button(f"สนใจรับเลี้ยง {potd.name}", type="primary"):
                    st.session_state.selected_pet_id = potd.pet_id
                    st.session_state.current_page = "🐶 Pet Details"
                    st.rerun()

    st.write("")
    st.markdown("<h3 style='color:#1E293B;'>รายการสัตว์เลี้ยงที่กำลังตามหาบ้านใหม่</h3>", unsafe_allow_html=True)
    
    display_pets = all_pets if st.session_state.home_species_filter == "ทั้งหมด" else [p for p in all_pets if p.species == st.session_state.home_species_filter]
    
    g_cols = st.columns(3)
    for idx, pet in enumerate(display_pets):
        with g_cols[idx % 3]:
            render_pet_card(pet)

# ==========================================
# 2. EXPLORE PETS
# ==========================================
elif st.session_state.current_page == "🔎 Explore Pets":
    st.markdown("## ค้นหาสัตว์เลี้ยงทั้งหมด")
    all_pets = pet_service.get_all_pets()
    kw = st.text_input("พิมพ์ชื่อ หรือสายพันธุ์ที่ต้องการค้นหา:", "")
    
    filtered = [p for p in all_pets if kw.lower() in p.name.lower() or kw.lower() in p.breed.lower()] if kw else all_pets
    st.write("")
    g_cols = st.columns(3)
    for idx, pet in enumerate(filtered):
        with g_cols[idx % 3]:
            render_pet_card(pet)

# ==========================================
# 3. COMPARE PETS
# ==========================================
elif st.session_state.current_page == "🔄 Compare Pets":
    st.markdown("## เปรียบเทียบสัตว์เลี้ยง")
    all_pets = pet_service.get_all_pets()
    pet_options = {f"{p.name} ({p.breed})": p for p in all_pets}

    selected_keys = st.multiselect(
        "เลือกสัตว์เลี้ยงที่ต้องการเปรียบเทียบ (2-3 ตัว):",
        options=list(pet_options.keys()),
        default=list(pet_options.keys())[:2] if len(pet_options) >= 2 else list(pet_options.keys()),
        max_selections=3
    )

    if len(selected_keys) < 2:
        st.info("กรุณาเลือกสัตว์เลี้ยงอย่างน้อย 2 ตัวเพื่อทำการเปรียบเทียบตารางคุณสมบัติ")
    else:
        selected_pets = [pet_options[k] for k in selected_keys]
        cols = st.columns(len(selected_pets))

        for idx, pet in enumerate(selected_pets):
            with cols[idx]:
                with st.container(border=True):
                    st.image(pet.image_url, use_container_width=True)
                    st.markdown(f"### {pet.name}")
                    st.caption(f"{pet.breed} ({pet.species})")
                    st.divider()
                    st.markdown(f"อายุ: `{pet.age} ปี`")
                    st.markdown(f"สถานที่: `{pet.location}`")
                    st.markdown(f"พื้นที่: `{pet.living_space}`")
                    st.markdown(f"ระดับพลังงาน: `{pet.activity_level}`")
                    st.markdown(f"รายเดือน: `{pet.cost_monthly:,} บาท`")
                    st.markdown(f"แรกรับ: `{pet.cost_initial:,} บาท`")
                    st.markdown(f"วัคซีน: `{'ฉีดแล้ว' if pet.vaccinated else 'ยังไม่ฉีด'}`")
                    st.write("")
                    if st.button(f"เลือก {pet.name}", key=f"cmp_btn_{pet.pet_id}", type="primary", use_container_width=True):
                        st.session_state.selected_pet_id = pet.pet_id
                        st.session_state.current_page = "🐶 Pet Details"
                        st.rerun()

# ==========================================
# 4. MATCH QUIZ
# ==========================================
elif st.session_state.current_page == "🎯 Match Quiz":
    st.markdown("## Match Quiz — แบบทดสอบค้นหาน้องที่ใช่")
    st.caption("ตอบคำถามสั้นๆ 4 ข้อ ระบบจะช่วยคำนวณความเข้ากันได้กับไลฟ์สไตล์ของคุณ")

    with st.container(border=True):
        with st.form("simple_quiz_form"):
            q1 = st.selectbox("1. สัตว์เลี้ยงประเภทไหนที่คุณสนใจ?", ["เปิดรับทุกชนิด", "Dog", "Cat", "Rabbit", "Bird", "Hamster", "Hedgehog"])
            q2 = st.selectbox("2. ลักษณะที่อยู่อาศัยของคุณเป็นแบบไหน?", ["คอนโด / หอพัก", "บ้านเดี่ยว / มีสวน"])
            q3 = st.selectbox("3. คุณมีเวลาว่างทำกิจกรรมร่วมกับสัตว์เลี้ยงวันละเท่าไร?", ["งานยุ่งมาก (น้อยกว่า 1 ชม./วัน)", "ปานกลาง (1-3 ชม./วัน)", "มีเวลาเต็มที่ (> 3 ชม./วัน)"])
            q4 = st.selectbox("4. งบประมาณสำหรับดูแลน้องต่อเดือนที่คุณสะดวก?", ["ประหยัด (<1,000 บาท/เดือน)", "ปานกลาง (1,000-2,500 บาท/เดือน)", "พร้อมเปย์ (>2,500 บาท/เดือน)"])

            submit_btn = st.form_submit_button("เริ่มค้นหาสัตว์เลี้ยงที่เหมาะกับฉัน", type="primary", use_container_width=True)

    if submit_btn or "quiz_results" in st.session_state:
        if submit_btn:
            u_answers = {
                "species": q1,
                "living_space": "คอนโด" if "คอนโด" in q2 else "บ้านเดี่ยว",
                "time": q3,
                "budget": q4
            }
            st.session_state.quiz_results = pet_service.calculate_simple_match(u_answers)

        results = st.session_state.quiz_results
        st.write("")
        st.markdown(f"### พบน้องๆ ที่เข้ากับคุณ ({len(results)} ตัว)")

        g_cols = st.columns(3)
        for idx, item in enumerate(results):
            pet = item["pet"]
            score = item["score"]
            reasons = item["reasons"]

            with g_cols[idx % 3]:
                with st.container(border=True):
                    st.image(pet.image_url, use_container_width=True)
                    st.progress(score / 100)
                    st.markdown(f"Match Score: `{score}%`")
                    st.markdown(f"### {pet.name}")
                    st.caption(f"{pet.breed} ({pet.species})")
                    st.divider()
                    for r in reasons:
                        st.caption(r)
                    st.divider()

                    if st.button("ดูรายละเอียดน้อง", key=f"qz_det_{pet.pet_id}", type="primary", use_container_width=True):
                        st.session_state.selected_pet_id = pet.pet_id
                        st.session_state.current_page = "🐶 Pet Details"
                        st.rerun()

# ==========================================
# 5. CARE BUDGET CALCULATOR
# ==========================================
elif st.session_state.current_page == "💰 Care Budget Calc":
    st.markdown("## เครื่องคำนวณงบประมาณการเลี้ยงดู")
    st.caption("ระบบประเมินค่าใช้จ่ายเบื้องต้นเพื่อช่วยในการวางแผนทางการเงินก่อนตัดสินใจรับเลี้ยงสัตว์")
    
    all_pets = pet_service.get_all_pets()
    if not all_pets:
        st.info("ไม่พบข้อมูลสัตว์เลี้ยงในระบบ")
    else:
        pet_names = [f"{p.name} ({p.species} - {p.breed})" for p in all_pets]
        sel_idx = st.selectbox("เลือกสัตว์เลี้ยงที่ต้องการคำนวณงบประมาณ:", range(len(all_pets)), format_func=lambda x: pet_names[x])
        pet = all_pets[sel_idx]

        with st.container(border=True):
            col_b1, col_b2 = st.columns([1, 1.2])
            
            with col_b1:
                st.image(pet.image_url, use_container_width=True)
                st.markdown(f"### {pet.name}")
                st.write(f"ชนิด: {pet.species} | สายพันธุ์: {pet.breed}")
                st.write(f"สถานที่พัก: {pet.location}")

            with col_b2:
                st.markdown("#### ประมาณการค่าใช้จ่ายเบื้องต้น")
                st.write(f"ค่าใช้จ่ายแรกรับ (Initial Cost): {pet.cost_initial:,} บาท")
                st.write(f"ค่าใช้จ่ายประจำเดือน (Monthly Cost): {pet.cost_monthly:,} บาท / เดือน")
                st.write("")
                
                months = st.slider("เลือกระยะเวลาการเลี้ยงดูที่ต้องการคำนวณ (เดือน):", 1, 36, 12)
                total_monthly = pet.cost_monthly * months
                total_budget = pet.cost_initial + total_monthly
                
                st.divider()
                st.metric(label=f"งบประมาณรวมประเมิน ({months} เดือน)", value=f"{total_budget:,} บาท")
                st.caption(f"* คำนวณจาก ค่าแรกรับ {pet.cost_initial:,} บาท + ค่าเลี้ยงดูรายเดือน ({pet.cost_monthly:,} x {months} เดือน = {total_monthly:,} บาท)")

        st.write("")
        st.markdown("### รายละเอียดหมวดหมู่ค่าใช้จ่าย")
        
        col_desc1, col_desc2 = st.columns(2)
        
        with col_desc1:
            with st.container(border=True):
                st.markdown("#### 1. ค่าใช้จ่ายแรกรับ (Initial Costs)")
                st.markdown("""
                ค่าใช้จ่ายก้อนแรกที่เกิดขึ้นเมื่อเริ่มรับสัตว์เลี้ยงเข้ามาดูแล ประกอบด้วย:
                
                * **การตรวจสุขภาพและวัคซีนเริ่มต้น:** ค่าตรวจเลือด ตรวจคัดกรองโรคติดต่อ และการฉีดวัคซีนพื้นฐานเข็มแรก
                * **การทำหมันและเวชภัณฑ์:** กรณีสัตว์เลี้ยงยังไม่ได้ทำหมัน รวมถึงค่ายาและอุปกรณ์ทำแผล
                * **อุปกรณ์และสิ่งของจำเป็นเริ่มต้น:**
                    * กรง กระเป๋าเดินทาง หรือกรงเคลื่อนย้าย
                    * เบาะนอน ที่นอน และชามใส่อาหาร-น้ำ
                    * สายจูง ปลอกคอ หรือกระบะทราย
                    * ของเล่น แปรงขน และกรรไกรตัดเล็บ
                """)

        with col_desc2:
            with st.container(border=True):
                st.markdown("#### 2. ค่าใช้จ่ายประจำเดือน (Monthly Costs)")
                st.markdown("""
                ค่าใช้จ่ายหมุนเวียนที่ต้องจัดสรรในทุกๆ เดือน ตลอดระยะเวลาการเลี้ยงดู ประกอบด้วย:
                
                * **อาหารหลักและโภชนาการ:** อาหารเม็ด อาหารเปียก หรืออาหารเสริมตามวัย
                * **วัสดุสิ้นเปลือง:** ทรายแมว แผ่นรองซับ หรือทรายรองกรง
                * **การป้องกันพยาธิและพาหะ:** ยาหยดหลังหรือยาทานป้องกันเห็บ หมัด พยาธิหัวใจ และพยาธิทางเดินอาหาร
                * **การดูแลสุขอนามัย:** แชมพูสุนัข/แมว หรือค่าบริการตัดขนและทำความสะอาด
                * **เงินสำรองการรักษา:** เงินสำรองฉุกเฉินกรณีเจ็บป่วยหรือเกิดอุบัติเหตุ
                """)

# ==========================================
# 6. PET DETAILS & CONTACT
# ==========================================
elif st.session_state.current_page == "🐶 Pet Details":
    pet = pet_service.get_pet_by_id(st.session_state.selected_pet_id)
    if st.button("← กลับหน้าหลัก"):
        st.session_state.current_page = "🏠 Home"
        st.rerun()

    if pet:
        with st.container(border=True):
            d1, d2 = st.columns(2)
            with d1: 
                st.image(pet.image_url, use_container_width=True)
            with d2:
                st.markdown(f"# {pet.name}")
                st.caption(f"สายพันธุ์: {pet.breed} • ชนิด: {pet.species}")
                st.divider()
                st.write(f"อายุ: {pet.age} ปี | เพศ: {pet.gender}")
                st.write(f"สถานที่พัก: {pet.location}")
                st.write(f"ประวัติและความน่ารัก: {pet.description}")

        st.write("")
        st.markdown("### ฟอร์มยื่นคำขอรับเลี้ยง (Adoption Application)")
        with st.container(border=True):
            with st.form("contact_form"):
                c_a, c_b = st.columns(2)
                with c_a:
                    name = st.text_input("ชื่อ-นามสกุล ผู้ขอรับเลี้ยง *")
                    phone = st.text_input("เบอร์โทรศัพท์ติดต่อ *")
                with c_b:
                    line = st.text_input("LINE ID")
                    space = st.selectbox("ลักษณะที่อยู่อาศัยปัจจุบัน", ["คอนโด / หอพัก", "บ้านเดี่ยว", "ทาวน์เฮาส์"])
                note = st.text_area("ข้อความเพิ่มเติม หรือประสบการณ์การเลี้ยงสัตว์")
                
                if st.form_submit_button("ยื่นคำขอรับเลี้ยงน้อง", type="primary", use_container_width=True):
                    if name and phone:
                        pet_service.submit_application(pet.pet_id, name, phone, line, "", space, "", note)
                        st.balloons()
                        st.success("ส่งคำขอเรียบร้อยแล้ว! เจ้าหน้าที่จะติดต่อกลับโดยเร็วที่สุด")
                    else:
                        st.error("กรุณากรอกชื่อ และเบอร์โทรศัพท์ให้ครบถ้วน")

# ==========================================
# 7. FAVORITES
# ==========================================
elif st.session_state.current_page == "❤ Favorites":
    st.markdown("## สัตว์เลี้ยงที่คุณบันทึกไว้")
    favs = [p for p in pet_service.get_all_pets() if p.pet_id in st.session_state.favorites]
    if not favs:
        st.info("คุณยังไม่ได้กดบันทึกสัตว์เลี้ยงตัวใดไว้ สามารถกด Save ได้จากหน้าหลัก")
    else:
        g = st.columns(3)
        for i, p in enumerate(favs):
            with g[i%3]: render_pet_card(p)

# ==========================================
# 8. ADMIN SYSTEM
# ==========================================
elif st.session_state.current_page == "📊 Admin System":
    st.markdown("## ระบบผู้ดูแลหลังบ้าน (Adoption Management)")

    apps = pet_service.get_all_applications()
    all_pets = pet_service.get_all_pets()
    pet_dict = {p.pet_id: p for p in all_pets}

    total_apps = len(apps)
    pending_count = sum(1 for a in apps if a.get("status") == "Pending")
    approved_count = sum(1 for a in apps if a.get("status") == "Approved")
    rejected_count = sum(1 for a in apps if a.get("status") == "Rejected")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("คำขอทั้งหมด", f"{total_apps} รายการ")
    with m2: st.metric("รอดำเนินการ", f"{pending_count} รายการ")
    with m3: st.metric("อนุมัติแล้ว", f"{approved_count} รายการ")
    with m4: st.metric("ปฏิเสธ", f"{rejected_count} รายการ")

    st.divider()
    st.markdown("### รายการคำขอรับเลี้ยงทั้งหมด")

    if not apps:
        st.info("ยังไม่มีคำขอรับเลี้ยงในระบบ")
    else:
        for app in reversed(apps):
            app_id = app.get("app_id", "APP000")
            status = app.get("status", "Pending")
            pet_info = pet_dict.get(app.get("pet_id"), None)
            pet_name = pet_info.name if pet_info else app.get("pet_id")

            with st.container(border=True):
                head_col1, head_col2 = st.columns([3, 1])
                with head_col1:
                    st.markdown(f"#### คำขอ #{app_id} — สนใจรับเลี้ยง: **น้อง {pet_name}**")
                with head_col2:
                    if status == "Pending":
                        st.markdown('<span class="status-pending">Pending</span>', unsafe_allow_html=True)
                    elif status == "Approved":
                        st.markdown('<span class="status-approved">Approved</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="status-rejected">Rejected</span>', unsafe_allow_html=True)

                col_info1, col_info2, col_actions = st.columns([1.5, 1.5, 1.2])
                with col_info1:
                    st.write(f"ผู้สมัคร: {app.get('applicant_name')}")
                    st.write(f"เบอร์โทร: {app.get('phone')}")
                with col_info2:
                    st.write(f"ที่อยู่อาศัย: {app.get('space_type')}")
                    st.caption(f"ยื่นเมื่อ: {app.get('submitted_at')}")

                with col_actions:
                    btn_c1, btn_c2 = st.columns(2)
                    with btn_c1:
                        if st.button("อนุมัติ", key=f"appr_{app_id}", type="primary", use_container_width=True):
                            pet_service.update_app_status(app_id, "Approved")
                            st.rerun()
                    with btn_c2:
                        if st.button("ปฏิเสธ", key=f"rej_{app_id}", use_container_width=True):
                            pet_service.update_app_status(app_id, "Rejected")
                            st.rerun()