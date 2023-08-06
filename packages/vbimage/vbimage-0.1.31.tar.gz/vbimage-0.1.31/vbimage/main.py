import click


#from .resize import resize
#from .info import info
from .removebg import removebg
from .pixelate import pixelate
from .blur import blur
from .stack import stack
from .render import render
from .layer import layer
from .grid import grid

CONTEXT_SETTINGS = dict(
        help_option_names = [
            '-h',
            '--help'
        ]
)

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


main.add_command(layer)
main.add_command(render)
main.add_command(stack)
main.add_command(blur)
main.add_command(pixelate)
main.add_command(removebg)
main.add_command(grid)
#main.add_command(resize)
#main.add_command(info)
