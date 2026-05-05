import streamlit as st
from datetime import datetime, date

from api_client import get_json, put_json, ApiClientError


DAY_OPTIONS_AR = {
    "Saturday":  "السبت",
    "Sunday":    "الأحد",
    "Monday":    "الاثنين",
    "Tuesday":   "الثلاثاء",
    "Wednesday": "الأربعاء",
    "Thursday":  "الخميس",
    "Friday":    "الجمعة",
}
DAY_OPTIONS = list(DAY_OPTIONS_AR.keys())


def parse_time_value(value: str):
    if not value:
        return datetime.strptime("10:00", "%H:%M").time()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(value).strip(), fmt).time()
        except Exception:
            continue
    return datetime.strptime("10:00", "%H:%M").time()


def time_to_12h(t) -> tuple[int, int, str]:
    """تحويل وقت 24h لـ 12h + AM/PM"""
    h = t.hour
    m = t.minute
    period = "AM" if h < 12 else "PM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return h12, m, period


def build_time_str(hour12: int, minute: int, period: str) -> str:
    """تحويل 12h + AM/PM لـ HH:MM بصيغة 24h للحفظ"""
    h = hour12 % 12
    if period == "PM":
        h += 12
    return f"{h:02d}:{minute:02d}"


def render_settings_view():
    st.subheader("الإعدادات")
    st.markdown("### مواعيد العمل")

    try:
        booking = get_json("/settings/booking")
    except ApiClientError as e:
        st.error(str(e))
        return

    # -- تحليل الأوقات الحالية --
    start_h12, start_m, start_period = time_to_12h(parse_time_value(booking.get("start_time", "10:00")))
    end_h12,   end_m,   end_period   = time_to_12h(parse_time_value(booking.get("end_time",   "18:00")))

    # -- أيام الطوارئ الحالية --
    current_emergency = booking.get("emergency_closed_dates", [])

    with st.form("booking_settings_form"):
        # أيام العمل بالعربي
        selected_days_ar = st.multiselect(
            "أيام العمل",
            options=list(DAY_OPTIONS_AR.values()),
            default=[DAY_OPTIONS_AR[d] for d in booking.get("working_days", []) if d in DAY_OPTIONS_AR],
        )

        st.markdown("**وقت البداية**")
        start_hour = st.selectbox(
            "الساعة (بداية)", list(range(1, 13)), index=start_h12 - 1, key="start_h"
        )
        start_minute = st.selectbox(
            "الدقيقة (بداية)", [0, 15, 30, 45],
            index=[0,15,30,45].index(start_m) if start_m in [0,15,30,45] else 0,
            key="start_m", format_func=lambda x: f"{x:02d}"
        )
        start_ampm = st.selectbox(
            "ص/م (بداية)", ["AM", "PM"], index=0 if start_period == "AM" else 1, key="start_p"
        )

        st.markdown("**وقت النهاية**")
        end_hour = st.selectbox(
            "الساعة (نهاية)", list(range(1, 13)), index=end_h12 - 1, key="end_h"
        )
        end_minute = st.selectbox(
            "الدقيقة (نهاية)", [0, 15, 30, 45],
            index=[0,15,30,45].index(end_m) if end_m in [0,15,30,45] else 0,
            key="end_m", format_func=lambda x: f"{x:02d}"
        )
        end_ampm = st.selectbox(
            "ص/م (نهاية)", ["AM", "PM"], index=0 if end_period == "AM" else 1, key="end_p"
        )

        slot_duration_minutes = st.number_input(
            "مدة الحجز بالدقائق",
            min_value=15,
            step=15,
            value=int(booking.get("slot_duration_minutes", 60)),
        )

        st.markdown("**أيام الطوارئ** (اختار التاريخ ثم اضغط إضافة)")
        new_emergency_date = st.date_input("اختار يوم الطوارئ", value=date.today(), key="em_date")
        add_emergency = st.form_submit_button("إضافة يوم طوارئ")
        if add_emergency:
            date_str = str(new_emergency_date)
            if date_str not in current_emergency:
                current_emergency.append(date_str)
                st.success(f"تمت إضافة {new_emergency_date.strftime('%d/%m/%Y')}")

        if current_emergency:
            st.markdown("**الأيام المضافة:**")
            for d in current_emergency:
                try:
                    formatted = datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
                    st.markdown(f"- {formatted}")
                except Exception:
                    st.markdown(f"- {d}")

        submitted = st.form_submit_button("💾 حفظ مواعيد العمل", use_container_width=True)
        if submitted:
            # تحويل الأيام من عربي لإنجليزي
            ar_to_en = {v: k for k, v in DAY_OPTIONS_AR.items()}
            selected_days_en = [ar_to_en[d] for d in selected_days_ar if d in ar_to_en]

            try:
                put_json("/settings/booking", {
                    "working_days": selected_days_en,
                    "start_time": build_time_str(start_hour, start_minute, start_ampm),
                    "end_time":   build_time_str(end_hour,   end_minute,   end_ampm),
                    "slot_duration_minutes": int(slot_duration_minutes),
                    "emergency_closed_dates": current_emergency,
                })
                st.success("تم حفظ مواعيد العمل")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    st.markdown("---")

    if current_emergency:
        st.markdown("### حذف يوم طوارئ")
        to_remove = st.selectbox(
            "اختار اليوم للحذف",
            options=current_emergency,
            format_func=lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if len(d) == 10 else d,
        )
        if st.button("حذف هذا اليوم", type="primary"):
            current_emergency.remove(to_remove)
            try:
                put_json("/settings/booking", {
                    **booking,
                    "emergency_closed_dates": current_emergency,
                })
                st.success("تم حذف اليوم")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    st.markdown("---")
    st.markdown("### بيانات المعرض")

    try:
        contact = get_json("/settings/contact")
    except ApiClientError as e:
        st.error(str(e))
        return

    with st.form("business_contact_form"):
        phone = st.text_input("رقم الهاتف", value=contact.get("phone", ""))
        address = st.text_input("العنوان التفصيلي", value=contact.get("address", ""))
        location_url = st.text_input("رابط اللوكيشن", value=contact.get("location_url", ""))

        submitted = st.form_submit_button("حفظ بيانات المعرض", use_container_width=True)
        if submitted:
            try:
                put_json("/settings/contact", {
                    "phone": phone,
                    "address": address,
                    "location_url": location_url,
                })
                st.success("تم حفظ بيانات المعرض")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    st.markdown("---")
    st.markdown("### إعدادات الكاش")

    try:
        cache_settings = get_json("/settings/cache")
    except ApiClientError as e:
        st.error(str(e))
        return

    with st.form("cache_settings_form"):
        repeat_threshold = st.number_input(
            "عدد التكرار المطلوب لتفعيل الكاش",
            min_value=1,
            step=1,
            value=int(cache_settings.get("repeat_threshold", 3)),
        )
        ttl_hours = st.number_input(
            "مدة الكاش بالساعات",
            min_value=1,
            step=1,
            value=int(cache_settings.get("ttl_hours", 24)),
        )

        submitted = st.form_submit_button("حفظ إعدادات الكاش", use_container_width=True)
        if submitted:
            try:
                put_json("/settings/cache", {
                    "repeat_threshold": int(repeat_threshold),
                    "ttl_hours": int(ttl_hours),
                })
                st.success("تم حفظ إعدادات الكاش")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))


