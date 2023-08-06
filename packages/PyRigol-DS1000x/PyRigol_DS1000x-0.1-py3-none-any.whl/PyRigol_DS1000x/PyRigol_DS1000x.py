
from math import isclose


class WaveformPreamble:
    def __init__(self, data: str):
        data = data.split(',')

        self.format = data[0]
        if self.format == '0':
            self.format = 'BYTE'
        elif self.format == '1':
            self.format = 'WORD'
        elif self.format == '2':
            self.format = 'ASC'

        self.type = data[1]
        if self.type == '0':
            self.type = 'NORM'
        elif self.type == '1':
            self.type = 'MAX'
        elif self.type == '2':
            self.type = 'RAW'

        # an integer between 1 and 12000000
        self.points = int(data[2])
        # number of averages in the average sample mode and 1 in other modes
        self.count = int(data[3])
        # averages time difference between two neighboring points in the X direction
        self.x_increment = float(data[4])
        # start time of the waveform data in the X direction
        self.x_origin = float(data[5])
        # reference time of the data point in the X direction
        self.x_reference = float(data[6])
        # waveform increment in the Y direction.
        self.y_increment = float(data[7])
        # vertical offset relative to the "Vertical Reference Position" in the Y direction
        self.y_origin = float(data[8])
        # vertical reference position in the Y direction.
        self.y_reference = float(data[9])

    def __repr__(self) -> str:
        return str(self.__dict__)


class Waveform:
    def __init__(self, points, preamble: WaveformPreamble) -> None:
        self.header = None
        self.preamble = preamble
        self.x = [self.preamble.x_origin +
                  i * self.preamble.x_increment for i in range(preamble.count)]
        self.y = []
        if type(points) == list:
            for i in points:
                self._extract_data(i)
        else:
            self._extract_data(points)

    def xy(self):
        return ((self.x[i], self.y[i]) for i in range(len(self.x)))

    def _extract_data(self, data: str):
        self.header = data[:len('#NXXXXXXXXX')]
        self.y.append(data[len('#NXXXXXXXXX'):].split(','))

    def __repr__(self) -> str:
        return str(self.__dict__)


class Channel:
    def __init__(self, scope, name: str) -> None:
        self.scope = scope
        self.name = name
        self.number = int(self.name[-1])

        self._valid_bandwith_limit = ['OFF', '20M']
        self._bandwith_limit = self.bandwith_limit()

        self._valid_attenuation = ['0.01', '0.02', '0.05', '0.1', '0.2',
                                   '0.5', '1', '2', '5', '10', '20', '50', ' 100', '200', '500', '1000']
        self._probe_ratio = self.probe_ratio()
        self._scale = self.scale()

        self._valid_coupling = ['AC', 'DC', 'GND']
        self._coupling = self.coupling()

        self._display = self.display()
        self._invert = self.invert()
        self._offset = self.offset()
        self._voltage_range = self.range()

    def _set_get(self, cmd: str, valid: list, mode: str = None):
        cmd = cmd.format(self.number)
        if mode is None:
            cmd += '?'
            val = self.scope.query(cmd)
            return val
        else:
            if valid is not None and mode not in valid:
                raise Exception('invalid value')
            else:
                cmd += f' {mode}'
                self.scope.write(cmd)
                return mode

    def bandwith_limit(self, mode: str = None):
        self._bandwith_limit = self._set_get(':CHANnel{}:BWLimit',
                                             self._valid_bandwith_limit, mode)
        return self._bandwith_limit

    def coupling(self, mode: str = None):
        self._coupling = self._set_get(
            ':CHANnel{}:COUPling', self._valid_coupling, mode)
        return self._coupling

    def display(self, mode: bool = None):
        self._display = self._set_get(':CHANnel{}:DISPlay', None, mode)
        return self._display

    def invert(self, mode: bool = None):
        self._invert = self._set_get(':CHANnel{}:INVert', None, mode)
        return self._invert

    def offset(self, val: float = None):
        data_valid = False
        if val is not None:
            if isclose(self._probe_ratio, 1.0):
                if self._voltage_range >= 0.5:
                    if -100.0 <= val <= 100.0:
                        data_valid = True
                else:
                    if -2.0 <= val <= 2.0:
                        data_valid = True
            elif isclose(self._probe_ratio, 10.0):
                if self._voltage_range >= 5.0:
                    if -1000.0 <= val <= 1000.0:
                        data_valid = True
                else:
                    if -20.0 <= val <= 20.0:
                        data_valid = True
        else:
            data_valid = True

        if data_valid:
            self._offset = self._set_get(':CHANnel{}:OFFSet', None, val)
            return self._offset
        else:
            raise Exception('value out of range')

    def range(self, val: float = None):
        if val is not None:
            if isclose(self._probe_ratio, 1.0) and not 0.008 <= val <= 80.0 or \
                    isclose(self._probe_ratio, 10.0) and not 0.08 <= val <= 800.0:
                raise Exception('value out of range')
        self._voltage_range = self._set_get(':CHANnel{}:RANGe', None, val)
        return self._voltage_range

    def cal_timebase_delay(self, val: float = None):
        return self._set_get(':CHANnel{}:RANGe', None, val)

    def scale(self, val: float = None):
        self._scale = self._set_get(':CHANnel{}:SCALe', None, val)
        return self._scale

    def probe_ratio(self, val: float = None):
        if val is None or True in [isclose(i, val) for i in self._valid_attenuation]:
            self._probe_ratio = self._set_get(':CHANnel{}:PROBe', None, val)
            return self._probe_ratio
        else:
            raise Exception('invalid value')

    # todo : units, vernier


