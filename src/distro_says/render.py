from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_ascii(ascii_art: str | None) -> None:
    if ascii_art:
        console.print(ascii_art)


def print_summary(name: str, tagline: str, line: str, json_mode: bool = False) -> None:
    if json_mode:
        console.print_json(data={"name": name, "tagline": tagline, "message": line})
        return

    body = Text.assemble(
        ("Tagline: ", "bold"), tagline, "\n",
        ("Message: ", "bold"), line
    )
    console.print(Panel(body, title=name, expand=False))
