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
        "You are given two independent identification opinions for this same image, "
        "produced blindly by different models -- neither saw the other's answer, and "
        "neither should be assumed correct by default. Their order carries no meaning.\n\n"
        "Blind opinions:\n"
        "{options_block}\n\n"
        "{clip_evidence_block}"
        "Follow these rules strictly:\n"
        "   1. Look at the image yourself before deciding; treat everything above as leads to check, not answers to confirm.\n"  # noqa
        "   2. Agreement between the two blind opinions is not strong evidence on its own -- both come from models of the same family, which can share the same systematic mistakes (e.g. confusing two different works by the same artist). Do not treat their agreement as a majority vote.\n"  # noqa
        "   3. A well-scored visual similarity match is a different, independent kind of evidence. If it is clearly supported by the image, prefer it even when both blind opinions disagree with it.\n"  # noqa
        "   4. You must select your final answer from the titles listed above (blind opinions and/or evidence candidates). Do not propose a title that appears in none of them, even if you recognize the artist's style and can think of other well-known works by that artist -- recognizing the artist is not the same as identifying the specific piece, and guessing a plausible-sounding title you were not given is worse than saying you don't know.\n"  # noqa
        "   5. Only if the image clearly does not match any listed title or artist at all -- a genuinely different subject, medium, or period -- may you identify it independently from the image itself.\n"  # noqa
        "   6. Use the specified language ({language}).\n"
        "   7. If you cannot confidently select among the listed titles and rule 5 does not apply either, use null instead of guessing.\n"  # noqa
        "   8. Return **only** a valid JSON object -- no explanations, no text outside the JSON.\n\n"  # noqa
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
