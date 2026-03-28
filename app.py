import streamlit as st
import pandas as pd
import time
import random

# --- ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LyricMuse | Smart Subtitle Studio", page_icon="🎼", layout="wide")

# --- ฟังก์ชันจำลอง AI (Mockup Functions) ---
# ในการใช้งานจริง คุณสามารถเชื่อมต่อ Gemini API หรือ OpenAI API ในส่วนนี้ได้
def analyze_mood(text):
    moods = ["#Melancholic", "#Fantasy", "#Empowering", "#Romantic", "#Upbeat"]
    return random.sample(moods, 2)

def count_syllables(text):
    # จำลองการนับพยางค์ (ใช้งานจริงอาจใช้ไลบรารี PyThaiNLP หรือนับสระภาษาอังกฤษ)
    return len(str(text).split())

def mock_translate(text, tone):
    # จำลองการแปลตามระดับภาษา
    if tone == "Literary (ภาษากวี)":
        return "ดั่งสายลมกระซิบผ่านกาลเวลา"
    elif tone == "Contemporary (ร่วมสมัย)":
        return "เหมือนลมที่พัดผ่านไปอย่างช้าๆ"
    else:
        return "เหมือนลมที่พัดไป"

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

# ตัวแปรสำหรับเก็บข้อมูลชั่วคราว (Session State)
if 'raw_lyrics' not in st.session_state:
    st.session_state['raw_lyrics'] = ""
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
if 'df_draft' not in st.session_state:
    st.session_state['df_draft'] = pd.DataFrame()

# ---------------------------------------------------------
# ขั้นตอนที่ 1: Ingest & Analyze
# ---------------------------------------------------------
with tabs[0]:
    st.markdown('<p class="big-font">📝 วางเนื้อหาและให้ AI ทำความเข้าใจ</p>', unsafe_allow_html=True)
    raw_text = st.text_area("วางเนื้อเพลงต้นทาง (ภาษาอังกฤษ / ภาษาอื่นๆ):", height=200, placeholder="Paste your lyrics here...")
    
    if st.button("🔍 ถอดรหัสและวิเคราะห์ (Analyze)", type="primary"):
        if raw_text:
            with st.spinner("AI กำลังกวาดสายตาอ่านเนื้อเพลง..."):
                time.sleep(1) # จำลองเวลาประมวลผล
                st.session_state['raw_lyrics'] = raw_text
                st.session_state['mood_tags'] = analyze_mood(raw_text)
                st.session_state['analyzed'] = True
                st.success("วิเคราะห์เสร็จสิ้น! ไปที่แท็บ '2. Smart First Draft' ได้เลย")
        else:
            st.warning("กรุณาวางเนื้อเพลงก่อนครับ")

    if st.session_state['analyzed']:
        st.write("### 🏷️ Auto-Tagging (Mood Analysis)")
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in st.session_state['mood_tags']])
        st.markdown(tags_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# ขั้นตอนที่ 2 & 3: Smart First Draft & Interactive Polishing
# ---------------------------------------------------------
with tabs[1]:
    st.markdown('<p class="big-font">✨ สร้างวัตถุดิบตั้งต้น (The Smart First Draft)</p>', unsafe_allow_html=True)
    if not st.session_state['analyzed']:
        st.info("กรุณาวิเคราะห์เนื้อเพลงในขั้นตอนที่ 1 ก่อนครับ")
    else:
        tone_selected = st.select_slider(
            "🎚️ ปรับระดับภาษา (Tone & Register Slider)",
            options=["Casual (กันเอง)", "Contemporary (ร่วมสมัย)", "Literary (ภาษากวี)"],
            value="Contemporary (ร่วมสมัย)"
        )
        
        if st.button("🪄 สร้างดราฟต์แรก (Generate Draft)"):
            lines = st.session_state['raw_lyrics'].strip().split('\n')
            lines = [line for line in lines if line.strip() != ""] # ลบบรรทัดว่าง
            
            data = []
            for line in lines:
                src_syl = count_syllables(line)
                translated = mock_translate(line, tone_selected)
                tgt_syl = count_syllables(translated)
                
                data.append({
                    "Source (ต้นทาง)": line,
                    "Translation (คำแปล)": translated,
                    "Syllables (พยางค์)": f"{src_syl} -> {tgt_syl}",
                    "Literal Meaning (แปลตรงตัว)": f"Meaning of: {line}"
                })
            
            st.session_state['df_draft'] = pd.DataFrame(data)
            st.success("สร้างดราฟต์สำเร็จ! ไปปรับแก้ในแท็บถัดไปได้เลย")

with tabs[2]:
    st.markdown('<p class="big-font">✍️ ปรับแต่งและขัดเกลา (Interactive Polishing)</p>', unsafe_allow_html=True)
    st.write("พื้นที่ทำงานหลัก: คุณสามารถ **ดับเบิ้ลคลิก** ที่ช่อง Translation เพื่อแก้ไขคำแปลได้ทันที")
    
    if not st.session_state['df_draft'].empty:
        # ใช้ st.data_editor เป็น Smart Block-Based Workspace
        edited_df = st.data_editor(
            st.session_state['df_draft'],
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Literal Meaning (แปลตรงตัว)": st.column_config.TextColumn("Literal Meaning (เทียบคำ)", disabled=True),
                "Source (ต้นทาง)": st.column_config.TextColumn("Source", disabled=True),
                "Syllables (พยางค์)": st.column_config.TextColumn("พยางค์", disabled=True)
            }
        )
        st.session_state['df_draft'] = edited_df # อัปเดตข้อมูลเมื่อแก้ไข
        
        st.divider()
        st.write("### 🔠 Thematic Rhyme Finder (ตัวช่วยหาคำคล้องจอง)")
        col1, col2 = st.columns(2)
        with col1:
            search_word = st.text_input("พิมพ์คำที่ต้องการหาสัมผัส (เช่น: ใจ)")
        with col2:
            if search_word:
                st.info("คำแนะนำ: ไป, ไกล, นัย, ภัย, ไหล (ตรงกับ Mood: #Melancholic)")
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
        
        # แปลง DataFrame เป็น CSV
        @st.cache_data
        def convert_df(df):
            # เลือกเฉพาะคอลัมน์ที่จำเป็นสำหรับทำซับ
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
