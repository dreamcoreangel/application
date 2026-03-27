import streamlit as st
import re

# ==========================================
# ตั้งค่าหน้าเพจ
# ==========================================
st.set_page_config(page_title="Game Loca Studio (Thai)", layout="wide")

st.title("🎮 Game Localization Studio (Thai Edition)")
st.markdown("ระบบผู้ช่วยแปลเกมภาษาไทย อัจฉริยะ ป้องกันตัวแปรแตก และจำลองหน้าจอจริง")

# ==========================================
# Sidebar สำหรับเลือกโหมดการทำงาน
# ==========================================
menu = st.sidebar.selectbox("เลือกโมดูลการทำงาน", [
    "1. Lore & Context Engine",
    "2. UI & Thai Rendering Sandbox",
    "3. Code & Variable Armor",
    "4. Gaming Standard QA"
])

# ==========================================
# 1. ระบบจัดการจักรวาลเกมและบริบท (Lore & Context Engine)
# ==========================================
if menu == "1. Lore & Context Engine":
    st.header("📖 1. Lore & Context Engine")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dynamic Pronoun Matrix")
        speaker = st.selectbox("ผู้พูด", ["พระราชา", "อัศวิน", "ชาวบ้าน"])
        listener = st.selectbox("ผู้ฟัง", ["พระราชา", "อัศวิน", "ชาวบ้าน"])
        
        # จำลอง Logic สรรพนาม
        if speaker == "พระราชา" and listener == "อัศวิน":
            st.info("💡 **คำแนะนำสรรพนาม:** เรา (ผู้พูด) / เจ้า, ท่าน (ผู้ฟัง)")
        elif speaker == "ชาวบ้าน" and listener == "พระราชา":
            st.info("💡 **คำแนะนำสรรพนาม:** ข้าพระพุทธเจ้า, กระหม่อม (ผู้พูด) / ฝ่าบาท (ผู้ฟัง)")
        else:
            st.info("💡 **คำแนะนำสรรพนาม:** ข้า (ผู้พูด) / เอ็ง, เจ้า (ผู้ฟัง)")

    with col2:
        st.subheader("Visual Asset Linker")
        source_text = "He opened the old Chest."
        st.write(f"**Source Text:** {source_text}")
        
        # จำลองการเจอคำศัพท์ใน Termbase
        if "Chest" in source_text:
            with st.expander("🔍 พบคำศัพท์ใน Termbase: Chest"):
                st.image("https://images.unsplash.com/photo-1610419307730-80410427c3da?w=300", caption="คำแปลที่ถูกต้องในบริบทนี้: หีบสมบัติ (ไม่ใช่ หน้าอก)")
                
    st.divider()
    st.subheader("Branching Dialogue Viewer")
    st.code("""
    [Start] "Who goes there?"
      ├── (Choice 1) "A friend!" -> "Prove it, show your seal."
      └── (Choice 2) [Attack] -> "Guards! To arms!" (You are translating this line)
    """, language="plaintext")

# ==========================================
# 2. สภาพแวดล้อมจำลองและแก้ปัญหาภาษาไทย (UI & Thai Sandbox)
# ==========================================
elif menu == "2. UI & Thai Rendering Sandbox":
    st.header("🖥️ 2. UI & Thai Rendering Sandbox")
    
    source = "I don't think we have enough time to defeat the dragon before sunset."
    st.write(f"**ต้นฉบับ:** {source}")
    
    translation = st.text_area("ใส่คำแปลภาษาไทยของคุณที่นี่:", "ข้าไม่คิดว่าพวกเราจะมีเวลาเหลือพอที่จะปราบมังกรตัวนั้นก่อนที่พระอาทิตย์จะตกดินนะ")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Live UI Text-Box Simulator")
        char_limit = 50
        st.write(f"**จำลองกล่องข้อความ (ลิมิต {char_limit} ตัวอักษร):**")
        
        # แสดงกล่อง UI จำลอง
        box_color = "#2e7b32" if len(translation) <= char_limit else "#c62828"
        st.markdown(f"""
        <div style="background-color: #333; color: white; padding: 20px; border-radius: 10px; border: 3px solid {box_color}; width: 100%; height: 120px; font-family: Tahoma, sans-serif;">
            {translation}
        </div>
        """, unsafe_allow_html=True)
        
        if len(translation) > char_limit:
            st.error(f"⚠️ ข้อความยาวเกินไป! ({len(translation)}/{char_limit} ตัวอักษร) ตัวหนังสืออาจจะล้นกรอบหน้าจอเกม")
        else:
            st.success(f"✅ ความยาวผ่านเกณฑ์ ({len(translation)}/{char_limit})")

    with col2:
        st.subheader("Thai Font Engine Fixer")
        # จำลองการเช็คสระซ้อน (วรรณยุกต์ลอย) ง่ายๆ โดยใช้ Regex เช็คว่ามีวรรณยุกต์ติดกันหรือไม่ (ในของจริงจะซับซ้อนกว่านี้)
        invalid_thai = re.search(r'[\u0E48-\u0E4B]{2,}', translation)
        if invalid_thai:
            st.error("🚨 ตรวจพบวรรณยุกต์ซ้อนทับกัน (วรรณยุกต์ลอย/สระจม) กรุณาตรวจสอบ!")
        elif "ำ" in translation and re.search(r'[\u0E48-\u0E4B]ำ', translation):
             st.warning("⚠️ ตรวจพบการใช้ สระอำ ตามหลังวรรณยุกต์ บางเอนจินเกมอาจเรนเดอร์ผิดพลาด")
        else:
            st.success("✅ ไม่พบปัญหาสระจมหรือวรรณยุกต์ลอยในระดับเบื้องต้น")

