import time

import click
import mw_api
import csv
import datetime


# commands
# 1.
# full_measure --time --pause --num --path/to/csv
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
@click.option('--port',  default='/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0', type=str
              , help="path to serial port like: /dev/ttyUSB0")
@click.pass_context
def mw(ctx, port):
    click.echo('Initializing the serial port handler')
    click.echo('It might take 2 sec because we need time for AVR device to reboot')
    ctx.obj = mw_api.MWHandler(addr=port, baudrate=115200, timeout=3)
    click.echo('Handler created successfully')


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.pass_obj
def get_temp(mwhandler, verbose):
    if verbose:
        click.echo('Trying to get temp data from mw temp sensor')
    json_res = mwhandler.send_message("get_temp", [0, 0])
    status = json_res['args']['status']
    data = json_res['args']['data']
    if verbose:
        click.echo('Raw answer:')
        click.echo(json_res)
    click.echo(f'Answer: {status}, Data: {data}')


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.pass_obj
def get_status(mwhandler, verbose):
    if verbose:
        click.echo('Trying to get info from mw sensor')
    json_res = mwhandler.send_message("get_status", [0, 0])
    status = json_res['args']['status']
    data = json_res['args']
    if verbose:
        click.echo('Raw answer:')
        click.echo(json_res)
    click.echo(f'Answer: {status}\nData: {data}')


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.pass_obj
def get_spectrum(mwhandler, verbose):
    if verbose:
        click.echo('Trying to get spectrum from mw sensor')
    json_res = mwhandler.send_message("get_spectrum", [0, 0])
    status = json_res['args']['status']
    data = json_res['args']['data']
    if verbose:
        click.echo('Raw answer:')
        click.echo(json_res)
    click.echo(f'Answer: {status}\nData: {data}')


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.option('-l', '--led', default='test', type=click.Choice(['test', 'uv', 'ir', 'white'], case_sensitive=False))
@click.option('-s', '--state', default=False, type=bool)
@click.pass_obj
def set_led(mwhandler, verbose, led, state):
    if verbose:
        click.echo(f'Trying to set led {led} to state {state} on mw sensor')
    json_res = mwhandler.send_message("set_led", [led, state])
    status = json_res['args']['status']
    # data = json_res['args']['data']
    if verbose:
        click.echo('Raw answer:')
        click.echo(json_res)
    click.echo(f'Answer: {status}')


def on_led_measure(led, mwhandler, measure_interval, sleep_interval, verbose):
    # set led on
    if verbose:
        click.echo(f'Trying to set {led} led to state on')
    json_res = mwhandler.send_message("set_led", [led, True])
    if verbose:
        click.echo(json_res)
    click.echo("{} on: {}".format(led, json_res['args']['status']))
    # sleep
    time.sleep(measure_interval)  # to stable led temp
    # measure spectrum
    if verbose:
        click.echo('Trying to get spectrum from mw sensor')
    led_spectrum_json = mwhandler.send_message("get_spectrum", [0, 0])
    click.echo("get spectrum: {}".format(led_spectrum_json['args']['status']))
    if verbose:
        click.echo(led_spectrum_json)
    # turn led off
    if verbose:
        click.echo(f'Trying to set {led} led to state off')
    json_res = mwhandler.send_message("set_led", [led, False])
    click.echo("{} off: {}".format(led, json_res['args']['status']))
    if verbose:
        click.echo(json_res)
    # sleep
    time.sleep(sleep_interval)
    return led_spectrum_json


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True, help="verbosity")
@click.option('-mi', '--measure_interval', type=int, help="leds turn-on time in seconds")
@click.option('-si', '--sleep_interval', type=int, help="leds turn-off time in seconds")
@click.option('-p', '--path', default=None, type=click.Path(), help="path to csv file, if no output will go to console")
@click.option('-n', '--number', default=1, type=int, help="number of measures")
@click.pass_obj
def series_measure(mwhandler, measure_interval, sleep_interval, verbose, number, path):

    for i in range(0, number):
    # one cycle of measurements

        # spectrums
        ir_time = datetime.datetime.now()
        ir_spectrum_json = on_led_measure("ir", mwhandler, measure_interval, sleep_interval, verbose)
        white_time = datetime.datetime.now()
        white_spectrum_json = on_led_measure("white", mwhandler, measure_interval, sleep_interval, verbose)
        uv_time = datetime.datetime.now()
        uv_spectrum_json = on_led_measure("uv", mwhandler, measure_interval, sleep_interval, verbose)

        ir_data = ir_spectrum_json['args']['data']
        white_data = white_spectrum_json['args']['data']
        uv_data = uv_spectrum_json['args']['data']

        # finally temp
        if verbose:
            click.echo('Trying to get temp data from mw temp sensor')
        temp_json = mwhandler.send_message("get_temp", [0, 0])
        status = temp_json['args']['status']
        temp_data = temp_json['args']['data'][0]
        if verbose:
            click.echo('Raw answer:')
            click.echo(temp_json)
            click.echo(f'Answer: {status}, Data: {temp_data}')

        # write to csv
        if path:
            with open(path, 'a+', newline='') as csvfile:
                dwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                ir_data_row = [str(ir_time.date()),
                                str(ir_time.time()),
                                temp_data,
                                measure_interval,
                                sleep_interval,
                                "ir"]
                ir_data_row.extend(ir_data)
                dwriter.writerow(ir_data_row)

                white_data_row = [str(white_time.date()),
                                str(white_time.time()),
                                temp_data,
                                measure_interval,
                                sleep_interval,
                                "white"]
                white_data_row.extend(white_data)
                dwriter.writerow(white_data_row)

                uv_data_row = [str(uv_time.date()),
                                str(uv_time.time()),
                                temp_data,
                                measure_interval,
                                sleep_interval,
                                "uv"]
                uv_data_row.extend(uv_data)
                dwriter.writerow(uv_data_row)
        else:
            # print to console
            click.echo()
            click.echo(f"{ir_time} ir measure spectrum: {ir_data}")
            click.echo(f"{white_time}  white measure spectrum: {white_data}")
            click.echo(f"{uv_time} uv measure spectrum: {uv_data}")
            click.echo(f"temperature: {temp_data}")


if __name__ == "__main__":
    mw()

