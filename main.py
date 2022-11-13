import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import yfinance as yf
import streamlit as st
st.title("株価可視化アプリ")
st.sidebar.write("""
# GAFA株価
こちらは米国株価可視化ツールです。以下のオプションから表示週数を指定
""")
st.sidebar.write("""
## 表示週数を選択
""")
weeks=st.sidebar.slider("週数",1,52*2,1)
st.write(f"""
## 過去　**{weeks}週間** のGAFA株価
""")

st.cache()
tickers={
    "apple":"AAPL",
    "facebook":"Meta",
    "google":"GOOGL",
    "microsoft":"MSFT",
    "netflix":"NFLX",
    "amazon":"AMZN"
}
def get_data(weeks,tickers):
    df=pd.DataFrame()
    for company in tickers.keys():
        tkr=yf.Ticker(tickers[company])
        hist=tkr.history(period=f"{weeks*7}d")
        hist.index=hist.index.strftime("%d %B %Y")
        hist=hist[["Close"]]
        hist.columns=[company]
        hist=hist.T
        hist.index.name="Name"
        df=pd.concat([df,hist])
    return df
df=get_data(weeks,tickers)
companies=st.multiselect(
    "会社名を選択してください",
    list(df.index),
    ["google","amazon","facebook"]
)
if not companies:
    st.error("少なくとも一社は選んでください")
else:
    data=df.loc[companies]
    st.sidebar.write("""
    ## 株価の範囲指定""")
    ymin,ymax=st.sidebar.slider(
    "範囲を指定してください",
    0,1000,(int(data.min(axis=1).min()),int(data.max(axis=1).max())))
    st.write("### 株価(USD)",data.sort_index())
    data=data.T.reset_index()
    data=pd.melt(data,id_vars=["Date"]).rename(columns={"value":"Stock Prices(USD)"})
    chart=(
    alt.Chart(data)
        .mark_line(opacity=0.8,clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices(USD):Q",stack=None,scale=alt.Scale(domain=[ymin,ymax])),
            color="Name:N"
        )
    )
    st.altair_chart(chart,use_container_width=True)
