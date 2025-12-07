import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="کانورتور صورتحساب الکترونیک - رسمی", layout="wide")
st.title("کانورتور رسمی صورتحساب الکترونیک")
st.markdown("**مطابق آخرین دستورالعمل سازمان امور مالیاتی ایران - نسخه ۱۴۰۴**")

# ورود ساده
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.sidebar.form("login"):
        st.header("ورود به سامانه")
        if st.text_input("نام کاربری", value="admin") == "admin" and st.text_input("رمز عبور", type="password", value="123456") == "123456":
            if st.form_submit_button("ورود"):
                st.session_state.logged_in = True
                st.rerun()
        else:
            st.form_submit_button("ورود", disabled=True)
    st.stop()

if st.sidebar.button("خروج"):
    st.session_state.logged_in = False
    st.rerun()

# ذخیره تنظیمات
config_file = "config.json"
user_config = {}
if os.path.exists(config_file):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except:
        user_config = {}

# تمام الگوها بر اساس نوع صورتحساب
templates = {
    "نوع اول": {
        "الگوی اول (فروش)": {
            "required": ["شماره منحصر به فرد مالیاتی","تاریخ و زمان صدور صورتحساب (میلادی)","نوع صورتحساب","الگوی صورتحساب","موضوع صورتحساب","شماره اقتصادی فروشنده","مجموع مبلغ قبل از کسر تخفیف","مجموع مبلغ پس از کسر تخفیف","مجموع مالیات بر ارزش افزوده","مجموع سایر مالیات، عوارض و وجوه قانونی","مجموع صورتحساب","شناسه کالا/خدمت","تعداد/مقدار","مبلغ واحد","مبلغ قبل از تخفیف","مبلغ تخفیف","مبلغ بعد از تخفیف","نرخ مالیات بر ارزش افزوده","مبلغ مالیات بر ارزش افزوده","مبلغ کل کالا/خدمت"],
            "optional": ["سریال صورتحساب داخلی","شماره اقتصادی خریدار","کد پستی خریدار","روش تسویه","مبلغ پرداختی نقدی","شماره سوئیچ پرداخت"]
        },
        "الگوی دوم (فروش ارز)": {
            "required": ["شماره منحصر به فرد مالیاتی","تاریخ و زمان صدور","نوع ارز","نرخ خرید ارز","مبلغ ریالی","مجموع صورتحساب"],
            "optional": ["شماره قرارداد","نوع شخص خریدار"]
        },
        "الگوی سوم (طلا، جواهر و پلاتین)": {
            "required": ["شماره منحصر به فرد مالیاتی","تاریخ و زمان صدور","وزن خالص","عیار","قیمت هر گرم","اجرت ساخت","سود فروشنده","حق العمل","جمع کل اجرت، حق العمل و سود","مالیات بر ارزش افزوده","مجموع صورتحساب"],
            "optional": ["شماره قرارداد حق العملکاری","کد پستی خریدار","روش تسویه"]
        },
        "الگوی چهارم (پیمانکاری)": { "required": ["شماره منحصر به فرد مالیاتی","شماره قرارداد","مبلغ صورت وضعیت","مالیات","مجموع صورتحساب"], "optional": [] },
        "الگوی پنجم (قبوض خدماتی)": { "required": ["شماره منحصر به فرد مالیاتی","شماره اشتراک","مبلغ مصرف","مالیات","مجموع صورتحساب"], "optional": [] },
        "الگوی ششم (بلیط هواپیما)": { "required": ["شماره منحصر به فرد مالیاتی","شماره پرواز","مبدا","مقصد","مبلغ بلیط","مجموع صورتحساب"], "optional": [] },
        "الگوی هفتم (صادرات)": { "required": ["شماره منحصر به فرد مالیاتی","شماره پروانه گمرکی","شماره کوتاژ","مبلغ صادراتی","مجموع صورتحساب"], "optional": [] },
        "الگوی هشتم (بارنامه)": { "required": ["شماره منحصر به فرد مالیاتی","شماره بارنامه","مبدا","مقصد","کرایه حمل","مجموع صورتحساب"], "optional": [] },
        "الگوی نهم (فرآورده نفتی)": { "required": ["شماره منحصر به فرد مالیاتی","نوع فرآورده","مقدار","قیمت واحد","مبلغ کل","مجموع صورتحساب"], "optional": [] },
        "الگوی یازدهم (بورس کالا)": { "required": ["شماره منحصر به فرد مالیاتی","شماره اعلامیه فروش","نوع کالا","مقدار","قیمت واحد","مجموع صورتحساب"], "optional": [] },
        "الگوی سیزدهم (بیمه)": { "required": ["شماره منحصر به فرد مالیاتی","شناسه بیمه نامه","حق بیمه","مالیات","مجموع صورتحساب"], "optional": ["شناسه الحاقیه"] },
    },
    "نوع دوم": {
        "الگوی سوم (طلا) - نوع دوم": {
            "required": ["شماره منحصر به فرد مالیاتی","تاریخ و زمان صدور","وزن خالص","عیار","قیمت هر گرم","اجرت ساخت","سود فروشنده","حق العمل","جمع کل اجرت و سود","مالیات","مجموع صورتحساب"],
            "optional": ["روش تسویه","شماره قرارداد"]
        },
        "الگوی نهم (نفتی) - نوع دوم": {
            "required": ["شماره منحصر به فرد مالیاتی","نوع فرآورده","مقدار","قیمت واحد","عوارض","مالیات","مجموع صورتحساب"],
            "optional": []
        },
        "الگوی سیزدهم (بیمه) - نوع دوم": {
            "required": ["شماره منحصر به فرد مالیاتی","شناسه بیمه نامه","نوع بیمه","حق بیمه","کارمزد","مالیات","مجموع صورتحساب"],
            "optional": []
        }
    }
}

