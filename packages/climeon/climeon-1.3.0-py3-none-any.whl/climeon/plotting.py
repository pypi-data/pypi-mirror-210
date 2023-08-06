"""Climeon plotting utilities."""

# Standard modules
import math

# External modules
from pandas import DataFrame
from plotly.graph_objects import Scattergl
from plotly.subplots import make_subplots
from plotly_resampler import FigureResampler, FigureWidgetResampler, \
    EveryNthPoint

DEFAULT_HEIGHT = 900

STATES = [
    "INIT",
    "IDLE",
    "READY",
    "START",
    "RUNNING",
    "STOP",
    "MANUAL",
    "",
    "NOT_AVAILABLE",
    "TIMEOUT"
]

START_STATES = [
    "INIT",
    "AWAIT_COLD_WATER",
    "START_DT",
    "START_MAIN_PUMP",
    "AWAIT_HOT_WATER",
    "PHT_FLUSH_COOLING",
    "PHT_HEAT_UP_GAS",
    "PHT_HEAT_UP_COILS",
    "PHT_HEAT_UP_TURBINE",
    "PHT_DEC_BOOSTER",
    "COND_BEAR",
    "START_TURBINE",
    "PRE_COND_TURBINE",
    "AWAIT_TURBINE_SPEED",
    "START_BOOSTER_PUMP",
    "RAMP_UP_TURBINE",
    "AWAIT_START_SPEED"
]

STATUS_WORD = [
    "READY",
    "IDLE",
    "STARTING",
    "RUNNING",
    "STOPPING",
    "PLANNED_STOP",
    "UNPLANNED_STOP",
    "TIMEOUT",
    "LIMPMODE",
    "", # VACANT
    "", # VACANT
    "", # ALARM
    "", # CRITICAL_ALARM
    "", # EMERGENCY_ALARM
    "", # WARNING
    "", # VACANT
    "TURBINE_RUN",
    "MAIN_PUMP_RUN",
    "BOOSTER_PUMP_RUN",
    "BOOSTER_VALVE_OPEN",
    "COOLING_VALVE_OPEN",
    "", # VACANT
    "ATU_EVACUATING",
    "", # VACANT
    "", # DRAIN_VALVE_OPEN
    "", # SPRAY_VALVE_OPEN
    "", # GAS_VALVE_OPEN
    "", # EXHAUST_VALVE_OPEN
    "", # VACANT
    "", # VACANT
    "", # VACANT
    "REMOTE_CONTROL"
]

STATE_MAP = {
    "State [-]": STATES,
    "StartState [-]": START_STATES,
    "StatusWord [-]": STATUS_WORD
}

def add_transition(fig, data, variable, color="blue", template="%s", pos=1):
    """Add status transitions for a specific variable in a plotly figure."""
    # pylint: disable=too-many-arguments
    if variable not in data:
        return
    states = STATE_MAP[variable] if variable in STATE_MAP else None
    edges = data[abs(data[variable].diff()) > 0][variable].astype(int)
    for idx, (timestamp, state) in enumerate(zip(edges.index, edges)):
        if state == 0:
            continue
        if variable in ["StatusWord [-]", "SecondaryStatusWord [-]"] and idx > 0:
            bit = int(state ^ edges[idx-1]).bit_length() - 1
            if not (state >> bit) & 1 or not states[bit]:
                continue
            text = "%s" % states[bit]
        elif states and not states[state]:
            continue
        elif states:
            text = template % states[state]
        elif "%s" in template:
            text = template % state
        else:
            text = template
        fig.add_vline(x=timestamp, line_width=1, line_dash="dash", line_color=color)
        fig.add_annotation(x=timestamp, y=pos, text=text, yref="paper")

