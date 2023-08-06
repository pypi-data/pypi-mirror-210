
import click
import os
from PIL import Image

bg_path = "/Users/vaibhavblayer/10xphysics/backgrounds/bg_instagram.jpg"


@click.command(
        help="Adds background to any transparent image"
        )
@click.option(
        '-i', 
        '--image', 
        type=click.Path(),
        default="./main.png",
        help="Front Image"
        )
@click.option(
        '-b', 
        '--background', 
        type=click.Path(),
        default=bg_path,
        help="Background Image"
        )
@click.option(
        '-o',
        '--outputfile',
        type=click.Path(),
        default="./new.png",
        show_default=True,
        help="Output file name"
        )
@click.option(
        '-p',
        '--position',
        type=click.Tuple([int, int]),
        default=(0, 0),
        show_default=True,
        help="Position of the frontImage wrt center."
        )
def stack(image, background, outputfile, position):
    background = Image.open(background)
    frontImage = Image.open(image)
    frontImage = frontImage.convert("RGBA")
    background = background.convert("RGBA")
    background = background.resize((frontImage.width, frontImage.height))
    width = (background.width - frontImage.width) // 2
    height = (background.height - frontImage.height) // 2
    background.paste(frontImage, (width+position[0], height+position[1]), frontImage)
    background.save(outputfile, format="png")

    click.echo(f'{image} is overlayed on top of the background.')

#    with click.progressbar([1, 2, 3]) as bar:
#        for x in bar:
#            print(f"sleep({x})...")
#            time.sleep(x)







