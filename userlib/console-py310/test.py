from handler import Console

console = Console()


@console.match(lambda text: text.strip().upper() == "HELLO")
def hello(_: str):
    console.print("Hello World!\n")


while True:
    console.seek("> ", lambda _: console.print("Unknown command.\n"))
