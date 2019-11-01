import unreal_engine as ue


def import_asset(stage, source, target, skeleton=None, shot_info=None):

    from unreal_engine.classes import PyFbxFactory, Skeleton
    from unreal_engine.enums import EFBXImportType

    target = target[:-1] if target[-1] in ['\\', '/'] else target

    ue.log('<<<--- stage: %s --->>>' % stage)
    ue.log('<<<--- source: %s --->>>' % source)
    ue.log('<<<--- target: %s --->>>' % target)
    ue.log('<<<--- skeleton: %s --->>>' % skeleton)

    factory = PyFbxFactory()
    factory.ImportUI.bCreatePhysicsAsset = False
    factory.ImportUI.bImportMaterials = True if stage in ['mdl'] else False
    factory.ImportUI.bImportAnimations = True if stage in ['cam', 'lyt', 'anm'] else False

    if stage == 'cam':
        setup_sequencer(source, target, shot_info)
        return

    if stage in ['lyt', 'anm']:
        factory.ImportUI.MeshTypeToImport = EFBXImportType.FBXIT_Animation
        data = factory.ImportUI.AnimSequenceImportData
        data.CustomSampleRate = 25

        if not skeleton:
            ue.log_error("<<<--- No skeleton information found --->>>")
            return

        skel_assets = ue.get_assets_by_class('Skeleton')
        for skel in skel_assets:
            if skel.get_name().count(skeleton):
                ue.log('<<<--- Found skeleton "%s" --->>>' % skel.get_name())
                factory.ImportUI.skeleton = skel
                break
        else:
            ue.log_error('<<<--- No matching skeleton found for "%s" --->>>' % skeleton)
            return

    factory.factory_import_object(source, target)


def setup_sequencer(source, target, shot_info):
    import os
    from unreal_engine.classes import LevelSequenceFactoryNew, CineCameraActor, MovieScene3DTransformTrack
    from unreal_engine.structs import MovieSceneObjectBindingID
    from unreal_engine.enums import EMovieSceneObjectBindingSpace

    name = os.path.basename(source).lower().split('.fbx')[0]

    for seq in ue.get_assets_by_class('LevelSequence'):
        if seq.get_display_name() == name:
            seq.conditional_begin_destroy()
            break

    factory = LevelSequenceFactoryNew()
    seq = factory.factory_create_new(target + ('/%s' % name))
    seq.MovieScene.FixedFrameInterval = 1.0 / 25.0
    world = ue.get_editor_world()

    cine_camera = world.actor_spawn(CineCameraActor)
    cine_camera.set_actor_label('MainCam')

    camera_cut_track = seq.sequencer_add_camera_cut_track()
    camera = camera_cut_track.sequencer_track_add_section()
    camera_guid = seq.sequencer_add_actor(cine_camera)

    camera.CameraBindingID = MovieSceneObjectBindingID(
        Guid=ue.string_to_guid(camera_guid),
        Space=EMovieSceneObjectBindingSpace.Local
    )

    seq.sequencer_remove_track(seq.sequencer_possessable_tracks(camera_guid)[0])
    transform_track = seq.sequencer_add_track(MovieScene3DTransformTrack, camera_guid)
    transform_section = transform_track.sequencer_track_add_section()
    transform_section.sequencer_import_fbx_transform(fbx_file, source)

    seq.MovieScene.DisplayRate.Numerator = 25.0
    seq.sequencer_changed(True)

    seq.save_package()
