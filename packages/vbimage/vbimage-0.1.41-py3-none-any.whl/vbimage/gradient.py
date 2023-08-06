import subprocess
import click
import os
from PIL import Image, ImageFilter


@click.command(
        help="Creates an image using given size and color."
        )
@click.option(
        '-s', 
        '--size', 
        type=click.Tuple([int, int]),
        default=(1600, 1600),
        show_default=True,
        help="Size of image:(width, height)"
        )
@click.option(
        '-d',
        '--dpi',
        type=click.INT,
        default=320,
        show_default=True,
        help='DPI of the image'
        )
@click.option(
        '-o', 
        '--outputimage', 
        type=click.Path(),
        default="./background.png",
        show_default=True,
        help="Resized output image"
        )
@click.option(
        '-r',
        '--radius',
        type=click.INT,
        default=2,
        show_default=True,
        help='Radius of GaussianBlur'
        )
@click.option(
        '-t',
        '--opacity',
        type=click.FLOAT,
        default=1,
        show_default=True,
        help="Opacity of bluredimage"
        )
@click.option(
        '-c',
        '--color',
        type=click.Tuple([str, str, str, str]),
        default=('green', 'red', 'blue', 'yellow'),
        show_default=True,
        help='Color of the corners'
        )
def gradient(size, outputimage, radius, opacity, color, dpi):


    try:
        os.makedirs('temp', exist_ok=True)
        main_tex = os.path.join('temp', 'main.tex')
        try:
            with open(main_tex, 'w') as file:
                file.write(f'\\documentclass[utf-8]{{article}}\n')
                file.write(f'\\usepackage{{v-equation}}\n')
                file.write(f'\\geometry{{paperwidth={size[0]/dpi}in, paperheight={size[1]/dpi}in}}\n')
                file.write(f'\\begin{{document}}\n')
                file.write(f'\\begin{{tikzpicture}}\n')
                file.write(f'[remember picture,overlay]\n')
                file.write(f'\\shade[upper right={color[0]}, upper left={color[1]}, lower left={color[2]}, lower right={color[3]}](current page.south west)rectangle(current page.north east);\n')
                file.write(f'\\end{{tikzpicture}}\n')
                file.write(f'\\end{{document}}')

                try:
                    os.chdir('./temp')
                    try:
                        os.system(f'pdflatex -shell-escape main.tex')
                    except:
                        click.secho(f'H')

                except:
                    click.secho(f'\tFaild pdflatex', fg='bright_red')
        except:
            click.secho(f'\tFailed writing file', fg='bright_red')
    except:
        click.secho(f'\tFailed directories', fg='bright_red')
    

    #click.secho(f'\tImage of size {size}, color {color} rendered -> {os.path.basename(outputimage)}', fg='bright_red')