def add_transitions(fig, data):
    """Add all possible state transitions.

    Parameters:
        fig (figure):       A plotly figure.
        data (DataFrame):   A pandas dataframe with data.
    """
    # pylint: disable=too-many-arguments
    add_transition(fig, data, "State [-]", pos=0.96)
    add_transition(fig, data, "AlarmCode [-]", "red", "AlarmCode %s", 1.04)
    add_transition(fig, data, "NoOfGreasingCyclesFrontBearing [-]", template="Front greasing")
    add_transition(fig, data, "NoOfGreasingCyclesRearBearing [-]", template="Rear greasing")
    add_transition(fig, data, "NoOfAtuCycles [-]", "green", "ATU", 1.02)
    if "State [-]" not in data:
        add_transition(fig, data, "StatusWord [-]", pos=0.96)
    if "Wetgas detected [-]" in data:
        color_code(fig, data["Wetgas detected [-]"], [None, "red"])
    elif "SecondaryStatusWord [-]" in data:
        wet_gas = (data["SecondaryStatusWord [-]"].dropna().astype(int) & (1 << 10) > 0) * 1
        color_code(fig, wet_gas, [None, "red"])

def color_code(fig, state, colors, text=""):
    """Color code the background of a plot based on state."""
    state_notnull = state.fillna(False)
    state_changes = state_notnull[state_notnull.diff() != 0]
    for idx, timestamp in enumerate(state_changes.index):
        if idx == len(state_changes) - 1:
            end_idx = state.index[-1]
        else:
            end_idx = state_changes.index[idx + 1]
        color = colors[int(state_changes[timestamp])]
        if color is not None:
            fig.add_vrect(timestamp, end_idx, annotation_text=text,
                          fillcolor=color, opacity=0.2, line_width=0)

def get_figure(rows=1, secondary_y=True, resampler=False, height=DEFAULT_HEIGHT):
    """Convenience function for creating a plotly figure.

    Parameters:
        rows (int): Amount of plot rows to include (subplots).
        secondary_y (bool): Indicates if secondary y-axis should be enabled.
        resampler (bool): Indicates if resampling should be done dynamically
                          to improve loading times.
        height (int): Figure height.
    """
    specs = [[{"secondary_y": secondary_y}] for _ in range(rows)]
    fig = make_subplots(rows, 1, shared_xaxes=True, vertical_spacing=0.02, specs=specs)
    if resampler:
        if is_notebook():
            fig = FigureWidgetResampler(fig)
        else:
            fig = FigureResampler(fig)
    fig.update_layout(hovermode="x", height=height)
    fig.update_traces(mode="lines", hovertemplate=None)
    return fig

