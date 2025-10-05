from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """Extracts the text from an HTML document."""

    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def feed(self, data):
        position = data.find("<body")
        if position == -1:
            super().feed(data)
            return
        super().feed(data[position:])

    def get_text(self):
        """Returns the text from the HTML document."""
        return "".join(self.text_parts).replace("\n", " ").strip()


def get_html_text(description: str) -> str:
    """Returns the text from the HTML document."""
    text_value: str
    if description:
        parser = HTMLTextExtractor()
        parser.feed(description)
        text_value = parser.get_text()
        parser.close()
    else:
        text_value = ""
    return text_value
