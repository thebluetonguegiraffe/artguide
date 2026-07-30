import os

import reflex as rx

# In the Docker deploy REFLEX_PORT is set so frontend + backend share a single
# exposed port. Left unset, `reflex run` keeps its normal dev ports (3000/8000).
_prod_port = os.environ.get("REFLEX_PORT")
_prod_overrides = {}
if _prod_port:
    _public_url = os.environ.get("DASHBOARD_PUBLIC_URL", f"http://localhost:{_prod_port}")
    _prod_overrides = {
        "frontend_port": int(_prod_port),
        "backend_port": int(_prod_port),
        "backend_host": "0.0.0.0",
        "api_url": _public_url,
        "deploy_url": _public_url,
    }

config = rx.Config(
    app_name="artguide_app",
    telemetry_enabled=False,
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                accent_color="amber",
                gray_color="sand",
                radius="large",
                panel_background="solid",
            ),
        ),
    ],
    **_prod_overrides,
)
