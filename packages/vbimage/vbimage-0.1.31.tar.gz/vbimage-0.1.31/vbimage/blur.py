
import click
import os
from PIL import Image, ImageFilter


@click.command(
        help="Adds background to any transparent image"
        )
@click.option(
        '-i', 
        '--inputimage', 
        type=click.Path(),
        default="./main.png",
        show_default=True,
        help="Front Image"
        )
@click.option(
        '-o', 
        '--outputimage', 
        type=click.Path(),
        default="./main_resized.png",
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
def blur(inputimage, outputimage, radius, opacity):
    inputimage = Image.open(inputimage)
    bluredimage = inputimage.filter(ImageFilter.GaussianBlur(radius))

    datas = bluredimage.getdata()
    newData = []
    for item in datas:
        newData.append((item[0], item[1], item[2], int(opacity*item[3])))

    bluredimage.putdata(newData)
    
    bluredimage.save(outputimage, format="png")
    click.echo(f'{inputimage} is blured to radius {radius} as {outputimage}.')








