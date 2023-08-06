import os
from datetime import date
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot as plt
import platform
import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from covidcast import plotting


CURRENT_PATH="./tests"


def _convert_to_array(fig: matplotlib.figure.Figure) -> np.array:
    """Covert Matplotlib Figure into an numpy array for comparison."""
    return np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)  # get np array representation


def _convert_from_array(arr: np.array) -> matplotlib.figure.Figure:
    fig = plt.figure()
    ax = fig.add_subplot(111, frameon=False)
    ax.imshow(arr)
    return fig

def save_actual_expected(name, act, exp):
    fig = _convert_from_array(act)
    plt.savefig("{name}.actual.png")
    fig = _convert_from_array()
    plt.savefig("{name}.expected.png")

def run_test_plot():
    matplotlib.use("agg")
    # load expected choropleth as an array
    expected = np.load(os.path.join(CURRENT_PATH, "reference_data/expected_plot_arrays.npz"))

    # test county plots
    test_county = pd.read_csv(
        os.path.join(CURRENT_PATH, "reference_data/test_input_county_signal.csv"), dtype=str)
    test_county["time_value"] = test_county.time_value.astype("datetime64[D]")
    test_county["value"] = test_county.value.astype("float")

    # w/o megacounties
    no_mega_fig1 = plotting.plot(test_county,
                                 time_value=date(2020, 8, 4),
                                 combine_megacounties=False)
    
    # give margin of +-2 for floating point errors and weird variations (1 isn't consistent)
    save_actual_expected("no_mega_1", _convert_to_array(no_mega_fig1), expected["no_mega_1"])

    no_mega_fig2 = plotting.plot_choropleth(test_county,
                                            cmap="viridis",
                                            figsize=(5, 5),
                                            edgecolor="0.8",
                                            combine_megacounties=False)
    save_actual_expected("no_mega_2", _convert_to_array(no_mega_fig2), expected["no_mega_2"])

    # w/ megacounties
    mega_fig = plotting.plot_choropleth(test_county, time_value=date(2020, 8, 4))
    # give margin of +-2 for floating point errors and weird variations (1 isn't consistent)
    save_actual_expected("mega", _convert_to_array(mega_fig), expected["mega"])

    # test state
    test_state = pd.read_csv(
        os.path.join(CURRENT_PATH, "reference_data/test_input_state_signal.csv"), dtype=str)
    test_state["time_value"] = test_state.time_value.astype("datetime64[D]")
    test_state["value"] = test_state.value.astype("float")
    state_fig = plotting.plot(test_state)
    save_actual_expected("state", _convert_to_array(state_fig), expected["state"])

    # test MSA
    test_msa = pd.read_csv(
        os.path.join(CURRENT_PATH, "reference_data/test_input_msa_signal.csv"), dtype=str)
    test_msa["time_value"] = test_msa.time_value.astype("datetime64[D]")
    test_msa["value"] = test_msa.value.astype("float")
    msa_fig = plotting.plot(test_msa)
    save_actual_expected("msa", _convert_to_array(msa_fig), expected["msa"])

    # test bubble
    msa_bubble_fig = plotting.plot(test_msa, plot_type="bubble")
    from matplotlib import pyplot as plt
    save_actual_expected("msa_bubble",_convert_to_array(msa_bubble_fig), expected["msa_bubble"])

run_test_plot()
