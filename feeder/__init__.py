import jinja2


JinjaEnvironment = jinja2.Environment(
    loader=jinja2.PackageLoader("feeder", "templates"),
    autoescape=jinja2.select_autoescape(
        enabled_extensions=("html", "html.j2", "xml", "xml.j2"),
    ),
)


def render_template(spider, **ctx):
    template_name = spider
    if not isinstance(spider, str):
        template_name = spider.name

    return JinjaEnvironment.get_template(f"{template_name}.html.j2").render(ctx)


def render_feed(items):
    return JinjaEnvironment.get_template("atom.xml.j2").render(items=items)


def render_opml(items):
    return JinjaEnvironment.get_template("opml.xml.j2").render(items=items)


def render_nginx(password, output_dir):
    return JinjaEnvironment.get_template("nginx.conf.j2").render(
        password=password,
        output_dir=output_dir,
    )
