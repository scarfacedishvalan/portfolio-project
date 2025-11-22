import dash
from dash import html
from dash_extensions import Lottie
import json
# Create Dash app
app = dash.Dash(__name__)

# Layout with a looping Lottie animation
app.layout = html.Div([
    Lottie(
        options=dict(loop=True, autoplay=True),
        width="25%",
        height="25%",
        # url="https://assets1.lottiefiles.com/packages/lf20_jcikwtux.json"
        url="/assets/flowchart2.json"
    )
])

# Run the app
if __name__ == "__main__":
    app.run(debug=True)  # ✅ new method
