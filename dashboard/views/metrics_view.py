import streamlit as st

from api_client import get_json, ApiClientError


def render_metrics_view():
    st.subheader("المؤشرات")

    try:
        metrics = get_json("/metrics")
        health = get_json("/health")
        db_health = get_json("/health/db")
    except ApiClientError as e:
        st.error(str(e))
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("عدد الرسائل", metrics.get("messages", 0))
    c2.metric("عدد الحجوزات", metrics.get("bookings", 0))
    c3.metric("عدد الأخطاء", metrics.get("errors", 0))

    c4, c5 = st.columns(2)
    c4.metric("عدد مرات نجاح الكاش", metrics.get("cache_hits", 0))
    c5.metric("عدد مرات فشل الكاش", metrics.get("cache_misses", 0))

    st.markdown("---")
    st.markdown("### حالة الخدمة")

    c6, c7 = st.columns(2)
    api_status = health.get("status", "unknown")
    db_status = db_health.get("status", "unknown")

    if api_status == "ok":
        c6.success(f"حالة الـ API: {api_status}")
    else:
        c6.error(f"حالة الـ API: {api_status}")

    if db_status == "ok":
        c7.success(f"حالة قاعدة البيانات: {db_status}")
    else:
        c7.error(f"حالة قاعدة البيانات: {db_status}")
