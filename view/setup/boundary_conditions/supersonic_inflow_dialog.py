#!/usr/bin/env python
# -*- coding: utf-8 -*-

from coredb import coredb
from coredb.coredb_writer import CoreDBWriter

from PySide6.QtWidgets import QMessageBox

from view.widgets.resizable_dialog import ResizableDialog
from .supersonic_inflow_dialog_ui import Ui_SupersonicInflowDialog
from .turbulence_model_helper import TurbulenceModelHelper
from .boundary_db import BoundaryDB


class SupersonicInflowDialog(ResizableDialog):
    RELATIVE_XPATH = '/supersonicInflow'

    def __init__(self, parent, bcid):
        super().__init__(parent)
        self._ui = Ui_SupersonicInflowDialog()
        self._ui.setupUi(self)

        self._db = coredb.CoreDB()
        self._xpath = BoundaryDB.getXPath(bcid)
        self._turbulenceWidget = TurbulenceModelHelper.createWidget(self._xpath)

        if self._turbulenceWidget is not None:
            self._ui.dialogContents.layout().addWidget(self._turbulenceWidget)

        self._load()

    def accept(self):
        xpath = self._xpath + self.RELATIVE_XPATH

        writer = CoreDBWriter()
        writer.append(xpath + '/velocity/x', self._ui.xVelocity.text(), self.tr("X-Velocity"))
        writer.append(xpath + '/velocity/y', self._ui.yVelocity.text(), self.tr("Y-Velocity"))
        writer.append(xpath + '/velocity/z', self._ui.zVelocity.text(), self.tr("Z-Velocity"))
        writer.append(xpath + '/staticPressure', self._ui.staticPressure.text(), self.tr("Static Pressure"))
        writer.append(xpath + '/staticTemperature', self._ui.staticTemperature.text(), self.tr("Static Temperature"))

        if self._turbulenceWidget is not None:
            self._turbulenceWidget.appendToWriter(writer)

        errorCount = writer.write()
        if errorCount > 0:
            QMessageBox.critical(self, self.tr("Input Error"), writer.firstError().toMessage())
        else:
            super().accept()

    def _load(self):
        xpath = self._xpath + self.RELATIVE_XPATH

        self._ui.xVelocity.setText(self._db.getValue(xpath + '/velocity/x'))
        self._ui.yVelocity.setText(self._db.getValue(xpath + '/velocity/y'))
        self._ui.zVelocity.setText(self._db.getValue(xpath + '/velocity/z'))
        self._ui.staticPressure.setText(self._db.getValue(xpath + '/staticPressure'))
        self._ui.staticTemperature.setText(self._db.getValue(xpath + '/staticTemperature'))

        if self._turbulenceWidget is not None:
            self._turbulenceWidget.load()
