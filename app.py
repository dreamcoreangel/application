import streamlit as st
import pandas as pd
import time
import random
import json
import google.generativeai as genai

# --- ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LyricMuse | Smart Subtitle Studio", page_icon="🎼", layout="wide")

# --- การตั้งค่า Gemini API (จัดการความลับผ่าน Streamlit Secrets) ---
# อย่าใส่ API key ลงในโค้ดโดยตรง!
# ให้ไปที่ Advanced Settings -> Secrets ใน Streamlit Cloud Dashboard และใส่:
# gemini_api_key = "YOUR_API_KEY_HERE"
try:
    api_key = st.secrets["gemini_api_key"]
    genai.configure(api_key=api_key)
    
    # ให้ระบบค้นหาโมเดลที่รองรับการสร้างข้อความโดยอัตโนมัติ
    available_model = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_model = m.name
            break # เจอโมเดลแรกที่ใช้ได้ให้เลือกตัวนั้นเลย
            
    if available_model:
        model = genai.GenerativeModel(available_model)
    else:
        st.error("ไม่พบโมเดล AI ที่รองรับในบัญชีของคุณ")
        model = None
        
except Exception as e:
    st.error(f"การตั้งค่า Gemini API ล้มเหลว: {e}")
    model = None

# --- ฟังก์ชันจำลอง AI และ ฟังก์ชันแปลจริง ---
def analyze_mood(text):
    if not model: return ["#Error"]
    
    prompt = f"Analyze the mood of these song lyrics. Provide only 2 tags, e.g., '#Fantasy, #Melancholic'. Do not provide any conversational text. Lyrics: '{text[:2000]}...'" # จำกัดจำนวนตัวอักษรเพื่อความปลอดภัย
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().split(', ')
    except Exception as e:
        st.warning(f"การวิเคราะห์อารมณ์ล้มเหลว: {e}")
        return ["#AnalysisError"]

