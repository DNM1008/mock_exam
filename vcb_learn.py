import random
import pandas as pd
import streamlit as st


# 1. Load data
@st.cache_data
def load_questions(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.rename(
            columns={
                "Nội dung câu hỏi": "question",
                "A": "a",
                "B": "b",
                "C": "c",
                "D": "d",
                "Answer": "answer",
            }
        )
        df["answer"] = df["answer"].str.lower().str.strip()
        return df.sample(frac=1).reset_index(drop=True)
    except Exception as e:
        st.error(f"Không thể tải file: {e}")
        return pd.DataFrame()


# 2. Initialize Session State
def init_state():
    if "quiz_data" not in st.session_state:
        df = load_questions("questions_2.xlsx")
        quiz_data = []

        for _, row in df.iterrows():
            options = ["a", "b", "c", "d"]
            shuffled = options.copy()
            random.shuffle(shuffled)

            quiz_data.append(
                {
                    "question": row["question"],
                    "shuffled_options": shuffled,
                    "options_text": {opt: row[opt] for opt in options},
                    "correct": row["answer"],
                }
            )

        st.session_state.quiz_data = quiz_data
        st.session_state.current_index = 0
        st.session_state.quiz_complete = False

        # NEW STATE
        st.session_state.user_answers = {}  # {idx: "a"}
        st.session_state.answered = set()  # {idx}


def main():
    st.set_page_config(page_title="Học Trắc Nghiệm", layout="centered")
    st.title("📖 Học từng câu hỏi")

    init_state()

    data = st.session_state.quiz_data
    idx = st.session_state.current_index
    q = data[idx]

    # Sidebar navigation
    with st.sidebar:
        st.write("📌 Điều hướng")

        jump_idx = st.selectbox(
            "Chọn câu:",
            options=list(range(len(data))),
            format_func=lambda x: f"Câu {x + 1}",
            index=idx,
        )

        if jump_idx != idx:
            st.session_state.current_index = jump_idx
            st.rerun()

        st.write(f"✅ Đã trả lời: {len(st.session_state.answered)}/{len(data)}")

    # Progress
    progress = (len(st.session_state.answered)) / len(data)
    st.progress(progress)
    st.write(f"**Câu hỏi {idx + 1} / {len(data)}**")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Trước"):
            if idx > 0:
                st.session_state.current_index -= 1
                st.rerun()

    with col3:
        if st.button("➡️ Sau"):
            if idx < len(data) - 1:
                st.session_state.current_index += 1
                st.rerun()

    # Question
    st.subheader(q["question"])

    # Current answer (if already answered)
    prev_answer = st.session_state.user_answers.get(idx)

    user_choice = st.radio(
        "Chọn đáp án đúng:",
        options=q["shuffled_options"],
        format_func=lambda x: f"{x.upper()}. {q['options_text'][x]}",
        key=f"q_{idx}",
        index=q["shuffled_options"].index(prev_answer)
        if prev_answer in q["shuffled_options"]
        else None,
    )

    # Save answer
    if st.button("Lưu câu trả lời"):
        if user_choice:
            st.session_state.user_answers[idx] = user_choice
            st.session_state.answered.add(idx)
            st.rerun()
        else:
            st.warning("Vui lòng chọn một đáp án trước!")

    # Show feedback if answered
    if idx in st.session_state.user_answers:
        user_choice = st.session_state.user_answers[idx]
        correct_choice = q["correct"]

        if user_choice == correct_choice:
            st.success(f"✅ Đúng: {correct_choice.upper()}")
        else:
            st.error(f"❌ Sai")

            # FULL COMPARISON (your request)
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Bạn chọn:**")
                st.write(
                    f"{user_choice.upper()}. {q['options_text'][user_choice]}"
                )

            with col2:
                st.write("**Đáp án đúng:**")
                st.write(
                    f"{correct_choice.upper()}. {q['options_text'][correct_choice]}"
                )

        # Always show correct answer explanation
        st.info(
            f"**Đáp án:** {correct_choice.upper()}. {q['options_text'][correct_choice]}"
        )

    # Completion check
    if len(st.session_state.answered) == len(data):
        st.success("🎊 Bạn đã hoàn thành toàn bộ câu hỏi!")


if __name__ == "__main__":
    main()
