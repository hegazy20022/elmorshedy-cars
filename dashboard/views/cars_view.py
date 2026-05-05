import pandas as pd
import streamlit as st

from api_client import (
    get_json,
    post_json,
    put_json,
    delete_json,
    post_files,
    ApiClientError,
)
from helpers import translate_dataframe_columns, translate_dataframe_values


CLASS_LEVEL_OPTIONS = ["", "فئة أولى", "فئة ثانية", "فئة ثالثة"]


def render_car_images_section(car_id: int):
    st.markdown("### صور العربية")

    try:
        images = get_json(f"/car-images/{car_id}")
    except ApiClientError as e:
        st.error(str(e))
        return

    uploaded_files = st.file_uploader(
        "ارفع صور العربية بحد أقصى 10 صور",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key=f"car_upload_{car_id}",
    )

    if st.button("حفظ الصور", key=f"save_images_{car_id}", use_container_width=True):
        if not uploaded_files:
            st.warning("اختر صورة أو أكثر أولًا")
        else:
            try:
                files_payload = []
                for f in uploaded_files:
                    files_payload.append(
                        ("files", (f.name, f.getvalue(), f.type or "image/jpeg"))
                    )

                post_files(f"/car-images/{car_id}", files=files_payload)
                st.success("تم رفع الصور بنجاح")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    if images:
        st.markdown("### الصور الحالية")
        cols = st.columns(2)

        for idx, img in enumerate(images):
            with cols[idx % 2]:
                image_url = f"http://127.0.0.1:8000{img['image_url']}"
                st.image(image_url, use_container_width=True)

                if st.button(
                    "حذف الصورة",
                    key=f"delete_img_{img['image_id']}",
                    use_container_width=True,
                ):
                    try:
                        delete_json(f"/car-images/{img['image_id']}")
                        st.success("تم حذف الصورة")
                        st.rerun()
                    except ApiClientError as e:
                        st.error(str(e))
    else:
        st.info("لا توجد صور لهذه العربية")


