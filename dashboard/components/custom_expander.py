import streamlit as st


class CustomExpander:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        st.markdown(
            """
            <style>
            details {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                border-radius: 0 !important;
            }

            summary {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
                border-radius: 0 !important;
            }

            summary:hover {
                background-color: transparent !important;
            }

            .streamlit-expander {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
            }

            .streamlit-expanderHeader, .streamlit-expanderContent {
                border: none !important;
                box-shadow: none !important;
                background-color: transparent !important;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        self.expander = st.expander(self.label)
        return self.expander

    def __exit__(self, exc_type, exc, tb):
        pass
