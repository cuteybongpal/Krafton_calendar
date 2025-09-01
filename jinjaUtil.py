from jinja2 import Environment, FileSystemLoader

def render(path, data : dict):
    env = Environment(loader = FileSystemLoader('templates'))
    template = env.get_template(path+".html")
    rendered_template = template.render(**data)
    return rendered_template
