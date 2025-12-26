def generate_conversation_title(
    question: str,
    max_length: int = 40
) -> str:
    """
    Génère un titre de conversation à partir de la première question.
    - Nettoie les espaces
    - Coupe à une longueur max
    - Ajoute "..." si nécessaire
    """

    if not question:
        return "محادثة جديدة"

    clean_question = question.strip().replace("\n", " ")

    if len(clean_question) <= max_length:
        return clean_question

    return clean_question[:max_length].rstrip() + "..."
