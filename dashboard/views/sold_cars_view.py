import pandas as pd
import streamlit as st

from api_client import get_json, post_json, put_json, delete_json, ApiClientError
from helpers import translate_dataframe_columns, translate_dataframe_values


def render_sold_cars_view():
    st.subheader("العربيات المباعة")

    top1, top2 = st.columns(2)
    with top1:
        if st.button("تحديث البيانات", key="refresh_sold_cars", use_container_width=True):
            st.rerun()
    with top2:
        show_add_form = st.toggle("إظهار فورم إضافة عملية بيع", value=True, key="toggle_sold_cars")

    # =========================
    # إضافة عملية بيع
    # =========================
    if show_add_form:
        with st.expander("إضافة عملية بيع جديدة", expanded=True):
            with st.form("add_sold_car_form"):
                car_id = st.number_input("رقم العربية", min_value=1, step=1)
                customer_id = st.number_input("رقم العميل", min_value=0, step=1)
                buyer_name = st.text_input("اسم المشتري")
                buyer_phone = st.text_input("رقم التليفون")
                buyer_address = st.text_input("العنوان")
                cash_price = st.number_input("السعر كاش", min_value=0.0, step=1000.0)
                down_payment = st.number_input("المقدم", min_value=0.0, step=1000.0)
                remaining_amount = st.number_input("المتبقي", min_value=0.0, step=1000.0)
                installment_months = st.number_input("عدد الشهور", min_value=0, step=1)
                installment_end_date = st.text_input("تاريخ انتهاء التقسيط YYYY-MM-DD")
                installment_value = st.number_input("قيمة القسط", min_value=0.0, step=1000.0)

                submitted = st.form_submit_button("حفظ عملية البيع", use_container_width=True)
                if submitted:
                    try:
                        post_json("/sold-cars", {
                            "car_id": int(car_id),
                            "customer_id": int(customer_id) if customer_id else None,
                            "buyer_name": buyer_name,
                            "buyer_phone": buyer_phone,
                            "buyer_address": buyer_address,
                            "cash_price": cash_price,
                            "down_payment": down_payment,
                            "remaining_amount": remaining_amount,
                            "installment_months": int(installment_months),
                            "installment_end_date": installment_end_date or None,
                            "installment_value": installment_value,
                        })
                        st.success("تمت إضافة عملية البيع")
                        st.rerun()
                    except ApiClientError as e:
                        st.error(str(e))

    # =========================
    # تحميل البيانات
    # =========================
    try:
        rows = get_json("/sold-cars")
    except ApiClientError as e:
        st.error(str(e))
        return

    st.markdown("---")
    st.markdown("### البيانات الحالية")

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عمليات بيع حالياً")

    # =========================
    # تعديل / حذف
    # =========================
    st.markdown("---")
    st.markdown("### تعديل أو حذف عملية بيع")

    if not rows:
        st.warning("لا توجد بيانات للتعديل أو الحذف")
        return

    labels = {f"بيع {r['sale_id']} - {r.get('buyer_name') or ''}": r for r in rows}
    selected_label = st.selectbox("اختر عملية البيع", list(labels.keys()))
    selected = labels[selected_label]

    with st.form("edit_sold_car_form"):
        car_id = st.number_input("رقم العربية", min_value=1, step=1, value=int(selected.get("car_id") or 1))
        customer_id = st.number_input("رقم العميل", min_value=0, step=1, value=int(selected.get("customer_id") or 0))
        buyer_name = st.text_input("اسم المشتري", value=selected.get("buyer_name") or "")
        buyer_phone = st.text_input("رقم التليفون", value=selected.get("buyer_phone") or "")
        buyer_address = st.text_input("العنوان", value=selected.get("buyer_address") or "")
        cash_price = st.number_input("السعر كاش", min_value=0.0, value=float(selected.get("cash_price") or 0))
        down_payment = st.number_input("المقدم", min_value=0.0, value=float(selected.get("down_payment") or 0))
        remaining_amount = st.number_input("المتبقي", min_value=0.0, value=float(selected.get("remaining_amount") or 0))
        installment_months = st.number_input("عدد الشهور", min_value=0, step=1, value=int(selected.get("installment_months") or 0))
        installment_end_date = st.text_input("تاريخ انتهاء التقسيط YYYY-MM-DD", value=selected.get("installment_end_date") or "")
        installment_value = st.number_input("قيمة القسط", min_value=0.0, value=float(selected.get("installment_value") or 0))

        submitted = st.form_submit_button("تعديل عملية البيع", use_container_width=True)
        if submitted:
            try:
                put_json(f"/sold-cars/{selected['sale_id']}", {
                    "car_id": int(car_id),
                    "customer_id": int(customer_id) if customer_id else None,
                    "buyer_name": buyer_name,
                    "buyer_phone": buyer_phone,
                    "buyer_address": buyer_address,
                    "cash_price": cash_price,
                    "down_payment": down_payment,
                    "remaining_amount": remaining_amount,
                    "installment_months": int(installment_months),
                    "installment_end_date": installment_end_date or None,
                    "installment_value": installment_value,
                })
                st.success("تم تعديل عملية البيع")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    if st.button("حذف عملية البيع", key="delete_sold_car", type="primary", use_container_width=True):
        try:
            delete_json(f"/sold-cars/{selected['sale_id']}")
            st.success("تم حذف عملية البيع")
            st.rerun()
        except ApiClientError as e:
            st.error(str(e))
