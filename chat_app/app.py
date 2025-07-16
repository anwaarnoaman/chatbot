import streamlit as st
import requests
import json
import re

# --- Default Settings ---
DEFAULT_API_URL = "http://localhost:8063"
DEFAULT_SYSTEM_PROMPT = """
You are an intelligent assistant capable of answering a wide range of questions using your internal knowledge.

You also have access to a tool called `internet_search_tool` that allows you to perform real-time web searches to get up-to-date information.

<instructions>
<instruction>You must decide whether to answer directly or to trigger the `internet_search_tool`.</instruction>
<instruction>Use your own knowledge if the question is general, timeless, or clearly answerable from your internal knowledge.</instruction>
<instruction>Use your own knowledge if the topic is about facts, science, definitions, instructions, or logic that hasn’t changed recently.</instruction>
<instruction>Use the `internet_search_tool` if the user asks for recent, breaking, or currently happening events.</instruction>
<instruction>Use the `internet_search_tool` if the topic involves live data such as stock prices, weather, news, or sports.</instruction>
<instruction>Use the `internet_search_tool` if you are unsure or not confident in your answer.</instruction>
<instruction>If you call a tool, explain why using a `reasoning` field.</instruction>
<instruction>Include a Sources section as a JSON-style list (e.g., ["url1", "url2"]) at the end of your response.</instruction>
<instruction>Your answer must be formatted in Markdown.</instruction>
<instruction>If using a tool, explain why, provide a summary, and list Sources in JSON format without bullets.</instruction>
<instruction>Your goal is to be clear, helpful, and correct.</instruction>
</instructions>
""".strip()

# --- State Initialization ---
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_disabled" not in st.session_state:
    st.session_state.input_disabled = False
if "show_system_prompt" not in st.session_state:
    st.session_state.show_system_prompt = False
if "hybrid_search" not in st.session_state:
    st.session_state.hybrid_search = True
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

# --- API Call ---
def send_message_to_api(messages, hybrid_search=True, stream=False):
    payload = {
        "messages": [{"role": "system", "content": st.session_state.system_prompt}] + messages,
        "hybrid_search": hybrid_search
    }
    headers = {"Content-Type": "application/json"}

    if stream:
        with requests.post(f"{st.session_state.api_url}/chat/stream", json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            buffer = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    buffer += chunk.decode("utf-8")
                    while "\n\n" in buffer:
                        event, buffer = buffer.split("\n\n", 1)
                        lines = event.splitlines()
                        data_lines = [line[6:] for line in lines if line.startswith("data: ")]
                        data = "".join(data_lines)
                        if data.strip():
                            yield data
    else:
        response = requests.post(f"{st.session_state.api_url}/chat", json=payload, headers=headers)
        response.raise_for_status()
        yield response.json()["response"]

# --- Response Parser ---
def parse_response(text):
    sources = []
    pattern = r"(?mi)^Sources\s*\n(\[.*?\])\s*$"
    match = re.search(pattern, text)
    if match:
        try:
            sources = json.loads(match.group(1))
        except Exception:
            sources = []
        text = text[:match.start()].strip()
    return text, sources

# --- Display Response ---
def display_assistant_response(raw_text):
    main_text, sources = parse_response(raw_text)
    st.markdown(main_text, unsafe_allow_html=True)
    if sources:
        with st.expander("Sources"):
            for src in sources:
                st.markdown(f"- [{src}]({src})" if src.startswith("http") else f"- {src}")

# --- Main App ---
def main():
    st.title("Chatbot")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        st.session_state.api_url = st.text_input("API URL", value=st.session_state.api_url)
        st.session_state.hybrid_search = st.checkbox("Enable Internet Search", value=st.session_state.hybrid_search)

        if st.button("Show/Hide System Prompt"):
            st.session_state.show_system_prompt = not st.session_state.show_system_prompt

        if st.session_state.show_system_prompt:
            st.subheader("System Prompt (Editable)")
            new_prompt = st.text_area("System Prompt", value=st.session_state.system_prompt, height=400)
            if new_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_prompt
                st.success("System prompt updated!")

    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input prompt
    prompt = st.chat_input("You:", disabled=st.session_state.input_disabled)
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.input_disabled = True
        assistant_message = ""
        placeholder = st.empty()

        with st.spinner("Assistant is typing..."):
            for chunk in send_message_to_api(st.session_state.messages, stream=True, hybrid_search=st.session_state.hybrid_search):
                assistant_message += chunk
                placeholder.empty()
                with placeholder.chat_message("assistant"):
                    display_assistant_response(assistant_message)

        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        st.session_state.input_disabled = False

if __name__ == "__main__":
    main()
