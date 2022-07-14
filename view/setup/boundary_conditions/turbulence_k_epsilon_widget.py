#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget

from coredb import coredb
from .turbulence_k_epsilon_widget_ui import Ui_turbulenceKEpsilonWidget
from .boundary_db import KEpsilonSpecification


class TurbulenceKEpsilonWidget(QWidget):
    RELATIVE_XPATH = '/turbulence/k-epsilon'

    def __init__(self, xpath):
        super().__init__()
        self._ui = Ui_turbulenceKEpsilonWidget()
        self._ui.setupUi(self)

        self._specificationMethods = {
            KEpsilonSpecification.K_AND_EPSILON.value: self.tr("K and Epsilon"),
            KEpsilonSpecification.INTENSITY_AND_VISCOSITY_RATIO.value: self.tr("Intensity and Viscosity Ratio"),
        }
        self._setupSpecificationMethodCombo()

        self._db = coredb.CoreDB()
        self._xpath = xpath

        self._connectSignalsSlots()

        self._specificationMethodChanged()

    def load(self):
        path = self._xpath + self.RELATIVE_XPATH

        self._ui.specificationMethod.setCurrentText(
            self._specificationMethods[self._db.getValue(path + '/specification')])
        self._ui.turbulentKineticEnergy.setText(self._db.getValue(path + '/turbulentKineticEnergy'))
        self._ui.turbuelnetDissipationRate.setText(self._db.getValue(path + '/turbulentDissipationRate'))
        self._ui.turbulentIntensity.setText(self._db.getValue(path + '/turbulentIntensity'))
        self._ui.turbulentViscosityRatio.setText(self._db.getValue(path + '/turbulentViscosityRatio'))
        self._specificationMethodChanged()

    def appendToWriter(self, writer):
        path = self._xpath + self.RELATIVE_XPATH

        specification = self._ui.specificationMethod.currentData()
        writer.append(path + '/specification', specification, None)
        if specification == KEpsilonSpecification.K_AND_EPSILON.value:
            writer.append(path + '/turbulentKineticEnergy', self._ui.turbulentKineticEnergy.text(),
                          self.tr("Turbulent Kinetic Energy"))
            writer.append(path + '/turbulentDissipationRate', self._ui.turbuelnetDissipationRate.text(),
                          self.tr("Turbulent Dissipation Rate"))
        elif specification == KEpsilonSpecification.INTENSITY_AND_VISCOSITY_RATIO.value:
            writer.append(path + '/turbulentIntensity', self._ui.turbulentIntensity.text(),
                          self.tr("Turbulent Intensity"))
            writer.append(path + '/turbulentViscosityRatio', self._ui.turbulentViscosityRatio.text(),
                          self.tr("Turbulent Viscosity Ratio"))

    def _connectSignalsSlots(self):
        self._ui.specificationMethod.currentIndexChanged.connect(self._specificationMethodChanged)

    def _setupSpecificationMethodCombo(self):
        for value, text in self._specificationMethods.items():
            self._ui.specificationMethod.addItem(text, value)

    def _specificationMethodChanged(self):
        specification = self._ui.specificationMethod.currentData()
        self._ui.kAndEpsilon.setVisible(
            specification == KEpsilonSpecification.K_AND_EPSILON.value)
        self._ui.intensityAndViscocityRatio.setVisible(
            specification == KEpsilonSpecification.INTENSITY_AND_VISCOSITY_RATIO.value)
