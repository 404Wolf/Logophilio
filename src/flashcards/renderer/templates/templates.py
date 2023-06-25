from jinja2 import Environment, PackageLoader, select_autoescape

jinjaEnv = Environment(
    loader=PackageLoader("flashcards", "renderer/templates"),
    autoescape=select_autoescape(),
)

flashcardFrontTemplate = jinjaEnv.get_template("front.svg")
flashcardBackTemplate = jinjaEnv.get_template("back.svg")
