
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
        type=click.Tuple([int, int, int]),
        default=(255, 0, 0),
        show_default=True,
        help='COlor of the image'
        )
def render(size, outputimage, radius, opacity, color):
    inputimage = Image.new('RGBA', size)
    #bluredimage = inputimage.filter(ImageFilter.GaussianBlur(radius))

    datas = inputimage.getdata()
    newData = []
    for item in datas:
        newData.append((color[0], color[1], color[2], int(opacity*255)))

    inputimage.putdata(newData)

    inputimage.save(outputimage, format="png")
    click.secho(f'\tImage of size {size}, color {color} rendered -> {os.path.basename(outputimage)}', fg='bright_red')








