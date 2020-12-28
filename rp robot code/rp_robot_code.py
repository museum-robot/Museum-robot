# import libraries 
import RPi.GPIO as GPIO
import time
from threading import Thread, Lock, Event
import threading

# run command line in the terminal
from subprocess import call

# camera
# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import cv2

import requests
import json
import os
import playsound
from gtts import gTTS

# for solve sound problem
import pygame  # for play mp3 file
from mutagen.mp3 import MP3  # solve file length problem

# for db get
import urllib

# for string copy
import copy

# for find wifi networks
from wifi import Cell  # pip install wifi

import datetime
import math


"""
GPIO and PWM init
"""
# another option to set gpio
# GPIO.setmode(GPIO.BCM)

# set pin mapping to BOARD->numbers of the pins
GPIO.setmode(GPIO.BOARD)

# turn off channel warnings messages
GPIO.setwarnings(False)

#cleanup GPIO
GPIO.cleanup()

### BOARD pin numbers
#pins on or off
PIN_ON = 1
PIN_OFF = 0
#led warnings pins
BATTERY_WARNING=11
WIFI_CONNECTION_WARNING=13
# setup for distance sensor
TRIG = 22
ECHO = 24
# en 1 right wheel
RIGHT_WHEEL_ENABLE = 37
# en 2 left wheel
LEFT_WHEEL_ENABLE = 26
# left wheel forward
LEFT_WHEEL_FORWARD = 29
# right wheel forward
RIGHT_WHEEL_FORWARD = 35
# left wheel backwards
LEFT_WHEEL_BACKWARDS = 31
# right wheel backwards
RIGHT_WHEEL_BACKWARDS = 33
# left outside IR sensor
LEFT_OUTSIDE_SENSOR = 40
# left inside IR sensor
LEFT_INSIDE_SENSOR = 38
# right outside IR sensor
RIGHT_OUTSIDE_SENSOR = 32
# right inside IR sensor
RIGHT_INSIDE_SENSOR = 36

### Set GPIO pins as output
GPIO.setup(LEFT_WHEEL_FORWARD, GPIO.OUT)
GPIO.setup(RIGHT_WHEEL_FORWARD, GPIO.OUT)
GPIO.setup(LEFT_WHEEL_BACKWARDS, GPIO.OUT)
GPIO.setup(RIGHT_WHEEL_BACKWARDS, GPIO.OUT)
GPIO.setup(RIGHT_WHEEL_ENABLE, GPIO.OUT)
GPIO.setup(LEFT_WHEEL_ENABLE, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(WIFI_CONNECTION_WARNING, GPIO.OUT)
GPIO.setup(BATTERY_WARNING, GPIO.OUT)

### Set GPIO pins as input
GPIO.setup(ECHO, GPIO.IN)
# 2 light=0 (white=0); 1 light=1 (black=1)
GPIO.setup(LEFT_INSIDE_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_INSIDE_SENSOR, GPIO.IN)
GPIO.setup(LEFT_OUTSIDE_SENSOR, GPIO.IN)
GPIO.setup(RIGHT_OUTSIDE_SENSOR, GPIO.IN)

# set pwm for both wheels
PWM_RIGHT_WHEEL = GPIO.PWM(RIGHT_WHEEL_ENABLE, 100)
PWM_LEFT_WHEEL = GPIO.PWM(LEFT_WHEEL_ENABLE, 100)
PWM_BATTERY_WARNING = GPIO.PWM(BATTERY_WARNING, 0.5)

# turn of warning leds
GPIO.output(BATTERY_WARNING, 0)
GPIO.output(WIFI_CONNECTION_WARNING, 0)



def forward(right_wheel_pwm=100, left_wheel_pwm=100):
    """
    makes the robot to drive forward by a given speed.

    Parameters:
    right_wheel_pwm (int): the speed of the right wheel.
    left_wheel_pwm (int): the speed of the left wheel.

    """
    PWM_RIGHT_WHEEL.ChangeDutyCycle(right_wheel_pwm)  # change right wheel PWM
    PWM_LEFT_WHEEL.ChangeDutyCycle(left_wheel_pwm)  # change left wheel PWM
    GPIO.output(LEFT_WHEEL_FORWARD, 1)  # turn left wheel forward on
    GPIO.output(RIGHT_WHEEL_FORWARD, 1)  # turn right wheel forward on
    GPIO.output(LEFT_WHEEL_BACKWARDS, 0)  # turn left wheel backwards off
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 0)  # turn right wheel backwards off


def backwards(right_wheel_pwm=100, left_wheel_pwm=100):
    """
    makes the robot to drive backwards by a given speed.

    Parameters:
    right_wheel_pwm (int): the speed of the right wheel.
    left_wheel_pwm (int): the speed of the left wheel.

    """
    PWM_RIGHT_WHEEL.ChangeDutyCycle(right_wheel_pwm)  # change right wheel PWM
    PWM_LEFT_WHEEL.ChangeDutyCycle(left_wheel_pwm)  # change left wheel PWM
    GPIO.output(LEFT_WHEEL_FORWARD, 0)  # turn left wheel forward off
    GPIO.output(RIGHT_WHEEL_FORWARD, 0)  # turn right wheel forward off
    GPIO.output(LEFT_WHEEL_BACKWARDS, 1)  # turn left wheel backwards on
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 1)  # turn right wheel backwards on


