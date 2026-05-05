import pandas as pd
import streamlit as st

from api_client import get_json, put_json, delete_json, ApiClientError
from helpers import translate_dataframe_columns, translate_dataframe_values


def render_cache_view():
    st.subheader("الكاش")

    search = st.text_input("ابحث في الكاش", placeholder="اكتب سؤال أو نية أو رد مخزن")

    try:
        if search.strip():
            rows = get_json(f"/cache?search={search.strip()}")
        else:
            rows = get_json("/cache")
    except ApiClientError as e:
        st.error(str(e))
        return

    st.markdown("### بيانات الكاش الحالية")

    if rows:
        df = pd.DataFrame(rows)
        df = translate_dataframe_values(df, "cache")
        df = translate_dataframe_columns(df, "cache")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عناصر كاش حالياً")

    st.markdown("---")
    st.markdown("### تعديل أو حذف عنصر كاش")

    if not rows:
        st.warning("لا توجد عناصر للتعديل أو الحذف")
        return

    labels = {
        f"كاش {r['cache_id']} - {r.get('intent', '')}": r
        for r in rows
    }

    selected_label = st.selectbox("اختر عنصر الكاش", list(labels.keys()))
    selected = labels[selected_label]

    with st.form("edit_cache_form"):
        cached_answer = st.text_area(
            "الرد المخزن",
            value=selected.get("cached_answer") or "",
            height=150,
        )
        repeat_count = st.number_input(
            "عدد التكرار",
            min_value=0,
            step=1,
            value=int(selected.get("repeat_count") or 0),
        )
        is_active = st.checkbox(
            "نشط",
            value=bool(selected.get("is_active")),
        )

        submitted = st.form_submit_button("تعديل عنصر الكاش", use_container_width=True)

        if submitted:
            try:
                put_json(
                    f"/cache/{selected['cache_id']}",
                    {
                        "cached_answer": cached_answer,
                        "repeat_count": int(repeat_count),
                        "is_active": is_active,
                    },
                )
                st.success("تم تعديل عنصر الكاش")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    c1, c2 = st.columns(2)

    with c1:
        if st.button("تعطيل عنصر الكاش", use_container_width=True):
            try:
                put_json(f"/cache/{selected['cache_id']}/disable", {})
                st.success("تم تعطيل عنصر الكاش")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    with c2:
        if st.button("حذف عنصر الكاش", type="primary", use_container_width=True):
            try:
                delete_json(f"/cache/{selected['cache_id']}")
                st.success("تم حذف عنصر الكاش")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))
