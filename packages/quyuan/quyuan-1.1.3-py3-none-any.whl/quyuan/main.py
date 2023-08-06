#!/usr/bin/env python3
"""
quyuan: a utility for illustrating human and other species chromosomes
https://github.com/tcztzy/quyuan
"""
__author__ = ["Tang Ziya", "Lavanya Rishishar", "Aroon Chande"]
__copyright__ = "Copyright 2019, Applied Bioinformatics Lab"
__license__ = "GPLv3"

import json
import logging
import os
import pickle
import pkgutil
import re

import cairosvg
import click

from quyuan import __version__

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

COORDINATES = {
    "1": {"cx": 128.6, "cy": 1.5, "ht": 1654.5, "width": 118.6},
    "2": {"cx": 301.4, "cy": 43.6, "ht": 1612.4, "width": 118.6},
    "3": {"cx": 477.6, "cy": 341.4, "ht": 1314.7, "width": 118.6},
    "4": {"cx": 655.6, "cy": 517.9, "ht": 1138.1, "width": 118.6},
    "5": {"cx": 835.4, "cy": 461, "ht": 1195.1, "width": 118.6},
    "6": {"cx": 1012.4, "cy": 524.2, "ht": 1131.8, "width": 118.6},
    "7": {"cx": 1198.2, "cy": 608.5, "ht": 1047.5, "width": 118.6},
    "8": {"cx": 1372.9, "cy": 692.8, "ht": 963.2, "width": 118.6},
    "9": {"cx": 1554.5, "cy": 724.4, "ht": 931.6, "width": 118.6},
    "10": {"cx": 1733.8, "cy": 766.6, "ht": 889.4, "width": 118.6},
    "11": {"cx": 1911.5, "cy": 766.6, "ht": 889.4, "width": 118.6},
    "12": {"cx": 2095.6, "cy": 769.7, "ht": 886.3, "width": 118.6},
    "13": {"cx": 129.3, "cy": 2068.8, "ht": 766.1, "width": 118.6},
    "14": {"cx": 301.6, "cy": 2121.5, "ht": 713.4, "width": 118.6},
    "15": {"cx": 477.5, "cy": 2153.1, "ht": 681.8, "width": 118.6},
    "16": {"cx": 656.7, "cy": 2232.2, "ht": 602.8, "width": 118.6},
    "17": {"cx": 841.2, "cy": 2290.7, "ht": 544.3, "width": 118.6},
    "18": {"cx": 1015.7, "cy": 2313.9, "ht": 521.1, "width": 118.6},
    "19": {"cx": 1199.5, "cy": 2437.2, "ht": 397.8, "width": 118.6},
    "20": {"cx": 1374.4, "cy": 2416.1, "ht": 418.9, "width": 118.6},
    "21": {"cx": 1553, "cy": 2510.9, "ht": 324.1, "width": 118.6},
    "22": {"cx": 1736.9, "cy": 2489.8, "ht": 345.1, "width": 118.6},
    "X": {"cx": 1915.7, "cy": 1799.21, "ht": 1035.4, "width": 118.6},
    "Y": {"cx": 2120.9, "cy": 2451.6, "ht": 382.7, "width": 118.6},
}

CHROM_SIZES: dict = json.loads(pkgutil.get_data("quyuan", "chrom_sizes.json"))


