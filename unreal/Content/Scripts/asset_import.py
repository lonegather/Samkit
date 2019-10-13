import unreal_engine as ue


def import_asset(stage, source, target, skeleton=None):
    from unreal_engine.classes import PyFbxFactory, Skeleton

    target = target[:-1] if target[-1] in ['\\', '/'] else target

    factory = PyFbxFactory()
    factory.ImportUI.bCreatePhysicsAsset = False
    factory.ImportUI.bImportMaterials = True if stage in ['mdl'] else False
    factory.ImportUI.bImportAsSkeletal = True if stage in ['skn', 'rig', 'blk', 'anm'] else False
    factory.ImportUI.bImportAnimations = True if stage in ['blk', 'anm'] else False
    factory.ImportUI.skeleton = Skeleton(skeleton) if stage in ['blk', 'anm'] else None
    factory.factory_import_object(source, target)
