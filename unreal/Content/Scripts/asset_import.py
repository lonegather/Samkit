import unreal_engine as ue


def import_asset(stage, source, target, skeleton=None, shot=None):

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
        setup_sequencer(source, target, shot)
        return

    if stage in ['lyt', 'anm']:
        factory.ImportUI.MeshTypeToImport = EFBXImportType.FBXIT_Animation
        data = factory.ImportUI.AnimSequenceImportData
        data.CustomSampleRate = shot['fps']

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


def setup_sequencer(source, target, shot):
    import os
    from importlib import reload
    from unreal_engine.classes import LevelSequenceFactoryNew, CineCameraActor, MovieScene3DTransformTrack, MovieSceneSkeletalAnimationTrack, Character
    from unreal_engine.structs import MovieSceneObjectBindingID
    from unreal_engine.enums import EMovieSceneObjectBindingSpace
    from unreal_engine import FTransform
    import fbx_extract
    reload(fbx_extract)

    name = os.path.basename(source).lower().split('.fbx')[0]
    seq = ue.find_asset('%s/%s.%s' % (target, name, name))
    if seq:
        ue.delete_asset(seq.get_path_name())

    # Create Utility objects
    fps = shot['fps']
    start = shot['start']
    end = shot['end']
    world = ue.get_editor_world()
    factory = LevelSequenceFactoryNew()
    skin_assets = ue.get_assets_by_class('SkeletalMesh')
    anim_assets = ue.get_assets_by_class('AnimSequence')

    # Create LevelSequencer object and setup
    seq = factory.factory_create_new(target + ('/%s' % name))
    seq.MovieScene.DisplayRate.Numerator = fps
    seq.MovieScene.FixedFrameInterval = 1.0 / fps
    seq.sequencer_set_view_range(start / fps, end / fps)
    seq.sequencer_set_working_range(start / fps, end / fps)
    seq.sequencer_set_playback_range(start / fps, end / fps)
    seq.sequencer_changed(True)

    for skin_name, anim_name in zip(shot['chars'], shot['anims']):
        for skin in skin_assets:
            if skin.get_name().count(skin_name):
                break
        for anim in anim_assets:
            if anim.get_name().count(anim_name):
                break
        ue.log_warning(skin.get_name() + ': ' + anim.get_name())

        # spawn a new character and modify it (post_edit_change will allow the editor/sequencer to be notified of actor updates)
        character = world.actor_spawn(Character)
        # notify modifications are about to happen...
        character.modify()
        character.Mesh.SkeletalMesh = skin
        # finalize the actor
        character.post_edit_change()

        # add to the sequencer as a possessable (shortcut method returning the guid as string)
        guid = seq.sequencer_add_actor(character)

        # add an animation track mapped to the just added actor
        anim_track = seq.sequencer_add_track(MovieSceneSkeletalAnimationTrack, guid)

        # create animation section (assign AnimSequence field to set the animation to play)
        anim_section = anim_track.sequencer_track_add_section()
        anim_section.sequencer_set_section_range(start / fps, end / fps)
        anim_section.Params.Animation = anim
        anim_section.RowIndex = 0

    # Create a camera actor in the level
    cine_camera = world.actor_spawn(CineCameraActor)
    cine_camera.set_actor_label('MainCam')

    # Create a camera cut track (only one allowed)
    camera_cut_track = seq.sequencer_add_camera_cut_track()
    seq.sequencer_changed(True)

    # Create camera section upon the track and setup
    camera = camera_cut_track.sequencer_track_add_section()
    camera.sequencer_set_section_range(start / fps, end / fps)

    # Add the camera actor to the LevelSequencer
    camera_guid = seq.sequencer_add_actor(cine_camera)
    ue.log_warning(camera_guid)

    # Bind the camera section with the camera actor through camera id
    camera.CameraBindingID = MovieSceneObjectBindingID(
        Guid=ue.string_to_guid(camera_guid),
        Space=EMovieSceneObjectBindingSpace.Local
    )
    seq.sequencer_changed(True)

    seq.sequencer_remove_track(seq.sequencer_possessable_tracks(camera_guid)[0])
    seq.sequencer_changed(True)
    transform_track = seq.sequencer_add_track(MovieScene3DTransformTrack, camera_guid)
    transform_section = transform_track.sequencer_track_add_section()
    transform_section.sequencer_set_section_range(start / fps, end / fps)
    seq.sequencer_changed(True)

    focal_section = None
    for obj in seq.MovieScene.ObjectBindings:
        for track in obj.tracks:
            if track.sequencer_get_display_name() == 'CurrentFocalLength':
                focal_section = track.sequencer_track_sections()[0]
                focal_section.sequencer_set_section_range(start / fps, end / fps)

    extractor = fbx_extract.FbxCurvesExtractor(source)
    for k, v in extractor.object_keys('MainCam').items():
        transform_section.sequencer_section_add_key(k, FTransform(*v[1:]))
        focal_section.sequencer_section_add_key(k, v[0])

    seq.sequencer_changed(True)

    seq.save_package()
