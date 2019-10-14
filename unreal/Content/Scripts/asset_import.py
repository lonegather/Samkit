import unreal_engine as ue


def import_asset(stage, source, target, skeleton=None):

    from unreal_engine.classes import PyFbxFactory, Skeleton
    from unreal_engine.enums import EFBXImportType

    target = target[:-1] if target[-1] in ['\\', '/'] else target

    factory = PyFbxFactory()
    factory.ImportUI.bCreatePhysicsAsset = False
    factory.ImportUI.bImportMaterials = True if stage in ['mdl'] else False
    factory.ImportUI.bImportAnimations = True if stage in ['blk', 'anm'] else False

    if stage in ['blk', 'anm']:
        factory.ImportUI.MeshTypeToImport = EFBXImportType.FBXIT_Animation

    skel_assets = ue.get_assets_by_class('Skeleton')
    for skel in skel_assets:
        if stage in ['blk', 'anm'] and skeleton and skel.get_name().count(skeleton):
            factory.ImportUI.skeleton = skel
            break

    factory.factory_import_object(source, target)