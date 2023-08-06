

import markdown2 as md


md2_extras = [
    'break-on-newline',
    'code-friendly',
    'cuddled-lists',
    'fenced-code-blocks',
    'footnotes',
    'header-ids',
    'smarty-pants',
    'strike',
    'tables',
    'tg-spoiler',
    'tag-friendly',
    'task_list',
]


def marquedown(document: str, /, **kwargs) -> str:
    """
    Convert both Marquedown and Markdown into HTML.
    """

    if kwargs.get('citation', True):
        from .citation import citation
        document = citation(document)

    if kwargs.get('labellist', True):
        from .labellist import labellist
        document = labellist(document)

    if kwargs.get('qrgen') is not None:
        # Parse QR codes with provided QRGenerator
        from .qr import qr
        document = qr(document, kwargs.get('qrgen'))

    if kwargs.get('video', True):
        from .video import video
        document = video(document)
        
    html = md.markdown(document, extras=md2_extras)

    if kwargs.get('bblike', True):
        from .bblike import bblike
        html = bblike(html)

    return html