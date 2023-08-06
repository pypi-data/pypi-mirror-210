import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import os


def create_treemap_data(df):
    basic_info_df = None
    if os.path.exists("company_basic_info.csv"):
        basic_info_df = pd.read_csv("company_basic_info.csv")
        basic_info_df["stock_id"] = basic_info_df["stock_id"].astype(str)
    else:
        url = "https://raw.githubusercontent.com/twfxjjbw/stockinfo/main/company_basic_info.csv"
        basic_info_df = pd.read_csv(url)
        basic_info_df["stock_id"] = basic_info_df["stock_id"].astype(str)
        basic_info_df.to_csv("company_basic_info.csv", index=False)
    basic_info_df["stock_id_name"] = basic_info_df["stock_id"] + basic_info_df["公司簡稱"]
    df = df.merge(
        basic_info_df[["stock_id", "stock_id_name", "產業類別", "市場別", "實收資本額(元)"]],
        how="left",
        on="stock_id",
    )
    df = df.rename(columns={"產業類別": "category", "市場別": "market", "實收資本額(元)": "base"})
    df = df.dropna(thresh=5)
    df["market_value"] = round(df["base"] / 10 * df["close"] / 100000000, 2)
    df["turnover_ratio"] = df["turnover"] / (df["turnover"].sum()) * 100
    df["country"] = "TW-Stock"
    return df


def plot_tw_stock_treemap(
    df, area_ind="turnover_ratio", item="return_ratio", color_scales="Temps"
):
    df = create_treemap_data(df)
    if df is None:
        return None
    df["custom_item_label"] = round(df[item], 2).astype(str)

    if area_ind not in ["market_value", "turnover", "turnover_ratio"]:
        return None

    if item in ["return_ratio"]:
        color_continuous_midpoint = 0
    else:
        color_continuous_midpoint = np.average(df[item], weights=df[area_ind])

    fig = px.treemap(
        df,
        path=["country", "market", "category", "stock_id_name"],
        values=area_ind,
        color=item,
        color_continuous_scale=color_scales,
        color_continuous_midpoint=color_continuous_midpoint,
        custom_data=["custom_item_label", "close", "turnover"],
        title=f"TW-Stock Market TreeMap"
        f"---area_ind:{area_ind}---item:{item} <span style='color:blue'>last_updated:{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</span><BR>",
        width=1600,
        height=800,
    )

    fig.update_traces(
        textposition="middle center",
        textfont_size=24,
        texttemplate="%{label}(%{customdata[1]})<br>%{customdata[0]}",
    )
    return fig