def render_cars_view():
    st.subheader("العربيات")

    top1, top2 = st.columns(2)
    with top1:
        if st.button("تحديث البيانات", use_container_width=True):
            st.rerun()
    with top2:
        show_add_form = st.toggle("إظهار فورم إضافة عربية", value=True)

    # =========================
    # إضافة عربية
    # =========================
    if show_add_form:
        with st.expander("إضافة عربية جديدة", expanded=True):
            with st.form("add_car_form"):
                car_name = st.text_input("اسم العربية")
                brand = st.text_input("الماركة")
                model = st.text_input("الموديل")
                model_year = st.number_input("سنة الإصدار", min_value=1950, max_value=2100, step=1, value=2007)
                color = st.text_input("اللون")
                description = st.text_area("الوصف")
                license_status = st.text_input("حالة الرخصة")
                cash_price = st.number_input("السعر كاش", min_value=0.0, step=1000.0)
                installment_price = st.number_input("السعر قسط", min_value=0.0, step=1000.0)

                transmission = st.selectbox("الفتيس", ["", "automatic", "manual"])
                fuel_type = st.selectbox("نوع الوقود", ["", "petrol", "diesel", "hybrid", "gas"])
                body_type = st.selectbox("نوع العربية", ["", "sedan", "suv", "hatchback"])
                class_level = st.selectbox("فئة العربية", CLASS_LEVEL_OPTIONS)
                engine_cc = st.number_input("سعة الموتور", min_value=0, step=100)
                fuel_economy_level = st.selectbox("استهلاك البنزين", ["", "low", "medium", "high"])
                mileage = st.number_input("العداد", min_value=0, step=1000)
                paint_status = st.text_input("حالة الرش")

                city_friendly = st.checkbox("مناسبة للمدينة")
                family_friendly = st.checkbox("مناسبة للعائلة")
                reliable = st.checkbox("اعتمادية")
                economic = st.checkbox("اقتصادية")

                usage_tags = []
                if reliable:
                    usage_tags.append("اعتمادية")
                if economic:
                    usage_tags.append("اقتصادية")
                if family_friendly:
                    usage_tags.append("عائلية")
                if city_friendly:
                    usage_tags.append("مدينة")

                submitted = st.form_submit_button("حفظ العربية", use_container_width=True)

                if submitted:
                    try:
                        post_json("/cars", {
                            "car_name": car_name,
                            "brand": brand,
                            "model": model,
                            "model_year": int(model_year),
                            "color": color,
                            "description": description,
                            "license_status": license_status,
                            "cash_price": cash_price,
                            "installment_price": installment_price,
                            "transmission": transmission,
                            "fuel_type": fuel_type,
                            "body_type": body_type,
                            "class_level": class_level,
                            "engine_cc": int(engine_cc),
                            "usage_tags": usage_tags,
                            "city_friendly": city_friendly,
                            "family_friendly": family_friendly,
                            "fuel_economy_level": fuel_economy_level,
                            "mileage": int(mileage),
                            "paint_status": paint_status,
                            "is_sold": False,
                            "is_available": True,
                        })
                        st.success("تمت إضافة العربية")
                        st.rerun()
                    except ApiClientError as e:
                        st.error(str(e))

    # =========================
    # تحميل البيانات
    # =========================
    try:
        rows = get_json("/cars")
    except ApiClientError as e:
        st.error(str(e))
        return

    st.markdown("---")
    st.markdown("### البيانات الحالية")

    if rows:
        df = pd.DataFrame(rows)
        df = translate_dataframe_values(df, "cars")
        df = translate_dataframe_columns(df, "cars")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد عربيات حالياً لكن يمكنك الإضافة من الفورم بالأعلى")

    # =========================
    # تعديل / حذف
    # =========================
    st.markdown("---")
    st.markdown("### تعديل أو حذف عربية")

    if not rows:
        st.warning("لا يمكن التعديل أو الحذف الآن لأنه لا توجد بيانات بعد")
        st.selectbox("اختر العربية", options=["لا توجد عربيات"], disabled=True)
        st.text_input("اسم العربية", disabled=True)
        st.text_input("الماركة", disabled=True)
        st.text_input("الموديل", disabled=True)

        col1, col2 = st.columns(2)
        with col1:
            st.button("تعديل العربية", disabled=True, use_container_width=True)
        with col2:
            st.button("حذف العربية", disabled=True, use_container_width=True)
        return

    labels = {f"عربية {r['car_id']} - {r.get('car_name') or ''}": r for r in rows}
    selected_label = st.selectbox("اختر العربية", list(labels.keys()))
    selected = labels[selected_label]

    st.markdown("## صور العربية المختارة")
    st.info(f"أنت الآن على العربية رقم {selected['car_id']}")

    with st.expander("إدارة صور العربية", expanded=True):
        render_car_images_section(selected["car_id"])

    st.markdown("---")

    selected_class_level = selected.get("class_level") or ""
    if selected_class_level not in CLASS_LEVEL_OPTIONS:
        selected_class_level = ""

    with st.form("edit_car_form"):
        car_name = st.text_input("اسم العربية", value=selected.get("car_name") or "")
        brand = st.text_input("الماركة", value=selected.get("brand") or "")
        model = st.text_input("الموديل", value=selected.get("model") or "")
        model_year = st.number_input(
            "سنة الإصدار",
            min_value=1950,
            max_value=2100,
            value=int(selected.get("model_year") or 2000)
        )
        color = st.text_input("اللون", value=selected.get("color") or "")
        description = st.text_area("الوصف", value=selected.get("description") or "")
        license_status = st.text_input("حالة الرخصة", value=selected.get("license_status") or "")
        cash_price = st.number_input("السعر كاش", min_value=0.0, value=float(selected.get("cash_price") or 0))
        installment_price = st.number_input("السعر قسط", min_value=0.0, value=float(selected.get("installment_price") or 0))

        transmission = st.text_input("الفتيس", value=selected.get("transmission") or "")
        fuel_type = st.text_input("نوع الوقود", value=selected.get("fuel_type") or "")
        body_type = st.text_input("نوع العربية", value=selected.get("body_type") or "")
        class_level = st.selectbox(
            "فئة العربية",
            CLASS_LEVEL_OPTIONS,
            index=CLASS_LEVEL_OPTIONS.index(selected_class_level),
        )
        engine_cc = st.number_input("سعة الموتور", min_value=0, value=int(selected.get("engine_cc") or 0))
        fuel_economy_level = st.text_input("استهلاك البنزين", value=selected.get("fuel_economy_level") or "")
        mileage = st.number_input("العداد", min_value=0, value=int(selected.get("mileage") or 0))
        paint_status = st.text_input("حالة الرش", value=selected.get("paint_status") or "")

        city_friendly = st.checkbox("مناسبة للمدينة", value=bool(selected.get("city_friendly")))
        family_friendly = st.checkbox("مناسبة للعائلة", value=bool(selected.get("family_friendly")))
        is_sold = st.checkbox("تم البيع", value=bool(selected.get("is_sold")))
        is_available = st.checkbox("متاحة", value=bool(selected.get("is_available")))

        submitted = st.form_submit_button("تعديل العربية", use_container_width=True)
        if submitted:
            try:
                put_json(f"/cars/{selected['car_id']}", {
                    "car_name": car_name,
                    "brand": brand,
                    "model": model,
                    "model_year": int(model_year),
                    "color": color,
                    "description": description,
                    "license_status": license_status,
                    "cash_price": cash_price,
                    "installment_price": installment_price,
                    "transmission": transmission,
                    "fuel_type": fuel_type,
                    "body_type": body_type,
                    "class_level": class_level,
                    "engine_cc": int(engine_cc),
                    "city_friendly": city_friendly,
                    "family_friendly": family_friendly,
                    "fuel_economy_level": fuel_economy_level,
                    "mileage": int(mileage),
                    "paint_status": paint_status,
                    "is_sold": is_sold,
                    "is_available": is_available,
                })
                st.success("تم تعديل العربية")
                st.rerun()
            except ApiClientError as e:
                st.error(str(e))

    if st.button("حذف العربية", type="primary", use_container_width=True):
        try:
            delete_json(f"/cars/{selected['car_id']}")
            st.success("تم حذف العربية")
            st.rerun()
        except ApiClientError as e:
            st.error(str(e))
