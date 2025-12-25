from .rag_index import search
from .llm_answer import llm_answer
from .question_parser import parse_question


def rag_pipeline(question: str) -> str:
    question = parse_question(question)

    if not question:
        return "الرجاء طرح سؤال واضح."

    # On limite légèrement le contexte pour laisser finir Gemini
    chunks = search(question, top_k=50)

    if not chunks:
        return "لا تتوفر معطيات كافية للإجابة عن هذا السؤال."

    context = "\n\n".join(chunks)

    return llm_answer(question, context)


# ==================================================
# MODE DISCUSSION (CHAT CONTINU)
# ==================================================
if __name__ == "__main__":
    print("🟢 مرحبًا بك في مساعد التوجيه الجامعي")
    print("📝 يمكنك طرح عدة أسئلة متتالية")
    print("⛔ اكتب exit للخروج\n")

    while True:
        question = input("❓ اطرح سؤالك: ").strip()

        if not question:
            print("⚠️ الرجاء إدخال سؤال.\n")
            continue

        if question.lower() in ["exit", "quit", "خروج"]:
            print("\n👋 بالتوفيق في مسارك الجامعي")
            break

        answer = rag_pipeline(question)

        print("\n🟢 الإجابة:\n")
        print(answer)
        print("\n" + "-" * 60 + "\n")
