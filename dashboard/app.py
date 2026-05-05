import streamlit as st

from api_client import get_json, post_json, ApiClientError
from ui_labels import TABLE_LABELS_AR
from views.bookings_view import render_bookings_view
from views.cars_view import render_cars_view
from views.conversations_view import render_conversations_view
from views.control_view import render_control_view
from views.cache_view import render_cache_view
from views.logs_view import render_logs_view
from views.metrics_view import render_metrics_view
from views.settings_view import render_settings_view
from views.sold_cars_view import render_sold_cars_view
from views.purchase_requests_view import render_purchase_requests_view
from views.analytics_view import render_analytics_view

st.set_page_config(
    page_title="لوحة تحكم معرض المرشدي",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* تطبيق من اليمين لليسار على المحتوى الداخلي فقط عشان القائمة الجانبية متبوظش في الموبايل */
.block-container, 
section[data-testid="stSidebar"] > div {
    direction: rtl !important;
    text-align: right !important;
}

/* الحفاظ على اتجاه الأيقونات والقوائم الأساسية */
header[data-testid="stHeader"] {
    direction: ltr !important;
}

/* منع أي سحب أفقي */
html, body, .stApp {
    overflow-x: hidden !important;
}

/* الحاوية الأساسية */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}

/* العناوين */
h1, h2, h3, h4, h5, h6 {
    word-break: break-word !important;
    line-height: 1.4 !important;
}

/* الأزرار */
.stButton > button {
    width: 100% !important;
    min-height: 46px !important;
    border-radius: 10px !important;
    font-size: 15px !important;
}

/* الحقول */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
div[data-baseweb="select"] > div {
    font-size: 16px !important;
}

/* الجداول */
[data-testid="stDataFrame"] {
    overflow-x: auto !important;
}

/* الصور */
img {
    max-width: 100% !important;
    height: auto !important;
    border-radius: 10px !important;
}

/* السايد بار */
section[data-testid="stSidebar"] {
    min-width: 260px !important;
}

/* الموبايل */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1rem !important; }

    /* ضبط القائمة الجانبية في الموبايل لتعمل بكفاءة دون التداخل */
    section[data-testid="stSidebar"] {
        width: 250px !important;
        max-width: 250px !important;
    }
    
    /* إصلاح اتجاه الراديو باتون داخل القائمة الجانبية */
    .stRadio > div[role="radiogroup"] {
        direction: rtl !important;
    }
    
    .stRadio label {
        padding-right: 10px !important;
        justify-content: flex-end !important;
        flex-direction: row-reverse !important;
    }
    
    /* جعل زر القائمة الجانبية (الهامبرجر) يظهر بوضوح */
    button[kind="header"] {
        margin-left: auto !important;
    }
}
</style>
""", unsafe_allow_html=True)


def render_login():
    st.title("تسجيل دخول الداشبورد")
    st.caption("أدخل الباسورد للمتابعة")

    with st.form("dashboard_login_form"):
        password = st.text_input("الباسورد", type="password")
        submitted = st.form_submit_button("دخول", use_container_width=True)

        if submitted:
            try:
                post_json("/dashboard-auth/login", {"password": password})
                st.session_state["dashboard_authenticated"] = True
                st.success("تم تسجيل الدخول")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))


def check_auth() -> bool:
    if "dashboard_authenticated" not in st.session_state:
        st.session_state["dashboard_authenticated"] = False

    try:
        auth_status = get_json("/dashboard-auth/status")
        enabled = auth_status.get("enabled", True)
    except Exception as e:
        st.error(f"تعذر التحقق من حالة المصادقة: {e}")
        return False

    if not enabled:
        return True

    if st.session_state["dashboard_authenticated"]:
        return True

    render_login()
    return False


if not check_auth():
    st.stop()

st.title("لوحة تحكم معرض المرشدي")
st.caption("إدارة الحجوزات والعربيات والمحادثات والتحكم والكاش والسجلات")

if st.sidebar.button("تسجيل خروج", use_container_width=True):
    st.session_state["dashboard_authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### القائمة الرئيسية")

menu_items = [
    ("bookings", TABLE_LABELS_AR["bookings"]),
    ("cars", TABLE_LABELS_AR["cars"]),
    ("conversations", TABLE_LABELS_AR["conversations"]),
    ("control", TABLE_LABELS_AR["control"]),
    ("cache", TABLE_LABELS_AR["cache"]),
    ("logs", "السجلات والأخطاء"),
    ("metrics", "المؤشرات"),
    ("settings", "الاعدادات"),
    ("sold_cars", "العربيات المباعة"),
    ("purchase_requests", "العربيات المشتراة"),
    ("analytics", "التحليلات الذكية"),
]

labels = [label for _, label in menu_items]
keys = {label: key for key, label in menu_items}

selected_label = st.sidebar.radio("الأقسام", labels, index=0)
selected_key = keys[selected_label]

if selected_key == "bookings":
    render_bookings_view()
elif selected_key == "cars":
    render_cars_view()
elif selected_key == "conversations":
    render_conversations_view()
elif selected_key == "control":
    render_control_view()
elif selected_key == "cache":
    render_cache_view()
elif selected_key == "logs":
    render_logs_view()
elif selected_key == "metrics":
    render_metrics_view()
elif selected_key == "settings":
    render_settings_view()
elif selected_key == "sold_cars":
    render_sold_cars_view()
elif selected_key == "purchase_requests":
    render_purchase_requests_view()
elif selected_key == "analytics":
    render_analytics_view()
