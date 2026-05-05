import streamlit as st
import pandas as pd
from datetime import datetime, time

from api_client import get_json, post_json, put_json, delete_json, ApiClientError


def format_time_12h(value):
    if value in (None, ""):
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%I:%M %p").lstrip("0")

    value_str = str(value).strip()

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            parsed = datetime.strptime(value_str, fmt)
            return parsed.strftime("%I:%M %p").lstrip("0")
        except Exception:
            continue

    return value_str


def parse_time_value(value):
    if isinstance(value, time):
        return value

    if value in (None, ""):
        return datetime.strptime("10:00", "%H:%M").time()

    value_str = str(value).strip()

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value_str, fmt).time()
        except Exception:
            continue

    return datetime.strptime("10:00", "%H:%M").time()


def render_bookings_view():
    st.subheader("الحجوزات")

    top1, top2 = st.columns(2)
    with top1:
        if st.button("تحديث البيانات", use_container_width=True):
            st.rerun()
    with top2:
        show_add_form = st.toggle("إظهار فورم إضافة حجز", value=True)

    if show_add_form:
        with st.expander("إضافة حجز جديد", expanded=True):
            with st.form("add_booking_form"):
                car_id = st.number_input("رقم العربية", min_value=1, step=1)
                customer_id = st.number_input("رقم العميل", min_value=1, step=1)
                customer_name = st.text_input("اسم العميل")
                customer_phone = st.text_input("هاتف العميل")
                customer_address = st.text_input("العنوان")
                booking_date = st.date_input("تاريخ الحجز")
                booking_time = st.time_input("وقت الحجز", value=parse_time_value("10:00"))
                notes = st.text_area("ملاحظات")

                submitted = st.form_submit_button("حفظ الحجز")
                if submitted:
                    try:
                        post_json("/bookings", {
                            "car_id": int(car_id),
                            "customer_id": int(customer_id),
                            "customer_name": customer_name,
                            "customer_phone": customer_phone,
                            "customer_address": customer_address,
                            "booking_date": booking_date.isoformat(),
                            "booking_time": booking_time.strftime("%H:%M:%S"),
                            "notes": notes,
                        })
                        st.success("تمت إضافة الحجز")
                        st.rerun()
                    except ApiClientError as e:
                        st.error(str(e))

    try:
        rows = get_json("/bookings")
    except ApiClientError as e:
        st.error(str(e))
        return

    st.markdown("---")
    st.markdown("### البيانات الحالية")

    if rows:
        df = pd.DataFrame(rows)

        possible_time_columns = ["وقت_الحجز", "booking_time", "وقت الحجز"]
        for col in possible_time_columns:
            if col in df.columns:
                df[col] = df[col].apply(format_time_12h)

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد حجوزات حالياً لكن يمكنك الإضافة من الفورم بالأعلى")

    st.markdown("---")
    st.markdown("### تعديل أو حذف حجز")

    if not rows:
        st.warning("لا يمكن التعديل أو الحذف الآن لأنه لا توجد بيانات بعد")
        st.selectbox("اختر الحجز", options=["لا توجد حجوزات"], disabled=True)
        st.text_input("اسم العميل", disabled=True)
        st.text_input("هاتف العميل", disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.button("تعديل الحجز", disabled=True, use_container_width=True)
        with col2:
            st.button("حذف الحجز", disabled=True, use_container_width=True)
        return

    labels = {f"حجز {r['رقم_الحجز']} - {r.get('اسم_العميل') or ''}": r for r in rows}
    selected_label = st.selectbox("اختر الحجز", list(labels.keys()))
    selected = labels[selected_label]

    selected_time_value = (
        selected.get("وقت_الحجز")
        or selected.get("booking_time")
        or selected.get("وقت الحجز")
        or "10:00"
    )

    with st.form("edit_booking_form"):
        customer_name = st.text_input("اسم العميل", value=selected.get("اسم_العميل") or "")
        customer_phone = st.text_input("هاتف العميل", value=selected.get("هاتف_العميل") or "")
        customer_address = st.text_input("العنوان", value=selected.get("العنوان") or "")
        notes = st.text_area("ملاحظات", value=selected.get("ملاحظات") or "")
        booking_date = st.date_input(
            "تاريخ الحجز",
            value=pd.to_datetime(selected.get("تاريخ_الحجز")).date() if selected.get("تاريخ_الحجز") else datetime.today().date()
        )
        booking_time = st.time_input("وقت الحجز", value=parse_time_value(selected_time_value))
        booking_status = st.selectbox(
            "الحالة",
            ["confirmed", "cancelled", "completed"],
            index=["confirmed", "cancelled", "completed"].index(
                selected.get("حالة_الحجز") or "confirmed"
            ) if (selected.get("حالة_الحجز") or "confirmed") in ["confirmed", "cancelled", "completed"] else 0
        )

        submitted = st.form_submit_button("تعديل الحجز")
        if submitted:
            try:
                put_json(f"/bookings/{selected['رقم_الحجز']}", {
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_address": customer_address,
                    "booking_date": booking_date.isoformat(),
                    "booking_time": booking_time.strftime("%H:%M:%S"),
                    "notes": notes,
                    "booking_status": booking_status,
                })
                st.success("تم تعديل الحجز")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    if st.button("حذف الحجز", type="primary", use_container_width=True):
        try:
            delete_json(f"/bookings/{selected['رقم_الحجز']}")
            st.success("تم حذف الحجز")
            st.rerun()
        except ApiClientError as e:
            st.error(str(e))
