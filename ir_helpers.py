import dash_bootstrap_components as dbc

def render_model_inputs(model_name):
    params = model_config.get(model_name, {}).get("parameters", [])
    input_components = []

    for param in params:
        input_components.append(dbc.Label(param["label"]))
        input_components.append(
            dbc.Input(
                id=param["id"],  # model-specific ID
                type="number",
                value=param["default"],
                step=0.01
            )
        )

    return input_components



model_config = {
    "vasicek": {
        "parameters": [
            {"id": "vasicek-a", "label": "Mean Reversion Speed (a)", "type": "float", "default": 0.1},
            {"id": "vasicek-b", "label": "Long-Term Mean (b)", "type": "float", "default": 0.05},
            {"id": "vasicek-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "vasicek-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    },
    "cir": {
        "parameters": [
            {"id": "cir-a", "label": "Mean Reversion Speed (a)", "type": "float", "default": 0.1},
            {"id": "cir-b", "label": "Long-Term Mean (b)", "type": "float", "default": 0.05},
            {"id": "cir-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "cir-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    },
    "hw": {
        "parameters": [
            {"id": "hw-theta", "label": "Drift Adjustment (θ)", "type": "float", "default": 0.02},
            {"id": "hw-lambda", "label": "Mean Reversion Speed (λ)", "type": "float", "default": 0.1},
            {"id": "hw-sigma", "label": "Volatility (σ)", "type": "float", "default": 0.01},
            {"id": "hw-r0", "label": "Initial Short Rate (r₀)", "type": "float", "default": 0.03}
        ]
    }
}

# Platform: Linux-6.12.12+bpo-cloud-amd64-x86_64-with-glibc2.31
# Architecture: ('64bit', 'ELF')
# CPU Count: 48