class WaveformMeasurement:
    # times
    period = 'PERiod', 1
    frequency = 'FREQuency', 1
    raise_time = 'RTIMe', 1
    fall_time = 'FTIMe', 1
    width_pos = 'PWIDth', 1
    width_neg = 'NWIDth', 1
    duty_pos = 'PDUTy', 1
    duty_neg = 'NDUTy', 1
    time_v_max = 'TVMAX', 1
    time_v_min = 'TVMIN', 1

    # pulses
    pulses_pos = 'PPULses', 1
    pulses_neg = 'NPULses', 1
    edges_pos = 'PEDGes', 1
    edges_neg = 'NEDGes', 1

    #delay and phase
    delay_raise_1_2 = 'RDELay', 2
    delay_fall_1_2 = 'FDELay', 2
    phase_raise_1_2 = 'RPHase', 2
    phase_fall_1_2 = 'FPHase', 2

    # voltage
    v_max = 'VMAX', 1
    v_min = 'VMIN', 1
    v_pp = 'VPP', 1
    v_top = 'VTOP', 1
    v_base = 'VBASe', 1
    v_amp = 'VAMP', 1
    v_upper = 'VUPper', 1
    v_mid = 'VMID', 1
    v_lower = 'VLOWer', 1
    v_avg = 'VAVG', 1
    v_rms = 'VRMS', 1
    overshoot = 'OVERshoot', 1
    preshoot = 'PREShoot', 1
    period_v_rms = 'PVRMS', 1
    variance = 'VARIance', 1

    # other
    rate_pos = 'PSLEWrate', 1
    rate_neg = 'NSLEWrate', 1
    area = 'MARea', 1
    period_area = 'MPARea', 1


class Measure:
    def __init__(self, id: int, scope, measurement: WaveformMeasurement, channel_a: Channel, channel_b: Channel = None, key: str = None) -> None:
        self.scope = scope
        self.measurement = measurement
        self.channel_a = channel_a
        self.channel_b = channel_b
        self.key = key
        self.id = id
        self.active = True

        self.cmd = ':MEASure:ITEM'
        self.cmd_tail = f' {measurement[0]}'

        if channel_a is not None:
            self.cmd_tail += f',{self.channel_a.name}'
        else:
            raise Exception('primary channel not provided')

        if self.measurement[1] == 2:
            if channel_b is not None:
                self.cmd_tail += f',{self.channel_b.name}'
            else:
                raise Exception('second channel not provided')

        # send the command to setup the measurement
        self.scope.write(self.cmd + self.cmd_tail)

    def read(self):
        return self.scope.query(self.cmd + '? ' + self.cmd_tail)

    def clear(self):
        self.scope.write(f':MEASure:CLEar ITEM{self.id}')
        self.active = False

    def recover(self):
        self.scope.write(f':MEASure:RECover ITEM{self.id}')
        self.active = True


class Counter:
    def __init__(self, scope) -> None:
        self.source = None
        self.scope = scope
        self.enable()
        self._active = False

    def enable(self, channel: Channel = None):
        if channel is None:
            self.remove()
            self._active = False
        else:
            if channel in self.scope.channels:
                self.source = channel
                self._active = True
                self.scope.write(f':MEASure:COUNter:SOURce {self.source.name}')
            else:
                raise Exception('invalid source channel')

    def read(self):
        if self._active:
            return float(self.scope.query(':MEASure:COUNter:VALue?'))
        else:
            return None

    def remove(self):
        self.active = False
        self.scope.write(f':MEASure:COUNter:SOURce OFF')