def turn_left(right_wheel_pwm=100, left_wheel_pwm=100):
    """
    makes the robot to make a left turn by a given speed.

    Parameters:
    right_wheel_pwm (int): the speed of the right wheel.
    left_wheel_pwm (int): the speed of the left wheel.

    """
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 0)  # turn right wheel backwards off
    GPIO.output(LEFT_WHEEL_FORWARD, 0)  # turn left wheel forward off
    GPIO.output(LEFT_WHEEL_BACKWARDS, 1)  # turn left wheel backwards on
    GPIO.output(RIGHT_WHEEL_FORWARD, 1)  # turn right wheel backwards on
    PWM_RIGHT_WHEEL.ChangeDutyCycle(right_wheel_pwm)  # change right wheel PWM
    PWM_LEFT_WHEEL.ChangeDutyCycle(left_wheel_pwm)  # change left wheel PWM


def turn_right(right_wheel_pwm=100, left_wheel_pwm=100):
    """
    makes the robot to make a right turn by a given speed.

    Parameters:
    right_wheel_pwm (int): the speed of the right wheel.
    left_wheel_pwm (int): the speed of the left wheel.

    """
    GPIO.output(RIGHT_WHEEL_FORWARD, 0)  # turn right wheel forward off
    GPIO.output(LEFT_WHEEL_BACKWARDS, 0)  # turn left wheel backwards off
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 1)  # turn right wheel backwards on
    GPIO.output(LEFT_WHEEL_FORWARD, 1)  # turn left wheel forward on
    PWM_RIGHT_WHEEL.ChangeDutyCycle(right_wheel_pwm)  # change right wheel PWM
    PWM_LEFT_WHEEL.ChangeDutyCycle(left_wheel_pwm)  # change left wheel PWM


def adjust_wheels_forward_speed_in_turns(right_wheel_pwm=100, left_wheel_pwm=100):
    """
    makes the robot to turn left or right by a given speed to both wheels.

    Parameters:
    right_wheel_pwm (int): the speed of the right wheel.
    left_wheel_pwm (int): the speed of the left wheel.

    """
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 0)  # turn right wheel backwards off
    GPIO.output(LEFT_WHEEL_FORWARD, 1)  # turn left wheel forward off
    GPIO.output(LEFT_WHEEL_BACKWARDS, 0)  # turn left wheel backwards on
    GPIO.output(RIGHT_WHEEL_FORWARD, 1)  # turn right wheel backwards on
    PWM_RIGHT_WHEEL.ChangeDutyCycle(right_wheel_pwm)  # change right wheel PWM
    PWM_LEFT_WHEEL.ChangeDutyCycle(left_wheel_pwm)  # change left wheel PWM



def stop_all_engines():
    """turn off all motors"""
    GPIO.output(LEFT_WHEEL_FORWARD, 0)
    GPIO.output(RIGHT_WHEEL_FORWARD, 0)
    GPIO.output(LEFT_WHEEL_BACKWARDS, 0)
    GPIO.output(RIGHT_WHEEL_BACKWARDS, 0)


def stop_driving_if_event_is_set(stop_driving_cv):
    """
    the robot will stop driving until there is not any event.

    Parameters:
    stop_driving_cv (Condition): lock for synchronisation and waiting.
    """
    # if one of the event is set the robot will stop his driving
    if barcode_event.is_set() or distance_event.is_set():
        # the thread take the lock
        with stop_driving_cv:
            stop_all_engines()
            print("stop driving")
            # the thread going to sleep on the lock and release it.the thread will wait for a wakeup call
            stop_driving_cv.wait()
            print("continue driving")


