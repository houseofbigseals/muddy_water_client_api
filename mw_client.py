import time

import click
import mw_api
import csv
import datetime


# commands
# 1.
# full_measure --time --pause --num --path/to/csv
# does this:
# measure temp,on white led, wait time, measure spectrum, write it to csv, off white led, wait pause time
# measure temp, on ir led, wait time, measure spectrum, write it to csv off, ir led, wait pause time
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


@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True, help="verbosity")
@click.option('-l', '--led', default='test', type=click.Choice(['test', 'uv', 'ir', 'white'], case_sensitive=False),
              help="type of led to work with")
@click.option('-mi', '--measure_interval', type=int, help="leds turn-on time in seconds")
@click.option('-si', '--sleep_interval', type=int, help="leds turn-off time in seconds")
@click.option('-p', '--path', default=None, type=click.Path(), help="path to csv file, if no output will go to console")
@click.option('-n', '--number', default=1, type=int, help="number of measures")
@click.pass_obj
def measure(mwhandler, led, measure_interval, sleep_interval, verbose, path, number):

    for i in range(0, number):
        led_time = datetime.datetime.now()
        spectrum_json, temp_json = on_led_measure(led, mwhandler, measure_interval, sleep_interval, verbose)

        spectrum_data = spectrum_json['args']['data']

        temp_data = temp_json['args']['data'][0]

        # write to csv
        if path:
            with open(path, 'a+', newline='') as csvfile:
                dwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                data_row = [str(led_time.date()),
                               str(led_time.time()),
                               temp_data,
                               measure_interval,
                               sleep_interval,
                               led]
                data_row.extend(spectrum_data)
                dwriter.writerow(data_row)
        else:
            # if no csv path selected, print to console
            click.echo(f"{led_time}, T:{temp_data}, ir measure spectrum: {spectrum_data}")


def on_led_measure(led, mwhandler, measure_interval, sleep_interval, verbose):
    """
    full measure operation with set led on, measure temp and spectrum, set led off, and sleep
    :param led: "white" or "uv" or "ir" or "test" or "background"
    :param mwhandler:
    :param measure_interval: in seconds, must be >= 1 sec
    :param sleep_interval: in seconds, must be >= 1 sec
    :param verbose:
    :return:
    """
    # set led on
    if (led != "background"):
        click.echo(datetime.datetime.now())
        if verbose:
            click.echo(f'Trying to set {led} led to state on')
        json_res = mwhandler.send_message("set_led", [led, True])
        click.echo(datetime.datetime.now())
        if verbose:
            click.echo(json_res)
        click.echo("{} on: {}".format(led, json_res['args']['status']))
        click.echo(datetime.datetime.now())
    else:
        # if we are measuring background, we don`t need to set led on
        # so we just wait same time
        time.sleep(0.35)

    # get status

    if verbose:
        click.echo('Trying to get full status data from mw device')
    full_state_json = mwhandler.send_message("get_status", [0, 0])

    # 0.35 sec is time of sending get_temp command and getting answer
    if verbose:
        click.echo('Raw answer:')
        click.echo(full_state_json)

    # if verbose:
    #     click.echo('Trying to get external temp data from mw temp sensor')
    # temp_json = mwhandler.send_message("get_temp", [0, 0])
    #
    # # 0.35 sec is time of sending get_temp command and getting answer
    # status = temp_json['args']['status']
    # temp_data = temp_json['args']['data'][0]
    # if verbose:
    #     click.echo('Raw answer:')
    #     click.echo(temp_json)
    #     click.echo(f'Answer: {status}, Data: {temp_data}')


    # sleep
    time.sleep(measure_interval - 0.35 - 0.35)  # to stable led temp
    # 0.35 sec is time of sending set_led command and getting answer
    # measure spectrum
    click.echo(datetime.datetime.now())
    if verbose:
        click.echo('Trying to get spectrum from mw sensor')
    led_spectrum_json = mwhandler.send_message("get_spectrum", [0, 0])
    # 0.45 sec is time of sending get_spectrum command and getting answer
    click.echo(datetime.datetime.now())
    click.echo("get spectrum: {}".format(led_spectrum_json['args']['status']))
    if verbose:
        click.echo(led_spectrum_json)


    if (led != "background"):
        # turn led off
        if verbose:
            click.echo(f'Trying to set {led} led to state off')
        click.echo(datetime.datetime.now())
        json_res = mwhandler.send_message("set_led", [led, False])
        # 0.35 sec is time of sending set_led command and getting answer
        click.echo("{} off: {}".format(led, json_res['args']['status']))
        if verbose:
            click.echo(json_res)
    else:
        # if we are measuring background, we don`t need to set led on
        # so we just wait same time
        time.sleep(0.35)

    click.echo(datetime.datetime.now())
    # sleep
    time.sleep(sleep_interval - 0.45 - 0.35)
    click.echo(datetime.datetime.now())
    click.echo(time.time())
    return led_spectrum_json, full_state_json


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
        white_time = datetime.datetime.now()
        white_spectrum_json, white_temp_json = on_led_measure("white", mwhandler, measure_interval, sleep_interval, verbose)
        ir_time = datetime.datetime.now()
        ir_spectrum_json, ir_temp_json = on_led_measure("ir", mwhandler, measure_interval, sleep_interval, verbose)
        uv_time = datetime.datetime.now()
        uv_spectrum_json, uv_temp_json = on_led_measure("uv", mwhandler, measure_interval, sleep_interval, verbose)

        white_data = white_spectrum_json['args']['data']
        ir_data = ir_spectrum_json['args']['data']
        uv_data = uv_spectrum_json['args']['data']

        white_temp_data = white_temp_json['args']['data'][0]
        ir_temp_data = ir_temp_json['args']['data'][0]
        uv_temp_data = uv_temp_json['args']['data'][0]

        # write to csv
        if path:
            with open(path, 'a+', newline='') as csvfile:
                dwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                white_data_row = [str(white_time.date()),
                                str(white_time.time()),
                                white_temp_data,
                                measure_interval,
                                sleep_interval,
                                "white"]
                white_data_row.extend(white_data)
                dwriter.writerow(white_data_row)

                ir_data_row = [str(ir_time.date()),
                                str(ir_time.time()),
                                ir_temp_data,
                                measure_interval,
                                sleep_interval,
                                "ir"]
                ir_data_row.extend(ir_data)
                dwriter.writerow(ir_data_row)

                uv_data_row = [str(uv_time.date()),
                                str(uv_time.time()),
                                uv_temp_data,
                                measure_interval,
                                sleep_interval,
                                "uv"]
                uv_data_row.extend(uv_data)
                dwriter.writerow(uv_data_row)
        else:
            # if no csv path selected, print to console
            click.echo()
            click.echo(f"{white_time}, T:{white_temp_data}, white measure spectrum: {white_data}")
            click.echo(f"{ir_time}, T:{ir_temp_data}, ir measure spectrum: {ir_data}")
            click.echo(f"{uv_time}, T:{uv_temp_data}, uv measure spectrum: {uv_data}")

