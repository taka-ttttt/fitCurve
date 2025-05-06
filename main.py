import streamlit as st
from app_package.storage import Storage
from app_package.views import upload_view, raw_data_view, ss_chart_view, fit_settings_view, fit_result_view


def main():
    storage = Storage(state=st.session_state)

    st.title("硬化則カーブフィッティング")
    upload_view.render(storage)
    raw_data_view.render(storage)
    ss_chart_view.render(storage)
    fit_settings_view.render(storage)
    fit_result_view.render(storage)

if __name__ == "__main__":
    main()