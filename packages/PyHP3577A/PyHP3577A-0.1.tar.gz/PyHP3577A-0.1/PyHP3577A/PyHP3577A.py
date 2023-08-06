class HP3577A:
    from PyAR488 import AR488

    """ module for controlling HP3577A from AR488 GPIb to USB adapter
        written by : Manuel Minutello"""

    class Inputs:
        class _I:
            def __init__(self, name: str, cmd: str) -> None:
                self.cmd = cmd
                self.name = name

        R = _I("R", "INR")
        A = _I("A", "INA")
        B = _I("B", "INB")
        A_R = _I("A/R", "A/R")
        B_R = _I("B/R", "B/R")
        D1 = _I("D1", "DI1")
        D2 = _I("D2", "DI2")
        D3 = _I("D3", "DI3")
        D4 = _I("D4", "DI4")
        user_defined = _I("UDI", "UDI")

        class _S:
            def __init__(self, cmd: str) -> None:
                self.cmd = cmd

        S11 = _S("I11")
        S21 = _S("I21")
        S12 = _S("I12")
        S22 = _S("I22")


    class Measurement:
        class _M:
            def __init__(self, cmd: str) -> None:
                self.cmd = cmd

        log_mag = _M("DF7")
        lin_mag = _M("DF6")
        phase = _M("DF5")
        polar = _M("DF4")
        real = _M("DF3")
        imaginary = _M("DF2")
        delay = _M("DF1")


    class MarkerGoTo:
        class _M:
            def __init__(self, cmd: str) -> None:
                self.cmd = cmd

        reference_level = _M("MTR")
        start_frequency = _M("MTA")
        stop_frequency = _M("MTB")
        center_frequency = _M("MTC")
        min = _M("MTN")
        max = _M("MTX")
        full_scale = _M("MTP")
        polar_phase_ref = _M("MPF")

    class SuffixUnit:
        class _U:
            def __init__(self, cmd:str) -> None:
                self.cmd = cmd
        dBm = _U("DBM")
        dBV = _U("DBV")
        dB_rel = _U("DBR")
        V = _U("V")
        mV = _U("MV")
        uV = _U("UV")
        nV = _U("NV")
        deg = _U("DEG")
        deg_span = _U("DSP")
        rad = _U("RAD")
        rad_span = _U("RSP")
        seconds = _U("SEC")
        ms = _U("MSC")
        us = _U("USC")
        ns = _U("NSC")
        percent = _U("%")
        MHz = _U("MHZ")
        kHz = _U("KHZ")
        Hz = _U("HZ")
        exp = _U("E")
        m = _U("MET")
        cm = _U("CM")
        
        _display_valid_suffixes = (dBm, dBV, dB_rel, V, mV, uV, nV, deg, deg_span, rad, rad_span, seconds, ms, us, ns, percent, MHz, kHz, Hz, exp)
        _source_valid_suffixes = (dBm, dBV, V, mV, uV, nV, seconds, ms, MHz, kHz, Hz, exp)
        _receiver_valid_suffixes = (m, cm, seconds, ms, us, ns, exp)

    class SweepType:
        class _S:
            def __init__(self, cmd: str) -> None:
                self.cmd = cmd

        linear = _S("ST1")
        alternate = _S("ST2")
        log = _S("ST3")
        amplitude = _S("ST4")
        cw = _S("ST5")
        discrete = _S("ST6")

    class SweepMode:
        class _SM:
            def __init__(self, cmd: str) -> None:
                self.cmd = cmd

        continuous = _SM("SM1")
        single = _SM("SM2")
        manual = _SM("SM3")
    
    class TriggerMode:
        class _T:
            def __init__(self, cmd:str) -> None:
                self.cmd = cmd
        
        free_run = _T("TG1")
        line = _T("TG2")
        external = _T("TG3")
        immediate = _T("TG4")

    def __init__(self, gpib_id: int, interface: AR488, name="HP3577A"):
        self.gpib_id = gpib_id
        self.interface = interface
        self.name = name

    def address(self):
        self.interface.address(self.gpib_id)

    def _write(self, msg: str):
        self.address()
        self.interface.bus_write(msg)

    def _query(self, msg: str, payload: bool = False, decode: bool = True):
        self.address()
        return self.interface.query(msg, payload=payload, decode=decode)

    def device_clear(self):
        self._write("DCL")

    def go_to_local(self):
        self._write("GTL")

    def select_input(self, channel: Inputs._I):
        self._write(channel.cmd)

    def select_s_measurement(self, s_measurement: Inputs._S):
        self._write(s_measurement.cmd)

    def enable_s_param(self, state: bool = True):
        self._write(f"SP{int(state)}")

    def select_measurement(self, measurement: Measurement._M):
        self._write(measurement.cmd)

    def enable_smith_chart(self, state: bool = True):
        self._write(f"GT{int(state)}")

    def enable_trace(self, state: bool = True):
        self._write(f"DF{int(state)}")

    def test_set_forward(self, direction: bool = True):
        if direction:
            self._write("TSF")
        else:
            self._write("TSR")

    def select_trace(self, trace: int):
        if 1<=trace<=2:
            self._write(f"TR{trace}")
        else:
            raise Exception(f"{trace} is not a valid trace")

    # scale
    def autoscale(self):
        self._write("ASL")

    def set_scale(self, val, unit):
        self._send_if_valid_unit("DIV", val, unit, self.SuffixUnit._display_valid_suffixes)

    # reference line
    def reference_line_level(self, val, unit):
        self._send_if_valid_unit("REF", val, unit, self.SuffixUnit._display_valid_suffixes)

    def set_reference_pos(self, val, unit):
        self._send_if_valid_unit("RPS", val, unit, self.SuffixUnit._display_valid_suffixes)

    def reference_line_enable(self, state: bool = True):
        self._write(f"RL{int(state)}")

    # phase slope
    def phase_slope_set_value(self, val, unit):
        self._send_if_valid_unit("PSL", val, unit, self.SuffixUnit._display_valid_suffixes)

    def phase_slope_enable(self, state: bool = True):
        self._write(f"PS{int(state)}")

    # marker
    def marker_set_position(self, val, unit):
        self._send_if_valid_unit("MKP", val, unit, self.SuffixUnit._display_valid_suffixes)

    def marker_enable(self, state: bool = True):
        self._write(f"MR{int(state)}")

    def marker_zero(self):
        self._write("ZMK")

    # marker offset
    def marker_enable_offset(self, state: bool = True):
        self._write(f"MO{int(state)}")

    def marker_set_offset(self, val, unit):
        self._send_if_valid_unit("MKO", val, unit, self.SuffixUnit._display_valid_suffixes)

    def marker_set_offset_frequency(self, val, unit):
        self._send_if_valid_unit("MOF", val, unit, self.SuffixUnit._display_valid_suffixes)

    def marker_set_offset_amplitude(self, val, unit):
        self._send_if_valid_unit("MOA", val, unit, self.SuffixUnit._display_valid_suffixes)

    def marker_enable_coupling(self, state: bool = True):
        self._write(f"CO{int(state)}")

    # polar graph control
    def polar_set_mag_offset(self, val, unit):
        self._send_if_valid_unit("PMO", val, unit, self.SuffixUnit._display_valid_suffixes)

    def polar_set_phase_offset(self, val, unit):
        self._send_if_valid_unit("PPO", val, unit, self.SuffixUnit._display_valid_suffixes)

    def polar_set_real_offset(self, val, unit):
        self._send_if_valid_unit("PRO", val, unit, self.SuffixUnit._display_valid_suffixes)

    def polar_set_img_offset(self, val, unit):
        self._send_if_valid_unit("PIO", val, unit, self.SuffixUnit._display_valid_suffixes)

    def polar_set_marker_units_re_img(self, val, unit):
        self._send_if_valid_unit("MRI", val, unit, self.SuffixUnit._display_valid_suffixes)

    def polar_set_marker_units_mg_ph(self, val, unit):
        self._send_if_valid_unit("MMP", val, unit, self.SuffixUnit._display_valid_suffixes)

    # quick markers
    def marker_go_to(self, snap_type: MarkerGoTo._M):
        self._write(snap_type.cmd)

    def marker_offset_equal_span(self):
        self._write("MOS")

    def marker_threshold(self, val, unit):
        self._send_if_valid_unit("MTV", val, unit, self.SuffixUnit._display_valid_suffixes)

    def marker_move_next(self):
        self._write("MLT")

    def marker_move_previous(self):
        self._write("MRT")

    # calibration
    def cal_normalize(self):
        self._write("NRM")

    def cel_normalize_short(self):
        self._write("NRS")

    def cal_partial(self):
        self._write("CPR")

    def cal_full(self):
        self._write("CFL")

    def cal_continue(self):
        self._write("CGO")

    # source control
    def sweep_type(self, mode: SweepType._S):
        self._write(mode.cmd)

    def sweep_mode(self, mode:SweepMode._SM):
        self._write(mode.cmd)

    def sweep_time(self, val, unit):
        self._send_if_valid_unit("SWT", val, unit, self.SuffixUnit._source_valid_suffixes)

    def sweep_step_time(self, val, unit):
        self._send_if_valid_unit("SMT", val, unit, self.SuffixUnit._source_valid_suffixes)

    def sweep_sample_time(self, val, unit):
        self._send_if_valid_unit("MSR", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_cw_frequency(self, val, unit):
        self._send_if_valid_unit("SFR", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_start_frequency(self, val, unit):
        self._send_if_valid_unit("FRA", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_stop_frequency(self, val, unit):
        self._send_if_valid_unit("FRB", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_center_frequency(self, val, unit):
        self._send_if_valid_unit("FRC", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_span_frequency(self, val, unit):
        self._send_if_valid_unit("FRS", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_frc_step_size(self, val):
        self._write(f"CFS {val}")

    def set_sweep_resolution(self, val:int):
        """set sweep steps (reoslution) in levels from 1 to 4 = 51, 101, 201, 401 steps"""
        if 1 <= val <= 4:
            self._write(f'RS{val}')
        else:
            raise Exception(f'{val} is not a valid sweep resolution')

    def sweep_full(self):
        self._write("FSW")

    def source_frequency_step_size(self, val, unit):
        self._send_if_valid_unit("FST", val, unit, self.SuffixUnit._source_valid_suffixes)

    # amplitude control
    def source_amplitude(self, val, unit):
        self._send_if_valid_unit("SAM", val, unit, self.SuffixUnit._source_valid_suffixes)

    def amplitude_step_size(self, unit, val):
        self._send_if_valid_unit("AST", val, unit, self.SuffixUnit._source_valid_suffixes)

    def source_clear_trip(self):
        self._write("CTS")
    
    def source_amplitude_sweep_range(self, start, stop, unit):
        self._send_if_valid_unit("AMA", start, unit, self.SuffixUnit._source_valid_suffixes)
        self._send_if_valid_unit("AMB", stop, unit, self.SuffixUnit._source_valid_suffixes)

    def sorce_amplitude_step(self, val):
        """set amplitude sweep steps (reoslution) in levels from 1 to 7 = 6, 11, 21, 51, 101. 201, 401 steps"""
        if 1 <= val <= 7:
            self._write(f'NS{val}')
        else:
            raise Exception(f'{val} is not a valid amplitude step value')

    # trigger
    def trigger_mode(self, new_trigger:TriggerMode._T):
        self._write(new_trigger.cmd)

    # receiver
    def receiver_rbw(self, val):
        """set receiver resolution bandwith in levels from 1 to 4 = 1Hz, 10Hz, 100Hz, 1kHz"""
        if 1 <= val <= 4:
            self._write(f'BW{val}')
        else:
            raise Exception(f'{val} is not a valid receiver resolution bandwith')

    def receiver_rbw_auto(self, state: bool = True):
        self._write(f"AU{int(state)}")

    def receiver_averaging_number(self, N:int):
        """sets averaging number N form 0 to 7 where the number is 2^N"""
        if 0<=N<=7:
            self._write(f'AV{N}')

    def receriver_chanenl_20dB_attenuation(self, channel:Inputs._I, enable:bool = True):
        if channel.name in ('A', 'B', 'R'):
            self._write(f'A{channel.name}{int(enable)+1}')
        else:
            raise Exception('ivnalid input channel, inly hardware input channels can have attenuation')

    def receiver_channel_1Meg_impedance(self, channel:Inputs._I, enable:bool = True):
        if channel.name in ('A', 'B', 'R'):
            self._write(f'I{channel.name}{int(enable)+1}')
        else:
            raise Exception('ivnalid input channel, inly hardware input channels can have input impedance contorl')

    def receiver_clear_trip(self):
        self._write("CRT")

    # length
    def set_chanel_length(self, channel:Inputs._I, val, unit:SuffixUnit._U):
        if channel.name in ('A', 'B', 'R'):
            self._send_if_valid_unit(f'LN{channel.name}', val, unit, self.SuffixUnit._receiver_valid_suffixes)
        else:
            raise Exception(f'{channel.name} can not be length compensated, only phisican channels can')

    def receiver_channel_legnth_enable(self, channel:Inputs._I, state: bool):
        if channel.name in ('A', 'B', 'R'):
            self._write(f'L{channel.name}{int(state)}')
        else:
            raise Exception(f'{channel.name} can not be length compensated, only phisican channels can')

    # diagnostic

    def beeper_enable(self, state: bool):
        self._write("BP1" if state else "BP0")

    def preset(self):
        self._write("IPR")

    # plot
    def plot_all(self, acquire:bool = True):
        cmd = 'PLA'
        if acquire:
            return self._query(cmd, payload=True)
        else:
            self._write(cmd)
        
    def plot_trace(self, trace: int, acquire:bool = True):
        if 1 <= trace <= 2:
            cmd = f"PL{trace}"
            if acquire:
                return self._query(cmd,payload=True)
            else:
                self._write(cmd)
        else:
            raise Exception('invalid trace "{}"'.format(trace))

    def plot_graticule(self, acquire:bool = True):
        cmd = 'PLG'
        if acquire:
            return self._query(cmd, payload=True)
        else:
            self._write(cmd)

    def plot_characteristic(self, acquire:bool = True):
        cmd = 'PLC'
        if acquire:
            return self._query(cmd, payload=True)
        else:
            self._write(cmd)

    def plot_trace_marker(self, trace: int, acquire:bool = True):
        if 1 <= trace <= 2:
            cmd = f"PM{trace}"
            if acquire:
                return self._query(cmd, payload=True)
            else:
                self._write(cmd)
        else:
            raise Exception(f'{trace} is not a valid trace')

    def plot_config_trace_linetype(self, trace: int, line_type:int):
        if 0 <= line_type <= 7:
            if 1<=trace<=2:
                self._write(f"T{trace}L{line_type}")
            else:
                raise Exception(f'{trace} is not a valid trace')
        else:
            raise Exception(f'{line_type} is not a valid line typoe, valid 0->7')

    def plot_config_trace_pen(self, trace: int, pen_number:int):
        if 1 <= trace <= 2:
            if 0<=pen_number<=8:
                self._write(f"T{trace}P{pen_number}")
            else:
                raise Exception(f'{pen_number} is not a valid pen number (0->8)')
        else:
            raise Exception(f'{trace} is not a valid trace')

    def plot_config_pen_graticulate(self, pen_number:int):
        if 0<=pen_number<=8:
            self._write(f'PGP{pen_number}')
        else:
            raise Exception(f'{pen_number} is not a valid pen number (0->8)')

    def plot_config_pen_speed_fast(self, fast: bool = True):
        self._write("PNM" if fast else "PNS")

    def plot_config_reset(self):
        self._write("PLD")

    def plot_config_set_plotter_address(self, addr: int):
        if 0 <= addr <= 30:
            self._write("HPB {}".format(addr))
        else:
            raise Exception('invalid GPIB address "{}"'.format(addr))

    # HPIB only commands
    def get_input_register_dump(self, reg: Inputs._I):
        if reg.name in ("A", "B", "R", "D1", "D2", "D3", "D4"):
            return self._query(f'DD{reg}', payload=True)
        else:
            raise Exception(f'invalid trace {reg}')

    def get_trace_dump(self, trace: int):
        if 1 <= trace <= 2:
            return self._query(f"DT{trace}", payload=True)
        else:
            raise Exception(f'invalid trace {trace}')

    def get_marker_dump(self, marker):
        if 1 <= marker <= 2:
            return self._query(f"DM{marker}", payload=True)
        else:
            raise Exception(f'invalid marker {marker}')

    def get_marker_position(self, marker):
        if 1 <= marker <= 2:
            return self._query(f"DM{marker}", payload=True)
        else:
            raise Exception(f'invalid marker {marker}')

    def get_instrument_status(self):
        return self._query("DMS", payload=True)

    def get_agerage_n(self):
        return self._query("DAN", payload=True)

    def get_instrument_charachteristics(self):
        return self._query("DCH", payload=True)

    def get_id(self):
        return self._query("ID?", payload=True)

    def graticulate_enable(self, state: bool = True):
        self._write(f"GR{int(state)}")

    def charachters_enable(self, state: bool = True):
        self._write(f"CH{int(state)}")

    def annotation_enable(self, state: bool = True):
        self._write(f"AN{int(state)}")

    def annotation_clear(self):
        self._write("ANC")

    def menu_enable(self, state: bool):
        self._write("MN1" if state else "MN0")

    def measurement_take(self):  # todo : verificare se ha payload
        self._write("TKM")

    # -------------------------
    def _send_if_valid_unit(self, command:str, value, unit:SuffixUnit._U, valid_units:tuple):
        if unit in valid_units:
            self._write(f"{command} {value} {unit.cmd}")
        else:
            raise Exception(f'{unit} is not a valid unit')