@mw.command()
@click.option('-v', '--verbose', default=False, is_flag=True, help="verbosity")
@click.option('-mi', '--measure_interval', type=int, help="leds turn-on time in seconds")
@click.option('-si', '--sleep_interval', type=int, help="leds turn-off time in seconds")
@click.option('-pi', '--pause_interval', type=int, help="pause between measures in seconds")
@click.option('-p', '--path', default=None, type=click.Path(), help="path to csv file, if no, output will go to the console")
@click.option('-n', '--number', default=1, type=int, help="number of measures")
@click.pass_obj
def triple_measure(mwhandler, measure_interval, sleep_interval, pause_interval, verbose, number, path):
    fails = 0
    max_fails = 3  # if there are nore than 3 fails in row, then reset serial connection
    i = 0

    while i < number:
    # one cycle of measurements
        already_failed = False
        try:
            # getting spectrums
            white_time = datetime.datetime.now()
            white_spectrum_json, white_temp_json = on_led_measure("white", mwhandler, measure_interval, sleep_interval, verbose)
            ir_time = datetime.datetime.now()
            ir_spectrum_json, ir_temp_json = on_led_measure("ir", mwhandler, measure_interval, sleep_interval, verbose)
            uv_time = datetime.datetime.now()
            uv_spectrum_json, uv_temp_json = on_led_measure("uv", mwhandler, measure_interval, sleep_interval, verbose)
            back_time = datetime.datetime.now()
            back_spectrum_json, back_temp_json = on_led_measure("background", mwhandler, measure_interval, sleep_interval, verbose)

        except Exception as e:
            already_failed = True
            click.echo("we got error: {}".format(e))

            if fails < max_fails:
                fails += 1
                click.echo("error counter: {}".format(fails))
                click.echo("lets try just to send that commands again")
                continue
            else:
                click.echo("too much errors!")
                click.echo("trying to reset serial connection")
                mwhandler.reset_serial()
                click.echo("serial connection updated")
                # reset errors counter
                fails = 0

        if not already_failed:
            white_data = white_spectrum_json['args']['data']
            ir_data = ir_spectrum_json['args']['data']
            uv_data = uv_spectrum_json['args']['data']
            back_data = back_spectrum_json['args']['data']

            white_temp_data = white_temp_json['args']['data'][0]
            ir_temp_data = ir_temp_json['args']['data'][0]
            uv_temp_data = uv_temp_json['args']['data'][0]
            back_temp_data = back_temp_json['args']['data'][0]

            # write to csv
            if path:
                with open(path, 'a+', newline='') as csvfile:
                    dwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    white_data_row = [str(white_time.date()),
                                    str(white_time.time()),
                                    white_temp_data,
                                    measure_interval,
                                    sleep_interval,
                                    "white"]
                    white_data_row.extend(white_data)
                    dwriter.writerow(white_data_row)

                    ir_data_row = [str(ir_time.date()),
                                    str(ir_time.time()),
                                    ir_temp_data,
                                    measure_interval,
                                    sleep_interval,
                                    "ir"]
                    ir_data_row.extend(ir_data)
                    dwriter.writerow(ir_data_row)

                    uv_data_row = [str(uv_time.date()),
                                    str(uv_time.time()),
                                    uv_temp_data,
                                    measure_interval,
                                    sleep_interval,
                                    "uv"]
                    uv_data_row.extend(uv_data)
                    dwriter.writerow(uv_data_row)

                    back_data_row = [str(back_time.date()),
                                    str(back_time.time()),
                                    back_temp_data,
                                    measure_interval,
                                    sleep_interval,
                                    "back"]
                    back_data_row.extend(back_data)
                    dwriter.writerow(back_data_row)
            else:
                # if no csv path selected, print to console
                click.echo()
                click.echo(f"{white_time}, T:{white_temp_data}, white measure spectrum: {white_data}")
                click.echo(f"{ir_time}, T:{ir_temp_data}, ir measure spectrum: {ir_data}")
                click.echo(f"{uv_time}, T:{uv_temp_data}, uv measure spectrum: {uv_data}")
                click.echo(f"{back_time}, T:{back_temp_data}, background measure spectrum: {back_data}")

            # then wait pause after triple measure
            time.sleep(pause_interval)
            # update counter
            i += 1



if __name__ == "__main__":
    mw()

