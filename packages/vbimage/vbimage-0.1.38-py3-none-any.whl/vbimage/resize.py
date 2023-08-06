
import click
import os
from PIL import Image



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
        '-s',
        '--size',
        type=click.Tuple([int, int]),
        default=(1600, 1600),
        show_default=True,
        help='Size of outputimage.'
        )
def resize(inputimage, outputimage, size):
    inputimage = Image.open(inputimage)
    outputimage = inputimage.resize((size[0], size[1]))
#    width = (background.width - frontImage.width) // 2
#    height = (background.height - frontImage.height) // 2
#    background.paste(frontImage, (width, height), frontImage)
    outputimage.save(outputimage, format="png")

    click.echo(f'{inputimage} is resized to {size} as {outputimage}.')

#    with click.progressbar([1, 2, 3]) as bar:
#        for x in bar:
#            print(f"sleep({x})...")
#            time.sleep(x)







