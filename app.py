import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="کانورتور فاکتور", layout="wide")
st.title("🛡️ کانورتور هوشمند فاکتور به فرمت مالیاتی")

# ورود ساده (بدون yaml)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

def login():
    with st.sidebar:
        st.header("🔐 ورود")
        uname = st.text_input("نام کاربری")
        pwd = st.text_input("رمز عبور", type="password")
        if st.button("ورود"):
            if uname == "admin" and pwd == "123456":
                st.session_state.logged_in = True
                st.session_state.username = uname
                st.success("ورود موفق!")
                st.rerun()
            else:
                st.error("❌ اشتباه است")
        st.info("نام کاربری: admin | رمز: 123456")

if not st.session_state.logged_in:
    login()
    st.stop()

# دکمه خروج
if st.sidebar.button("🚪 خروج"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

st.sidebar.success(f"خوش آمدید {st.session_state.username}!")

# الگوهای ساده (بدون yaml — مستقیم در کد)
templates = {
    "الگوی اول (فروش)": [
        "شماره منحصر به فرد مالیاتی", "تاریخ صدور", "نوع صورتحساب", "الگوی صورتحساب",
        "شماره اقتصادی فروشنده", "مجموع مبلغ قبل از تخفیف", "مجموع تخفیفات", 
        "مجموع مبلغ پس از تخفیف", "مجموع مالیات بر ارزش افزوده", "مجموع صورتحساب"
    ],
    "الگوی سوم (طلا، جواهر و پلاتین)": [
        "شماره منحصر به فرد مالیاتی", "تاریخ صدور", "وزن خالص", "عیار", "قیمت هر گرم",
        "اجرت ساخت", "سود فروشنده", "حق العمل", "جمع کل اجرت، حق العمل و سود", 
        "مجموع مالیات بر ارزش افزوده", "مجموع صورتحساب"
    ]
    # می‌تونی الگوهای بیشتر اضافه کنی
}

# تنظیمات ساده با JSON
config_file = "config.json"
user_config = {}
if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
        user_config = json.load(f)

st.header("📋 ۱. انتخاب الگوی صورتحساب")
template = st.selectbox("الگو را انتخاب کنید:", list(templates.keys()), key="template")

if template:
    st.success(f"✅ الگوی انتخاب شده: **{template}**")
    fields = templates[template]
    
    # مپینگ فیلدها
    st.header("🔄 ۲. مپ کردن ستون‌های فایل اکسل شما")
    mapping = user_config.get(template, {})
    new_mapping = {}
    
    for field in fields:
        default_col = mapping.get(field, "")
        col_input = st.text_input(
            f"ستون **{field}** در فایل شما (مثل A, B, H یا نام ستون):", 
            value=default_col, 
            key=f"{template}_{field}"
        )
        if col_input.strip():
            new_mapping[field] = col_input.strip()

    # ذخیره تنظیمات با JSON
    if st.button("💾 ذخیره تنظیمات (دفعه بعد لازم نیست دوباره مپ کنی)"):
        user_config[template] = new_mapping
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(user_config, f, ensure_ascii=False, indent=4)
        st.success("✅ تنظیمات ذخیره شد! حالا می‌تونی فایل آپلود کنی.")

    # آپلود و تبدیل
    st.header("📁 ۳. آپلود فایل و دریافت خروجی استاندارد")
    uploaded_file = st.file_uploader("فایل اکسل خود را آپلود کنید:", type=["xlsx", "xls"])

    if uploaded_file and new_mapping:
        try:
            # خواندن فایل
            df_input = pd.read_excel(uploaded_file)
            headers = df_input.columns.tolist()
            st.info(f"📊 فایل آپلود شد: {len(df_input)} ردیف، ستون‌ها: {', '.join([str(h) for h in headers[:5]])}...")

            # ایجاد خروجی استاندارد
            df_output = pd.DataFrame()
            missing_cols = []

            for field, user_col in new_mapping.items():
                col_found = False
                if user_col.isalpha() and len(user_col) <= 2:  # مثل A, B, AA
                    try:
                        col_idx = ord(user_col[0].upper()) - ord('A')
                        if len(user_col) > 1:
                            col_idx = col_idx * 26 + (ord(user_col[1].upper()) - ord('A'))
                        df_output[field] = df_input.iloc[:, col_idx]
                        col_found = True
                    except:
                        pass
                elif user_col.isdigit():  # شماره ستون مثل 1, 8
                    col_idx = int(user_col) - 1
                    if 0 <= col_idx < len(df_input.columns):
                        df_output[field] = df_input.iloc[:, col_idx]
                        col_found = True
                else:  # نام ستون
                    if user_col in headers:
                        df_output[field] = df_input[user_col]
                        col_found = True

                if not col_found:
                    df_output[field] = ""  # خالی اگر پیدا نشد
                    missing_cols.append(f"{field} ({user_col})")

            if missing_cols:
                st.warning(f"⚠️ ستون‌های پیدا نشده: {', '.join(missing_cols)} — این‌ها خالی می‌مونن.")

            # نمایش پیش‌نمایش
            st.subheader("🔍 پیش‌نمایش خروجی:")
            st.dataframe(df_output.head(10))

            # دانلودها
            col1, col2 = st.columns(2)
            with col1:
                csv_data = df_output.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 دانلود CSV",
                    data=csv_data,
                    file_name=f"فاکتور_استاندارد_{template.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            with col2:
                excel_data = df_output.to_excel(index=False, engine='openpyxl')
                st.download_button(
                    label="📥 دانلود Excel",
                    data=excel_data,
                    file_name=f"فاکتور_استاندارد_{template.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.success("🎉 تبدیل با موفقیت انجام شد! فایل‌های دانلود رو چک کن.")

        except Exception as e:
            st.error(f"❌ خطا در تبدیل: {str(e)} — لطفاً فایل رو چک کن یا ستون‌ها رو دوباره وارد کن.")

st.markdown("---")
st.caption("💡 نکته: برای الگوهای بیشتر یا تغییرات، با پشتیبانی تماس بگیر.")
