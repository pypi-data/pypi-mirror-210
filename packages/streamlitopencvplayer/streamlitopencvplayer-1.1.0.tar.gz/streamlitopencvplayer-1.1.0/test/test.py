import streamlit as st

from streamlitopencvplayer.app import display_video

# Initiate all session states used
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
if 'frames' not in st.session_state:
    st.session_state['frames'] = []


def main():

    alerts_dict = {"Alerts": [43, 64]}
    alerts = [43, 64]
    data = [[[10, 100, 290, 200], 0.82, 0, "Class 0"],
            [[55, 22, 100, 120], 0.9, 1, "Class 1"]]
    video_path = "https://cvlogger.blob.core.windows.net/clientsample/1678352121.8713963_1678352127.8713963.webm?se=2023-05-25T14%3A31%3A49Z&sp=r&sv=2021-08-06&sr=b&sig=358A3taHXFqd86m7CRCk9tbGW6V5K73nBD8H%2Bsu9QWk%3D"
    if video_path is not None:
        display_video(video_path, alerts_dict, alerts, data)


if __name__ == "__main__":
    main()
