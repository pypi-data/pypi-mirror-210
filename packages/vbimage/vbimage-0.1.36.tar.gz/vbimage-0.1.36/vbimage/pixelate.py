from PIL import Image


import click

@click.command(
        help="Pixelates any image."
        )
@click.option(
        '-i',
        '--inputfile',
        type=click.Path(),
        default="./main.png",
        show_default=True,
        help="Input file"
        )
@click.option(
        '-o',
        '--outputfile',
        type=click.Path(),
        default="./pixelated.png",
        show_default=True,
        help="Output file"
        )
@click.option(
        '-p',
        '--pixels',
        type=click.Tuple([int, int]),
        default=(16, 16),
        show_default=True,
        help="Pixelating size"
        )
def pixelate(inputfile, outputfile, pixels):
    image = Image.open(inputfile)
    p_image = image.resize(pixels, resample=Image.Resampling.BILINEAR)

    p_image.resize(image.size, Image.Resampling.NEAREST).save(outputfile, 'PNG')
