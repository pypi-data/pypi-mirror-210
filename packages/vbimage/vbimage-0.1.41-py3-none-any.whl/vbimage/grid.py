
import click
import os
from PIL import Image, ImageDraw, ImageFont



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
@click.option(
        '-S',
        '--stroke_width',
        type=click.INT,
        default=2,
        show_default=True,
        help='Stroke width of the lines.'
        )
def grid(inputimage, outputimage, step, stroke_width):
    
    with Image.open(inputimage) as im:
        W = im.width
        H = im.height
        font_size = int(0.3*W/step[0])
        draw = ImageDraw.Draw(im)
        fnt = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", font_size)
        for i in range(step[0]):
            draw.line([(i*W/step[0], H), (i*W/step[0], 0)], fill='black', width=stroke_width)
            draw.text((i*W/step[0], 2*font_size), f'{int(i*W/step[0])}', font=fnt, align='right')
    
        for j in range(step[1]):
            draw.line([(0, j*H/step[1]), (W, j*H/step[1])], fill='black', width=stroke_width)
            draw.text((font_size, j*H/step[1]), f'{int(j*H/step[1])}', font=fnt, align='left')


        im.save(outputimage, format="png")

    click.echo(f'{inputimage} is grided to step size {step} as {outputimage}.')

#    with click.progressbar([1, 2, 3]) as bar:
#        for x in bar:
#            print(f"sleep({x})...")
#            time.sleep(x)







