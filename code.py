# SPDX-FileCopyrightText: 2023 HeyJoFlyer
#
# SPDX-License-Identifier: MIT
import time
import displayio
import adafruit_displayio_ssd1306 #seperate libarary needs to be installed
import terminalio
from adafruit_display_text import label
import board
import busio
import digitalio
from pwmio import PWMOut
from analogio import AnalogIn
from rotaryio import IncrementalEncoder #seperate libarary needs to be installed

#If you haven't changed the board, don't change these values
ENCODER_PIN_1 = board.GP3
ENCODER_PIN_2 = board.GP4
FAN_PIN = board.GP1
TACHO_PIN = board.GP0
OK_BUTTON_PIN = board.GP2 #integrated into rotary encoder
BACK_BUTTON_PIN = board.GP8
ON_BUTTON_PIN = board.GP15
LED_R_PIN = board.GP16
LED_G_PIN = board.GP17
SCL_PIN = board.GP21
SDA_PIN = board.GP20
SHUNT_ADC = board.GP26
MOSFET_PIN = board.GP22
VOLTAGE_ADC = board.GP27

MOSFET_FREQUENCY = 100_000 # you can tune this, 100 kHz worked for me
MAX_CURRENT = 8
VOLT_TO_AMP = 2000 / 548 #you need to change this to your own measured value!
VOLT_TO_VOLT = 400000 / 37264 #you need to change this to your own!
CURRENT_OFFSET = -0.05 #you need to change this to your own or set it to zero!
VOLTAGE_OFFSET = -0.10 #you need to change this to your own or set it to zero!

def pin_setup():
    global fan
    global led_r
    global led_g
    global shunt
    global back_button
    global ok_button
    global on_button
    global encoder
    global mosfet
    global voltage_adc
    fan = PWMOut(FAN_PIN, frequency=25000, duty_cycle=0) # 25kHz for fan
    fan.duty_cycle = 0
    mosfet = PWMOut(MOSFET_PIN, frequency=MOSFET_FREQUENCY, duty_cycle=0)
    fan_tacho = digitalio.DigitalInOut(TACHO_PIN) #optional
    fan_tacho.direction = digitalio.Direction.INPUT #optional
    ok_button = digitalio.DigitalInOut(OK_BUTTON_PIN) #integrated into rotary encoder
    ok_button.direction = digitalio.Direction.INPUT #integrated into rotary encoder
    encoder = IncrementalEncoder(ENCODER_PIN_1, ENCODER_PIN_2)
    back_button = digitalio.DigitalInOut(BACK_BUTTON_PIN)
    back_button.direction = digitalio.Direction.INPUT
    back_button.pull = digitalio.Pull.UP
    on_button = digitalio.DigitalInOut(ON_BUTTON_PIN)
    on_button.direction = digitalio.Direction.INPUT
    on_button.pull = digitalio.Pull.UP
    shunt = AnalogIn(SHUNT_ADC)
    voltage_adc = AnalogIn(VOLTAGE_ADC)
    led_r = digitalio.DigitalInOut(LED_R_PIN)
    led_r.direction = digitalio.Direction.OUTPUT
    led_g = digitalio.DigitalInOut(LED_G_PIN)
    led_g.direction = digitalio.Direction.OUTPUT

def get_power(load_enabled):
    if load_enabled == True:
        current = (shunt.value * VOLT_TO_AMP / 65536 * 3.3) + CURRENT_OFFSET
    else:
        current = 0
    if current < 0:
        current = 0
    voltage = (voltage_adc.value * VOLT_TO_VOLT / 65536 * 3.3) + VOLTAGE_OFFSET
    if voltage < 0:
        voltage = 0
    power = "%.4f" % (current * voltage)
    display_voltage = "%.5f" % voltage
    display_current = "%.5f" % current
    return current, display_current, display_voltage, voltage, power

def integrate(voltage, current, old_time, old_voltage, old_current, total_energy, amp_hours): # This function logs and integrates the total power consumption
    integrate_time  = time.time()
    delta_time = (integrate_time - old_time) / 3600
    avg_current = (current + old_current) / 2
    amp_hours_this_cycle = avg_current * delta_time
    amp_hours += amp_hours_this_cycle
    avg_voltage = (old_voltage + voltage) / 2
    energy_this_cycle = amp_hours_this_cycle * avg_voltage
    total_energy += energy_this_cycle
    total_energy_display = "%.4f" % total_energy
    amp_hours_display = "%.4f" % amp_hours
    return integrate_time, voltage, current, total_energy, amp_hours, total_energy_display, amp_hours_display,

def main():
    # display setup
    i2c = busio.I2C(SCL_PIN, SDA_PIN)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    splash = displayio.Group()
    display.root_group = splash
    main_label = label.Label(terminalio.FONT, text = "init", color = 0xFFFFFF)
    splash.append(main_label)
    time.sleep(0.3)
    display.show(splash)

    position = 0
    pwm_value = 0
    encoder_enabled = True
    load_enabled = False
    current_setting = 1 # in Amps
    old_button_time = time.time()
    i = 0

    total_energy = float(0)
    amp_hours = float(0)
    old_time = time.time()
    start_time = time.time()
    old_current, _, _, old_voltage, _ = get_power(False)

    while True:
        last_position = position
        position = encoder.position
        current, display_current, display_voltage, voltage, power = get_power(load_enabled)
        old_time, old_voltage, old_current, total_energy, amp_hours, total_energy_display, amp_hours_display = integrate(voltage, current, old_time, old_voltage, old_current, total_energy, amp_hours)
        if on_button.value == False:
            if time.time() - old_button_time > 1:
                old_button_time = time.time()
                load_enabled = not load_enabled
        if load_enabled == True:
            led_g.value = True
            led_r.value = False
        else:
            led_g.value = False
            led_r.value = True
        if current < current_setting:
            pwm_value += 200
        else:
            pwm_value += -200
        if pwm_value < 0 or load_enabled == False:
            pwm_value = 0
        elif pwm_value > 2 ** 16 - 1:
            pwm_value = 2 ** 16 - 1
        mosfet.duty_cycle = pwm_value
        if encoder_enabled == True and last_position != position:
            current_setting += (position - last_position) / 10
            current_setting = round(current_setting, 1)
            if current_setting < 0:
                current_setting = 0

        if i == 100: # only execute every 100th run
            pwm_value_decimal = round(pwm_value / (2 ** 16), 3)
            text = f"\nTarget I: {current_setting}A, {pwm_value_decimal}\n\
I: {display_current}A, {amp_hours_display}Ah\n\
U: {display_voltage}V, T: {round(time.time() - start_time, 1)}s\n\
P: {power}W, {total_energy_display}Wh"
            main_label.text = text
            i = 0
        i += 1
    


pin_setup()
main()