# مرحله ۱: انتخاب نوع صورتحساب
invoice_type = st.selectbox("نوع صورتحساب را انتخاب کنید:", ["نوع اول", "نوع دوم"])

# مرحله ۲: انتخاب الگو بر اساس نوع
pattern = st.selectbox(f"الگوی {invoice_type} را انتخاب کنید:", list(templates[invoice_type].keys()))
template = templates[invoice_type][pattern]

st.success(f"الگوی انتخاب شده: **{pattern}** از نوع **{invoice_type}**")

# مپینگ اجباری
st.subheader("فیلدهای اجباری (همیشه نمایش داده می‌شوند)")
required_mapping = user_config.get(f"{invoice_type}_{pattern}", {}).get("required", {})
new_required = {}
for field in template["required"]:
    col = st.text_input(f"**{field}**", value=required_mapping.get(field, ""), key=f"req_{invoice_type}_{pattern}_{field}")
    if col.strip():
        new_required[field] = col.strip()

# اختیاری با باز/بسته
show_opt = st.checkbox("نمایش فیلدهای اختیاری")
if show_opt and template["optional"]:
    st.subheader("فیلدهای اختیاری")
    optional_mapping = user_config.get(f"{invoice_type}_{pattern}", {}).get("optional", {})
    new_optional = {}
    for field in template["optional"]:
        col = st.text_input(f"{field}", value=optional_mapping.get(field, ""), key=f"opt_{invoice_type}_{pattern}_{field}")
        if col.strip():
            new_optional[field] = col.strip()

# ذخیره
if st.button("ذخیره تنظیمات این الگو"):
    key = f"{invoice_type}_{pattern}"
    if key not in user_config:
        user_config[key] = {}
    user_config[key]["required"] = new_required
    if show_opt:
        user_config[key]["optional"] = new_optional
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(user_config, f, ensure_ascii=False, indent=4)
    st.success("تنظیمات ذخیره شد!")

# آپلود و تبدیل
uploaded = st.file_uploader("فایل اکسل خود را آپلود کنید", type=["xlsx"])
if uploaded:
    df = pd.read_excel(uploaded)
    output = pd.DataFrame()

    # شماره منحصر به فرد مالیاتی همیشه ستون اول
    if "شماره منحصر به فرد مالیاتی" in new_required:
        col = new_required["شماره منحصر به فرد مالیاتی"]
        if col.isdigit():
            output["شماره منحصر به فرد مالیاتی"] = df.iloc[:, int(col)-1]
        else:
            output["شماره منحصر به فرد مالیاتی"] = df[col]

    # بقیه فیلدها
    all_map = {**new_required, **(new_optional if show_opt else {})}
    for field, col in all_map.items():
        if field == "شماره منحصر به فرد مالیاتی":
            continue
        try:
            if col.isdigit():
                output[field] = df.iloc[:, int(col)-1]
            else:
                output[field] = df[col]
        except:
            output[field] = ""

    st.success("تبدیل انجام شد!")
    st.dataframe(output.head(10))

    excel = output.to_excel(index=False, engine='openpyxl')
    st.download_button(
        "دانلود فایل استاندارد (قابل آپلود در سامانه مودیان)",
        excel,
        f"صورتحساب_{invoice_type}_{pattern}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