def drive_on_line(stop_driving_cv):
    """
    an algorithm for driving on black line.

    Local variables:
    forward_right_speed (int): represents the right wheel forward speed
    forward_left_speed (int): represents the left wheel forward speed

    Parameters:
    stop_driving_cv (Condition): lock for synchronisation and waiting.

    """

    global at_home
    forward_right_speed = 28
    forward_left_speed = 25

    try:
        time.sleep(4)
        PWM_RIGHT_WHEEL.start(forward_right_speed)
        PWM_LEFT_WHEEL.start(forward_left_speed)
        # if end_drive_thread_life_event is set the thread will end his life.
        while not end_drive_thread_life_event.is_set():
            stop_driving_if_event_is_set(stop_driving_cv)
            
            if low_battery_stop_engines:
                stop_all_engines()
                continue
            if low_battery_power_event.is_set() and not at_home:
                stop_all_engines()
                play_mp3_file("/home/pi/play_text_and_sounds/battery_life_is_low_in_tour.mp3")
                back_to_home(stop_driving_cv)
            if num_of_completed_stations == len(current_tour_data) and not at_home:
                stop_all_engines()
                time.sleep(2)
                back_to_home(stop_driving_cv)
            # if at least one outside sensors see black line
            if GPIO.input(LEFT_OUTSIDE_SENSOR) == 1 or GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                # if all sensors see black line
                if GPIO.input(LEFT_INSIDE_SENSOR) == 1 and GPIO.input(RIGHT_INSIDE_SENSOR) == 1 and \
                        GPIO.input(LEFT_OUTSIDE_SENSOR) == 1 and GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                    stop_all_engines()
                    if not at_home:
                        print("going home")
                        back_to_home(stop_driving_cv)
                    # the thread will end his life, after finally block execution
                    else:
                        break
                # if both outside sensors see black line, the robot will drive forward so that the inside sensors
                # will also see black line
                if GPIO.input(LEFT_OUTSIDE_SENSOR) == 1 and GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                    forward(forward_right_speed, forward_left_speed)

                # right outside sensor detect black line, and therefore he turn right
                if GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                    # turn right algorithm
                    while not (GPIO.input(LEFT_INSIDE_SENSOR) == 1 and GPIO.input(RIGHT_INSIDE_SENSOR) == 0):
                        stop_driving_if_event_is_set(stop_driving_cv)
                        # in case this is not a real turn, and its actually the end or the start of the route
                        if GPIO.input(LEFT_OUTSIDE_SENSOR) == 1 and GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                            break
                        adjust_wheels_forward_speed_in_turns(2,33)
                # left outside sensor detect black line, and therefore he turn left
                if GPIO.input(LEFT_OUTSIDE_SENSOR) == 1:
                    # turn left algorithm
                    while not (GPIO.input(LEFT_INSIDE_SENSOR) == 0 and GPIO.input(RIGHT_INSIDE_SENSOR) == 1):
                        stop_driving_if_event_is_set(stop_driving_cv)
                        # in case this is not a real turn, and its actually the end or the start of the route
                        if GPIO.input(LEFT_OUTSIDE_SENSOR) == 1 and GPIO.input(RIGHT_OUTSIDE_SENSOR) == 1:
                            break
                        adjust_wheels_forward_speed_in_turns(37, 2)
            # if none of the outside sensors see black line
            else:
                # if both of the inside sensors see black or white drive forward
                if GPIO.input(LEFT_INSIDE_SENSOR) == 0 and GPIO.input(RIGHT_INSIDE_SENSOR) == 0:
                    forward(forward_right_speed, forward_left_speed)
                if GPIO.input(LEFT_INSIDE_SENSOR) == 1 and GPIO.input(RIGHT_INSIDE_SENSOR) == 1:
                    forward(forward_right_speed, forward_left_speed)
                # if left inside sensor see white and right inside sensor see black turn right
                if GPIO.input(LEFT_INSIDE_SENSOR) == 0 and GPIO.input(RIGHT_INSIDE_SENSOR) == 1:
                    turn_right(1, 35)

                # if left inside sensor see black and right inside sensor see white turn left
                if GPIO.input(LEFT_INSIDE_SENSOR) == 1 and GPIO.input(RIGHT_INSIDE_SENSOR) == 0:
                    turn_left(35, 1)
    finally:
        turn_around(stop_driving_cv)
        at_home = False
        end_distance_thread_life_event.set()


def turn_around(stop_driving_cv):
    """
    turns the robot 180 degrees.

    Local variables:
    right_wheel_speed (int): represents the right wheel speed
    left_wheel_speed (int): represents the left wheel speed
    """

    right_wheel_speed = 28
    left_wheel_speed = 38
    # algorithm to turn the robot around
    while GPIO.input(LEFT_OUTSIDE_SENSOR) == 1:
        stop_driving_if_event_is_set(stop_driving_cv)
        turn_left(right_wheel_speed, left_wheel_speed)
    # to let to robot to move a bit from the end/start point
    time.sleep(0.3)
    while GPIO.input(LEFT_OUTSIDE_SENSOR) == 0:
        stop_driving_if_event_is_set(stop_driving_cv)
        turn_left(right_wheel_speed, left_wheel_speed)
    while GPIO.input(RIGHT_INSIDE_SENSOR) == 0:
        stop_driving_if_event_is_set(stop_driving_cv)
        turn_left(right_wheel_speed, left_wheel_speed)

    stop_all_engines()


def back_to_home(stop_driving_cv):
    """
    Announcing the end of the tour, and turning around to return to the beginning of the route.
    """
    global at_home
    # the tour is over and the barcode scanning is no longer needed
    end_barcode_thread_life_event.set()
    
    play_mp3_file("/home/pi/play_text_and_sounds/end_tour.mp3")
    
    # a break after the announcing the end of the tour
    time.sleep(2)
    turn_around(stop_driving_cv)
    # not to do this function again
    at_home = True


def getDistance(stop_driving_cv, distance_cv):
    """
    an algorithm to measure the distance in front of the robot, and react accordingly.

    Parameters:
    stop_driving_cv (Condition): lock for synchronisation and waiting.
    distance_cv (Condition): lock for synchronisation and waiting.

    Local variables:
    there_is_obstacle (boolean): flag that indicates if there is an obstacle in front of the robot.
    stuck_time_end (time): Represents the current time to prevent the distance sensor from getting stuck
    stuck_time_start (time):Represents the initial time to prevent the distance sensor from getting stuck
    stuck_duration (int): Represents the difference between the initial time and the present time, in order to control the sensor
    critical_distance (int): Represents the critical distance, to prevent frontal collision.
    counter_obastacle_removed (int): saves the amount of times that the robot doesnt see obstacle after there was one.
    counter_obastacle_detected (int): saves the amount of times that the robot see obstacle after there was not one.
    """

    there_is_obstacle = False
    critical_distance = 20
    counter_obastacle_removed=0 
    counter_obastacle_detected=0 
    
    while not end_distance_thread_life_event.is_set():
        with distance_cv:
            if playing_station_event.is_set():
                distance_cv.wait()
        GPIO.output(TRIG, False)
        time.sleep(0.2)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        # The initial time before entering the loop
        stuck_time_start = time.time()
        while GPIO.input(ECHO) == 0:
            # The current time in the loop
            stuck_time_end = time.time()
            # The length of time in the loop
            stuck_duration = math.floor(stuck_time_end - stuck_time_start)
            # Stop the loop so that the thread does not get stuck in it
            if stuck_duration >= 1:
                break
            pulse_start = time.time()
        # Continue the algorithm in case there was a glitch
        if stuck_duration >= 1:
            continue
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        with stop_driving_cv:
            if distance < critical_distance:
                counter_obastacle_detected=counter_obastacle_detected+1
                counter_obastacle_removed=0
                if (not distance_event.is_set()) and counter_obastacle_detected>=2:
                    distance_event.set()
            else:
                counter_obastacle_detected=0
                counter_obastacle_removed=counter_obastacle_removed+1
                # to prevent doing this code unnecessary
                if there_is_obstacle and counter_obastacle_removed>=3:
                    distance_event.clear()
                    there_is_obstacle = False
                if not (barcode_event.is_set() or distance_event.is_set()):
                    stop_driving_cv.notify()

        if distance_event.is_set() and there_is_obstacle == False:
            there_is_obstacle = True
            play_mp3_file("/home/pi/play_text_and_sounds/obstacle.mp3")