# ฟังก์ชันแปลและปรับโทนโดยใช้ Gemini API
def get_llm_translation_and_polishing(text, tone, mood_tags):
    if not model: return text, text # คืนค่าเดิมถ้าไม่มีโมเดล
    
    # ถ้าเป็นพวกแท็กโครงสร้างเพลง เช่น [Verse 1] ให้ข้ามการแปล
    if text.strip().startswith("[") and text.strip().endswith("]"):
        return text, text

    mood_context = f" considering the general mood '{', '.join(mood_tags)}'" if mood_tags else ""

    # สร้าง Prompt ที่ชาญฉลาด
    # ขอกลับมาเป็น JSON เพื่อแยกคำแปลตรงตัว (literal) และคำแปลปรับโทน (polishing)
    prompt = f"""You are an expert lyric translator and a poet. Translate the following lyrics from its original language into Thai. 
    Provide two versions of the translation:
    1. A literal, direct translation into Thai.
    2. A creative translation into Thai that matches the requested tone of '{tone}'{mood_context}.

    Make sure the creative translation is poetic and suitable for song lyrics.
    The output should be strictly a JSON object with two keys: 'literal_thai' and 'polishing_thai'.
    Do not include markdown formatting or any other text in the output.

    Text to translate:
    '{text}'
    """

    try:
        response = model.generate_content(prompt)
        # ตรวจสอบว่าผลลัพธ์เป็น JSON ที่ถูกต้องหรือไม่
        json_str = response.text.strip()
        # บางครั้ง LLM อาจใส่ markdown block ในผลลัพธ์
        if json_str.startswith("```json") and json_str.endswith("```"):
            json_str = json_str[7:-3].strip()
        
        result = json.loads(json_str)
        return result['literal_thai'], result['polishing_thai']
    except Exception as e:
        # st.warning(f"การแปลภาษาล้มเหลว: {e}") # ปิดเพื่อไม่ให้ UI ดูรก
        return text, text # คืนค่าเดิมถ้าล้มเหลว

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
    st.markdown('<p class="big-font">📝 วางเนื้อหาและให้ AI ทำความเข้าใจ</p>', unsafe_allow_html=True)
    raw_text = st.text_area("วางเนื้อเพลงต้นทาง:", height=200, placeholder="Paste your lyrics here...")
    
    if st.button("🔍 ถอดรหัสและวิเคราะห์ (Analyze)", type="primary"):
        if raw_text and model:
            with st.spinner("AI กำลังกวาดสายตาอ่านเนื้อเพลง..."):
                st.session_state['raw_lyrics'] = raw_text
                # ใช้ Gemini วิเคราะห์อารมณ์
                st.session_state['mood_tags'] = analyze_mood(raw_text)
                st.session_state['analyzed'] = True
                st.success("วิเคราะห์เสร็จสิ้น! ไปที่แท็บ '2. Smart First Draft' ได้เลย")
        elif not model:
            st.warning("กรุณาตั้งค่า API key ก่อนครับ")
        else:
            st.warning("กรุณาวางเนื้อเพลงก่อนครับ")

    if st.session_state['analyzed']:
        st.write("### 🏷️ Auto-Tagging (Mood Analysis)")
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in st.session_state['mood_tags']])
        st.markdown(tags_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# ขั้นตอนที่ 2: Smart First Draft
# ---------------------------------------------------------
with tabs[1]:
    st.markdown('<p class="big-font">✨ สร้างวัตถุดิบตั้งต้น (The Smart First Draft)</p>', unsafe_allow_html=True)
    if not st.session_state['analyzed']:
        st.info("กรุณาวิเคราะห์เนื้อเพลงในขั้นตอนที่ 1 ก่อนครับ")
    elif not model:
        st.warning("กรุณาตั้งค่า API key ก่อนครับ")
    else:
        st.write("### 🎚️ ปรับระดับภาษา (Tone Slider)")
        tone_selected = st.select_slider(
            "ระดับภาษาที่ต้องการ:",
            options=["Casual (กันเอง)", "Contemporary (ร่วมสมัย)", "Literary (ภาษากวี)"],
            value="Contemporary (ร่วมสมัย)"
        )
        st.write(f"ระบบจะทำการแปลและปรับโทนเสียงให้เป็น '{tone_selected}' โดยอิงตามอารมณ์ของเพลง ({', '.join(st.session_state['mood_tags'])})")
        
        if st.button("🪄 สร้างดราฟต์แรก (Generate Draft)"):
            lines = st.session_state['raw_lyrics'].strip().split('\n')
            lines = [line.strip() for line in lines if line.strip() != ""] 
            
            data = []
            # สร้าง Progress bar ตอนแปล
            progress_text = "กำลังแปลและปรับโทนเนื้อเพลงทีละบรรทัดด้วย Gemini AI..."
            my_bar = st.progress(0, text=progress_text)
            
            for i, line in enumerate(lines):
                # โทรหา Gemini API เพื่อแปลและปรับโทน
                literal_th, polishing_th = get_llm_translation_and_polishing(line, tone_selected, st.session_state['mood_tags'])
                
                # กำหนดให้คำแปลดราฟต์คือคำแปลปรับโทนเลยครับ
                draft_th = polishing_th

                # สร้าง Data โดย **ลบ key 'Syllables' ออก**
                data.append({
                    "Source (ต้นทาง)": line,
                    "Translation (คำแปล)": draft_th,
                    "Literal Meaning (แปลตรงตัว)": literal_th
                })
                
                # อัปเดต Progress bar
                my_bar.progress((i + 1) / len(lines), text=progress_text)
            
            st.session_state['df_draft'] = pd.DataFrame(data)
            my_bar.empty()
            st.success("สร้างดราฟต์สำเร็จ! ไปปรับแก้ในแท็บที่ 3 ได้เลย")

# ---------------------------------------------------------
# ขั้นตอนที่ 3: Interactive Polishing
# ---------------------------------------------------------
with tabs[2]:
    st.markdown('<p class="big-font">✍️ ปรับแต่งและขัดเกลา (Interactive Polishing)</p>', unsafe_allow_html=True)
    st.write("พื้นที่ทำงานหลัก: คุณสามารถ **ดับเบิ้ลคลิก** ที่ช่อง Translation เพื่อแก้ไขคำแปลได้ทันที")
    
    if not st.session_state['df_draft'].empty:
        # แสดง Data Editor โดยกำหนดลำดับคอลัมน์ใหม่ Source -> Translation -> Literal
        # **ลบการตั้งค่าคอลัมน์ "พยางค์" ออก**
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
                st.info("คำแนะนำ: ไป, ไกล, นัย, ภัย, ไหล (อ้างอิงจาก Mood ของเพลง)")
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
