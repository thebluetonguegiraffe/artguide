class Prompts:
    """Collection of prompts used for ArtGuide agent."""

    SYSTEM_GUIDELINES = (
        "You are ArtGuide, an expert art historian and museum curator. "
        "Your task is to assist users in exploring and understanding famous artworks. "
        "Provide accurate information about paintings, artists, and historical context. "
        "Engage users with insightful commentary and answer their questions to the best of your ability. "  # noqa
        "If you are unsure about any information, respond with 'I don't know' rather than guessing."
    )

    ART_IDENTIFICATION_JUDGE_PROMPT = (
        "Your task is to analyze an image of a painting and identify the artwork.\n\n"
        "You are given a set of candidate identifications for this same image, "
        "produced independently by different sources. None of them has been verified, "
        "and none should be assumed correct by default -- their order carries no meaning "
        "and does not reflect confidence or reliability.\n\n"
        "Candidates:\n"
        "{options_block}\n\n"
        "Follow these rules strictly:\n"
        "   1. Look at the image yourself before deciding; treat the candidates as leads to check, not answers to confirm.\n"  # noqa
        "   2. If two or more candidates agree, or the image clearly supports one of them, use that identification.\n"  # noqa
        "   3. If the candidates disagree and the image does not clearly support any of them, decide independently from the image itself.\n"  # noqa
        "   4. Use the specified language ({language}).\n"
        "   5. If any information is uncertain, use null instead of guessing.\n"
        "   6. Return **only** a valid JSON object -- no explanations, no text outside the JSON.\n"  # noqa
        "   7. Limit the description to a maximum of {n_words} words.\n\n"
        "Once the painting is identified you must:\n"
        "In the specified language ({language}):\n"
        "   1. Write a concise and engaging description of the artwork.\n"
        "   2. Include relevant details about its historical context, artistic style, and significance.\n"  # noqa
        "   3. Limit the description to a maximum of {n_words} words.\n"
        "   4. Do not use asterisks, underscores, or any formatting symbols; the description must consist only of plain text.\n"  # noqa
        "   5. Include commas and full breaks to ensure the description is easily interpreted by a text-to-speech model.\n"  # noqa
        "   6. Specify the museum where the painting is exposed.\n"
        "   7. Specify the year the painting was created.\n"
        "   8. Specify the artist.\n"
        "\n\nRespond with a single JSON object with exactly these keys: "
        '"title", "artist", "year", "museum", "description". '
        'Use null for any value you cannot determine, including "title" when the image '
        "is not a painting."
    )

    ART_IDENTIFICATION_PROMPT = (
        "Your task is to analyze an image of a painting and identify the artwork.\n"
        "\nFollow these rules strictly:\n"
        "   1. Use the specified language ({language}):"
        "   2. Identify the artwork only if you are reasonably confident.\n"
        "   3. If any information is uncertain, use null instead of guessing.\n"
        "   4. Return **only** a valid JSON object — no explanations, no text outside the JSON.\n\n"  # noqa
        "   5. Limit the description to a maximum of {n_words} words"
        "Once the painting is recognized you must: "
        "In the specified language ({language}):\n"
        "   1. Write a concise and engaging description of the artwork'.\n"
        "   2. Include relevant details about its historical context, artistic style, and significance.\n"  # noqa
        "   3. Limit the description to a maximum of {n_words} words.\n"
        "   4. Do not use asterisks, underscores, or any formatting symbols; the description must consist only of plain text.\n"  # noqa
        "   5. Include commas and full breaks to ensure the description is easily interpreted by a text-to-speech model.\n"  # noqa
        "   6. Specify the museum where the painting is exposed "
        "   7. Specify the year the painting was created."
        "   8. Specify the artist"
        "\n\nRespond with a single JSON object with exactly these keys: "
        '"title", "artist", "year", "museum", "description". '
        'Use null for any value you cannot determine, including "title" when the image '
        "is not a painting."
    )

    DESCRIPTION_GENERATION = (
        "In the specified language ({language}):\n"
        "   1. Write a concise and engaging description of the artwork titled '{title}'.\n"
        "   2. Include relevant details about its historical context, artistic style, and significance.\n"  # noqa
        "   3. Limit the description to a maximum of {n_words} words.\n"
        "   4. Do not use asterisks, underscores, or any formatting symbols; the description must consist only of plain text.\n"  # noqa
        "   5. Include commas and full breaks to ensure the description is easily interpreted by a text-to-speech model.\n"  # noqa
        "   6. Specify the museum where the painting is exposed "
        "   7. Specify the year the painting was created."
    )
