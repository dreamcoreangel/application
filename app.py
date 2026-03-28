import streamlit as st
import pandas as pd
import time
from deep_translator import GoogleTranslator

# --- ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LyricMuse | Smart Subtitle Studio", page_icon="🎼", layout="wide")

# --- ฟังก์ชันแปลภาษา ---
def translate_line(text):
    # ข้ามการแปลถ้าเป็นแท็กโครงสร้างเพลง เช่น [Chorus]
    if text.strip().startswith("[") and text.strip().endswith("]"):
        return text
    try:
        return GoogleTranslator(source='auto', target='th').translate(text)
    except Exception:
        return text

# --- UI สไตล์ CSS ตกแต่ง ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #4A90E2; }
    </style>
""", unsafe_allow_html=True)

st.title("🎼 LyricMuse")
st.markdown("**สตูดิโอแปลซับไตเติลเพลงอัจฉริยะ (Smart Block-Based Workspace)**")
st.divider()

# --- Workflow ขั้นตอนต่างๆ ---
tabs = st.tabs(["1. Prepare Lyrics", "2. Smart First Draft", "3. Polishing & Export"])

if 'raw_lyrics' not in st.session_state:
    st.session_state['raw_lyrics'] = ""
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'df_draft' not in st.session_state:
    st.session_state['df_draft'] = pd.DataFrame()

# ---------------------------------------------------------
# ขั้นตอนที่ 1: Prepare Lyrics
# ---------------------------------------------------------
with tabs[0]:
    st.markdown('<p class="big-font">📝 วางเนื้อเพลงต้นทาง</p>', unsafe_allow_html=True)
    raw_text = st.text_area("วางเนื้อเพลงต้นฉบับลงที่นี่:", height=200, placeholder="Paste your lyrics here...")
    
    if st.button("🔍 เตรียมเนื้อเพลง", type="primary"):
        if raw_text:
            with st.spinner("กำลังเตรียมพื้นที่ทำงาน..."):
                time.sleep(0.5)
                st.session_state['raw_lyrics'] = raw_text
                st.session_state['analyzed'] = True
                st.success("เตรียมข้อมูลเสร็จสิ้น! ไปที่แท็บ '2. Smart First Draft' ได้เลย")
        else:
            st.warning("กรุณาวางเนื้อเพลงก่อนครับ")

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
                translated_text = translate_line(line)
                data.append({
                    "Source (ต้นทาง)": line,
                    "Translation (คำแปล)": translated_text
                })
                my_bar.progress((i + 1) / len(lines), text=progress_text)
            
            st.session_state['df_draft'] = pd.DataFrame(data)
            my_bar.empty()
            st.success("สร้างดราฟต์สำเร็จ! ไปปรับแก้ให้สละสลวยในแท็บที่ 3 ได้เลย")

# ---------------------------------------------------------
# ขั้นตอนที่ 3: Polishing & Export
# ---------------------------------------------------------
with tabs[2]:
    st.markdown('<p class="big-font">✍️ ปรับแต่งและส่งออก (Polishing & Export)</p>', unsafe_allow_html=True)
    st.write("พื้นที่ทำงานหลัก: คุณสามารถ **ดับเบิ้ลคลิก** ที่ช่อง Translation เพื่อขัดเกลาภาษาได้ตามต้องการ")
    
    if not st.session_state['df_draft'].empty:
        # ตารางสำหรับแก้ไขคำแปล
        edited_df = st.data_editor(
            st.session_state['df_draft'],
            use_container_width=True,
            num_rows="dynamic",
            column_order=["Source (ต้นทาง)", "Translation (คำแปล)"],
            column_config={
                "Source (ต้นทาง)": st.column_config.TextColumn("Source", disabled=True)
            }
        )
        st.session_state['df_draft'] = edited_df 
        
        st.divider()
        
        # ส่วนสำหรับการ Export ถูกย้ายมาไว้ด้านล่างตาราง
        st.write("### 💾 ส่งออกไฟล์ (Export)")
        st.write("เมื่อปรับแก้คำแปลเรียบร้อยแล้ว สามารถกดดาวน์โหลดไฟล์ CSV นำไปฝังในโปรแกรมทำซับไตเติลได้ทันที")
        
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
        st.info("กรุณาสร้างดราฟต์ในขั้นตอนที่ 2 ก่อนครับ")
