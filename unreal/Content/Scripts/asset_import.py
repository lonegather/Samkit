import unreal_engine as ue
from unreal_engine.classes import PyFbxFactory


def import_asset(stage, path, skeleton=None):
    factory = PyFbxFactory()
    factory.ImportUI.bImportAsSkeletal = True
