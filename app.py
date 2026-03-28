import streamlit as st
import pandas as pd
import time
import random
from deep_translator import GoogleTranslator

# --- ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LyricMuse | Smart Subtitle Studio", page_icon="🎼", layout="wide")

# --- ฟังก์ชันแปลภาษาและวิเคราะห์ (แบบไม่ใช้ GenAI) ---
def analyze_mood_mock(text):
    # จำลองการวิเคราะห์มู้ดเพื่อเป็นไกด์ไลน์ให้ผู้ใช้
    moods = ["#Melancholic", "#Fantasy", "#Empowering", "#Romantic", "#Upbeat", "#Dark"]
    return random.sample(moods, 2)

def translate_line(text):
    # ข้ามการแปลถ้าเป็นแท็กโครงสร้างเพลง เช่น [Chorus]
    if text.strip().startswith("[") and text.strip().endswith("]"):
        return text
    try:
        # ใช้ deep-translator (Google Translate) แปลตรงตัว
        return GoogleTranslator(source='auto', target='th').translate(text)
    except Exception:
        return text

# --- UI สไตล์ CSS ตกแต่ง ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #4A90E2; }
    .tag { background-color: #E8F4F8; padding: 5px 10px; border-radius: 15px; font-size: 14px; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎼 LyricMuse")
st.markdown("**สตูดิโอแปลซับไตเติลเพลงอัจฉริยะ (Smart Block-Based Workspace)**")
st.divider()

# --- Workflow ขั้นตอนต่างๆ ---
tabs = st.tabs(["1. Ingest & Analyze", "2. Smart First Draft", "3. Interactive Polishing", "4. Pacing & Export"])

if 'raw_lyrics' not in st.session_state:
    st.session_state['raw_lyrics'] = ""
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'mood_tags' not in st.session_state:
    st.session_state['mood_tags'] = []
if 'df_draft' not in st.session_state:
    st.session_state['df_draft'] = pd.DataFrame()

# ---------------------------------------------------------
# ขั้นตอนที่ 1: Ingest & Analyze
# ---------------------------------------------------------
with tabs[0]:
    st.markdown('<p class="big-font">📝 วางเนื้อหาและให้ระบบทำความเข้าใจ</p>', unsafe_allow_html=True)
    raw_text = st.text_area("วางเนื้อเพลงต้นทาง:", height=200, placeholder="Paste your lyrics here...")
    
    if st.button("🔍 เตรียมเนื้อเพลง (Ingest)", type="primary"):
        if raw_text:
            with st.spinner("กำลังเตรียมพื้นที่ทำงาน..."):
                time.sleep(0.5)
                st.session_state['raw_lyrics'] = raw_text
                st.session_state['mood_tags'] = analyze_mood_mock(raw_text)
                st.session_state['analyzed'] = True
                st.success("เตรียมข้อมูลเสร็จสิ้น! ไปที่แท็บ '2. Smart First Draft' ได้เลย")
        else:
            st.warning("กรุณาวางเนื้อเพลงก่อนครับ")

    if st.session_state['analyzed']:
        st.write("### 🏷️ Mood Guideline (แนวทางมู้ดเพลง)")
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in st.session_state['mood_tags']])
        st.markdown(tags_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# ขั้นตอนที่ 2: Smart First Draft
# ---------------------------------------------------------
with tabs[1]:
    st.markdown('<p class="big-font">✨ สร้างวัตถุดิบตั้งต้น (The First Draft)</p>', unsafe_allow_html=True)
    if not st.session_state['analyzed']:
        st.info("กรุณาวางเนื้อเพลงในขั้นตอนที่ 1 ก่อนครับ")
    else:
        st.write("💡 ระบบจะทำการแปลตรงตัว (Literal Translation) เพื่อสร้างเป็นโครงร่างตั้งต้นให้คุณนำไปขัดเกลาต่อในขั้นตอนต่อไป")
        
        if st.button("🪄 สร้างดราฟต์แรก (Generate Draft)"):
            lines = st.session_state['raw_lyrics'].strip().split('\n')
            lines = [line.strip() for line in lines if line.strip() != ""] 
            
            data = []
            progress_text = "กำลังแปลเนื้อเพลงทีละบรรทัด..."
            my_bar = st.progress(0, text=progress_text)
            
            for i, line in enumerate(lines):
                # แปลภาษาโดยใช้ Google Translator
                translated_text = translate_line(line)
                
                # นำคำแปลตั้งต้นใส่เข้าไปในตาราง
                data.append({
                    "Source (ต้นทาง)": line,
                    "Translation (คำแปล)": translated_text,
                    "Literal Meaning (แปลตรงตัว)": translated_text
                })
                
                my_bar.progress((i + 1) / len(lines), text=progress_text)
            
            st.session_state['df_draft'] = pd.DataFrame(data)
            my_bar.empty()
            st.success("สร้างดราฟต์สำเร็จ! ไปปรับแก้ให้สละสลวยในแท็บที่ 3 ได้เลย")

# ---------------------------------------------------------
# ขั้นตอนที่ 3: Interactive Polishing
# ---------------------------------------------------------
with tabs[2]:
    st.markdown('<p class="big-font">✍️ ปรับแต่งและขัดเกลา (Interactive Polishing)</p>', unsafe_allow_html=True)
    st.write("พื้นที่ทำงานหลัก: คุณสามารถ **ดับเบิ้ลคลิก** ที่ช่อง Translation เพื่อขัดเกลาภาษาให้เป็นบทกวีได้ตามต้องการ")
    
    if not st.session_state['df_draft'].empty:
        edited_df = st.data_editor(
            st.session_state['df_draft'],
            use_container_width=True,
            num_rows="dynamic",
            column_order=["Source (ต้นทาง)", "Translation (คำแปล)", "Literal Meaning (แปลตรงตัว)"],
            column_config={
                "Literal Meaning (แปลตรงตัว)": st.column_config.TextColumn("Literal Meaning (เทียบคำ)", disabled=True),
                "Source (ต้นทาง)": st.column_config.TextColumn("Source", disabled=True)
            }
        )
        st.session_state['df_draft'] = edited_df 
        
        st.divider()
        st.write("### 🔠 Thematic Rhyme Finder (ตัวช่วยหาคำคล้องจอง)")
        col1, col2 = st.columns(2)
        with col1:
            search_word = st.text_input("พิมพ์คำที่ต้องการหาสัมผัส (เช่น: ใจ)")
        with col2:
            if search_word:
                st.info("คำแนะนำ: ไป, ไกล, นัย, ภัย, ไหล (สามารถนำไปปรับใช้กับการแปลได้)")
    else:
        st.info("กรุณาสร้างดราฟต์ในขั้นตอนที่ 2 ก่อนครับ")

# ---------------------------------------------------------
# ขั้นตอนที่ 4: Pacing & Export
# ---------------------------------------------------------
with tabs[3]:
    st.markdown('<p class="big-font">⏱️ เช็กจังหวะและส่งออก (Pacing & Export)</p>', unsafe_allow_html=True)
    if not st.session_state['df_draft'].empty:
        st.write("**Mock Reading Pacer (จำลองความเร็ว)**")
        st.progress(70, text="Reading Pacing: 70% (ความเร็วอ่านกำลังดี ไม่ล้นจอ)")
        
        st.divider()
        st.write("เตรียมนำไปฝังใน Aegisub หรือ Premiere Pro")
        
        @st.cache_data
        def convert_df(df):
            export_df = df[["Source (ต้นทาง)", "Translation (คำแปล)"]]
            return export_df.to_csv(index=False).encode('utf-8')

        csv = convert_df(st.session_state['df_draft'])

        st.download_button(
            label="⬇️ Export เป็นไฟล์ CSV",
            data=csv,
            file_name='lyricmuse_subtitles.csv',
            mime='text/csv',
            type="primary"
        )
    else:
        st.info("ยังไม่มีข้อมูลสำหรับ Export ครับ")
