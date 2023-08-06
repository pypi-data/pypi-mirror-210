from qtpy.QtCore import QThread
from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, main, comon_parameters_fun
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq_plugins_piezoconcept.hardware.piezoconcept.piezoconcept import PiezoConceptPI, Position, Time


class DAQ_Move_PiezoConceptPI(DAQ_Move_base):
    """
    Plugin to drive piezoconcpet XY (Z) stages. There is a string nonlinear offset between the set position and the read
    position. It seems to bnot be problem in the sens where a given displacement is maintained. But because the read
    position is not "accurate", I've decided to ignore it and just trust the set position. So the return will be always
    strictly equal to the set position. However, if there is more that 10% difference raise a warning
    """

    _controller_units = 'µm'

    #find available COM ports
    import serial.tools.list_ports
    ports = [str(port)[0:4] for port in list(serial.tools.list_ports.comports())]
    port = 'COM6' if 'COM6' in ports else ports[0] if len(ports) > 0 else ''
    #if ports==[]:
    #    ports.append('')


    is_multiaxes = True
    stage_names = ['X', 'Y', 'Z']
    min_bound = -95  #*µm
    max_bound = 95  #µm
    offset = 100  #µm
    _epsilon = 3

    params= [{'title': 'Time interval (ms):', 'name': 'time_interval', 'type': 'int', 'value': 200},
             {'title': 'Controller Info:', 'name': 'controller_id', 'type': 'text', 'value': '', 'readonly': True},
             {'title': 'COM Port:', 'name': 'com_port', 'type': 'list', 'limits': ports, 'value': port},
             ]+comon_parameters_fun(is_multiaxes, stage_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: PiezoConceptPI = None

    def ini_stage(self, controller=None):

        self.ini_stage_init(old_controller=controller,
                            new_controller=PiezoConceptPI())
        if self.settings['multiaxes', 'multi_status'] == "Master":
            self.controller.init_communication(self.settings['com_port'])

        controller_id = self.controller.get_controller_infos()
        self.settings.child(('controller_id')).setValue(controller_id)

        self.settings.child('bounds', 'is_bounds').setValue(True)
        self.settings.child('bounds', 'min_bound').setValue(self.min_bound)
        self.settings.child('bounds', 'max_bound').setValue(self.max_bound)
        self.settings.child('scaling', 'use_scaling').setValue(True)
        self.settings.child('scaling', 'offset').setValue(self.offset)

        controller_id = self.controller.get_controller_infos()
        self.settings.child('controller_id').setValue(controller_id)

        self.settings.child('bounds', 'is_bounds').setValue(True)
        self.settings.child('bounds', 'min_bound').setValue(self.min_bound)
        self.settings.child('bounds', 'max_bound').setValue(self.max_bound)
        self.settings.child('scaling', 'use_scaling').setValue(True)
        self.settings.child('scaling', 'offset').setValue(self.offset)
        self.move_abs(0)

        info = controller_id
        initialized = True
        return info, initialized

    def close(self):
        """
            close the current instance of Piezo instrument.
        """
        self.controller.close_communication()

    def get_actuator_value(self):
        """
            Check the current position from the hardware.

            Returns
            -------
            float
                The position of the hardware.

            See Also
            --------
            DAQ_Move_base.get_position_with_scaling, daq_utils.ThreadCommand
        """
        position = self.controller.get_position(self.settings.child('multiaxes', 'axis').value())  #in
        if position.unit == 'n':
            pos = position.pos/1000  # in um
        else:
            pos = position.pos
        pos = self.get_position_with_scaling(pos)
        self.current_position = self.target_position  #should be pos but not precise enough conpared to set position
        self.emit_status(ThreadCommand('check_position', [self.target_position]))
        #print(pos)
        return self.target_position

    def move_abs(self, position):
        """

        Parameters
        ----------
        position: (float) target position of the given axis in um (or scaled units)

        Returns
        -------

        """
        position = self.check_bound(position)  #limits the position within the specified bounds (-100,100)
        self.target_position = position

        #get positions in controller units
        position = self.set_position_with_scaling(position)
        pos = Position(self.settings.child('multiaxes', 'axis').value(), int(position*1000), unit='n')
        out = self.controller.move_axis('ABS', pos)
        #self.move_is_done = True


    def move_rel(self, position):
        """
            Make the hardware relative move of the Piezo instrument from the given position after thread command signal was received in DAQ_Move_main.

            =============== ========= =======================
            **Parameters**  **Type**   **Description**

            *position*       float     The absolute position
            =============== ========= =======================

            See Also
            --------
            DAQ_Move_base.set_position_with_scaling, DAQ_Move_base.poll_moving

        """
        position = self.check_bound(self.current_position+position)-self.current_position
        self.target_position = position+self.current_position

        position = self.set_position_relative_with_scaling(position)

        pos = Position(self.settings.child('multiaxes', 'axis').value(), position*1000, unit='n')  # always use microns for simplicity
        out = self.controller.move_axis('REL', pos)

    def move_home(self):
        """
            Move to the absolute vlue 100 corresponding the default point of the Piezo instrument.

            See Also
            --------
            DAQ_Move_base.move_Abs
        """
        self.move_abs(0) #put the axis on the middle position so 100µm

    def stop_motion(self):
      """
        Call the specific move_done function (depending on the hardware).

        See Also
        --------
        move_done
      """
      self.move_done()


if __name__ == '__main__':
    main(__file__, init=False)

