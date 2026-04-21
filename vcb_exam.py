import random
import pandas as pd
import streamlit as st


# 1. Load data and shuffle questions
@st.cache_data
def load_questions(file_path):
    # Ensure the file exists or handle error
    try:
        df = pd.read_excel(file_path)
        df = df.rename(
            columns={
                "Nội dung câu hỏi": "question",
                "A": "a",
                "B": "b",
                "C": "c",
                "D": "d",
                "Answer": "answer",  # Match your header: 'Đáp án'
            }
        )
        # Standardize columns and clean answer strings
        df = df[["question", "a", "b", "c", "d", "answer"]]
        df["answer"] = df["answer"].str.lower().str.strip()
        return df.sample(frac=1).reset_index(drop=True)
    except Exception as e:
        st.error(f"Lỗi khi tải file: {e}")
        return pd.DataFrame()


# 2. Initialize quiz data
def initialize_quiz():
    df = load_questions("questions_2.xlsx")
    if df.empty:
        st.stop()

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

    st.session_state.quiz = quiz_data
    st.session_state.submitted = False
    st.session_state.confirm_submit = False


# 3. Helper to find unanswered questions
def find_unanswered(quiz_data):
    unanswered = []
    for i in range(len(quiz_data)):
        if st.session_state.get(f"answer_{i}") is None:
            unanswered.append(i + 1)
    return unanswered


# 4. Main App
def main():
    st.set_page_config(page_title="Bài kiểm tra", layout="wide")
    st.title("🧠 Bài kiểm tra trắc nghiệm")

    # Initialize session state
    if "quiz" not in st.session_state:
        initialize_quiz()

    quiz_data = st.session_state.quiz
    total = len(quiz_data)

    # --- DISPLAY QUESTIONS ---
    # We wrap this in a container to hide it if results are shown (optional)
    if not st.session_state.get("submitted", False):
        for i, qdata in enumerate(quiz_data):
            st.write(f"**Câu {i + 1}:** {qdata['question']}")
            st.radio(
                "Chọn đáp án:",
                options=qdata["shuffled_options"],
                format_func=lambda x: (
                    f"{x.upper()}. {qdata['options_text'][x]}"
                ),
                key=f"answer_{i}",
                index=None,
            )
            st.markdown("---")

        # --- SUBMIT LOGIC ---
        if not st.session_state.get("confirm_submit", False):
            if st.button("📊 Nộp bài và xem kết quả"):
                unanswered = find_unanswered(quiz_data)
                if unanswered:
                    st.session_state.confirm_submit = True
                    st.rerun()
                else:
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # Confirmation Dialog
            unanswered = find_unanswered(quiz_data)
            st.warning(
                f"⚠️ Bạn còn {len(unanswered)} câu chưa trả lời: {', '.join(map(str, unanswered))}"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🚀 Vẫn nộp bài"):
                    st.session_state.submitted = True
                    st.session_state.confirm_submit = False
                    st.rerun()
            with col2:
                if st.button("⬅️ Quay lại làm"):
                    st.session_state.confirm_submit = False
                    st.rerun()

    # --- RESULTS PAGE ---
    if st.session_state.get("submitted", False):
        correct_count = 0
        incorrect_details = []

        for i, q in enumerate(quiz_data):
            user_choice = st.session_state.get(f"answer_{i}")

            if user_choice == q["correct"]:
                correct_count += 1
            else:
                incorrect_details.append(
                    {
                        "index": i + 1,
                        "question": q["question"],
                        "user_choice": user_choice,
                        "correct": q["correct"],
                        "options": q["shuffled_options"],
                        "text": q["options_text"],
                    }
                )

        # Score display
        st.success(f"🎉 Bạn đã trả lời đúng {correct_count}/{total} câu hỏi!")
        st.progress(correct_count / total)

        if incorrect_details:
            st.markdown("## ❌ Chi tiết các câu chưa đúng")
            for detail in incorrect_details:
                with st.expander(
                    f"📌 Câu {detail['index']}: {detail['question'][:60]}..."
                ):
                    st.markdown(f"**Câu hỏi:** {detail['question']}")

                    for opt in detail["options"]:
                        is_correct = opt == detail["correct"]
                        is_user = opt == detail["user_choice"]

                        label = f"{opt.upper()}. {detail['text'][opt]}"
                        if is_correct:
                            label += " ✅ (Đáp án đúng)"
                        if is_user:
                            label += " ❌ (Bạn chọn)"

                        if is_correct:
                            st.write(f":green[{label}]")
                        elif is_user:
                            st.write(f":red[{label}]")
                        else:
                            st.write(label)
        else:
            st.balloons()
            st.info("🥳 Tuyệt vời! Bạn đã làm đúng tất cả các câu!")

        if st.button("🔁 Làm lại bài mới"):
            # Clear all session state except specific internal streamlit keys if necessary
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
