import unreal_engine as ue


def import_asset(stage, source, target, skeleton=None):
    from unreal_engine.classes import PyFbxFactory, Skeleton

    ue.log('stage:' + stage)
    ue.log('source:' + source)
    ue.log('target:' + target)
    ue.log('skeleton:' + skeleton)

    target = target[:-1] if target[-1] in ['\\', '/'] else target

    factory = PyFbxFactory()
    factory.ImportUI.bCreatePhysicsAsset = False
    factory.ImportUI.bImportMaterials = True if stage in ['mdl'] else False
    # factory.ImportUI.bImportAsSkeletal = True if stage in ['skn', 'rig'] else False
    factory.ImportUI.bImportAnimations = True if stage in ['blk', 'anm'] else False

    skel_assets = ue.get_assets_by_class('Skeleton')
    for skel in skel_assets:
        if skel.get_name() == skeleton:
            factory.ImportUI.skeleton = skel
            break

    factory.factory_import_object(source, target)