def barcode_scan(stop_driving_cv, distance_cv):
    """
    an algorithm to scan barcode and decode his content.
    
    Parameters:
    stop_driving_cv (Condition): lock for synchronisation and waiting.
    distance_cv (Condition): lock for synchronisation and waiting.

    Local variables:
    station_data_obj (object): the data of the scanned station
    """
    global num_of_completed_stations
    global last_station_name_scanned


    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                    help="path to output CSV file containing barcodes")
    args = vars(ap.parse_args())

    # initialize the video stream and allow the camera sensor to warm up
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2)

    # loop over the frames from the video stream
    while not end_barcode_thread_life_event.is_set():
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            text = "{} ({})".format(barcodeData, barcodeType)

            scanned_barcode_data = barcodeData

            # prevent from reacting to the same scanned barcode
            if last_station_name_scanned == scanned_barcode_data:
                break

            station_data_obj = find_station_to_play(scanned_barcode_data)
            if station_data_obj is None:
                last_station_name_scanned = scanned_barcode_data
                break

            with stop_driving_cv:
                barcode_event.set()
            with distance_cv:
                playing_station_event.set()

            if not low_battery_power_event.is_set():
                play_mp3_file("/home/pi/station_mp3_files/"+station_data_obj["station_name"]+".mp3")
                num_of_completed_stations = num_of_completed_stations+1

            last_station_name_scanned = scanned_barcode_data
            with distance_cv:
                playing_station_event.clear()
                distance_cv.notify()
            with stop_driving_cv:
                barcode_event.clear()
                if not (barcode_event.is_set() or distance_event.is_set()):
                    stop_driving_cv.notify()
            break
    vs.stop()


def get_all_stations_info(table_name, query_string):
    """
    send request to dataBase, for current tour information.

    Local variables:
    url (str): The address from which we want to extract the data
    headers (object): provides the needed data, for the request.
    response (object): contains the data from the request.

    Returns:
    tuple: the requested data and the status of the request.

    Parameters:
    table_name (string): represent the name of the table in the database
    query_string (string): represent the query of the desired action in the database
    """

    # perform query to get the current tour data.
    url = 'https://museumrobot-66ba.restdb.io/rest/'+table_name+query_string

    headers = {
        'content-type': "application/json",
        'x-apikey': "5f58ea37c5e01c1e033b8dbf",
        'cache-control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers)
    return response.json(), response.status_code


def find_station_to_play(station_name):
    """
    provides the station data by station name if exist.

    Parameters:
    station_name (str): the station name

    Returns:
    object: the station information if found
    """

    global current_tour_data
    for obj in current_tour_data:
        if obj["station_name"] == station_name:
            return obj
    return None


def create_mp3_for_station(station_obj):
    """
    convert the station info to mp3 file.

    Parameters:
    station_obj (object): the data of the scanned station

    Local variable:
    text_from_db (List): stores the text that will be converted to mp3 file.
    my_text (string): contains the text to be played in this station
    """

    text_from_db = []
    if station_obj["play_child"] is True:
        text_from_db.append("content for child. " + station_obj["child_content"])
    if station_obj["play_adult"] is True:
        text_from_db.append("content for adult. " + station_obj["adult_content"])

    my_text = "we arrived to, "+station_obj["station_name"]+" station."
    for temp_text in text_from_db:
        my_text=my_text+" "+temp_text

    language = 'en'
    mp3_file = gTTS(text=my_text, lang=language, slow=False)

    # in while loop because, the server of the library (gTTS) may be not available at the time
    while True:
        try:
            mp3_file.save("/home/pi/station_mp3_files/"+station_obj["station_name"]+".mp3")
            break
        except:
            print("exception in saving ggts")


def play_mp3_file(file_path):
    """
    play mp3 file by given file path.

    Local Variables:
    song (file): saves mp3 file information.
    song_length (int): length of the mp3 file in seconds.

    Parameters:
    file_path (str): the full path of the mp3 file that played.

    """
    global time_of_last_played_mp3_file
    global playing_mp3_file

    with play_mp3_file_condition:
        if playing_mp3_file:
            if threading.currentThread().getName() == "battery_manager_thread":
                if not low_battery_power_event.is_set():
                    return
            else:
                play_mp3_file_condition.wait()
        playing_mp3_file = True

    # the last time mp3 file was played
    time_of_last_played_mp3_file = time.time()

    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    song = MP3(file_path)
    song_length = song.info.length

    # if battery manager stopped the file from playing, there is no need being a sleep
    # sleep purpose = waiting till the file playing have ended
    for i in range(math.ceil(song_length)+2):
        time.sleep(1)
        if (i % 60) == 0:
            time_of_last_played_mp3_file = time.time()
        if not pygame.mixer.music.get_busy():
            break

    time_of_last_played_mp3_file = time.time()
    
    playing_mp3_file = False
    with play_mp3_file_condition:
        play_mp3_file_condition.notify()


def network_exist(network_name):
    """
    get network name and scan if this network exist.

    Parameters:
    scanned_network_information (object): provides scanned network information.

    Returns:
    boolean: returns True if network name was found, else False.
    """
    for j in range(10):
        scanned_network_information = Cell.all('wlan0')

        for i in scanned_network_information:
            # i.ssid: provides the network name from the object.
            if i.ssid == network_name:
                return True
        time.sleep(0.5)
    return False


def try_to_connect_to_wifi(network_name, password):
    """
    Performs an attempt to connect to the wireless network, according to the data obtained.

    Parameters:
    network_name (str): provide the network name.
    password (str): provide the network password.

    """

    # call()-> tells the OS which command line to run in the terminal
    # argv in this case are user name and password
    # connect_to_wifi.py: external file that we wrote, and can be found in the current folder.
    call("sudo python3 /home/pi/final_code/connect_to_wifi.py " + network_name + " " + password, shell=True)
    time.sleep(2)
    # tell the system to perform refresh to the wireless network.
    call("sudo wpa_cli -i wlan0 reconfigure", shell=True)
    time.sleep(10)


def wifi_connection_exist():
    """
    Checks if the wifi connection exist

    Local Variables:
    response (int): Saves the status code, of a request from the database.
    url (str): Saves the address to which we will refer, to check if there is a network connection.

    Returns:
    boolean: if there is an internet connection return True, else False.

    """
    url = "https://google.com"
    response = 0
    for i in range(2):
        try:
            response = requests.get(url).status_code
            if response == 200:
                return True
            time.sleep(2)
        except:
            return False
    return False


def get_barcode_data():
    """
    reads barcode and return his content.


    Returns:
    str: the content of the scanned barcode.
    """
    global waiting_for_barcode

    play_mp3_file("/home/pi/play_text_and_sounds/please_provide_barcode.mp3")
    waiting_for_barcode = True

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                    help="path to output CSV file containing barcodes")
    args = vars(ap.parse_args())

    # initialize the video stream and allow the camera sensor to warm up
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2)

    # loop over the frames from the video stream
    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            text = "{} ({})".format(barcodeData, barcodeType)
            scanned_barcode_data = barcodeData
            vs.stop()
            play_mp3_file("/home/pi/play_text_and_sounds/barcode_scanned_successfully.mp3")
            waiting_for_barcode = False
            return scanned_barcode_data


