import streamlit as st
from dashboard.translations import TEXT_TRANSLATIONS as tt


def create_sidebar():
    if "language" not in st.session_state:
        st.session_state.language = "en"

    if "speaker" not in st.session_state:
        st.session_state.speaker = "female"

    if "duration" not in st.session_state:
        st.session_state.duration = "short"

    # Store previous language to detect changes
    if "previous_language" not in st.session_state:
        st.session_state.previous_language = st.session_state.language

    with st.sidebar:
        st.header(tt[st.session_state.language]["config"])
        st.divider()

        # Language selector
        language_options = {tt[lang]["language_name"]: lang for lang in tt.keys()}

        selected_lang = st.selectbox(
            tt[st.session_state.language]["language"],
            options=list(language_options.keys()),
            index=list(language_options.values()).index(st.session_state.language),
            key="language_selector",
        )

        new_language = language_options[selected_lang]

        if new_language != st.session_state.previous_language:
            st.session_state.language = new_language
            st.session_state.previous_language = new_language
            st.rerun()

        # Speaker selector
        speaker_options = {
            tt[st.session_state.language]["female_speaker"]: "female",
            tt[st.session_state.language]["male_speaker"]: "male",
        }

        selected_speaker = st.selectbox(
            tt[st.session_state.language]["speaker"],
            options=list(speaker_options.keys()),
            index=list(speaker_options.values()).index(st.session_state.speaker),
            key="speaker_selector",
        )

        st.session_state.speaker = speaker_options[selected_speaker]

        # Duration selector
        duration_options = {
            tt[st.session_state.language]["short_audio"]: "short",
            tt[st.session_state.language]["medium_audio"]: "medium",
            tt[st.session_state.language]["long_audio"]: "long",
        }

        selected_duration = st.selectbox(
            tt[st.session_state.language]["description_duration"],
            options=list(duration_options.keys()),
            index=list(duration_options.values()).index(st.session_state.duration),
            key="duration_selector",
        )

        st.session_state.duration = duration_options[selected_duration]

        st.divider()

        st.header(tt[st.session_state.language]["links"])
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <a href="https://github.com/tu-usuario/tu-repo" target="_blank">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" width="24"> 
                </a>
                <span>{tt[st.session_state.language]["project_info"]}</span>
            </div>
            """,  # noqa
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-top: 8px;">
                <a href="mailto:thebluetonguegiraffe@gmail.com">
                    <img src="https://cdn-icons-png.flaticon.com/512/3178/3178158.png" width="24">
                </a>
                <span>{tt[st.session_state.language]["contact"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "language": st.session_state.language,
        "speaker": st.session_state.speaker,
        "duration": st.session_state.duration,
    }
