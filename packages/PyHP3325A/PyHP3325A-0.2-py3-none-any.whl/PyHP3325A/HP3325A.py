
def _constrain_com_len(val, limit):
    val_str = str(val)
    error = False
    if val > 0:
        if len(val_str) > limit:
            val_str = val_str[:limit]
            error = True
    else:
        if len(val_str) > limit + 1:
            val_str = val_str[:limit + 1]
            error = True
    if error:
        pass
    return val_str


class HP3325A:
    """ module for controlling HP3325A from AR488 GPIb to USB adapter
    written by : Manuel Minutello

    ->  use the functions to set up and read back the instrument"""
    # GPIB command on page 43 of manal

    from PyAR488 import AR488
    _function = {
        'DC': '0',
        'sine': '1',
        'square': '2',
        'triangle': '3',
        'ramp_positive': '4',
        'ramp_negative': '5'
    }

    class Functions:
        class _F:
            def __init__(self, id: int) -> None:
                self.command = f'FU{id}'
        DC = _F(0)
        sine = _F(1)
        square = _F(2)
        triangle = _F(3)
        ramp_up = _F(4)
        ramp_down = _F(5)

    class Units:
        class Amplitude:
            class _U:
                def __init__(self, command: str) -> None:
                    self.command = command
            Vp = _U('VO')
            mV = _U('MV')
            Vrms: _U('VR')
            mVrms: _U('MR')
            dBm: _U('DB')

        class Offset:
            class _U:
                def __init__(self, command: str) -> None:
                    self.command = command
            Vp = _U('VO')
            mV = _U('MV')

    class SweepMode:
        class _U:
            def __init__(self, command: int) -> None:
                self.command = command
        lin = _U(1)
        log = _U(2)

    class Modulation:
        class _M:
            def __init__(self, command: str, state: bool = False) -> None:
                self.state = '1' if state else '0'
                self.command = f'{command} {state}'

        def am(self, state: bool = False):
            return self._M('MA', state)

        def pm(self, state=False):
            return self._M('MP', state)

    class InstrumentState:
        def __init__(self,
                     program_error,
                     frequency,
                     amplitude,
                     offset,
                     phase,
                     sweep_start,
                     sweep_stop,
                     marker_freq,
                     sweep_time,
                     function) -> None:
            self.program_error = program_error
            self.frequency = frequency
            self.amplitude = amplitude
            self.offset = offset
            self.phase = phase
            self.sweep = (sweep_start, sweep_stop)
            self.sweep_time = sweep_time
            self.marker_freq = marker_freq
            self.function = function

    from time import sleep

    def __init__(self, interface: AR488, address, name='HP478A'):
        self.address = address
        self.interface = interface
        self.name = name

    def _write(self, command: str):
        """internal function that changes the interface address before writing on bus"""
        self.interface.address(self.address)
        self.interface.bus_write(command)

    def _query(self, command, payload=False, decode=True):
        """internal function that changes the interface address before query on bus"""
        self.interface.address(self.address)
        self.interface.query(command, payload, decode)

    def clear(self):
        """clear instrument"""
        self._write('DCI')  # todo : test

    # commands
    def set_function(self, function: Functions._F):
        """sets the generator function using builtin type line Functions.sine}"""
        self._write(function.command)

    def set_frequency(self, freq: float):
        """set output frequency in Hz, pay attension to the maximum frequency in each range"""
        freq_str = _constrain_com_len(freq, 11)
        self._write(f'FR {freq_str} HZ')  # also KH or MH valid
        # 7.0 ms for freq setting + 12.5ms for range selection
        self.sleep(0.02)

    def set_amplitude(self, value: float, unit: Units.Amplitude._U = Units.Amplitude._U):
        """set output voltage (50ohm), default unit is Volt. use Units.Amplitude.X where X is dBm, mV, Vrms ecc"""
        value_string = _constrain_com_len(value, 4)
        self._write(f'AM {value_string} {unit.command}')

    def set_offset(self, value: float, unit: Units.Offset._U = Units.Offset.Vp):
        """set output voltage (50ohm), default unit is Volt. use Units.Offset.X where X is V or mV"""
        value_string = _constrain_com_len(value, 4)
        self._write(f'OF {value_string} {unit.command}')

    def set_phase(self, phase: float):  # unit = deg
        """set output phase respect to sync signal, unit is DEG (0-359°)"""
        phase_str = _constrain_com_len(phase, 4)
        self._write(f'PH {phase_str} DE')

    def set_frequency_sweep(self, start_freq: float, stop_freq: float):
        """quick functon so set up a frequenyc sweep with START and STOP values in Hz"""
        start_freq_str = _constrain_com_len(start_freq, 11)
        self._write(f'ST {start_freq_str} HZ')  # also KH or MH valid

        stop_freq_str = _constrain_com_len(stop_freq, 11)
        self._write(f'SP {stop_freq_str} HZ')  # also KH or MH valid

    def set_marker_frequency(self, freq):
        """set marker frequency in Hz"""
        marker_str = _constrain_com_len(freq, 11)
        self._write(f'MF {marker_str} HZ')  # also KH or MH valid

    def set_sweep_time(self, time):
        """set sweep time in s"""
        time_str = _constrain_com_len(time, 4)
        self._write(f'TI {time_str} SE')

    def set_sweep_mode(self, mode: SweepMode._U = SweepMode.lin):
        """set swppe mode, use SweepMode.lin or log"""
        self._write(f'SM {mode.command}')

    def enable_front_panel_output(self):
        """pass the signal output to front panel connector"""
        self._write('RF1')

    def enable_rear_panel_output(self):
        """pass the signal output to rear panel connector"""
        self._write('RF2')

    def store_program(self, reg: int):
        if 0 <= reg <= 9:
            self._write(f'SR {reg}')

    def recall_program(self, reg: int):
        if 0 <= reg <= 9:
            self._write(f'RE {reg}')

    def auto_cal(self):
        """perform auto calibration"""
        self._write('AC')

    def start_single_sweep(self):
        """trigger the start of sweep"""
        self._write('SS')

    def start_continuous_sweep(self):
        """trigger the continuous sweep"""
        self._write('SC')

    def self_test(self):
        """perform self test"""
        self._write('TE')

    def get_instrument_state(self):
        return self.InstrumentState(
            self._query('IER', payload=True),
            self._query('IFR', payload=True),
            self._query('IAM', payload=True),
            self._query('IOF', payload=True),
            self._query('IPH', payload=True),
            self._query('IST', payload=True),
            self._query('ISP', payload=True),
            self._query('IMF', payload=True),
            self._query('ITI', payload=True),
            self._query('IFU', payload=True)
        )

    def enable_hv_output(self, state=True):
        """enable high voltage output option"""
        self._write(f'HV {1 if state else 0}')

    def set_modulation(self, mod: Modulation._M):
        """set modulation as Modulation.am(True) to enable AM modulation and False to disable"""
        self._write(mod.command)
