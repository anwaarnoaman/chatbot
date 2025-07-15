import streamlit as st
import requests
import json
import re

API_URL = "http://localhost:8000"

DEFAULT_SYSTEM_PROMPT = '''
You are an intelligent assistant capable of answering a wide range of questions using your internal knowledge.

You also have access to a tool called `internet_search_tool` that allows you to perform real-time web searches to get up-to-date information.

---

## 🎯 Decision Strategy:

You must decide whether to answer directly or to trigger the `internet_search_tool`.

### ✅ Use your own knowledge if:
- The question is general, timeless, or clearly answerable from your internal knowledge.
- The topic is about facts, science, definitions, instructions, or logic that hasn’t changed recently.

### 🔎 Use `internet_search_tool` if:
- The user asks for **recent**, **breaking**, or **currently happening** events.
- The topic involves **live data** (e.g., stock prices, weather, news, sports).
- You are unsure or not confident in your answer.

---

## 🧠 Tool Usage

If you call a tool, explain why using a `reasoning` field.

Include a **Sources** section as a JSON-style list (e.g., `["url1", "url2"]`) at the end.

---

## 🧾 Output Format

- Answer in Markdown.
- If using a tool:
  - Explain why.
  - Provide summary.
  - List **Sources** in JSON format (no bullets).

---

Your goal is to be clear, helpful, and correct.
'''

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

# --- API Call ---
def send_message_to_api(messages, hybrid_search=True, stream=False):
    payload = {
        "messages": [{"role": "system", "content": st.session_state.system_prompt}] + messages,
        "hybrid_search": hybrid_search
    }
    headers = {"Content-Type": "application/json"}

    if stream:
        with requests.post(f"{API_URL}/chat/stream", json=payload, headers=headers, stream=True) as response:
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
        response = requests.post(f"{API_URL}/chat", json=payload, headers=headers)
        response.raise_for_status()
        yield response.json()["response"]

# --- Response Parser ---
def parse_response(text):
    # Extract 'Sources' block
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
        if st.button("Show/Hide System Prompt"):
            st.session_state.show_system_prompt = not st.session_state.show_system_prompt

        if st.session_state.show_system_prompt:
            st.subheader("System Prompt (Editable)")
            new_prompt = st.text_area("System Prompt", value=st.session_state.system_prompt, height=400)
            if new_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_prompt
                st.success("System prompt updated!")

        st.session_state.hybrid_search = st.checkbox("Enable Hybrid Search", value=st.session_state.hybrid_search)

    # Show chat history
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

        for chunk in send_message_to_api(st.session_state.messages, stream=True, hybrid_search=st.session_state.hybrid_search):
            assistant_message += chunk
            placeholder.empty()
            with placeholder.chat_message("assistant"):
                display_assistant_response(assistant_message)

        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        st.session_state.input_disabled = False

if __name__ == "__main__":
    main()
