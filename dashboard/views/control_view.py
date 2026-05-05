import streamlit as st
from api_client import post_json, ApiClientError


def render_control_view():
    st.subheader("التحكم")

    st.markdown("### التحكم العام في الإيجنت")
    c1, c2 = st.columns(2)

    with c1:
        if st.button("تشغيل الإيجنت", use_container_width=True):
            post_json("/control/bot/enable")
            st.success("تم تشغيل الإيجنت")

    with c2:
        if st.button("إيقاف الإيجنت", use_container_width=True):
            post_json("/control/bot/disable")
            st.success("تم إيقاف الإيجنت")

    st.markdown("---")
    st.markdown("### التحكم في الكاش")

    if st.button("مسح الكاش بالكامل", type="primary", use_container_width=True):
        result = post_json("/control/cache/flush")
        st.success(f"تم تعطيل {result.get('deactivated_entries', 0)} عنصر من الكاش")

    st.markdown("---")
    st.markdown("### باسورد الداشبورد")

    with st.form("change_dashboard_password_form"):
        current_password = st.text_input("الباسورد الحالي", type="password")
        new_password = st.text_input("الباسورد الجديد", type="password")
        confirm_password = st.text_input("تأكيد الباسورد الجديد", type="password")
        submitted = st.form_submit_button("تغيير الباسورد", use_container_width=True)

        if submitted:
            if new_password != confirm_password:
                st.error("تأكيد الباسورد غير مطابق")
            else:
                try:
                    result = post_json("/dashboard-auth/change-password", {
                        "current_password": current_password,
                        "new_password": new_password,
                    })
                    st.success(result.get("message", "تم تغيير الباسورد"))
                except ApiClientError as e:
                    st.error(str(e))
