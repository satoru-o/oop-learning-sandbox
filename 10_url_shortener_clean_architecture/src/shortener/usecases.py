from typing import Protocol


class CodeGenerator(Protocol):
    def generate(self) -> str: ...


class ShortenUrl:
    def __init__(self, generator: CodeGenerator):
        self._generator = generator

    def execute(self, url: str) -> str:
        return self._generator.generate()