def draw(svg_header, svg_footer, input_file, prefix, build):
    """
    Create the SVG object
    """
    polygons = ""
    try:
        input_fh = open(input_file, "r")
    except (IOError, EOFError) as input_fh_e:
        print("Error opening input file!")
        raise input_fh_e
    svg_fn = f"{prefix}.svg"
    try:
        svg_fh = open(svg_fn, "w")
        svg_fh.write(svg_header)
    except (IOError, EOFError) as svg_fh_e:
        print("Error opening output file!")
        raise svg_fh_e
    line_num = 1
    for entry in input_fh:
        if entry.startswith("#"):
            continue
        entry = entry.rstrip().split("\t")
        if len(entry) != 7:
            exit(f"Line number {line_num} does not have 7 columns")
        chrm, start, stop, feature, size, col, chrcopy = entry
        chrm = chrm.replace("chr", "")
        start = int(start)
        stop = int(stop)
        size = float(size)
        feature = int(feature)
        chrcopy = int(chrcopy)
        if 0 > size > 1:
            print(
                f"Feature size, {size},on line {line_num} unclear. \
                Please bound the size between 0 (0%) to 1 (100%). Defaulting to 1."
            )
            size = 1
        if not re.match("^#.{6}", col):
            print(
                f"Feature color, {col}, on line {line_num} unclear. \
                Please define the color in hex starting with #. Defaulting to #000000."
            )
            col = "#000000"
        if chrcopy not in [1, 2]:
            print(
                f"Feature chromosome copy, {chrcopy}, on line {line_num}\
             unclear. Skipping..."
            )
            line_num = line_num + 1
            continue
        line_num = line_num + 1
        if feature == 0:  # Rectangle
            feat_start = (
                start * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            feat_end = (
                stop * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            width = COORDINATES[chrm]["width"] * size / 2
            if chrcopy == 1:
                x_pos = COORDINATES[chrm]["cx"] - width
            else:
                x_pos = COORDINATES[chrm]["cx"]
            y_pos = COORDINATES[chrm]["cy"] + feat_start
            height = feat_end - feat_start
            svg_fh.write(
                f'<rect x="{x_pos}" y="{y_pos}" fill="{col}" width="{width}"\
             height="{height}"/>'
                + "\n"
            )
        elif feature == 1:  # Circle
            feat_start = (
                start * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            feat_end = (
                stop * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            radius = COORDINATES[chrm]["width"] * size / 4
            if chrcopy == 1:
                x_pos = COORDINATES[chrm]["cx"] - COORDINATES[chrm]["width"] / 4
            else:
                x_pos = COORDINATES[chrm]["cx"] + COORDINATES[chrm]["width"] / 4
            y_pos = COORDINATES[chrm]["cy"] + (feat_start + feat_end) / 2
            svg_fh.write(
                f'<circle fill="{col}" cx="{x_pos}" cy="{y_pos}"\
             r="{radius}"/>'
                + "\n"
            )
        elif feature == 2:  # Triangle
            feat_start = (
                start * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            feat_end = (
                stop * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            if chrcopy == 1:
                x_pos = COORDINATES[chrm]["cx"] - COORDINATES[chrm]["width"] / 2
                sx_pos = 38.2 * size
            else:
                x_pos = COORDINATES[chrm]["cx"] + COORDINATES[chrm]["width"] / 2
                sx_pos = -38.2 * size
            y_pos = COORDINATES[chrm]["cy"] + (feat_start + feat_end) / 2
            sy_pos = 21.5 * size
            polygons += (
                f'<polygon fill="{col}" points="{x_pos-sx_pos},{y_pos-sy_pos} \
            {x_pos},{y_pos} {x_pos-sx_pos},{y_pos+sy_pos}"/>'
                + "\n"
            )
        elif feature == 3:  # Line
            y_pos1 = (
                start * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            )
            y_pos2 = stop * COORDINATES[chrm]["ht"] / CHROM_SIZES[build][chrm]
            y_pos = (y_pos1 + y_pos2) / 2
            y_pos += COORDINATES[chrm]["cy"]
            if chrcopy == 1:
                x_pos1 = COORDINATES[chrm]["cx"] - COORDINATES[chrm]["width"] / 2
                x_pos2 = COORDINATES[chrm]["cx"]
                svg_fh.write(
                    f'<line fill="none" stroke="{col}" stroke-miterlimit="10" \
                    x1="{x_pos1}" y1="{y_pos}" x2="{x_pos2}" y2="{y_pos}"/>'
                    + "\n"
                )
            else:
                x_pos1 = COORDINATES[chrm]["cx"]
                x_pos2 = COORDINATES[chrm]["cx"] + COORDINATES[chrm]["width"] / 2
                svg_fh.write(
                    f'<line fill="none" stroke="{col}" stroke-miterlimit="10" \
                    x1="{x_pos1}" y1="{y_pos}" x2="{x_pos2}" y2="{y_pos}"/>'
                    + "\n"
                )
        else:
            print(
                f"Feature type, {feature}, unclear. Please use either 0, 1, 2 or 3. Skipping..."
            )
            continue
    svg_fh.write(svg_footer)
    svg_fh.write(polygons)
    svg_fh.write("</svg>")
    svg_fh.close()
    logger.info(click.style(f"Successfully created SVG", fg="green"))


@click.command(name="quyuan")
@click.version_option(version=__version__)
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    default=None,
    metavar="<input.bed>",
    help="Input BED-like file",
)
@click.option(
    "-p",
    "--prefix",
    required=False,
    default="out",
    metavar="[output file prefix]",
    help='Output prefix [Default: "out"]',
)
@click.option(
    "-b",
    "--build",
    required=False,
    default="hg38",
    type=click.Choice(CHROM_SIZES.keys(), case_sensitive=False),
    help="Human genome build to use [Default: hg38]",
)
@click.option(
    "-f",
    "--force",
    required=False,
    default=False,
    help="Overwrite output files if they exist already",
    is_flag=True,
)
@click.option(
    "-ofmt",
    "--oformat",
    required=False,
    default="png",
    type=click.Choice(["png", "pdf", "ps", "svg"], case_sensitive=False),
    help="Output format for conversion",
)
@click.option(
    "-v",
    "--verbose",
    required=False,
    default=False,
    help="Display verbose output",
    is_flag=True,
)
def run(input_file, prefix, build, force, oformat, verbose):
    """
    quyuan: a utility for illustrating human chromosomes
    https://github.com/tcztzy/quyuan
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    if build not in CHROM_SIZES:
        exit(click.style(f"Build must be on of {CHROM_SIZES.keys()}, you supplied {build}.", fg="red"))

    svg_pkl_data = pkgutil.get_data("quyuan", "base.svg.p")
    svg_header, svg_footer = pickle.loads(svg_pkl_data)
    logger.info(click.style(f"Drawing chromosome ideogram using {input_file}", fg="blue"))
    if os.path.exists(f"{prefix}.svg") and force is False:
        logger.info(click.style(f"'{prefix}.svg' already exists.", fg="yellow"))
        click.confirm(f"Overwrite {prefix}.svg?", abort=True)
        click.secho(f"Overwriting existing file and saving to: {prefix}.svg", fg="blue")
    else:
        logger.info(click.style(f"Saving to: {prefix}.svg", fg="blue"))
    draw(svg_header, svg_footer, input_file, prefix, build)
    logger.info(click.style(f"Converting {prefix}.svg -> {prefix}.{oformat} ",fg="blue"))
    try:
        getattr(cairosvg, f"svg2{oformat}")(url=f"{prefix}.svg", write_to=f"{prefix}.{oformat}")
    except Exception as e:
        logger.info(click.style(f"Failed SVG to PNG conversion...", fg="red"))
        raise e
    finally:
        logger.info(click.style(
            f"Successfully converted SVG to {oformat.upper()}",
            fg="green",
        ))
