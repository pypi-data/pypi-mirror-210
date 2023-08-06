

class HP8903A:
    """ module for controlling HP8903A from AR488 GPIb to USB adapter
        written by : Manuel Minutello"""

    from PyAR488 import AR488

    class Trigger:
        class _T:
            def __init__(self, command: str) -> None:
                self.command = command

        free_run = _T('T0')
        hold = _T('T1')
        immediate = _T('T2')
        settling = _T('T3')

    class Measure:
        class Display:
            class _D:
                def __init__(self, command: str) -> None:
                    self.command = command

            frequency_display = _D('RL')
            measurement_display = _D('RR')

        class _M:
            def __init__(self, command: str, display, settling_time: float = 0) -> None:
                self.command = command
                self.display = display
                self.settling_time = settling_time

        ac_level = _M('M1', Display.measurement_display, 1)
        sinad = _M('M2', Display.measurement_display)
        thd = _M('M3', Display.measurement_display, 1.5)

        dc_level = _M('S1', Display.measurement_display)
        snr = _M('S2', Display.measurement_display)
        thd_level = _M('S3', Display.measurement_display)

        frequency = _M('', Display.frequency_display)

    class Exceptions:
        class ReadingTooLarge(Exception):
            def __init__(self) -> None:
                super().__init__('Reading too large')

        class CalculatedValueOutOf(Exception):
            def __init__(self) -> None:
                super().__init__('Calculated value out of range')

        class NotchTuneError(Exception):
            def __init__(self) -> None:
                super().__init__('Notch can not tune to input')

        class InputLevelTooHigh(Exception):
            def __init__(self) -> None:
                super().__init__('input level exceeds instrument specification')

        class InternalVoltmeterError(Exception):
            def __init__(self) -> None:
                super().__init__('Internal voltmeter can not make measurement')

        class SourceTuneError(Exception):
            def __init__(self) -> None:
                super().__init__('source can not tune as requested')

        class SourceFrequencyConfirmationError(Exception):
            def __init__(self) -> None:
                super().__init__('cannot confirm source frequency')

        class PlotterLimitError(Exception):
            def __init__(self) -> None:
                super().__init__('top and bottom plotter limits are identical')

        class RatioNotAlowed(Exception):
            def __init__(self) -> None:
                super().__init__('ratio not allowed in present mode')

        class InoutOverloadDetectorTrip(Exception):
            def __init__(self) -> None:
                super().__init__('Input overload detector trip in range hold')

        class MeasurementError(Exception):
            def __init__(self) -> None:
                super().__init__('cannot make measurement')

        class SweepPointsOutOfRange(Exception):
            def __init__(self) -> None:
                super().__init__('more than 255 totla points in sweep')

        class NoSignalSense(Exception):
            def __init__(self) -> None:
                super().__init__('No signal sensed at input')

        class ValueOutOfRange(Exception):
            def __init__(self) -> None:
                super().__init__('entered value out of range')

        class InvalidKeySequence(Exception):
            def __init__(self) -> None:
                super().__init__('Invalid Key Sequence')

        class InvalidFunctionPrefix(Exception):
            def __init__(self) -> None:
                super().__init__('invalid function prefix')

        class Invalid_HPIB_Code(Exception):
            def __init__(self) -> None:
                super().__init__('invalid HPIB code')

        class ServiceError(Exception):
            def __init__(self) -> None:
                super().__init__('Service related error, see paragraph 8-12 of service manual')

        class InvalidResponse(Exception):
            def __init__(self, response: str) -> None:
                super().__init__(f'invalid value {response}')

        class NoResponseFromInstrument(Exception):
            def __init__(self) -> None:
                super().__init__('no response within 3 attempts')
    from time import sleep

    def __init__(self, interface: AR488, address: int, name='HP8903A'):
        self.address = address
        self.interface = interface
        self.name = name

        self._current_measurement: self.Measure._M = self.Measure.ac_level
        self._current_trigger: self.Trigger._T = self.Trigger.free_run
        self._current_display: self.Measure.Display._D = self.Measure.Display.measurement_display

        self.concat_commands(
            self.special('41.0', send=False),  # reset instrument
            # enable status byte constrol for all condition
            self.special('22.7', send=False)
        )

    def _write(self, command, settling=0.9):
        # interface checks if send or already set
        self.interface.address(self.address)
        self.interface.bus_write(f'{command}')
        self.sleep(settling)  # give time  to controller to handle

    def read(self):
        self.interface.address(self.address)
        response: str = self.interface.read()

        # check if response is an error
        if response.startswith('+900') and response.endswith('E+05\r\n'):
            error_code = int(response[4:6])
            if error_code == 10:
                raise self.Exceptions.ReadingTooLarge
            elif error_code == 11:
                raise self.Exceptions.CalculatedValueOutOfRange
            elif error_code == 13:
                raise self.Exceptions.NotchTuneError
            elif error_code == 14:
                raise self.Exceptions.InputLevelTooHigh
            elif error_code == 17:
                raise self.Exceptions.InternalVoltmeterError
            elif error_code == 18:
                raise self.Exceptions.SourceTuneError
            elif error_code == 19:
                raise self.Exceptions.SourceFrequencyConfirmationError
            elif error_code == 25:
                raise self.Exceptions.PlotterLimitError
            elif error_code == 26:
                raise self.Exceptions.RatioNotAlowed
            elif error_code == 30:
                raise self.Exceptions.InoutOverloadDetectorTrip
            elif error_code == 31:
                raise self.Exceptions.MeasurementError
            elif error_code == 32:
                raise self.Exceptions.SweepPointsOutOfRange
            elif error_code == 96:
                raise self.Exceptions.NoSignalSense
            elif error_code == 20:
                raise self.Exceptions.ValueOutOfRange
            elif error_code == 21:
                raise self.Exceptions.InvalidKeySequence
            elif error_code == 22 or error_code == 23:
                raise self.Exceptions.InvalidFunctionPrefix
            elif error_code == 24:
                raise self.Exceptions.Invalid_HPIB_Code
            elif 65 <= error_code <= 89:
                raise self.Exceptions.ServiceError
            else:
                raise Exception(f'unknown instrument error:{error_code}')

        try:
            return float(response)
        except ValueError:
            raise self.Exceptions.InvalidResponse(f'invalid value {response}')

    def measure(self, measurement: Measure._M, send=True):
        command = ''
        settling_time = 0
        if self._current_measurement != measurement:
            command += measurement.command
            settling_time += measurement.settling_time
            self._current_measurement = measurement

        if measurement.display != self._current_display:
            command += self.select_dsiplay(measurement.display, send=False)

        if send:
            self._write(command, settling_time)
        return command

    def source(self, frequency: int = None, level: float = None, send=True):
        command = ''
        # todo : frequency
        if frequency is not None:
            command += f'FR{frequency}HZ'

        if level is not None:
            command += f'AP{level}VL'  # todo : format level for correct format

        if send:
            self._write(command)
        return command

    def source_sweep(self, start_f: int, stop_f: int, level: float = None, send=True):
        command = ''
        command += f'FA{start_f}FB{stop_f}'

        if level is not None:
            command += f'AP{level}VL'  # todo : format level for correct format

        if send:
            self._write(command)
        return command

    def sweep_enable(self, en=True, send=True):
        command = f'W{1 if en else 0}'
        if send:
            self._write(command)
        return command

    def special(self, f: str, send=True):
        command = f'{f}SP'
        if send:
            self._write(command)
        return command

    def special_special(self, f: str, send=True):
        command = f'{f}SS'
        if send:
            self._write(command)
        return command

    def ratio_enable(self, en=True, send=True):
        command = f'R{1 if en else 0}'
        if send:
            self._write(command)
        return command

    def trigger(self, trigger: Trigger._T, send=True):
        command = ''
        if self._current_trigger != trigger:
            self._current_trigger = trigger
            command += trigger.command

        if send:
            self._write(command)
        return command

    def select_dsiplay(self, display: Measure.Display._D, send=True):
        command = ''
        if display != self._current_display:
            self._current_display = display
            command += display.command

        if send:
            self._write(command)
        return command

    class StatusByte:
        def __init__(self, status_byte_string) -> None:

            status_byte_int = int(status_byte_string)

            status_bits_string = format(status_byte_int, 'b')
            while len(status_bits_string) < 8:  # fill all bits in a byte
                status_bits_string += '0'

            self.data_ready = True if status_bits_string[0] == '1' else False
            self.HPIB_error = True if status_bits_string[1] == '1' else False
            self.instrument_error = True if status_bits_string[2] == '1' else False
            self.srq = True if status_bits_string[6] == '1' else False

        def __repr__(self):
            return str(self.__dict__)

    def get_status_byte(self):
        response = self.interface.spoll(self.address)
        try:
            return self.StatusByte(response)
        except:
            raise self.Exceptions.InvalidResponse(
                f'invalid response from instrument :{response}')

    def concat_commands(self, *args):
        command = ''
        for a in args:
            command += a
        self._write(command)
        return command

    def await_measurement(self):
        # enable SRQ for data ready
        awaiting_data = True
        while awaiting_data:
            self.sleep(1)
            try:
                sb = self.get_status_byte()
            except self.Exceptions.InvalidResponse:
                try:
                    self.sleep(1)
                    sb = self.get_status_byte()
                except self.Exceptions.InvalidResponse:
                    try:
                        self.sleep(1)
                        sb = self.get_status_byte()
                    except self.Exceptions.InvalidResponse:
                        raise self.Exceptions.NoResponseFromInstrument
            if sb.data_ready:
                awaiting_data = False
                break
