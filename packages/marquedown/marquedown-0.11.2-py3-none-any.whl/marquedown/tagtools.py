

def tagstrip(text: str, tag: str) -> str:
    """
    Strips HTML tag from sides of text.
    """
    
    if contained(text, tag):
        left, right = tags(tag)
        return text.strip()[len(left):-len(right)].strip(" ").strip('\n')

    return text


def contained(text: str, tag: str) -> str:
    """
    Returns whether text is contained within a certain HTML tag.
    """
    left, right = tags(tag)
    stripped_text = text.strip()
    return stripped_text.startswith(left) and stripped_text.endswith(right)


def tags(tag: str) -> str:
    """
    Get left-hand and right-hand sides of a tag.
    """
    return f'<{tag}>', f'</{tag}>'