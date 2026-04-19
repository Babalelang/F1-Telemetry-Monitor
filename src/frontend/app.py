import dash
from src.frontend.layout import build_layout
from src.frontend.callbacks import register_callbacks

app = dash.Dash(
    __name__,
    title="F1 Telemetry",
    update_title=None,
    suppress_callback_exceptions=True,
)

app.layout = build_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)