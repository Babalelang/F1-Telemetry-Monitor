import dash
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.frontend.layout import build_layout
from src.frontend.callbacks import register_callbacks

app = dash.Dash(
    __name__,
    title="F1 Telemetry",
    update_title=None,
    suppress_callback_exceptions=True,
    assets_folder=os.path.join(os.path.dirname(__file__), "assets"),
)

app.layout = build_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=False, port=8050)

