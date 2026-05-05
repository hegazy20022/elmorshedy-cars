import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from api_client import get_json, post_json, ApiClientError


PRIMARY_COLOR = "#6366f1"  # Indigo
SECONDARY_COLOR = "#10b981"  # Emerald
COLOR_SEQUENCE = [PRIMARY_COLOR, SECONDARY_COLOR, "#f59e0b", "#ef4444", "#8b5cf6"]


def render_analytics_view():
    st.title("تحليلات المعرض الذكية")
    if not HAS_PLOTLY:
        st.warning("مكتبة Plotly مش متسطبة. جرب تشغل `pip install plotly` في التيرمينال عشان تشوف الرسومات البيانية بشكل أحلى.")
    
    st.caption("نظرة شاملة على أداء المعرض واهتمامات العملاء")

    try:
        stats = get_json("/analytics/stats")
        top_asked = get_json("/analytics/top-asked")
        top_booked = get_json("/analytics/top-booked")
        budget_trends = get_json("/analytics/budget-trends")
        latest_report = get_json("/analytics/latest-report")
    except ApiClientError as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return


    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الرسايل", stats.get("messages_count", 0))
    c2.metric("إجمالي الحجوزات", stats.get("bookings_count", 0))
    c3.metric("العملاء الجدد", stats.get("customers_count", 0))
    c4.metric("العربيات المتاحة", stats.get("available_cars_count", 0))

    st.markdown("---")


    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("الأكثر سؤالاً")
        if top_asked:
            df_asked = pd.DataFrame(top_asked)
            if HAS_PLOTLY:
                fig_asked = px.pie(
                    df_asked, 
                    values="count", 
                    names="car_name", 
                    hole=0.3,
                    color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR]
                )
                st.plotly_chart(fig_asked, use_container_width=True)
            else:
                st.bar_chart(df_asked.set_index("car_name"))
        else:
            st.info("لا توجد بيانات كافية حالياً")

    with col_right:
        st.subheader("الأكثر حجزاً للمعاينة")
        if top_booked:
            df_booked = pd.DataFrame(top_booked)
            if HAS_PLOTLY:
                fig_booked = px.pie(
                    df_booked, 
                    values="count", 
                    names="car_name",
                    hole=0.4,
                    color_discrete_sequence=[PRIMARY_COLOR, SECONDARY_COLOR]
                )
                st.plotly_chart(fig_booked, use_container_width=True)
            else:
                st.bar_chart(df_booked.set_index("car_name"))
        else:
            st.info("لا توجد بيانات كافية حالياً")

    st.markdown("---")
    

    st.subheader("توزيع ميزانيات العملاء")
    if budget_trends:
        df_budget = pd.DataFrame(budget_trends)
        if HAS_PLOTLY:
            fig_budget = px.pie(
                df_budget,
                values="value",
                names="label",
                hole=0.3,
                color_discrete_sequence=[SECONDARY_COLOR, PRIMARY_COLOR]
            )
            st.plotly_chart(fig_budget, use_container_width=True)
        else:
            st.bar_chart(df_budget.set_index("label"))
    
    st.markdown("---")


    st.subheader("تقرير الأيجنت التحليلي (AI)")
    
    if latest_report:
        with st.container(border=True):
            st.markdown(f"**تقرير شهر: {latest_report.get('report_month')}**")
            st.write(latest_report.get("report_text"))
            st.caption(f"تم التوليد في: {latest_report.get('generated_at')}")
    else:
        st.info("لم يتم توليد تقرير تحليل لهذا الشهر بعد")
        
    if st.button("توليد تقرير جديد الآن"):
        with st.spinner("الأيجنت بيحلل البيانات وبيكتب التقرير..."):
            try:
                res = post_json("/analytics/generate-report", {})
                st.success("تم توليد التقرير بنجاح!")
                st.rerun()
            except ApiClientError as e:
                st.error(f"فشل توليد التقرير: {e}")
