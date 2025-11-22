import interest_rates.ir_helpers as ir_helpers
from dash.dependencies import Input, Output
import dash
import numpy as np
import plotly.graph_objs as go
import numpy as np

def generate_summary_table(paths, t_grid, t_view):
    closest_index = (np.abs(t_grid - t_view)).argmin()
    time_closest = t_grid[closest_index]
    cross_section = paths[:, closest_index]

    # Compute statistics
    stats = [
        {"Statistic": "Time (closest to t_view)", "Value": f"{time_closest:.4f}"},
        {"Statistic": "Mean", "Value": f"{np.mean(cross_section):.4f}"},
        {"Statistic": "Median", "Value": f"{np.median(cross_section):.4f}"},
        {"Statistic": "Standard Deviation", "Value": f"{np.std(cross_section):.4f}"},
        {"Statistic": "Min", "Value": f"{np.min(cross_section):.4f}"},
        {"Statistic": "Max", "Value": f"{np.max(cross_section):.4f}"},
        {"Statistic": "Interquartile Range (IQR)", "Value": f"{np.percentile(cross_section, 75) - np.percentile(cross_section, 25):.4f}"},
        {"Statistic": "5th Percentile", "Value": f"{np.percentile(cross_section, 5):.4f}"},
        {"Statistic": "95th Percentile", "Value": f"{np.percentile(cross_section, 95):.4f}"}
    ]

    # Return DataTable
    return stats


def plot_distributions(paths, t_grid, t_view, nbins= 50):
    closest_index = (np.abs(t_grid - t_view)).argmin()
    time_closest = t_grid[closest_index]

    # Cross section at that time
    cross_section = paths[:, closest_index]

    # Plot histogram
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=cross_section,
        nbinsx=nbins,
        name=f'Distribution at t={time_closest:.2f} years'
    ))

    fig.update_layout(
        title=f'Distribution of Interest Rates at t ≈ {time_closest:.2f}',
        xaxis_title='Rate',
        yaxis_title='Frequency',
        bargap=0.1
    )

    return fig

def add_callbacks(app):
    @app.callback(
        Output("model-params-container", "children"),
        Input("model-select", "value")
    )
    def update_model_inputs(model_name):
        return ir_helpers.render_model_inputs(model_name)

    @app.callback(
        [
            Output("yield-curve-graph", "figure"),
            Output("simulation-store", "data")  # Store for paths and t
        ],
        Input("run-simulation-btn", "n_clicks"),
        Input("model-select", "value"),
        Input("model-params-container", "children"),
        Input("horizon-input", "value"),
        Input("paths-input", "value"),
        Input("timestep-input", "value"),
        prevent_initial_call=True
    )
    def run_simulation(n_clicks, model_name, param_children, T, M, N):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if "run-simulation-btn" in changed_id:
            try:
                params = {}
                for child in param_children:
                    try:
                        if model_name in child["props"]["id"]:
                            input_id = child["props"]["id"]
                            value = child["props"]["value"]
                            params[input_id] = value
                    except Exception:
                        continue

                if model_name == 'vasicek':
                    a = params.get("vasicek-a")
                    b = params.get("vasicek-b")
                    sigma = params.get("vasicek-sigma")
                    r0 = params.get("vasicek-r0")
                    if None in (a, b, sigma, r0, T, N, M):
                        print("None in Arguments!!")                        
                        return [dash.no_update, dash.no_update]

                    paths = ir_helpers.monte_carlo_vasicek_numba(a, b, sigma, r0, T, int(N), int(M))
                elif model_name == "cir":
                    a = params.get("cir-a")
                    b = params.get("cir-b")
                    sigma = params.get("cir-sigma")
                    r0 = params.get("cir-r0")
                    if None in (a, b, sigma, r0, T, N, M):
                        print("None in Arguments!!")
                        return [dash.no_update, dash.no_update]

                    paths = ir_helpers.monte_carlo_cir_numba(a, b, sigma, r0, T, int(N), int(M))                                        
                else:
                    return [dash.no_update, dash.no_update]                
                t = np.linspace(0, T, int(N) + 1)

                fig = go.Figure()
                for i in range(min(1000, len(paths))):
                    fig.add_trace(go.Scatter(x=t, y=paths[i], mode='lines'))
                model_name_str = ir_helpers.model_names[model_name]
                fig.update_layout(title=f"{model_name_str} Model Simulation (N = {N}, M = {M})", xaxis_title="Time", yaxis_title="Rate")
                fig.update_layout(showlegend=False)
                # Serialize for dcc.Store
                data = {"paths": paths.tolist(), "t": t.tolist()}

                return [fig, data]
            except Exception as e:
                print("Exception in simulations: ",  str(e))
                return [dash.no_update, dash.no_update]
        else:
            return [dash.no_update, dash.no_update]


    @app.callback(
        [Output("dist-graph", "figure"), Output("summary-table", "data")], 
        Input("cross-section-btn", "n_clicks"),
        Input("t-view", "value"),
        Input("simulation-store", "data"),
        Input("nbinsx-input", "value"),        
        prevent_initial_call=True
    )
    def update_distribution_graph(n, t_view, simulation_data, nbins):

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if "cross-section-btn" in changed_id:        
            # Extract paths and t from stored data
            try:
                paths = np.array(simulation_data.get("paths"))
                t_grid = np.array(simulation_data.get("t"))

                # Call your distribution plotting function
                fig = plot_distributions(paths, t_grid, t_view, nbins)

                summary_data = generate_summary_table(paths, t_grid, t_view)

                return [fig, summary_data]  
            except Exception as e:
                return [dash.no_update, dash.no_update]
        else:
            try:
                if simulation_data is None or t_view is None:
                    return [dash.no_update, dash.no_update]
                paths = np.array(simulation_data.get("paths"))
                t_grid = np.array(simulation_data.get("t"))

                # Call your distribution plotting function
                fig = plot_distributions(paths, t_grid, t_view)

                summary_data = generate_summary_table(paths, t_grid, t_view)

                return [fig, summary_data]  
            except Exception as e:
                return [dash.no_update, dash.no_update]

    @app.callback(
        Output("t-view", "value"),
        Input("horizon-input", "value"),
        prevent_initial_call=False  # Set this True if you don’t want it to fire initially
    )
    def set_tview_from_horizon(horizon):
        return horizon


    return app