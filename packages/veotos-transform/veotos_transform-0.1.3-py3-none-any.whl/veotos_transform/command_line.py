from veotos_transform import find_new_text
import click


@click.command()
@click.argument('text')
@click.option("--iteration", default=1, help="Obfuscation iteration.")
@click.option("--encircle", is_flag=True, help="Encircle characters.")
def main(text, iteration, encircle):
    if not encircle:
        new_text = find_new_text(text, iteration)
    else:
        new_text = find_new_text(text, iteration, 'y')
    click.echo(f"{new_text}")
