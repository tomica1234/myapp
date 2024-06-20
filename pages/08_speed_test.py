import streamlit as st
import speedtest
import matplotlib.pyplot as plt
import time

st.title('スピードテスト')
# def run_speedtest():
#     spt = speedtest.Speedtest()
#     spt.get_best_server()
#     download = round(spt.download() / 1_000_000)  # Mbps単位で変換
#     upload = round(spt.upload() / 1_000_000)  # Mbps単位で変換
#     st.write(f'download:{download},uoload:{upload}')
#     return download, upload
def run_speedtest():
    speed_test = speedtest.Speedtest()
    speed_test.get_best_server()

    # プログレスバーを設定
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text(f"ダウンロードテストを実行中...")

    download = speed_test.download() / 1_000_000  # Mbps単位で変換
    progress_bar.progress(50)  # 50%に更新

    progress_text.text(f"アップロードテストを実行中...")
    upload = speed_test.upload() / 1_000_000  # Mbps単位で変換
    progress_bar.progress(100)  # 完了を100%に更新
    progress_text.text(f"測定完了")

    # 結果をクリア
    time.sleep(1)
    progress_bar.empty()
    progress_text.empty()
    st.write(f'ダウンロード:{round(download)}アップロード:{round(upload)}')
    return download, upload
def plot_speeds(download, upload):
    labels = ['Download', 'Upload']
    speeds = [download, upload]
    plt.bar(labels, speeds, color=['blue', 'green'])
    plt.ylabel('Speed (Mbps)')
    plt.title('Internet Speed Test')
    st.pyplot(plt)

if st.button("測定"):
    download, upload = run_speedtest()
    plot_speeds(download, upload)
    