def start_tour():
    """creates the threads and their crucial data."""

    global distance_event
    global barcode_event
    global playing_station_event
    global end_distance_thread_life_event
    global end_drive_thread_life_event
    global end_barcode_thread_life_event
    global stop_driving_condition
    global stop_distance_sensor_condition
    global drive_on_line_thread
    global distance_thread
    global barcode_thread
    global in_tour
    global num_of_completed_stations

    play_mp3_file("/home/pi/play_text_and_sounds/start_tour.mp3")

    distance_event = Event()
    barcode_event = Event()
    playing_station_event = Event()
    end_distance_thread_life_event = Event()
    end_drive_thread_life_event = Event()
    end_barcode_thread_life_event = Event()
    stop_driving_condition = threading.Condition()
    stop_distance_sensor_condition = threading.Condition()
    drive_on_line_thread = Thread(name='drive_on_line_thread', target=drive_on_line, args=(stop_driving_condition,))
    distance_thread = Thread(name='distance_thread', target=getDistance,
                             args=(stop_driving_condition, stop_distance_sensor_condition,))
    barcode_thread = Thread(name='barcode_thread', target=barcode_scan,
                            args=(stop_driving_condition, stop_distance_sensor_condition,))

    in_tour = True

    # thread start
    drive_on_line_thread.start()
    distance_thread.start()
    barcode_thread.start()

    # wait for thread to finish
    drive_on_line_thread.join()
    distance_thread.join()
    barcode_thread.join()

    in_tour=False
    num_of_completed_stations=0


def shutdown_rp():
    """tells the system to shutdown """
    call("sudo shutdown now", shell=True)


