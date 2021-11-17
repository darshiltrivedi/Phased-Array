import adi
from functions import *
from project_config import *


def main():
    # This Main function would be eventually function of GUI
    # all other things will be called inside the GUI
    # Select and connect the Transreciever
    if "adf4159" in tx_source:
        pll = adi.adf4159(uri=rpi_ip)
        if sw_tx == 2:
            sdr = adi.ad9361(uri=lo_ip)
        else:
            sdr = adi.Pluto(uri=lo_ip)
        sdr_init(sdr, pll)

    elif "pluto" in tx_source:
        if sw_tx == 2:
            sdr = adi.ad9361(uri=lo_ip)
            sdr_init(sdr, sdr)
        else:
            sdr = adi.Pluto(uri=lo_ip)
            sdr_init(sdr, sdr)

    else:
        raise Exception("Please select appropriate transmitter source. Valid options 'pluto' or 'adf4159'")

    # channel 4 is the third, and channel 3 is the fourth
    # Select and connect the Beamformer/s. Each Beamformer has 4 channels
    if sw_tx == 2:
        adar = adi.adar1000_array(
            uri=rpi_ip,
            chip_ids=["BEAM0", "BEAM1"],
            device_map=[[1], [2]],
            element_map=[[1, 2, 3, 4], [5, 6, 7, 8]],
            device_element_map={
                1: [2, 1, 4, 3],
                2: [6, 5, 8, 7],
            },
        )
    else:
        adar = adi.adar1000_array(
            uri=rpi_ip,
            chip_ids=["BEAM0"],
            device_map=[[1]],
            element_map=[[1, 2, 3, 4]],
            device_element_map={
                1: [2, 1, 4, 3]
            },
        )

    beam_list = []  # List of Beamformers in order to steup and configure Individually.
    for device in adar.devices.values():
        beam_list.append(device)

    # initialize the ADAR1000
    for adar in beam_list:
        ADAR_init(adar)  # resets the ADAR1000, then reprograms it to the standard config/ Known state
        ADAR_set_RxTaper(adar)  # Set gain of each channel of all beamformer according to the Cal Values

    cal = input("Do you want to Calibrate the system?")
    if ("yes" or "Yes") in cal:
        Phase_calibration(beam_list, sdr)
        for adar in beam_list:
            ADAR_init(adar)  # resets the ADAR1000, then reprograms it to the standard config/ Known state
            ADAR_set_RxTaper(adar)  # Set gain of each channel of all beamformer according to the Cal Values

    ADAR_Plotter(beam_list, sdr)  # Rx down-converted signal and plot it to get sinc pattern


main()