class Timebase:
    def __init__(self, scope) -> None:
        self.scope = scope
        self._delay_enable = True  # only state implemented
        self._delay_offset = None
        self._delay_scale = None
        # todo, requires sample rate  ->>>>>>>>>>>>>>>>>>>>> ready to implement
        self._main_offset = None
        self._main_scale = None
        self._mode = None
        # todo : setup

    def enable_delay(self, state: bool = None):
        cmd = ':TIMebase:DELay:ENABle'
        if state is None:
            cmd += '?'
            val = self.scope.query(cmd)
            val = True if val == '1' else False
            self._delay_enable = val
        else:
            cmd += ' 1' if state else ' 0'
            self.scope.write(cmd)
            self._delay_enable = state
        return self._delay_enable


class PyRigol_DS1000x:
    import pyvisa
    import math
    import re

    def __init__(self, VISA_resource_manager: pyvisa.ResourceManager, address, connect: bool = True):
        self.rm = VISA_resource_manager
        self.interface = None
        self.address = address
        self.connected = False

        # acquisition
        self._acquire_mode = None  # done in setup
        self._valid_acquire_mode = ['NORM', 'AVER', 'PEAK', 'HRES']

        self.sample_rate = None  # done in setup
        self.memory_depth = None  # done in setup

        # local state
        self._waveform_source = None  # done in setup

        self._waveform_reading_mode = None  # done in setup
        self._valid_waveform_mode = ['NORM', 'MAX', 'RAW']

        self._waveform_return_format = None  # done in setup
        self._valid_waveform_format = ['WORD', 'BYTE', 'ASC']

        # measurement
        self._measurements:list[Measure] = []
        self._max_measurements = 6  # todo, check

        self.counter = None  # done in setup

        # validation
        self._valid_channels = ['CHAN1', 'CHAN2', 'CHAN3', 'CHAN4']
        self.channels = None  # done in setup

        # connection
        if connect:
            self.open()

    # -- interface management

    def setup(self):
        self.acquire_mode()
        self.acquire_sample_rate()
        self.acquire_memory_depth()

        self.waveform_source()
        self.waveform_read_mode()
        self.waveform_return_format('ASC')

        self.channels = [Channel(self, i) for i in self._valid_channels]
        self.counter = Counter(self)

    def write(self, data):
        if self.interface is not None:
            print(f'write ->{data}')
            self.interface.write(data)
        else:
            raise Exception('instrument not connected')

    def query(self, query_string: str):
        print(f'query ->{query_string}')
        response = self.interface.query(query_string)
        return response

    def open(self):
        try:
            self.interface = self.rm.open_resource(self.address,
                                                   read_termination='\n',
                                                   write_termination='\n')

            model = self.interface.model_name
            if model == 'DS1000Z Series':
                self.connected = True
                self.setup()
            else:
                self.connected = False
                self.interface.close()
                raise Exception(
                    f'Invalid instrument model, only DS1000Z Series scopes are supported, got : {model}')

        except self.pyvisa.errors.VisaIOError:
            self.connected = False
            raise Exception('Connection Failure, unable to open Visa resource')

    # IEEE compatible

    def idn(self):
        return self.query('*IDN?')

    # -- acquisition state

    def autoscale(self):
        """Enable the waveform auto setting function. The oscilloscope will automatically adjust the vertical scale, horizontal timebase, and trigger mode according to the input signal to realize optimum waveform display"""
        self.write(':AUToscale')

    def clear(self):
        """Clear all the waveforms on the screen"""
        self.write(':CLEar')

    def run(self):
        """Starts waveform acquisition"""
        self.write(':RUN')

    def stop(self):
        """Stops waveform acquisition"""
        self.write(':STOP')

    def single(self):
        """Set the oscilloscope to the single trigger mode."""
        self.write(':SINGle')

    def force_trigger(self):
        """Generate a trigger signal forcefully. This command is only applicable to the normal and single trigger modes"""
        self.write('TFORce')

    # -- acquire_section

    def averages(self, n: int = None):
        """Set or query the number of averages under the average acquisition mode."""
        cmd = ':ACQuire:AVERages'
        if n is None:
            cmd += '?'
            return self.query(cmd)
        else:
            val = self.math.log2(n)
            round_val = round(val)
            if self.math.isclose(val, round_val):
                val = int(self.math.log2(n))
                cmd += f' {n}'
                self.write(cmd)
            else:
                raise Exception(
                    f'average outside valid range 2^n for n in 1-10, given: {n}')

    def acquire_memory_depth(self, depth:int = None):
        """Set or query the memory depth of the oscilloscope (namely the number of waveform points that can be stored in a single trigger sample). The default unit is pts (points)."""
        cmd = ':ACQuire:MDEPth'
        if depth is None:
            cmd += '?'
            val = float(self.query(cmd))
            self.memory_depth = val
        else:
            pass  # todo
        return self.memory_depth

    def acquire_mode(self, mode: str = None):
        f"""Set or query the acquisition mode of the oscilloscope, valid:{self._valid_acquire_mode} """
        cmd = ':ACQuire:TYPE'
        if mode is None:
            cmd += '?'
            mode = self.query(cmd)
            self._acquire_mode = mode
        else:
            if mode in self._valid_acquire_mode:
                if self._acquire_mode != mode:
                    cmd += f' {mode}'
                    self.write(cmd)
                    self._acquire_mode = mode
            else:
                raise Exception(f'invalid acquire mode {mode}')
        return self._acquire_mode

    def acquire_sample_rate(self):
        """Query the current sample rate. The default unit is Sa/s"""
        val = self.query(':ACQuire:SRATe?')
        self.sample_rate = val
        return val

    # -- calibration

    def start_cal(self):
        """The oscilloscope starts to execute self-calibration"""
        self.write(':CALibrate:STARt')

    def stop_cal(self):
        """Exit the self-calibration at any time"""
        self.write(':CALibrate:QUIT')

    # -- measurement functions
    def add_measurement(self, meas: WaveformMeasurement, channel_a: Channel, channel_b: Channel = None, key=None):
        if len(self._measurements) > self._max_measurements:
            for i in range(len(self._measurements)):
                if not self._measurement[i].active:
                    self._measurements.pop(i)
                    self._measurements.append(
                        Measure(len(self._measurements)+1, self, meas, channel_a, channel_b, key))
                    return
            self._measurements.pop(0)
            self._measurements.append(
                Measure(len(self._measurements)+1, self, meas, channel_a, channel_b, key))
        else:
            self._measurements.append(
                Measure(len(self._measurements)+1, self, meas, channel_a, channel_b, key))

    def _get_measurement_by_key(self, key):
        if type(key) == int:
            if 0 <= key <= len(self.channels):
                return self._measurements[key]
            else:
                raise Exception('key out of range')
        elif type(key) == str:
            for m in self._measurements:
                if m.key == key:
                    return m
            raise Exception('key not found')
        else:
            raise Exception('invalid key type')

    def clear_measurement(self, key):
        id = self._get_measurement_by_key(key).id-1
        self._measurements[id].clear()

    def read_measurement(self, key):
        return float(self._get_measurement_by_key(key).read())

    # -- waveform get functions

    def waveform_read_mode(self, mode=None):
        cmd = ':WAVeform:MODE'
        if mode is None:
            cmd += '?'
            mode = self.query(cmd)
        elif mode in self._valid_waveform_mode:
            cmd += f' {mode}'
            self.write(cmd)
        else:
            raise Exception(f'invalid waveform mode {mode}')
        self._waveform_return_format = mode
        return mode

    def waveform_return_format(self, format: str = None):
        cmd = ':WAVeform:FORMat'
        if format is None:
            cmd += '?'
            format = self.query(cmd)
            self._waveform_return_format = format
        elif format in self._valid_waveform_format:
            cmd += f' {format}'
            self._waveform_return_format = format
        else:
            raise Exception(f'invalid waveform mode {format}')
        return self._waveform_return_format

    def waveform_source(self, source: str = None):
        cmd = ':WAVeform:SOURce'
        if source is None:
            cmd += '?'
            val = self.query(cmd)
            self._waveform_source = val
        elif self.re.sub(r'[a-z],', source) in self._valid_channels:  # any lowercase ignored
            if source != self._waveform_source:
                cmd += f' {source}'
                self.write(cmd)
                self._waveform_source = source
        else:
            raise Exception(f'invalid waveform source {source}')
        return self._waveform_source

    def get_waveform_preamble(self):
        return WaveformPreamble(self.query(':WAVeform:PREamble?'))

    def get_waveform(self, channel=None):
        self.waveform_source(channel)
        self.waveform_return_format('ASC')
        self.waveform_read_mode('NORM')
        self.stop()  # data can be transferred only in stop state
        # verify data length
        preamble = self.get_waveform_preamble()
        waveform = None
        if preamble.points > 15625:  # max value for ascii transfer
            segments = []
            position = 1
            while position < preamble.points:
                self.write(f':WAV:STAR {position}')
                self.write(f':WAV:STOP {position + 15625}')
                segments.append(self.query(':WAV:DATA?'))
                position += 15625
            waveform = Waveform(segments, preamble)
        else:
            waveform = Waveform(self.query(':WAV:DATA?'), preamble)
        self.run()
        return waveform
