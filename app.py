import streamlit as st
import pandas as pd
import os

# این خط مشکل yaml رو حل می‌کنه (در Streamlit Cloud)
try:
    import yaml
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

st.set_page_config(page_title="کانورتور فاکتور مالیاتی", layout="wide")
st.title("کانورتور هوشمند فاکتور به فرمت استاندارد سازمان امور مالیاتی")

# --- ورود ساده ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.sidebar.header("ورود")
    uname = st.sidebar.text_input("نام کاربری")
    pwd = st.sidebar.text_input("رمز عبور", type="password")
    if st.sidebar.button("ورود"):
        if uname == "admin" and pwd == "123456":
            st.session_state.logged_in = True
            st.sidebar.success("خوش آمدید!")
        else:
            st.sidebar.error("اشتباه است")

if not st.session_state.logged_in:
    login()
    st.stop()

if st.sidebar.button("خروج"):
    st.session_state.logged_in = False
    st.rerun()

# --- الگوها ---
templates = {
    "الگوی اول (فروش)": ["شماره فاکتور", "تاریخ", "نام مشتری", "مبلغ کل", "مالیات", "جمع نهایی"],
    "الگوی سوم (طلا و جواهر)": ["شماره فاکتور", "تاریخ", "وزن", "عیار", "قیمت هر گرم", "اجرت", "سود", "حق العمل", "مالیات", "جمع نهایی"]
}

# --- تنظیمات ---
config_file = "config.yaml"
if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
        user_config = yaml.safe_load(f) or {}
else:
    user_config = {}

st.header("انتخاب الگو")
template = st.selectbox("الگوی صورتحساب", list(templates.keys()))

if template:
    fields = templates[template]
    mapping = user_config.get(template, {})

    st.header("مپ کردن ستون‌ها")
    new_mapping = {}
    for field in fields:
        col = st.text_input(f"{field} → ستون در فایل شما؟", value=mapping.get(field, ""), key=field)
        if col:
            new_mapping[field] = col.strip()

    if st.button("ذخیره تنظیمات"):
        user_config[template] = new_mapping
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(user_config, f, allow_unicode=True)
        st.success("ذخیره شد!")

    uploaded = st.file_uploader("آپلود فایل اکسل", type=["xlsx", "xls"])
    if uploaded and new_mapping:
        df = pd.read_excel(uploaded)
        output = pd.DataFrame()
        headers = df.columns.tolist()

        for field, col in new_mapping.items():
            if col.isdigit():
                idx = int(col) - 1
            else:
                idx = headers.index(col) if col in headers else -1
            if 0 <= idx < len(df.columns):
                output[field] = df.iloc[:, idx]
            else:
                output[field] = ""

        st.success("تبدیل شد!")
        st.dataframe(output.head(10))

        csv = output.to_csv(index=False, encoding='utf-8-sig').encode()
        st.download_button("دانلود CSV", csv, f"فاکتور_{template}.csv", "text/csv")
        
        excel = output.to_excel(index=False, engine='openpyxl')
        st.download_button("دانلود Excel", excel, f"فاکتور_{template}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")