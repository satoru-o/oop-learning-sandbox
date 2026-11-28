from typing import Protocol


class CodeGenerator(Protocol):
    def generate(self) -> str: ...


class UrlRepository(Protocol):
    def save(self, code: str, url: str) -> None: ...

    def find(self, code: str) -> str | None: ...


class ShortenUrl:
    def __init__(self, generator: CodeGenerator, repository: UrlRepository):
        self._generator = generator
        self._repository = repository

    def execute(self, url: str) -> str:
        code = self._generator.generate()
        self._repository.save(code, url)
        return code
