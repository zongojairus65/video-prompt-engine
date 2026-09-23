import random

# Checked case-insensitively against the first sentence/line of the
# prompt only — not the whole text, per the intended behavior: the
# prompt should visibly open as an image-to-video request from its
# very first words, the way these are conventionally written for
# Veo/Kling/Runway image-to-video mode.
ANIMATION_KEYWORDS = (
    "anime",
    "transforme",
    "utilise",
    "pars de cette image",
    "conserve fidèlement l'image",
    "donne vie à",
)

ANIMATION_TEMPLATES = (
    "Anime l'image source tout en conservant exactement l'identité, "
    "le visage, les vêtements et l'environnement du personnage.",

    "Transforme cette image en vidéo sans modifier l'apparence du "
    "personnage.",

    "Conserve fidèlement l'image source et ajoute uniquement des "
    "mouvements naturels.",

    "Utilise cette image comme première frame et anime "
    "progressivement la scène.",

    "Pars de cette image et crée une séquence vidéo réaliste.",
)


def _first_segment(prompt: str) -> str:
    """Isolates the first line, or failing that the first sentence,
    of the prompt — the part the user's opening keyword is expected
    to appear in."""

    first_line = prompt.strip().split("\n", 1)[0]

    for punctuation in (".", "!", "?"):
        index = first_line.find(punctuation)
        if index != -1:
            first_line = first_line[: index + 1]
            break

    return first_line.lower()


def ensure_animation_framing(prompt: str) -> tuple[str, bool]:
    """Image-to-video mode only. If the prompt doesn't already open
    with recognizable animation/preservation framing, prepends one
    of ANIMATION_TEMPLATES so the parser treats it as an
    image-to-video request from the first sentence onward.

    Returns (possibly-modified prompt, whether a template was added).
    The original prompt is never mutated in place — the caller
    decides what to do with the returned value (e.g. keep using the
    untouched original for fidelity evaluation and history, while
    feeding the modified one to the Scene parser)."""

    segment = _first_segment(prompt)

    if any(keyword in segment for keyword in ANIMATION_KEYWORDS):
        return prompt, False

    template = random.choice(ANIMATION_TEMPLATES)

    return f"{template}\n{prompt}", True