def prepare_for_tour():
    """
    Makes sure all the data needed for the tour is up and running.

    The function verifies that there is a proper internet connection.
    If it does not exist, it helps the user to connect using a barcode.
    Also make sure that the station data for the tour has been downloaded properly.

    Local Variables:
    network_name (str): Provides the name of the wireless network scanned from the barcode.
    password (str): Provides the password of the wireless network scanned from the barcode.
    current_tour_data_status (int): Saves the status code, of a request from the database.

    """
    # wifi connection test
    if not wifi_connection_exist():
        turn_gpio_pin_on_or_off(WIFI_CONNECTION_WARNING,PIN_ON)  # turn on right led
        play_mp3_file("/home/pi/play_text_and_sounds/first_wifi_connection_failed.mp3")
        while True:
            try:
                # barcode data example = 'user_name','password'
                # eval() gets a string and converts it to tuple.
                network_name, password = eval(get_barcode_data())
                if not network_exist(network_name):
                    play_mp3_file("/home/pi/play_text_and_sounds/network_not_found_user_name_not_exist.mp3")
                else:
                    try_to_connect_to_wifi(network_name, password)
                    if not wifi_connection_exist():
                        play_mp3_file("/home/pi/play_text_and_sounds/error_connecting_to_network_wrong_password.mp3")
                    else:
                        break
            except:
                play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
    turn_gpio_pin_on_or_off(WIFI_CONNECTION_WARNING,PIN_OFF)  # turn off right led
    play_mp3_file("/home/pi/play_text_and_sounds/successfully_connected.mp3")

    # delay after connecting to the network
    time.sleep(2)

    # init museum_id
    global museum_id
    museum_id_token=0
    try:
        with open("/home/pi/final_code/museum_id.txt","r") as file:
            # Reading form a file
            museum_id = file.read()
            
        if len(list(museum_id))>5:
            museum_id_token=''.join(list(museum_id)[-5:])
            
        if museum_id_token !="@@#%$":
            play_mp3_file("/home/pi/play_text_and_sounds/provide_username_password_for_museum_website.mp3")
            while museum_id_token !="@@#%$":         
                try:
                    # eval() gets a string and converts it to tuple.
                    # barcode data example = 'user_name','password'
                    user_name, user_password = eval(get_barcode_data())
                    museum_id_data, museum_id_status = get_all_stations_info("login",'?q={"user name":"'+user_name+'","password":"'+user_password+'"}')
                    if museum_id_status == 200:
                        if museum_id_data:
                            # after we make sure that the user name and password correct,
                            # we save the specific museum_id, that belong to this user in a txt file
                            try:
                                with open("/home/pi/final_code/museum_id.txt", "w") as file:
                                    # Writing data to a file
                                    file.write(str(museum_id_data[0]["_id"])+"@@#%$")
                                museum_id = museum_id_data[0]["_id"]
                                break
                            except IOError as e:
                                print(e)
                        else:
                            play_mp3_file("/home/pi/play_text_and_sounds/Authentication_failed_in_museum_id.mp3")
                    else:
                        play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
                except:
                    play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
        else:
            museum_id=''.join(list(museum_id)[0:-5])
            
    except IOError as e:
        play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")

    play_mp3_file("/home/pi/play_text_and_sounds/preparation_has_begun.mp3")

    # check current tour data
    global current_tour_data
    #     there is valid wifi connection
    for i in range(2):
        current_tour_data, current_tour_data_status = get_all_stations_info("routeinfo",'?q={"museum_id":"%s","current_tour":true}'%museum_id)
        if current_tour_data_status == 200:
            break
    # check if the current_tour data was successfully pulled
    if current_tour_data_status != 200:
        play_mp3_file("/home/pi/play_text_and_sounds/Preparation_for_tour_failed.mp3")
        shutdown_rp()
    # check if there is data in current tour
    elif not current_tour_data:
        play_mp3_file("/home/pi/play_text_and_sounds/No_stations_selected_for_current_tour.mp3")
        shutdown_rp()

    # delete all files in home/pi/station_mp3_files
    call("sudo rm -rf /home/pi/station_mp3_files/*", shell=True)
    # create all mp3 files for the current tour stations
    for station_data in current_tour_data:
        create_mp3_for_station(station_data)

    play_mp3_file("/home/pi/play_text_and_sounds/Preparation_for_the_tour_was_completed_successfully.mp3")


def battery_manager():
    """
    an algorithm to maintain the battery remaining usage time.
    and prevent the speaker from turning off, after no sound was played in the last 10 minutes.

    Local variable:
    battery_power_25 (boolean): flag that indicates if battery power level is at 25%
    end_mp3_test_time (time): represent the time that have past since sound was played
    difference_in_seconds (int): represent the the num of seconds that sound wasn't played
    not_played_mp3_minutes (int): represent the the num of minutes that sound wasn't played
    """
    global battery_remaining_usage_time
    global low_battery_power_event
    global battery_is_full
    global low_battery_stop_engines
    battery_power_25 = False
    start_time_battery_status_is_up_to_date=time.time()
    end_time_battery_status_is_up_to_date=time.time()
    
    while True:
        if battery_is_full:
            battery_remaining_usage_time = FULL_BATTERY_CAPACITY
            battery_is_full=False
            battery_power_25=False
            low_battery_stop_engines=False
            low_battery_power_event.clear()
            PWM_BATTERY_WARNING.ChangeDutyCycle(0)  # turn off left led
        if battery_remaining_usage_time <= FULL_BATTERY_CAPACITY/4 and (not battery_power_25):
            battery_power_25 = True
            PWM_BATTERY_WARNING.ChangeDutyCycle(50)  # make the left led flicker
            if battery_is_full:
                PWM_BATTERY_WARNING.ChangeDutyCycle(0)  # turn off left led
                battery_power_25=False
        if not low_battery_power_event.is_set():
            if battery_remaining_usage_time <= CRITICAL_BATTERY_TIME:
                PWM_BATTERY_WARNING.ChangeDutyCycle(100)  # make the left led light constantly
                low_battery_power_event.set()
        if low_battery_power_event.is_set() and (not in_tour):
            low_battery_stop_engines=True
            if drive_on_line_thread.is_alive():
                low_battery_stop_engines=False
            elif battery_status_is_up_to_date:
                stop_all_engines()
                play_mp3_file("/home/pi/play_text_and_sounds/low_battery_power_detected.mp3")
                shutdown_rp()
            
                
        end_mp3_test_time = time.time()
        difference_in_seconds = end_mp3_test_time - time_of_last_played_mp3_file
        not_played_mp3_minutes = math.floor(difference_in_seconds / 60)
        if not_played_mp3_minutes >= 2:
            if distance_event:
                if distance_event.is_set():
                    play_mp3_file("/home/pi/play_text_and_sounds/Please_clear_the_way.mp3")
            if waiting_for_barcode:
                play_mp3_file("/home/pi/play_text_and_sounds/Still_waiting_for_barcode.mp3")

        if not_played_mp3_minutes >= 10:
            if at_home:
                play_mp3_file("/home/pi/play_text_and_sounds/driving_to_start_position.mp3")
            elif in_tour:
                play_mp3_file("/home/pi/play_text_and_sounds/soon_we_will_reach_the_station.mp3")
            else:
                play_mp3_file("/home/pi/play_text_and_sounds/the_preparation_for_the_tour_Still_in_progress.mp3")
        
        if not battery_status_is_up_to_date:
            end_time_battery_status_is_up_to_date=time.time()
            status_is_up_to_date_minutes=math.floor((end_time_battery_status_is_up_to_date-start_time_battery_status_is_up_to_date)/60)
            if status_is_up_to_date_minutes>=10:
                play_mp3_file("/home/pi/play_text_and_sounds/i_will_shutdown_to_save_battery.mp3")
                low_battery_power_event.set()
                shutdown_rp()
                
                
        time.sleep(60)

        try:
            if battery_remaining_usage_time > 0:
                battery_remaining_usage_time = battery_remaining_usage_time-1
                with open("/home/pi/final_code/battery_remaining_usage_time.txt", "w") as file:
                    # Writing data to a file
                    file.write(str(battery_remaining_usage_time))
        except IOError as e:
            print(e)


