class HP3478A:
    """HP3478A made simple with Python and the AR488 project!
    use the PyAR488 module to comunicate with the AR488 board and make you lab bench smart
    -> written by Minu"""
    from PyAR488 import AR488

    class Exceptions:
        class StatusByteException(Exception):
            def __init__(self) -> None:
                super().__init__('error reading instrument status byte')
        class InvalidDigits(Exception):
            def __init__(self) -> None:
                super().__init__('invalid digit count')

    def __init__(self, interface: AR488, address:int, name='HP3577A'):
        self.address = address
        self.interface = interface
        self.name = name

    def _write(self, command):
        self.interface.address(self.address)
        self.interface.bus_write(command)

    def read(self):
        self.interface.address(self.address)
        return float(self.interface.read())

    def query(self, command, payload=False, decode=True):
        self.interface.address(self.address)
        return self.interface.query(command, payload=payload, decode=decode)
    
    class Measure:
        class _MeasurementFunction:
            def __init__(self,code:str) -> None:
                 self.code = code

        V_DC = _MeasurementFunction('F1')
        V_AC = _MeasurementFunction('F2')
        I_DC = _MeasurementFunction('F5')
        I_AC = _MeasurementFunction('F6')
        OHM = _MeasurementFunction('F3')
        OHM_4W = _MeasurementFunction('F4')
        OHM_EXT = _MeasurementFunction('F7')
    
    class Trigger:
        class _TriggerFunction:
            def __init__(self, code:str):
                self.code = code
        
        internal = _TriggerFunction('T1')
        external = _TriggerFunction('T2')
        signle = _TriggerFunction('T3')
        hold = _TriggerFunction('T4')
        fast = _TriggerFunction('T5')
    
    def read_error_register(self):
        error_reg = self.query('E', payload=True)
        error_reg_bin = format(error_reg, 'b')
        error_bits = [True if i == '1' else False for i in error_reg_bin]
        error_log = []
        if error_bits[0]:
            error_log.append('0: incorrect cal ram checksum or range checksum error')
        if error_bits[1]:
            error_log.append('1:Main CPU RAM self-test failed')
        if error_bits[2]:
            error_log.append('Control ROM self test failed')
        if error_bits[3]:
            error_log.append('A/D slope error detected')
        if error_bits[4]:
            error_log.append('A/D self test failed')
        if error_bits[5]:
            error_log.append('A/D link fail (between U403 and U462')
        return error_log

    def enable_data_ready_srq(self, send: bool = True):
        """set bit 0 of SRQ mask, remains set until spoll or returns the formatted command string"""
        command_string = 'M01'
        if send:
            self._write(command_string)
        return command_string
        
    def print_text(self, text: str, send: bool = True):
        """prints an uppercase text on display or returns the formatted command string,
        the text remains for 10 minutes than blank, normal display by D1 command, CLEAR or error"""
        text = text.upper()
        if len(text) > 12:
            text = text[:12]
        command_string = f'D2{text}'
        if send:
            self._write(command_string)  # D3 is same but do not update annunciators
        return command_string

    def normal_display(self, send: bool = True):
        """switch to normal reading display or returns the formatted command string"""
        command_string = 'D1'
        if send:
            self._write(command_string)
        return command_string
    
    def clear_status_register(self, send: bool = True):
        """switch to normal reading display or returns the formatted command string"""
        command_string = 'K'
        if send:
            self._write(command_string)
        return command_string
    

    class StatusByte:
        def __init__(self, raw_data):
            response_bits = format(raw_data, 'b')
            self.data_ready = response_bits[0] == '1'
            self.syntax_error = response_bits[2] == '1'
            self.internal_error = response_bits[3] == '1'
            self.front_panel_srq = response_bits[4] == '1'
            self.invalid_calibration = response_bits[5] == '1'
            self.srq = response_bits[6] == '1'
            self.power_on_srq = response_bits[7] == '1'


    def get_status_byte(self):
        """returns the status byte of the instrument as an int or a dict"""
        response = self.interface.spoll(self.address)
        try:
            response = int(response)
        except ValueError:
            raise self.Exceptions.StatusByteException()
        
        return self.StatusByte(response)
    
    def measure(self, new_measurement:Measure._MeasurementFunction, send:bool = True):
        command_string = new_measurement.code
        if send:
            self._write(command_string)
        return command_string
    
    def trigger(self, new_trigger:Trigger._TriggerFunction, send:bool = True):
        command_string = new_trigger.code
        if send:
            self._write(command_string)
        return command_string

    def enable_auto_zero(self, send: bool = True):
        """enable auto zero function or returns the formatted command string"""
        command_string = 'Z1'
        if send:
            self._write(command_string)
        return command_string
    
    def disable_auto_zero(self, send: bool = True):
        """disable auto zero function or returns the formatted command string"""
        command_string = 'Z0'
        if send:
            self._write(command_string)
        return command_string
    
    def enable_auto_range(self, send: bool = True):
        """enable auto range or returns the formatted command string"""
        command_string = 0
        if send:
            self._write(command_string)
        return command_string
    
    def set_digits(self, new_digits:float, send = True):
        if new_digits not in (3.5, 4.5, 6.5):
            raise self.Exceptions.InvalidDigits
        command_string = f'N{int(new_digits-0.5)}'  #example N3 -> 3.5 digits
        if send:
            self._write(command_string)
        return command_string

    def push(self, *args:list[str]):
        """list of tuples arranged as (function, argument) and packs all programming codes to in a single command,
        use to optimize instrument settling time"""
        command_string = ''
        if len(args) > 0:
            for i in args:
                command_string += i
            self._write(command_string)
        return command_string