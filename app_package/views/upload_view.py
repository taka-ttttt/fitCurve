import streamlit as st
from ..storage import Storage

def render(storage: Storage):
    """
    ・CSVファイルをアップロード
    ・ファイル選択時にstorage.on_file_uploadedによりRawDataとして保存
    """
    uploaded_file = st.file_uploader(
        "CSVファイルをアップロード",
        type="csv",
    )
    if uploaded_file is not None:
        storage.on_file_uploaded(uploaded_file)
        st.success("ファイルを読み込みました！")
