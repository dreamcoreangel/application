import streamlit as st
import pandas as pd
import time
import random
import json
import re
import google.generativeai as genai

# --- ตั้งค่าหน้าเพจ ---
st.set_page_config(page_title="LyricMuse | Smart Subtitle Studio", page_icon="🎼", layout="wide")

# --- การตั้งค่า Gemini API ---
try:
    api_key = st.secrets["gemini_api_key"]
    genai.configure(api_key=api_key)
    
    # ค้นหาโมเดลที่รองรับอัตโนมัติ
    available_model = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_model = m.name
            break 
            
    if available_model:
        model = genai.GenerativeModel(available_model)
    else:
        st.error("ไม่พบโมเดล AI ที่รองรับ")
        model = None
        
except Exception as e:
    st.error(f"การตั้งค่า Gemini API ล้มเหลว: {e}")
    model = None

# --- ฟังก์ชัน AI ---
def analyze_mood(text):
    if not model: return ["#Error"]
    prompt = f"Analyze the mood of these song lyrics. Provide only 2 tags, e.g., '#Fantasy, #Melancholic'. Do not provide any conversational text. Lyrics: '{text[:2000]}...'"
    try:
        response = model.generate_content(prompt)
        return response.text.strip().split(', ')
    except Exception:
        return ["#AnalysisError"]

# ฟังก์ชันแปลแบบ "มัดรวมรวดเดียว (Batch)"
def batch_translate_lyrics(lines, tone, mood_tags):
    if not model: 
        return [{"source": line, "literal_thai": line, "polishing_thai": line} for line in lines]
        
    mood_context = f" considering the mood '{', '.join(mood_tags)}'" if mood_tags else ""
    
    # จัดเตรียมเนื้อเพลงแบบใส่ตัวเลข เพื่อไม่ให้ AI ข้ามบรรทัด
    numbered_lines = "\n".join([f"{i}:: {line}" for i, line in enumerate(lines)])
    
    prompt = f"""You are an expert lyric translator. Translate the following lyrics into Thai.
    Tone requested: '{tone}'{mood_context}.
    
    Output MUST be strictly a JSON array of objects. Do not write anything else.
    Each object must have these exact keys:
    "source": the original lyric line
    "literal_thai": literal direct translation
    "polishing_thai": creative translation matching the tone (if line is a tag like [Chorus], keep it as is).

    Lyrics to translate:
    {numbered_lines}
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # ใช้ Regex เพื่อดึงมาเฉพาะส่วนที่เป็น JSON Array [...] (ป้องกัน AI พิมพ์ข้อความอื่นแถมมา)
        match = re.search(r'\[.*\]', text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            result = json.loads(json_str)
            return result
        else:
            raise ValueError("รูปแบบข้อมูลที่ AI ตอบกลับมาไม่ถูกต้อง")
            
    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการแปล: {e}")
        # ถ้าพัง ให้คืนค่าเดิมกลับไป จะได้แก้ไขแมนนวลต่อได้
        return [{"source": line, "literal_thai": line, "polishing_thai": line} for line in lines]

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

# --- Tab 1 ---
with tabs[0]:
    st.markdown('<p class="big-font">📝 วางเนื้อหาและให้ AI ทำความเข้าใจ</p>', unsafe_allow_html=True)
    raw_text = st.text_area("วางเนื้อเพลงต้นทาง:", height=200, placeholder="Paste your lyrics here...")
    
    if st.button("🔍 ถอดรหัสและวิเคราะห์ (Analyze)", type="primary"):
        if raw_text and model:
            with st.spinner("AI กำลังกวาดสายตาอ่านเนื้อเพลง..."):
                st.session_state['raw_lyrics'] = raw_text
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

# --- Tab 2 ---
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
            
            # ใช้ st.spinner แทน Progress Bar เพราะส่งรวดเดียว
            with st.spinner("กำลังแปลและปรับโทนเนื้อเพลงรวดเดียวทั้งเพลง (อาจใช้เวลา 10-20 วินาที)..."):
                translated_data = batch_translate_lyrics(lines, tone_selected, st.session_state['mood_tags'])
                
                data = []
                for item in translated_data:
                    data.append({
                        "Source (ต้นทาง)": item.get("source", ""),
                        "Translation (คำแปล)": item.get("polishing_thai", ""),
                        "Literal Meaning (แปลตรงตัว)": item.get("literal_thai", "")
                    })
                
                st.session_state['df_draft'] = pd.DataFrame(data)
                st.success("สร้างดราฟต์สำเร็จ! ไปปรับแก้ในแท็บที่ 3 ได้เลย")

# --- Tab 3 ---
with tabs[2]:
    st.markdown('<p class="big-font">✍️ ปรับแต่งและขัดเกลา (Interactive Polishing)</p>', unsafe_allow_html=True)
    st.write("พื้นที่ทำงานหลัก: คุณสามารถ **ดับเบิ้ลคลิก** ที่ช่อง Translation เพื่อแก้ไขคำแปลได้ทันที")
    
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
                st.info("คำแนะนำ: ไป, ไกล, นัย, ภัย, ไหล (อ้างอิงจาก Mood ของเพลง)")
    else:
        st.info("กรุณาสร้างดราฟต์ในขั้นตอนที่ 2 ก่อนครับ")

# --- Tab 4 ---
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
