import click
import mw_api


# commands
# 1.
# full_measure --time --pause --num
# does this:
# measure temp, on ir led, wait time, measure spectrum, write it to csv off, ir led, wait pause time
# measure temp,on white led, wait time, measure spectrum, write it to csv, off white led, wait pause time
# measure temp,on uv led, wait time, measure spectrum, write it to csv, off uv led, wait pause time
# run that num counts
# 2.
# measure --time --pause --led [ir, uv, white]
# does this:
# measure temp, on selected led, wait time, measure spectrum, write it to csv, off selected led, wait pause time
# 3.
# set_led --led --state
# just show on screen, no save to csv
# 4.
# get_temp
# just show on screen, no save to csv
# 5.
# get_measure
# just show on screen, no save to csv
# 6.
# start_new_exp --name --pause --time --someparams
# creates new folder with new config and new csv


@click.group()
def mw():
    pass

@mw.command()
def get_temp():
    click.echo('Initialized the database')

@mw.command()
def initdb():
    click.echo('Initialized the database')

@mw.command()
def dropdb():
    click.echo('Dropped the database')

@mw.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo(f"Hello {name}!")


if __name__ == "__main__":
    print("fuuuu")

    # fuuu()
    # hello()
    mw()

