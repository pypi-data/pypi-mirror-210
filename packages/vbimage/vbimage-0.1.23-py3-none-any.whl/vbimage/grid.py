
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
        default="./main_grided.png",
        show_default=True,
        help="Resized output image"
        )
@click.option(
        '-s',
        '--step',
        type=click.Tuple([int, int]),
        default=(10, 10),
        show_default=True,
        help='Number of division.'
        )
def grid(inputimage, outputimage, step):
    inputimage = Image.open(inputimage)
    draw = ImageDraw.Draw(inputimage)
    for i in step[0]:
        W = inputimage.width
        H = inputimage.height
        draw.line([(i*W/step[0], H), (i*W/step[0], 0)], fill='black', width=2)
    
    for j in step[1]:
        W = inputimage.width
        H = inputimage.height
        draw.line([(0, i*H/step[1]), (W, i*H/step[1])], fill='black', width=2)


    draw.save(outputimage, format="png")

    click.echo(f'{inputimage} is grided to step size {step} as {outputimage}.')

#    with click.progressbar([1, 2, 3]) as bar:
#        for x in bar:
#            print(f"sleep({x})...")
#            time.sleep(x)







