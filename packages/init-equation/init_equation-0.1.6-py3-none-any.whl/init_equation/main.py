import click
import os
import time


from .chapters import chapters_list
from .equation import Equation
from .choice_option import ChoiceOption

path_parent = os.environ["TEX_PARENT_PATH"] 

eqn_number_without_database = f'{int(time.strftime("%H%M%S%d%m%Y")):14}'

link = r"""
\def\gdrive{Link}
"""

qrcode = r"""
\pagebreak

\vspace*{\fill}
\begin{center}
    \fbox{\qrcode[height=2cm]{\gdrive}}
\end{center}
\vspace*{\fill}
"""

size_square = f'\\vgeometry\n\n'
size_h_rectangle = f'\\vgeometry[8][4.5][15][15][10][10]\n\n'
size_v_rectangle = f'\\vgeometry[4.5][8][15][15][10][10]\n\n'

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(
        context_settings = CONTEXT_SETTINGS,
        help="Creates problem format tex file"
        )
@click.option(
        '-c',
        '--chapter',
        prompt='Chapters',
        type=click.Choice(
            chapters_list,
            case_sensitive=False),
        cls=ChoiceOption,
        help="Chapter name",
        )
@click.option(
        '-s',
        '--size',
        prompt='Size',
        default=1,
        type=click.Choice(['square', 'h-rectangle', 'v-rectangle']),
        cls=ChoiceOption,
        show_default=True,
        help="Size of the canvas"
        )
@click.option(
        '-n',
        '--equation_number',
        type=click.INT
        )
@click.option(
        '-a',
        '--append_to_database',
        is_flag=True,
        default=True,
        prompt=True,
        help="flag (-a turns-on) appends the equation to database"
        )
@click.option(
        '-c',
        '--copy',
        is_flag=True,
        prompt=True,
        default=False,
        show_default=True,
        help="If true copies the previous main.tex file"
        )
def main(chapter, size, equation_number, append_to_database, copy):
    equation = Equation(chapter, path_parent)
    if append_to_database:
        try:
            equation_number = equation.get_data(1)[0][0] + 1
        except:
            equation_number = 1
        equation.insert_data()
    else:
        equation_number = eqn_number_without_database

    path_equation = os.path.join(
            equation.path_equation(),
            f'equation-{equation_number:02}'
            )

    path_equation_to_copy_from = os.path.join(
            equation.path_equation(),
            f'equation-{equation_number-1:02}'
            )

    os.makedirs(path_equation, exist_ok=True)
    main_tex = os.path.join(path_equation, 'main.tex')
    download_dir = os.path.join(path_equation, 'downloads')
    os.makedirs(download_dir, exist_ok=True)

    if copy:
        os.system(f'cp {path_equation_to_copy_from}/main.tex {path_equation}/main.tex')
    else:
        with open(main_tex, 'w') as file:
            file.write(f'\\documentclass{{article}}\n')
            file.write(f'\\usepackage{{v-equation}}\n')
            if size == 'square':
                file.write(size_square)
            elif size == 'h-rectangle':
                file.write(size_h_rectangle)
            elif size == 'v-rectangle':
                file.write(size_v_rectangle)

            file.write(f'\\begin{{document}}\n')
            file.write(link)
            file.write(f'\\vtitle[title]\n')
            file.write(f'\\begin{{center}}\n')
            file.write(f'\\begin{{tikzpicture}}\n')
            file.write(f'\\tzdot*(0, 0)\n')
            file.write(f'\\end{{tikzpicture}}\n')
            file.write(f'\\end{{center}}\n')
            file.write(f'\\vspace*{{\\fill}}\n')
            file.write(f'\\begin{{align*}}\n')
            file.write(f'\\int x dx\n')
            file.write(f'\\end{{align*}}\n')
            file.write(f'\\vspace*{{\\fill}}\n')
            file.write(qrcode)
            file.write(f'\\end{{document}}\n')



    os.system(f'bat {main_tex}')
    time.sleep(1)
    os.system(f'open -a texmaker {main_tex}')
    print('\n\topening texmaker ...\n')
    time.sleep(1)
