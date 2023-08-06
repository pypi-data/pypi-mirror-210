
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
		'--tolerance',
		type=click.INT,
		default=10,
		show_default=True,
		help="Tolerence: amount of color variation for croomakey."
		)
def removebg(inputimage, outputimage, color, tolerance):
	inputimage = Image.open(inputimage)
	img = inputimage.convert("RGBA")
	datas = img.getdata()
	newData = []

	for item in datas:
		if crommakey(color[0], tolerance, item[0]) and crommakey(color[1], tolerance, item[1]) and crommakey(color[2], tolerance, item[2]):
			newData.append((255, 255, 255, 0))
		else:
			newData.append(item)

	img.putdata(newData)
	img.save(outputimage, "PNG")
	click.echo(f'{inputimage} is processed as {outputimage}.')