def init_battery_manager_thread():
    """
    initialization for battery manager

    Local variables:
    read_completed (boolean): flag that indicates whether read from the file was successful
    barcode_data (string): saves the data from the scanned barcode
    """

    global battery_manager_thread
    global battery_remaining_usage_time
    global CRITICAL_BATTERY_TIME
    global low_battery_power_event
    global battery_is_full
    global battery_status_is_up_to_date
    global low_battery_stop_engines
    read_completed = False
    
    PWM_BATTERY_WARNING.start(0)

    while not read_completed:
        try:
            with open("/home/pi/final_code/battery_remaining_usage_time.txt", "r") as file:
                # Reading form a file
                battery_remaining_usage_time = int(file.read())
            with open("/home/pi/final_code/time_takes_drive_from_start_to_finish.txt", "r") as file:
                # Reading form a file
                CRITICAL_BATTERY_TIME = int(file.read())
            read_completed=True
        except IOError as e:
            print(e)

    low_battery_power_event=Event()
    battery_manager_thread = Thread(name='battery_manager_thread', target=battery_manager)
    battery_manager_thread.start()


# check battery
    barcode_data=0
    play_mp3_file("/home/pi/play_text_and_sounds/Is_the_battery_fully_charged.mp3")
    while barcode_data != "yes" and barcode_data!="no":
        barcode_data=get_barcode_data()
        if barcode_data == "yes":
            try:
                with open("/home/pi/final_code/battery_remaining_usage_time.txt", "w") as file:
                    # Writing data to a file
                    file.write(str(FULL_BATTERY_CAPACITY))
                battery_is_full=True
                low_battery_stop_engines=False
                low_battery_power_event.clear()
                PWM_BATTERY_WARNING.ChangeDutyCycle(0)  # turn off left led
            except IOError as e:
                print(e)
        elif barcode_data != "no":
            play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
    battery_status_is_up_to_date=True       


def drive_to_end_and_back():
    """
    driving from the start point to the end and back.
    """

    global distance_event
    global barcode_event
    global playing_station_event
    global end_distance_thread_life_event
    global end_drive_thread_life_event
    global end_barcode_thread_life_event
    global stop_driving_condition
    global stop_distance_sensor_condition
    global drive_on_line_thread
    global distance_thread

    distance_event = Event()
    barcode_event = Event()
    playing_station_event = Event()
    end_distance_thread_life_event = Event()
    end_drive_thread_life_event = Event()
    end_barcode_thread_life_event = Event()
    stop_driving_condition = threading.Condition()
    stop_distance_sensor_condition = threading.Condition()
    drive_on_line_thread = Thread(name='drive_on_line_thread', target=drive_on_line, args=(stop_driving_condition,))
    distance_thread = Thread(name='distance_thread', target=getDistance,
                             args=(stop_driving_condition, stop_distance_sensor_condition,))

    # thread start
    drive_on_line_thread.start()
    distance_thread.start()

    # wait for thread to finish
    drive_on_line_thread.join()
    distance_thread.join()


def turn_gpio_pin_on_or_off(pin_number,pin_on_or_off):
    """
    Turn the given pin number according to pin_on_or_off.

    Parameters:
    pin_number (int): the number of the pin on the board
    pin_on_or_off (int): tells the function which operation to do on the pin
    """
    GPIO.output(pin_number, pin_on_or_off)

