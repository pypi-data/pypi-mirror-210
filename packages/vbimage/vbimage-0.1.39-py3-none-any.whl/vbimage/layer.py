
import click
import os
from PIL import Image


def crommakey(value:int, tolerance:int, match_value:int)->bool:
	if (value-tolerance) >= 0:
		l_value = value - tolerance
	else:
		l_value = 0

	if (value+tolerance) <= 255:
		u_value = value + tolerance
	else:
		u_value = 255

	if match_value <= u_value and match_value >= l_value:
		return True
	else:
		return False


@click.command(
        help="Replaces any color with other color."
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
        default="./main_removedbg.png",
        show_default=True,
        help="Resized output image"
        )
@click.option(
		'-c',
		'--color',
		type=click.Tuple([int, int, int]),
		default=(255, 255, 255),
		show_default=True,
		help="Color to be removed"
		)
@click.option(
		'-t',
		'--opacity',
		type=click.FLOAT,
		default=1,
		show_default=True,
		help="Opacity of the color"
		)
def layer(inputimage, outputimage, color, opacity):
    
    inputfile = os.path.basename(inputimage)
    outputfile = os.path.basename(outputimage)

    inputimage = Image.open(inputimage)
    img = inputimage.convert("RGBA")
    datas = img.getdata()

    newData = []

    for item in datas:
        if item[3] != 0:
            newData.append((color[0], color[1], color[2], item[3]))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(outputimage, "PNG")
    click.secho(f'\t{inputfile} is processed as {outputfile}', fg='bright_green')





