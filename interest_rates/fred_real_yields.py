import pandas_datareader.data as web
import datetime
import datetime
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "yields_history.csv")

class USYieldCurveLoader:
    
    # Maturity mapping in months
    DGS_MATURITY_MAP_MONTHS = {
        1:  "DGS1MO",   # 1 Month
        3:  "DGS3MO",   # 3 Months
        6:  "DGS6MO",   # 6 Months
        12: "DGS1",     # 1 Year
        24: "DGS2",     # 2 Years
        36: "DGS3",     # 3 Years
        60: "DGS5",     # 5 Years
        84: "DGS7",     # 7 Years
        120:"DGS10",    # 10 Years
        240:"DGS20",    # 20 Years
        360:"DGS30"     # 30 Years
    }

    def __init__(self):
        self.start_date = datetime.datetime.today() - datetime.timedelta(days=365)
        self.end_date = datetime.datetime.today()
        self.data = None
        self.reversed_map = {v: k for k, v in self.DGS_MATURITY_MAP_MONTHS.items()}
        self.all_securities = list(self.DGS_MATURITY_MAP_MONTHS.values())

    def load_data(self, dump = True, use_cache = True):
        today = datetime.datetime.today()
        start_date = self.start_date
        end_date = self.end_date

        # If file doesn't exist, fetch from API
        if not os.path.exists(DATA_FILE) or not use_cache:
            print("Data file not found. Fetching from API...")
            data = web.DataReader(self.all_securities, "fred", start_date, end_date)
            if dump:
                data.to_csv(DATA_FILE)
            self.data = data
            return data

        # Load existing file
        data = pd.read_csv(DATA_FILE, index_col=0, parse_dates=True)
        last_date = data.index.max()

        # Check if the last date is less than 1 business day before today
        if last_date.date() >= (today - BDay(2)).date():
            print("Data file is up to date.")
            self.data = data
            return data

        # Fetch missing dates and append
        missing_start = last_date + datetime.timedelta(days=1)
        print(f"Fetching missing data from {missing_start.date()} to {end_date.date()}...")
        new_data = web.DataReader(self.all_securities, "fred", missing_start, end_date)

        # Append and save
        data = pd.concat([data, new_data])
        data = data[~data.index.duplicated(keep='last')]
        if dump:
            data.to_csv(DATA_FILE)
        self.data = data
        return data
    
    def set_data(self, data, asof_date: None):
        df = data.copy()
        if asof_date is not None:
            df = df.loc[:asof_date]
        self.data = df


    def get_latest_yield_quotes(self):
        """
        Returns the latest available yield curve as {maturity_in_months: yield_value}.
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data first.")

        latest_data = self.data.tail(1).to_dict("records")[0]
        return {self.reversed_map[sec]: value for sec, value in latest_data.items()}
    
    def get_curve_data_for_fitting(self):
        """
        Returns the latest available yield curve as {maturity_in_months: yield_value}.
        """
        latest_curve = self.get_latest_yield_quotes()
        # df = pd.DataFrame(columns = [, "discount_factors", "continuous_zero_rates"])
        df = pd.DataFrame(list(latest_curve.items()), columns=["tau", "yield_from_source"])
        df["tau"] = df["tau"]/12 # Annualise
        y_bey = df["yield_from_source"].to_numpy()/100
        taus = df["tau"].to_numpy()
        P = 1.0 / (1.0 + y_bey * taus)
        df["discount_factors"] = P
        df["continuous_zero_rates"] = -np.log(P) / taus
        return df



    def plot_historical_yields(self):

        fig = go.Figure()
        maturity_map= self.DGS_MATURITY_MAP_MONTHS
        if self.data is None:
            data = self.load_data()
        df = self.data

        # Iterate maturities in ascending order of months
        for months, col in sorted(maturity_map.items()):
            if col not in df.columns:
                continue  # Skip if column not in data
            label = f"{months} Months" if months < 12 else f"{months // 12} Years"
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=label,
                line=dict(width=2)
            ))

        fig.update_layout(
            title="Historical U.S. Treasury Yields",
            xaxis_title="Date",
            yaxis_title="Yield (%)",
            hovermode="x unified",
            template="plotly_white",
            legend=dict(
                title="Maturity",
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=40, r=40, t=60, b=40)
        )

        return fig



# Example usage:
if __name__ == "__main__":
    start = datetime.datetime(2025, 1, 1)
    end = datetime.datetime(2025, 8, 1)

    curve_loader = USYieldCurveLoader()
    data = curve_loader.load_data()
    # df = curve_loader.get_curve_data_for_fitting()
    # latest_curve = curve_loader.get_latest_yield_quotes()
    # df_fit = curve_loader.get_curve_data_for_fitting()
    print(data)
