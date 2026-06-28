import streamlit as st
import wikipedia
import requests
from groq import Groq

st.set_page_config(page_title="J.A.R.V.I.S. Web", page_icon="🤖")

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are J.A.R.V.I.S., a helpful AI assistant.
You must always answer clearly and concisely.
If the user asks for weather, respond normally in text; do not call any tools from inside the model.
If the user asks for Wikipedia-style knowledge, respond in your own words.
Language style: calm, friendly, slightly formal, mix of English and simple Hindi if user does that.
"""

def groq_chat(messages):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.4,
    )
    return completion.choices[0].message.content

def get_weather(city):
    url = "https://wttr.in/{}?format=j1".format(city)
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        feels = current["FeelsLikeC"]
        desc = current["weatherDesc"][0]["value"]
        return f"Current weather in {city}: {temp_c}°C, feels like {feels}°C, {desc}."
    except Exception:
        return "Sorry, weather service is not responding right now."

def get_wiki_summary(query):
    title = query.strip().replace(" ", "_")
    if not title:
        return "Please type a topic first."
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "umar-jarvis-app/1.0"},
            timeout=8,
        )
        if r.status_code != 200:
            return "Wikipedia did not find an article with that exact title."
        data = r.json()
        extract = data.get("extract")
        if not extract:
            return "Wikipedia article does not have a short summary."
        return extract
    except Exception:
        return "Wikipedia is not reachable right now."

st.title("🤖 J.A.R.V.I.S. – Web Edition")

with st.sidebar:
    st.header("Control Panel")
    st.write("This is the cloud-safe web version of J.A.R.V.I.S.")
    st.write("No local PC control. Only chat, weather and Wikipedia-style knowledge.")
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write("Quick tools:")
    city_input = st.text_input("Weather city name")
    if st.button("Check Weather"):
        if city_input.strip():
            reply = get_weather(city_input.strip())
            st.write(reply)
    wiki_input = st.text_input("Wikipedia topic")
    if st.button("Wiki Summary"):
        if wiki_input.strip():
            reply = get_wiki_summary(wiki_input.strip())
            st.write(reply)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {"role": "system", "content": SYSTEM_PROMPT.strip()}
    )
    st.session_state.messages.append(
        {"role": "assistant", "content": "Namaste. I am the cloud version of J.A.R.V.I.S. Ask me anything."}
    )

for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
        st.markdown(m["content"])

user_input = st.chat_input("Type your message here")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
        if m["role"] in ("system", "user", "assistant")
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = groq_chat(history)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})