def standard_plot(data, resampler=True, height=DEFAULT_HEIGHT):
    """Create a plot with state transitions and useful variables."""
    # pylint: disable=too-many-statements
    fig = get_figure(rows=2, resampler=resampler, height=height)

    # 1st plot: Power and Control with state transitions
    # 1st axis [kW], [%]
    add_trace(fig, data, "PowerOutput [kW]", 1)
    add_trace(fig, data, "AV25Pos [%]", 1)
    add_trace(fig, data, "AV26Pos [%]", 1)
    add_trace(fig, data, "Fcp91Speed [%]", 1)
    add_trace(fig, data, "Fcp92Speed [%]", 1)

    # 2nd axis [rpm]
    add_trace(fig, data, "TurbSpeed [rpm]", 1, secondary_y=True)

    # 2nd plot: Variables galore
    # 1st axis [deg C]

    # Hot side
    add_trace(fig, data, "T38 [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "T39 [deg C]", 2, visible="legendonly")
    data["HX DT [deg C]"] = data["T38 [deg C]"] - data["T39 [deg C]"]
    add_trace(fig, data, "HX DT [deg C]", 2, visible="legendonly")
    if "T42 [deg C]" in data:
        lower_gas = data["T33 [deg C]"].fillna(data["T42 [deg C]"])
        upper_gas = data["T51 [deg C]"].fillna(data["T54 [deg C]"])
        data["Gas [deg C]"] = DataFrame([lower_gas, upper_gas]).min()
    else:
        data["Gas [deg C]"] = data["T33 [deg C]"]
    if "HxCalcBoilingPoint [deg C]" in data:
        boil = data["HxCalcBoilingPoint [deg C]"]
    else:
        boil = 1219.97 / (7.1327 - (data["P74 [bar]"] / 0.00133322).apply(math.log10)) - 230.653
    data["SuperHeat [deg C]"] = data["Gas [deg C]"] - boil
    data["DT Gas [deg C]"] = data["T38 [deg C]"] - data["Gas [deg C]"]
    add_trace(fig, data, "Gas [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "SuperHeat [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "DT Gas [deg C]", 2, visible="legendonly")

    # Cold side
    add_trace(fig, data, "T36 [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "T37 [deg C]", 2, visible="legendonly")
    data["CX DT [deg C]"] = data["T37 [deg C]"] - data["T36 [deg C]"]
    data["Pinch [deg C]"] = data["T35 [deg C]"] - data["T36 [deg C]"]
    add_trace(fig, data, "CX DT [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "Pinch [deg C]", 2, visible="legendonly")

    # Turbine
    if "T43 [deg C]" in data:
        data["Coil [deg C]"] = data[["T43 [deg C]", "T44 [deg C]", "T45 [deg C]"]].max(axis=1)
        add_trace(fig, data, "Coil [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "T46 [deg C]", 2, visible="legendonly")
    add_trace(fig, data, "T47 [deg C]", 2, visible="legendonly")

    # 2nd axis [bar], [-]
    data["TurbPressDiff [bar]"] = data["P74 [bar]"] - data["P71 [bar]"]
    data["TurbPressRatio [-]"] = data["P74 [bar]"] / data["P71 [bar]"]
    data["Cushion [bar]"] = data["Cushion [mbar]"] / 1000
    if "P81 [bar]" in data:
        data["CX DP water [bar]"] = data["P79 [bar]"] - data["P81 [bar]"]
    data["CX DP media [bar]"] = data["P101 [bar]"] - data["P77 [bar]"]
    data["FCP91 DP [bar]"] = data["P101 [bar]"] - data["P72 [bar]"]
    data["Condenser DP [bar]"] = data["P77 [bar]"] - data["P71 [bar]"]
    add_trace(fig, data, "TurbPressDiff [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "TurbPressRatio [-]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "Cushion [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "P71 [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "CX DP water [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "CX DP media [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "FCP91 DP [bar]", 2, visible="legendonly", secondary_y=True)
    add_trace(fig, data, "Condenser DP [bar]", 2, visible="legendonly", secondary_y=True)

    fig["layout"]["yaxis"]["title"] = "[kW], [%]"
    fig["layout"]["yaxis2"]["title"] = "[rpm]"
    fig["layout"]["yaxis2"]["showgrid"] = False
    fig["layout"]["yaxis2"]["zeroline"] = False
    fig["layout"]["yaxis3"]["title"] = "[deg C]"
    fig["layout"]["yaxis4"]["title"] = "[bar], [-]"
    fig["layout"]["yaxis4"]["showgrid"] = False
    fig["layout"]["yaxis4"]["zeroline"] = False

    add_transitions(fig, data)
    return fig

def add_trace(fig, data, variable, row=1, visible=None, secondary_y=False):
    """Add a trace to a resampled plotly figure."""
    # pylint: disable=too-many-arguments
    if not variable in data:
        return
    if isinstance(fig, FigureWidgetResampler):
        trace = Scattergl(name=variable, visible=visible)
        fig.add_trace(trace, row=row, col=1, secondary_y=secondary_y,
                      hf_x=data.index, hf_y=data[variable].values,
                      downsampler=EveryNthPoint(interleave_gaps=False))
    else:
        trace = Scattergl(x=data.index, y=data[variable].values, name=variable,
                          visible=visible)
        fig.add_trace(trace, row=row, col=1, secondary_y=secondary_y)

def is_notebook():
    """Check if code is running in a notebook."""
    try:
        get_ipython()
        return True
    except NameError:
        return False