# ==========================================
# 3. เกราะป้องกันโค้ดและตัวแปร (Code & Variable Armor)
# ==========================================
elif menu == "3. Code & Variable Armor":
    st.header("🛡️ 3. Code & Variable Armor")
    
    source_code_text = "Welcome back, {Player_Name}! You have \\c[2]%d\\c[0] Gold."
    st.write("**ต้นฉบับ:**", source_code_text)
    
    # ดึง Tags ออกมาจากต้นฉบับ
    required_tags = ["{Player_Name}", "\\c[2]", "%d", "\\c[0]"]
    st.info(f"🔒 **Tags ที่ห้ามลบ/แก้ไข:** `{'`, `'.join(required_tags)}`")
    
    user_input = st.text_area("คำแปลของคุณ:", "ยินดีต้อนรับกลับมานะ {Player_Name}! ตอนนี้ท่านมีทองอยู่ \\c[2]%d\\c[0] เหรียญ")
    
    # ระบบตรวจสอบ Tags
    missing_tags = [tag for tag in required_tags if tag not in user_input]
    if missing_tags:
        st.error(f"❌ โค้ดพังแน่! คุณลบหรือพิมพ์ Tags เหล่านี้ผิด: `{'`, `'.join(missing_tags)}`")
    else:
        st.success("✅ Tags ครบถ้วน เกมไม่แครชแน่นอน!")
        
        st.subheader("Placeholder Preview (จำลองการแสดงผลจริง)")
        preview = user_input.replace("{Player_Name}", "**อัศวินสมชาย**").replace("%d", "**50,000**")
        # จำลอง Color Code
        preview = preview.replace("\\c[2]", "<span style='color: gold;'>").replace("\\c[0]", "</span>")
        
        st.markdown(f"<div style='font-size: 18px;'>{preview}</div>", unsafe_allow_html=True)

# ==========================================
# 4. ระบบตรวจสอบคุณภาพเฉพาะทางเกม (Gaming Standard QA)
# ==========================================
elif menu == "4. Gaming Standard QA":
    st.header("✅ 4. Gaming Standard QA")
    
    platform = st.radio("เลือกแพลตฟอร์มเป้าหมาย", ["PlayStation", "Xbox"])
    text_to_qa = st.text_area("ข้อความที่รอตรวจสอบ:", "กดปุ่ม A เพื่อดู Achievements ของคุณ ไอระยำ!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Console Terminology Checker")
        # จำลอง Terminology
        if platform == "PlayStation":
            if "Achievements" in [t.strip(",.!") for t in text_to_qa.split()]:
                st.error("❌ ผิดมาตรฐาน PlayStation! ควรใช้คำว่า **Trophies** แทน **Achievements**")
            if "ปุ่ม A" in text_to_qa:
                st.error("❌ ผิดมาตรฐาน PlayStation! ควรใช้ **ปุ่ม X** หรือ **ปุ่มกากบาท**")
        elif platform == "Xbox":
            if "Trophies" in text_to_qa:
                st.error("❌ ผิดมาตรฐาน Xbox! ควรใช้คำว่า **Achievements**")
            st.success("✅ คำศัพท์แพลตฟอร์มถูกต้อง")

    with col2:
        st.subheader("Profanity & Age Rating Filter")
        bad_words = ["ระยำ", "สัส", "เหี้ย"]
        
        found_bad_words = [word for word in bad_words if word in text_to_qa]
        if found_bad_words:
            st.warning(f"🔞 ตรวจพบคำหยาบคาย: {', '.join(found_bad_words)}")
            st.write("หากเกมนี้เป็นเรต PEGI 3 (สำหรับทุกวัย) คุณจำเป็นต้องแก้คำเหล่านี้")
        else:
            st.success("🟢 เนื้อหาสะอาด ผ่านเกณฑ์ทุกวัย")
