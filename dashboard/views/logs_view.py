import json
import os
import pandas as pd
import streamlit as st

from helpers import translate_dataframe_columns, translate_dataframe_values


def _read_json_lines(filepath: str, limit: int = 100):
    if not os.path.exists(filepath):
        return []

    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f.readlines()[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                rows.append({"message": line})

    return list(reversed(rows))


def render_logs_view():
    st.subheader("السجلات والأخطاء")

    tab1, tab2 = st.tabs(["سجلات التطبيق", "سجلات الأخطاء"])

    with tab1:
        app_logs = _read_json_lines("logs/app.log", limit=100)
        if not app_logs:
            st.info("لا توجد سجلات تطبيق بعد")
        else:
            df = pd.DataFrame(app_logs)
            df = translate_dataframe_values(df, "logs")
            df = translate_dataframe_columns(df, "logs")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        error_logs = _read_json_lines("logs/error.log", limit=100)
        if not error_logs:
            st.info("لا توجد أخطاء مسجلة بعد")
        else:
            df = pd.DataFrame(error_logs)
            df = translate_dataframe_values(df, "logs")
            df = translate_dataframe_columns(df, "logs")
            st.dataframe(df, use_container_width=True, hide_index=True)
