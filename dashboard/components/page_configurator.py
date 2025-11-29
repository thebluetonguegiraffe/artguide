import streamlit as st

from dashboard.pages.sidebar import create_sidebar


class PageConfigurator:

    def __init__(
        self,
        title="ArtGuide App",
        icon="img/logo-removebg.png",
        layout="centered",
        sidebar_state="collapsed",
        bg_color="#f7f4ee",
        topbar_color="#d4d0ca",
        sidebar_bg="#d4d0ca",
        sidebar_border="#c2bdb7",
    ):

        self.title = title
        self.icon = icon
        self.layout = layout
        self.sidebar_state = sidebar_state
        self.bg_color = bg_color
        self.topbar_color = topbar_color
        self.sidebar_bg = sidebar_bg
        self.sidebar_border = sidebar_border

    def configure(self):
        """Main method called by the app."""
        self._set_page_config()
        self._inject_css()
        config = create_sidebar()
        return config

    def _set_page_config(self):
        """Configure Streamlit page settings once."""
        st.set_page_config(
            page_title=self.title,
            page_icon=self.icon,
            layout=self.layout,
            initial_sidebar_state=self.sidebar_state,
        )

    def _inject_css(self):
        """Inject custom CSS into Streamlit only once."""

        css = f"""
        <style>
            /* App background */
            [data-testid="stAppViewContainer"] {{
                background-color: {self.bg_color} !important;
            }}

            /* Hide Streamlit elements */
            button[kind="header"] {{ display: none !important; }}
            [data-testid="stSidebarNav"] {{ display: none !important; }}
            [data-testid="stStatusWidget"] {{ display: none !important; }}
            #MainMenu {{ visibility: hidden !important; }}
            footer {{ visibility: hidden !important; }}

            /* Sidebar background */
            [data-testid="stSidebar"] > div:first-child {{
                background-color: {self.sidebar_bg} !important;
                border-right: 2px solid {self.sidebar_border} !important;
            }}

            /* Header bar */
            [data-testid="stHeader"] {{
                background-color: {self.topbar_color} !important;
            }}
        </style>
        """

        st.markdown(css, unsafe_allow_html=True)
