import streamlit as st


class CustomSpinner:
    CSS_INSERTED = False

    def __init__(self, placeholder, message=""):
        self.placeholder = placeholder
        self.message = message

    def _inject_css(self):
        if not CustomSpinner.CSS_INSERTED:
            st.markdown(
                """
            <style>
            .custom-spinner-container {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 0;
                margin: 0;
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Spinner */
            .custom-spinner {
                border: 3px solid #e6e6e6;
                border-top: 3px solid #ff6b6b;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 0.9s linear infinite;
                background: transparent !important;
            }

            .custom-spinner-message {
                font-weight: 600;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )
            CustomSpinner.CSS_INSERTED = True

    def show(self):
        self._inject_css()
        html = f"""
        <div class="custom-spinner-container">
            <div class="custom-spinner"></div>
            <span class="custom-spinner-message">{self.message}</span>
        </div>
        """
        self.placeholder.markdown(html, unsafe_allow_html=True)

    def clear(self):
        self.placeholder.empty()
