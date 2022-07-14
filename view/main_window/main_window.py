#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QMainWindow, QWidget, QFileDialog
from PySide6.QtCore import Qt

from view.case_wizard.case_wizard import CaseWizard
from view.setup.general.general_page import GeneralPage
from view.setup.materials.material_page import MaterialPage
from view.setup.models.models_page import ModelsPage
from view.setup.cell_zone_conditions.cell_zone_conditions_page import CellZoneConditionsPage
from view.setup.boundary_conditions.boundary_conditions_page import BoundaryConditionsPage
from view.setup.reference_values.reference_values_page import ReferenceValuesPage
from view.solution.numerical_conditions.numerical_conditions_page import NumericalConditionsPage
from view.solution.monitors.monitors_page import MonitorsPage
from view.solution.initialization.initialization_page import InitializationPage
from view.solution.run_calculation.run_calculation_page import RunCalculationPage
from openfoam.case_generator import CaseGenerator
from openfoam.polymesh.polymesh_loader import PolyMeshLoader
from .content_view import ContentView
from .main_window_ui import Ui_MainWindow
from .menu_view import MenuView, MenuItem
from .mesh_dock import MeshDock
from .console_dock import ConsoleDock


class MenuPage:
    def __init__(self, pageClass=None):
        self._pageClass = pageClass
        self._index = -1 if pageClass else 0

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    def createPage(self):
        return self._pageClass()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._wizard = None

        self._menuView = MenuView(self._ui.menuView)
        self._contentView = ContentView(self._ui.formView, self._ui)

        self._emptyDock = self._ui.emptyDock
        self._emptyDock.setTitleBarWidget(QWidget())
        self._meshDock = MeshDock(self)
        self._consoleDock = ConsoleDock(self)

        self._addDockTabified(self._consoleDock)
        self._addDockTabified(self._meshDock)

        self._menuPages = {
            MenuItem.MENU_TOP.value: MenuPage(),
            MenuItem.MENU_SETUP_GENERAL.value: MenuPage(GeneralPage),
            MenuItem.MENU_SETUP_MATERIALS.value: MenuPage(MaterialPage),
            MenuItem.MENU_SETUP_MODELS.value: MenuPage(ModelsPage),
            MenuItem.MENU_SETUP_CELL_ZONE_CONDITIONS.value: MenuPage(CellZoneConditionsPage),
            MenuItem.MENU_SETUP_BOUNDARY_CONDITIONS.value: MenuPage(BoundaryConditionsPage),
            MenuItem.MENU_SETUP_REFERENCE_VALUES.value: MenuPage(ReferenceValuesPage),
            MenuItem.MENU_SOLUTION_NUMERICAL_CONDITIONS.value: MenuPage(NumericalConditionsPage),
            MenuItem.MENU_SOLUTION_MONITORS.value: MenuPage(MonitorsPage),
            MenuItem.MENU_SOLUTION_INITIALIZATION.value: MenuPage(InitializationPage),
            MenuItem.MENU_SOLUTION_RUN_CALCULATION.value: MenuPage(RunCalculationPage),
        }

        self._constantLoadingDir = None

        self._connectSignalsSlots()

    def tabifyDock(self, dock):
        self.tabifyDockWidget(self._emptyDock, dock)

    def _connectSignalsSlots(self):
        self._ui.actionExit.triggered.connect(self.close)
        self._ui.actionNew.triggered.connect(self._openWizard)
        self._ui.actionSave.triggered.connect(self._save)
        self._ui.actionLoad_Mesh.triggered.connect(self._loadMesh)
        self._menuView.currentMenuChanged.connect(self._changeForm)

    def _openWizard(self, signal):
        self._wizard = CaseWizard()

        self._wizard.exec()

    def _save(self):
        dirName = QFileDialog.getExistingDirectory(self)
        if dirName:
            CaseGenerator(dirName).generateFiles(self._constantLoadingDir)

    def _loadMesh(self):
        # fileName = QFileDialog.getOpenFileName(self, self.tr("Open Mesh"), "", self.tr("OpenFOAM Mesh (*.foam)"))
        # if fileName[0]:
        #     self._meshDock.showMesh(fileName[0])
        dirName = QFileDialog.getExistingDirectory(self)
        if dirName:
            PolyMeshLoader().load(dirName)
            self._constantLoadingDir = dirName

            currentMenu = self._menuView.currentMenu()
            if currentMenu == MenuItem.MENU_SETUP_CELL_ZONE_CONDITIONS.value\
                    or currentMenu == MenuItem.MENU_SETUP_BOUNDARY_CONDITIONS.value:
                idx = self._menuPages[currentMenu].index
                if idx > 0:
                    self._contentView.page(idx).load()

    def _changeForm(self, currentMenu):
        page = self._menuPages[currentMenu]
        if page.index < 0:
            newPage = page.createPage()
            page.index = self._contentView.addPage(newPage)

        self._contentView.changePane(page.index)

    def _addDockTabified(self, dock):
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.tabifyDock(dock)
        self._ui.menuView_2.addAction(dock.toggleViewAction())
