# Raspberry Pi Pico Open Source DC Load with OLED Display

This project is an open-source DC load built using a Raspberry Pi Pico microcontroller and an OLED display. It allows users to simulate different loads on power sources, monitor voltage, current, and other parameters, and display them on an OLED screen.

## Features

- Simulate various loads on DC power sources.
- Measure voltage, current, and other parameters.
- Display real-time data on an OLED screen.
- Open-source design using Raspberry Pi Pico.
- Mine does a maximum 36V and around 7A, max power around 100W

## Requirements

- Raspberry Pi Pico microcontroller with circuitpython (you can use the one provided in this repo, i would recommend downloading the newest `.uf2`file from [here](https://circuitpython.org/board/raspberry_pi_pico/)`) A Raspberry Pi Pico will work as well but would be wasted!
- OLED SSD 1306
- Rotary Encoder
- Big Power Resistor
- 2 Mosfets
- Big Mosfet Heatsink
- 5V Linear Regulator
- Resistors, capacitors, diodes and other electronic components (refer to the schematic or for details) The values are just approximate! Your values will limit the maximum voltage for the voltage dividers as the Raspberry Pi Pico has a max ADC voltage of 3,3V. The capacitor choice will also affect the maximum input voltage.
- Soldering iron and solder
- PCB (from JLCPCB or other manufactures, I got mine for 5€)

## Installation

1. `git clone https://github.com/HeyJoFlyer/open-pico-load.git`.

2. Connect the components based on the schematic provided (`schematic.svg`).
![alt text](https://github.com/HeyJoFlyer/open-pico-load/raw/schematic.svg "Logo Title Text 1")

4. Flash the Circuitpython firmware onto the Raspberry Pi Pico.

5. Upload the code and the libraries (which only work for Circuipython 8.x) to the Pico with the file explorer.

## Usage

1. Connect the Board to a DC power source (7-25V, assuming your fan supports that voltage).

1. Connect your load you want to observe using the screw terminal or solder it directly.

1. Adjust the load settings using the rotary encoder.

1. Monitor the voltage, current, and power on the OLED display.

1. Use the load to test different power sources and observe their behavior.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
Circuipython and the libraries included are licensed under the [MIT License](LICENSE).
