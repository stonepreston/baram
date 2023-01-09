#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import qasync

from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from openfoam.run import runUtility
from openfoam.file_system import FileSystem
from openfoam.polymesh.polymesh_loader import PolyMeshLoader
from view.widgets.progress_dialog import ProgressDialog


logger = logging.getLogger(__name__)


class MeshType(Enum):
    POLY_MESH = auto()
    FLUENT_2D = auto()
    FLUENT_3D = auto()
    STAR_CCM = auto()
    GMSH = auto()
    IDEAS = auto()
    NAMS_PLOT3D = auto()


OPENFOAM_MESH_CONVERTERS = {
    MeshType.POLY_MESH: None,
    MeshType.FLUENT_2D: ('fluentMeshToFoam', '-writeSets', '-writeZones'),
    MeshType.FLUENT_3D: ('fluent3DMeshToFoam',),
    MeshType.STAR_CCM: ('ccm26ToFoam',),
    MeshType.GMSH: ('gmshToFoam',),
    MeshType.IDEAS: ('ideasUnvToFoam',),
    MeshType.NAMS_PLOT3D: ('plot3dToFoam',),
}


class MeshManager(QObject):
    meshChanged = Signal()

    def __init__(self, window):
        super().__init__()

        self._window = window

    @qasync.asyncSlot()
    async def scale(self, x, y, z):
        progress = ProgressDialog(self._window, self.tr('Mesh Scaling'), self.tr('Scaling the mesh.'))

        try:
            proc = await runUtility('transformPoints', '-allRegions', '-scale', f'({x} {y} {z})',
                                    cwd=FileSystem.caseRoot())
            result = await proc.wait()

            if result:
                progress.error(self.tr('Mesh scaling failed.'))
            else:
                progress.finish(self.tr('Mesh scaling is complete'))
                self.meshChanged.emit()
        except Exception as ex:
            logger.info(ex, exc_info=True)
            progress.error(self.tr('Error occurred:\n' + str(ex)))

    @qasync.asyncSlot()
    async def translate(self, x, y, z):
        progress = ProgressDialog(self._window, self.tr('Mesh Translation'), self.tr('Translating the mesh.'))

        try:
            proc = await runUtility(
                'transformPoints', '-allRegions', '-translate', f'({x} {y} {z})', cwd=FileSystem.caseRoot())
            result = await proc.wait()

            if result:
                progress.error(self.tr('Mesh translation failed.'))
            else:
                progress.finish(self.tr('Mesh translation is complete'))
                self.meshChanged.emit()
        except Exception as ex:
            logger.info(ex, exc_info=True)
            progress.error(self.tr('Error occurred:\n' + str(ex)))

    @qasync.asyncSlot()
    async def rotate(self, origin, axis, angle):
        progress = ProgressDialog(self._window, self.tr('Mesh Rotation'), self.tr('Rotating the mesh.'))

        try:
            proc = await runUtility('transformPoints', '-allRegions',
                                    '-origin', f'({" ".join(origin)})',
                                    '-rotate-angle', f'(({" ".join(axis)}) {angle})',
                                    cwd=FileSystem.caseRoot())
            result = await proc.wait()

            if result:
                progress.error(self.tr('Mesh rotation failed.'))
            else:
                progress.finish(self.tr('Mesh rotation is complete'))
                self.meshChanged.emit()
        except Exception as ex:
            logger.info(ex, exc_info=True)
            progress.error(self.tr('Error occurred:\n' + str(ex)))

    async def importOpenFoamMesh(self, path: Path):
        progress = ProgressDialog(self._window, self.tr('Mesh Loading'), self.tr('Checking the mesh.'))

        try:
            progress.setText(self.tr('Loading the boundaries.'))
            await PolyMeshLoader().loadMesh(path)
            progress.close()
        except Exception as ex:
            logger.info(ex, exc_info=True)
            progress.error(self.tr('Error occurred:\n' + str(ex)))

    async def importMesh(self, path, meshType):
        progress = ProgressDialog(self._window, self.tr('Mesh Loading'), self.tr('Converting the mesh.'))

        try:
            await FileSystem.copyFileToCase(path)

            proc = await runUtility(*OPENFOAM_MESH_CONVERTERS[meshType], path.name, cwd=FileSystem.caseRoot())
            progress.setProcess(proc)
            if await proc.wait():
                progress.error(self.tr('File conversion failed.'))
            elif not progress.canceled():
                progress.setText(self.tr('Loading the boundaries.'))
                await PolyMeshLoader().loadMesh()
                await FileSystem.removeFile(path.name)
                progress.close()
        except Exception as ex:
            logger.info(ex, exc_info=True)
            progress.error(self.tr('Error occurred:\n' + str(ex)))

    @classmethod
    def convertUtility(cls, meshType):
        return OPENFOAM_MESH_CONVERTERS[meshType][0]