##################
"""
the main function of the program

Local Variables:
there_was_tour (bool): A flag that indicating whether there was a tour beforehand.
distance_event (Event): A flag that indicating whether there was an obstacle, that interferes with robot driving.
barcode_event (Event): A flag that indicating whether, a found barcode belongs to current tour.
playing_station_event (Event): A flag that indicating whether, station content is being played.
end_distance_thread_life_event (Event): A flag that indicating whether, to end distance_thread life.
end_drive_thread_life_event (Event): A flag that indicating whether, to end drive_on_line_thread life.
end_barcode_thread_life_event (Event): A flag that indicating whether, to end barcode_thread life.
stop_driving_condition (Condition Variable): Lock and key, for running critical code.
stop_distance_sensor_condition (Condition Variable): Lock and key, for running critical code.
drive_on_line_thread (Thread): Thread that responsible to run the function: drive_on_line().
distance_thread (Thread): Thread that responsible to run the function: getDistance().
barcode_thread (Thread): Thread that responsible to run the function: barcode_scan().
current_tour_data (object): Saves the station data needed for the tour.
br_data (str): the scanned barcode content.
last_station_name_scanned (str): saves the last scanned station name.
at_home (boolean): flag that indicates whether the robot arrive to the start position.
battery_remaining_usage_time (int): indicates the remaining battery life in minutes
battery_manager_thread (Thread): Thread that responsible to run the function: battery_manager().
low_battery_power_event (Event): A flag that indicating whether, battery power is low.
museum_id (string): string that contains the museum id,
by which we will extract data from the database that belongs to this museum
play_mp3_file_condition (Condition Variable): Lock and key, for running critical code.
playing_mp3_file (boolean): flag that indicating whether, mp3 file is currently being played.
in_tour (boolean): flag that indicating whether, the robot is currently in tour.
num_of_completed_stations (int): saves the amount of stations that have been played in current tour.
waiting_for_barcode (boolean): flag that indicating whether, the robot is waiting for barcode.
FULL_BATTERY_CAPACITY (int): represent the full battery work time in minutes   
CRITICAL_BATTERY_TIME (int): tells the battery manger what is the critical time to stop the robot  
time_of_last_played_mp3_file (time): saves the last time that the speaker made sound 
battery_is_full (boolean): flag that indicating whether, the battery is full.
battery_status_is_up_to_date (boolean): flag that indicating whether, the battery status is up to date.
low_battery_stop_engines (boolean): flag that indicating whether, the battery power is low and the engines need to stop.


Local variables:
start_test_time (time): represent the start time of "init_admin"
end_test_time (time): represent the end time of "init_admin"
difference (int): saves half of the duration in minutes that "init_admin" takes
br_data (string): saves the scanned barcode data

"""

# global variables
there_was_tour = False
distance_event = 0
barcode_event = 0
playing_station_event = 0
end_distance_thread_life_event = 0
end_drive_thread_life_event = 0
end_barcode_thread_life_event = 0
stop_driving_condition = 0
stop_distance_sensor_condition = 0
drive_on_line_thread = drive_on_line_thread = Thread(name='drive_on_line_thread', target=drive_on_line, args=(stop_driving_condition,))
distance_thread = 0
barcode_thread = 0
current_tour_data = 0
last_station_name_scanned = 'last is empty'
at_home = False
battery_manager_thread=0
battery_remaining_usage_time=0
low_battery_power_event=0
museum_id=""
play_mp3_file_condition=threading.Condition()
playing_mp3_file=False
in_tour=False
num_of_completed_stations=0
waiting_for_barcode = False
FULL_BATTERY_CAPACITY = 360
CRITICAL_BATTERY_TIME = 0
time_of_last_played_mp3_file = time.time()
battery_is_full=False 
low_battery_stop_engines=False 
battery_status_is_up_to_date=False 



pygame.mixer.init()
init_battery_manager_thread()
prepare_for_tour()
play_mp3_file("/home/pi/play_text_and_sounds/want_to_start_the_tour.mp3")
while True:
    if low_battery_power_event.is_set():
        play_mp3_file("/home/pi/play_text_and_sounds/low_battery_power_detected.mp3")
        shutdown_rp()
    br_data = get_barcode_data()
    # start tour or shutdown himself
    if br_data == "yes":
        if there_was_tour:
            prepare_for_tour()
            play_mp3_file("/home/pi/play_text_and_sounds/want_to_start_the_tour.mp3")
            br_data=0
            while br_data !="yes" and br_data!="no":
                br_data = get_barcode_data()
                if br_data == "no":
                    shutdown_rp()
                elif br_data !="yes" and br_data!="no":
                    play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
        start_tour()
        if not low_battery_power_event.is_set():
            # all ok, choose if to start another tour
            play_mp3_file("/home/pi/play_text_and_sounds/another_tour.mp3")
        there_was_tour = True
    elif br_data == "same" and there_was_tour == True:
        start_tour()
        if not low_battery_power_event.is_set():
            play_mp3_file("/home/pi/play_text_and_sounds/another_tour.mp3")
    elif br_data == "no":
        shutdown_rp()
    elif br_data == "init_admin":
        start_test_time = datetime.datetime.now()
        drive_to_end_and_back()
        end_test_time=datetime.datetime.now()
        difference=end_test_time-start_test_time
        difference=math.ceil(difference.seconds/120)

        play_mp3_file("/home/pi/play_text_and_sounds/save_init_admin_result.mp3")
        br_data=0
        while br_data !="yes" and br_data!="no":
            br_data=get_barcode_data()
            if br_data== "yes":
                try:
                    with open("/home/pi/final_code/time_takes_drive_from_start_to_finish.txt", "w") as file:
                        # Writing data to a file
                        file.write(str(difference))
                except IOError as e:
                    print(e)
                shutdown_rp()
            elif br_data!="no":
                play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")
        if not low_battery_power_event.is_set():
            play_mp3_file("/home/pi/play_text_and_sounds/want_to_start_the_tour.mp3")
    else:
        play_mp3_file("/home/pi/play_text_and_sounds/barcode_not_valid.mp3")

print("main closed")

