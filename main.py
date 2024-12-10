import streamlit as st
import requests
import os
from langchain_ollama import OllamaLLM
from langchain_community.chat_models import ChatOpenAI


# タイトルと説明
st.title("天気感覚ポエム")
st.write("このアプリは、東京都の天気を検索し、天気に基づいてポエムを生成します。")

# 天気データを取得する関数
def get_weather_data():
    API_URL = "https://weather.tsukumijima.net/api/forecast/city/130010"  # 東京都の都市コード
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # ステータスコードがエラーの場合例外を発生
        data = response.json()
        return data
    except Exception as e:
        st.error(f"天気データを取得するのに失敗しました：{e}")
        return None

# ローカル環境でOllamaを利用する関数
def generate_poem_with_ollama(weather_description):
    try:
        llm = OllamaLLM(
            model="llama3.2",  # 使用するモデル名
            base_url="http://localhost:11434"  # OllamaサーバーのURL
        )
        prompt = f"天気は「{weather_description}」です。日本語でこの天気からインスピレーションを得た短いポエムを書いてください。"
        response = llm.invoke(prompt)  # invokeを使用
        return response
    except Exception as e:
        return f"ポエムを生成するのに失敗しました：{e}"

# デプロイ環境でOpenAIを利用する関数
def generate_poem_with_openai(weather_description):
    try:
        # LangChainのOpenAI Chatインターフェースを利用
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7
        )
        prompt = f"天気は「{weather_description}」です。日本語でこの天気からインスピレーションを得た短いポエムを書いてください。"
        response = llm.invoke(prompt)  # invokeを使用


        # レスポンスのcontentフィールドを取得
        if hasattr(response, "content"):
            return response.content
        else:
            return "No content available in the response."
    except Exception as e:
        return f"ポエムを生成するのに失敗しました：{e}"

# 天気データを取得
weather_data = get_weather_data()

if weather_data:
    # 天気予報データを整形
    forecasts = weather_data.get("forecasts", [])
    forecast_options = {f["dateLabel"]: f for f in forecasts}

    # 日付を選択
    select_day = st.selectbox("日付を選択", forecast_options.keys())

    # 選択された日の天気データを取得
    selected_weather = forecast_options[select_day]
    weather_description = selected_weather["telop"]

    # 天気予報を表示
    st.write(f"### {select_day}の天気予報：")
    st.write(f"- 日付：{selected_weather['date']}")
    st.write(f"- 気象：{weather_description}")
    st.image(selected_weather["image"]["url"], caption=selected_weather["image"]["title"])

    # 動作環境に応じてポエム生成
    st.write("### 天気感覚のポエム：")
    if os.getenv("ENVIRONMENT") == "PRODUCTION":
        # デプロイ環境でOpenAIを利用
        poem = generate_poem_with_openai(weather_description)
    else:
        # ローカル環境でOllamaを利用
        poem = generate_poem_with_ollama(weather_description)
        # poem = generate_poem_with_openai(weather_description)

    st.write(poem)

else:
    st.write("天気データを取得するのに失敗しました。もう一度試してください.")
