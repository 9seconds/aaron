import jinja2


JinjaEnvironment = jinja2.Environment(
    loader=jinja2.PackageLoader("feeder", "templates"),
    autoescape=jinja2.select_autoescape(
        enabled_extensions=("html", "html.j2", "xml", "xml.j2"),
    ),
)


def render_template(spider, **ctx):
    return JinjaEnvironment.get_template(f"{spider.name}.html.j2").render(ctx)


def render_feed(items):
    return JinjaEnvironment.get_template("atom.xml.j2").render(items=items)
