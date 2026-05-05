import streamlit as st
import pandas as pd
from api_client import get_json, post_json


def render_conversations_view():
    st.subheader("المحادثات")

    rows = get_json("/conversations")
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        labels = {f"{r.get('اسم العميل') or 'بدون اسم'} - {r.get('معرف المستخدم')}": r for r in rows}
        selected_label = st.selectbox("اختر المحادثة", list(labels.keys()))
        selected = labels[selected_label]
        telegram_user_id = selected["معرف المستخدم"]

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("إيقاف الإيجنت في هذا الشات", use_container_width=True):
                post_json(f"/conversations/{telegram_user_id}/takeover")
                st.success("تم إيقاف الإيجنت في هذا الشات")
        with c2:
            if st.button("إرجاع الإيجنت لهذا الشات", use_container_width=True):
                post_json(f"/conversations/{telegram_user_id}/resume")
                st.success("تمت إعادة الإيجنت لهذا الشات")
        with c3:
            if st.button("إيقاف مؤقت", use_container_width=True):
                post_json(f"/conversations/{telegram_user_id}/pause")
                st.success("تم الإيقاف المؤقت")
    else:
        st.info("لا توجد محادثات حالياً")
