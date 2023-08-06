from os import sep


class WrapperComponents:
    @staticmethod
    def textWrap(text: str, color: str = "white", bold=False) -> str:
        return f"[{color}][b]{text}[/b][/]" if bold else f"[{color}]{text}[/]"

    @staticmethod
    def textWrapBold(text: str, color: str = "white") -> str:
        return WrapperComponents.textWrap(text, color, bold=True)

    @staticmethod
    def textWrapUnderline(text: str, color: str = "white", bold=False) -> str:
        return f"[{color}][u]{text}[/u][/]" if bold else f"[{color}][u]{text}[/u][/]"

    @staticmethod
    def textWrapBoldUnderline(text: str, color: str = "white") -> str:
        return WrapperComponents.textWrapUnderline(text, color, bold=True)

    @staticmethod
    def link(text: str, link: str) -> str:
        return f"[link={link}]{text}[/link]"

    @staticmethod
    def format_file_path_link(file_path: str, color: str = "white") -> str:
        return WrapperComponents.textWrap(
            f"[link=file:{sep}{sep}{file_path}]{file_path}[/link]", color
        )


if __name__ == "__main__":
    from rich import print as rprint

    rprint(WrapperComponents.textWrap("Hello World!"))
    rprint(WrapperComponents.textWrapBold("Hello World!"))
    rprint(WrapperComponents.textWrapUnderline("Hello World!"))
    rprint(WrapperComponents.textWrapBoldUnderline("Hello World!"))
    rprint(WrapperComponents.link("luxluth - GitHub", "github.com/luxluth"))
