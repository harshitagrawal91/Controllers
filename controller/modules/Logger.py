# ipop-project
# Copyright 2016, University of Florida
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import logging.handlers as lh
import os
from controller.framework.ControllerModule import ControllerModule


class Logger(ControllerModule):
    def __init__(self, cfx_handle, module_config, module_name):
        super(Logger, self).__init__(cfx_handle, module_config, module_name)
        self._logger = None

    def initialize(self):
        # Extracts the controller Log Level from the ipop-config file,
        # If nothing is provided the default is INFO
        level = logging.INFO
        if "LogLevel" in self._cm_config:
            level = getattr(logging, self._cm_config["LogLevel"])

        # If the Logging is set to Console by the User
        if self._cm_config["Device"] == "Console":
            # Console logging
            logging.basicConfig(format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
                                datefmt="%H:%M:%S",
                                level=level)
            self._logger = logging.getLogger("IPOP console logger")

        # If the Logging is set to File by the User
        elif self._cm_config["Device"] == "File":
            # Extracts the filepath else sets logs to current working directory
            filepath = self._cm_config.get("Directory", "./")
            fqname = filepath + \
                self._cm_config.get("CtrlLogFileName", "ctrl.log")
            if not os.path.exists(filepath):
                os.makedirs(filepath, exist_ok=True)
            if os.path.isfile(fqname):
                os.remove(fqname)
            self._logger = logging.getLogger("IPOP Rotating Log")
            self._logger.setLevel(level)
            # Creates rotating filehandler
            handler = lh.RotatingFileHandler(filename=fqname,
                                             maxBytes=self._cm_config["MaxFileSize"],
                                             backupCount=self._cm_config["MaxArchives"])
            formatter = logging.Formatter(
                "[%(asctime)s.%(msecs)03d] %(levelname)s:%(message)s", datefmt="%Y%m%d %H:%M:%S")
            handler.setFormatter(formatter)
            # Adds the filehandler to the Python logger module
            self._logger.addHandler(handler)

         # If the Logging is set to All by the User
        else:
            self._logger = logging.getLogger("IPOP Console & File Logger")
            self._logger.setLevel(level)

            #Console Logger
            console_handler = logging.StreamHandler()
            console_log_formatter = logging.Formatter(
                "[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
                datefmt="%H:%M:%S")
            console_handler.setFormatter(console_log_formatter)
            self._logger.addHandler(console_handler)

            # Extracts the filepath else sets logs to current working directory
            filepath = self._cm_config.get("Directory", "./")
            fqname = filepath + \
                self._cm_config.get("CtrlLogFileName", "ctrl.log")
            if not os.path.exists(filepath):
                os.makedirs(filepath, exist_ok=True)
            if os.path.isfile(fqname):
                os.remove(fqname)

            #File Logger
            # Creates rotating filehandler
            file_handler = lh.RotatingFileHandler(filename=fqname)
            file_log_formatter = logging.Formatter(
                "[%(asctime)s.%(msecs)03d] %(levelname)s:%(message)s", datefmt="%Y%m%d %H:%M:%S")
            file_handler.setFormatter(file_log_formatter)
            self._logger.addHandler(file_handler)

        self._logger.info("Logger: Module loaded")

    def process_cbt(self, cbt):
        if cbt.op_type == "Request":
            # Extracting the logging level information from the CBT action tag
            if cbt.request.action == "LOG_DEBUG" or cbt.request.action == "debug":
                self._logger.debug("%s: %s", cbt.request.initiator, cbt.request.params)
                cbt.set_response(None, True)
            elif cbt.request.action == "LOG_INFO" or cbt.request.action == "info":
                self._logger.info("%s: %s", cbt.request.initiator, cbt.request.params)
                cbt.set_response(None, True)
            elif cbt.request.action == "LOG_WARNING" or cbt.request.action == "warning":
                self._logger.warning("%s: %s", cbt.request.initiator, cbt.request.params)
                cbt.set_response(None, True)
            elif cbt.request.action == "LOG_ERROR" or cbt.request.action == "error":
                self._logger.error("%s: %s", cbt.request.initiator, cbt.request.params)
                cbt.set_response(None, True)
            elif cbt.request.action == "LOG_QUERY_CONFIG":
                cbt.set_response(self._cm_config, True)
            else:
                self._logger.warning("%s: Unsupported CBT action %s", self._module_name, str(cbt))
                cbt.set_response("Unsupported CBT action", False)
            self.complete_cbt(cbt)
        elif cbt.op_type == "Response":
            self.free_cbt(cbt)

    def timer_method(self):
        pass

    def terminate(self):
        logging.shutdown()
