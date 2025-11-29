import tempfile
import os
import streamlit as st
from dotenv import load_dotenv

from dashboard.components.custom_expander import CustomExpander
from dashboard.components.custom_spinner import CustomSpinner
from dashboard.components.page_configurator import PageConfigurator
from dashboard.translations import TEXT_TRANSLATIONS as tt
from dashboard.utils import play_audio_streamlit

from src.agent.artguide_agent import ArtGuide

config = PageConfigurator().configure()


def app_artguide():
    language = config["language"]
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None

    col1, _, _ = st.columns([2, 1, 1])
    with col1:
        st.image("img/placeholder_title.png", width="stretch")

    if st.session_state.uploaded_image is None:
        tab1, tab2 = st.tabs([tt[language]["upload_image_tab"], tt[language]["take_photo_tab"]])

        with tab1:
            st.markdown(
                """
                <style>
                div[data-testid="stFileUploader"] > section {
                    background-color: #ffffff;
                    padding: 15px;
                    border-radius: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            uploaded_file = st.file_uploader(
                label="not_shown",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
            )
            if uploaded_file:
                st.session_state.uploaded_image = uploaded_file
                st.rerun()

        with tab2:
            st.markdown(
                """
                <style>
                /* Target the camera input container */
                div[data-testid="stCameraInput"] > section {
                    background-color: #ffffff;  /* Change this to any color */
                    padding: 15px;
                    border-radius: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            camera_photo = st.camera_input(
                label="not_shown",
                label_visibility="collapsed",
            )
            if camera_photo:
                st.session_state.uploaded_image = camera_photo
                st.rerun()

    elif st.session_state.uploaded_image is not None:
        load_dotenv()
        agent = ArtGuide(config=config)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(st.session_state.uploaded_image.getvalue())
            temp_image_path = tmp_file.name

        try:
            col1, col2 = st.columns([1, 1])

            with col1:
                image_placeholder = st.empty()

            with col2:
                title_placeholder = st.empty()
                year_placeholder = st.empty()
                museum_placeholder = st.empty()
                audio_placeholder = st.empty()
                spinner_placeholder = st.empty()

            audio_generating = False

            for update in agent.run_streaming(temp_image_path):
                if "top_result" in update["state"]:
                    title = update["state"]["top_result"]["title"]
                    artist = update["state"]["top_result"]["artist"]

                    with col1:
                        image_placeholder.image(st.session_state.uploaded_image)

                    with col2:
                        title_placeholder.markdown(
                            f"### {title}\n" f"{tt[language]['by']} **{artist}**"
                        )
                        if not audio_generating:
                            spinner = CustomSpinner(
                                spinner_placeholder, tt[language]["generating_audio"]
                            )
                            spinner.show()
                            audio_generating = True

                if "sr" in update["state"]:
                    spinner_placeholder.empty()
                    with col2:
                        year_placeholder.markdown(f"🗓️ {update['state']['top_result']['year']}")
                        museum_placeholder.markdown(f"🏛️ {update['state']['top_result']['museum']}")
                        play_audio_streamlit(
                            update["state"]["samples"], update["state"]["sr"], audio_placeholder
                        )
                        with CustomExpander(tt[language]["description"]) as expander:
                            expander.write(update["state"]["top_result"]["description"])
                    audio_generating = False

                if 'status' in update['state'] and update["state"]['status'] == "error":
                    with col1:
                        image_placeholder.image(st.session_state.uploaded_image)

                    with col2:
                        title_placeholder.markdown(f"### {tt[language]['unknown']}")
                        st.error(tt[language]["retry"], icon="⚠️")

        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state.uploaded_image = None
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    st.write("")
    cols = st.columns([1, 1])
    with cols[0]:
        if st.button(tt[language]["back"], use_container_width=True, key="bk_btn"):
            st.switch_page("main.py")
    with cols[1]:
        if st.button(tt[language]["upload_another"], use_container_width=True, key="restart_btn"):
            st.rerun()


app_artguide()
