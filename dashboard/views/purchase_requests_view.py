import pandas as pd
import streamlit as st

from api_client import get_json, post_json, put_json, delete_json, ApiClientError


def render_purchase_requests_view():
    st.subheader("العربيات المشتراة من العملاء")

    top1, top2 = st.columns(2)
    with top1:
        if st.button("تحديث البيانات", key="refresh_purchase_requests", use_container_width=True):
            st.rerun()
    with top2:
        show_add_form = st.toggle("إظهار فورم إضافة عربية مشتراة", value=True, key="toggle_purchase_requests")

    # =========================
    # إضافة
    # =========================
    if show_add_form:
        with st.expander("إضافة عربية مشتراة من عميل", expanded=True):
            with st.form("add_purchase_request_form"):
                seller_name = st.text_input("اسم البائع")
                seller_phone = st.text_input("رقم التليفون")
                seller_address = st.text_input("العنوان")
                car_name = st.text_input("اسم العربية")
                brand = st.text_input("الماركة")
                model = st.text_input("الموديل")
                model_year = st.number_input("سنة الإصدار", min_value=1950, max_value=2100, step=1, value=2007)
                color = st.text_input("اللون")
                license_status = st.text_input("حالة الرخصة")
                description = st.text_area("الوصف")
                asking_price = st.number_input("السعر المطلوب", min_value=0.0, step=1000.0)
                status = st.text_input("الحالة", value="pending")

                submitted = st.form_submit_button("حفظ العربية المشتراة", use_container_width=True)
                if submitted:
                    try:
                        post_json("/purchase-requests", {
                            "seller_name": seller_name,
                            "seller_phone": seller_phone,
                            "seller_address": seller_address,
                            "car_name": car_name,
                            "brand": brand,
                            "model": model,
                            "model_year": int(model_year),
                            "color": color,
                            "license_status": license_status,
                            "description": description,
                            "asking_price": asking_price,
                            "status": status,
                        })
                        st.success("تمت إضافة العربية المشتراة")
                        st.rerun()
                    except ApiClientError as e:
                        st.error(str(e))

    # =========================
    # تحميل البيانات
    # =========================
    try:
        rows = get_json("/purchase-requests")
    except ApiClientError as e:
        st.error(str(e))
        return

    st.markdown("---")
    st.markdown("### البيانات الحالية")

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عربيات مشتراة حالياً")

    # =========================
    # تعديل / حذف
    # =========================
    st.markdown("---")
    st.markdown("### تعديل أو حذف سجل")

    if not rows:
        st.warning("لا توجد بيانات للتعديل أو الحذف")
        return

    labels = {f"سجل {r['request_id']} - {r.get('car_name') or ''}": r for r in rows}
    selected_label = st.selectbox("اختر السجل", list(labels.keys()))
    selected = labels[selected_label]

    with st.form("edit_purchase_request_form"):
        seller_name = st.text_input("اسم البائع", value=selected.get("seller_name") or "")
        seller_phone = st.text_input("رقم التليفون", value=selected.get("seller_phone") or "")
        seller_address = st.text_input("العنوان", value=selected.get("seller_address") or "")
        car_name = st.text_input("اسم العربية", value=selected.get("car_name") or "")
        brand = st.text_input("الماركة", value=selected.get("brand") or "")
        model = st.text_input("الموديل", value=selected.get("model") or "")
        model_year = st.number_input("سنة الإصدار", min_value=1950, max_value=2100, step=1, value=int(selected.get("model_year") or 2007))
        color = st.text_input("اللون", value=selected.get("color") or "")
        license_status = st.text_input("حالة الرخصة", value=selected.get("license_status") or "")
        description = st.text_area("الوصف", value=selected.get("description") or "")
        asking_price = st.number_input("السعر المطلوب", min_value=0.0, value=float(selected.get("asking_price") or 0))
        status = st.text_input("الحالة", value=selected.get("status") or "pending")

        submitted = st.form_submit_button("تعديل السجل", use_container_width=True)
        if submitted:
            try:
                put_json(f"/purchase-requests/{selected['request_id']}", {
                    "seller_name": seller_name,
                    "seller_phone": seller_phone,
                    "seller_address": seller_address,
                    "car_name": car_name,
                    "brand": brand,
                    "model": model,
                    "model_year": int(model_year),
                    "color": color,
                    "license_status": license_status,
                    "description": description,
                    "asking_price": asking_price,
                    "status": status,
                })
                st.success("تم تعديل السجل")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    if st.button("حذف السجل", key="delete_purchase_request", type="primary", use_container_width=True):
        try:
            delete_json(f"/purchase-requests/{selected['request_id']}")
            st.success("تم حذف السجل")
            st.rerun()
        except ApiClientError as e:
            st.error(str(e))
