import pyblish.api


class AnimationCharacterCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder + 0.11
    label = 'Collect Influences'
    families = ['blk', 'anm']

    def process(self, context):
        from maya import cmds

        context.data['references'] = []
        for ref in cmds.ls(type='reference'):
            context.data['references'].append({
                'node': ref,
                'namespace': cmds.referenceQuery(ref, namespace=True),
                'filename': cmds.referenceQuery(ref, filename=True),
            })


class AnimationFPSValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.29
    label = 'Validate Animation FPS'
    families = ['blk', 'anm']

    def process(self, instance):
        from maya import cmds

        assert cmds.currentUnit(q=True, time=True) == 'pal', \
            'Current FPS is NOT 25.'

    @staticmethod
    def fix():
        from maya import cmds

        cmds.currentUnit(time='pal', updateAnimation=False)
        return True


class AnimationCameraValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.28
    label = 'Validate Animation Camera'
    families = ['blk', 'anm']

    def process(self, instance):
        from maya import cmds

        for shape in cmds.ls(type='camera'):
            cam = cmds.listRelatives(shape, allParents=True)[0]
            if cam == 'MainCam':
                return
        assert False, 'MainCam NOT found.'


class AnimationExtractor(pyblish.api.InstancePlugin):

    order = pyblish.api.ExtractorOrder
    label = 'Export FBX Data'
    families = ['anm']

    def process(self, instance):
        import os
        from maya import cmds, mel
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        name = instance.data['name']
        path = instance.data['pathDat'].replace('\\', '/')

        if not os.path.exists(path):
            os.makedirs(path)

        for joint in cmds.ls(type='joint'):
            if 'Root' not in joint:
                continue

            char = joint.split(':')[0]
            cmds.select(joint, r=True)

            mel.eval('FBXExportAnimationOnly -v true;')
            mel.eval('FBXExportAxisConversionMethod convertAnimation;')
            mel.eval('FBXExportBakeComplexAnimation -v true;')
            mel.eval('FBXExportCameras -v false;')
            mel.eval('FBXExportConstraints -v false;')
            mel.eval('FBXExportEmbeddedTextures -v false;')
            mel.eval('FBXExportFileVersion -v FBX201400;')
            mel.eval('FBXExportGenerateLog -v false;')
            mel.eval('FBXExportLights -v false;')
            mel.eval('FBXExportQuaternion -v quaternion;')
            mel.eval('FBXExportReferencedAssetsContent -v false;')
            mel.eval('FBXExportScaleFactor 1.0;')
            mel.eval('FBXExportShapes -v false;')
            mel.eval('FBXExportSkeletonDefinitions -v false;')
            mel.eval('FBXExportSkins -v false;')
            mel.eval('FBXExportSmoothingGroups -v false;')
            mel.eval('FBXExportSmoothMesh -v false;')
            mel.eval('FBXExportTangents -v true;')
            mel.eval('FBXExportUpAxis z;')
            mel.eval('FBXExportUseSceneName -v true;')
            mel.eval('FBXExport -f "{path}/{name}_{char}_anm.fbx" -s'.format(**locals()))

        cmds.select('MainCam', r=True)
        mel.eval('FBXExportCameras -v true;')
        mel.eval('FBXExport -f "{path}/{name}_MainCam_anm.fbx" -s'.format(**locals()))
