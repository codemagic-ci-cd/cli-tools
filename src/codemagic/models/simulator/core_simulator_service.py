from __future__ import annotations

import subprocess

from codemagic.mixins import RunningCliAppMixin
from codemagic.utilities import log


class CoreSimulatorService(RunningCliAppMixin):

    def __init__(self):
        self.logger = log.get_logger(self.__class__)

    def _kill_service(self):
        cmd = ('killall', '-9', 'com.apple.CoreSimulator.CoreSimulatorService')
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, show_output=False)
                process.raise_for_returncode()
            else:
                subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()
        except subprocess.CalledProcessError as cpe:
            self.logger.debug('Failed to kill com.apple.CoreSimulator.CoreSimulatorService: %s', cpe)

    def ensure_clean_state(self):
        """
        With Xcode 12 sometimes the builds fail with error "Failed to find newest available Simulator runtime"
        Indication for that to happen is when some of the simulators are unavailable with state
        'unavailable, failed to open liblaunch_sim.dylib'. An option to overcome this is by using the workaround
        proposed in this SO thread https://stackoverflow.com/a/63530321 by killing the CoreSimulatorService.
        """

        cmd = ('xcrun', 'simctl', 'list', 'devices')
        invalid_simulator_state = 'unavailable, failed to open liblaunch_sim.dylib'

        self.logger.debug('Check for CoreSimulatorService health')
        cli_app = self.get_current_cli_app()
        try:
            if cli_app:
                process = cli_app.execute(cmd, suppress_output=True)
                process.raise_for_returncode()
                devices_output = process.stdout
            else:
                devices_output = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()
        except subprocess.CalledProcessError as cpe:
            self.logger.debug('Failed to obtain simulators listing: %s', cpe)
            self._kill_service()
        else:
            if invalid_simulator_state in devices_output:
                self.logger.debug('CoreSimulatorService is potentially poisoned, kill it')
                self._kill_service()
            else:
                self.logger.debug('CoreSimulatorService seems to be alright')
