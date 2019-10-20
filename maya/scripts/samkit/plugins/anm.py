import pyblish.api


'''
class AnimationCharacterCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder + 0.11
    label = 'Collect Character'
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
'''


class AnimationFPSValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.29
    label = 'Validate Animation FPS'
    families = ['blk', 'anm']

    def process(self, instance):
        from maya import cmds

        assert cmds.currentUnit(q=True, time=True) == 'pal', \
            'Current FPS is NOT 25.'

    @staticmethod
    def fix(objects):
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
        project = task['project']
        tag = task['tag']

        mint = int(cmds.playbackOptions(q=1, min=1))
        maxt = int(cmds.playbackOptions(q=1, max=1))
        mins = '%04d' % mint
        maxs = '%04d' % maxt

        if not os.path.exists(path):
            os.makedirs(path)

        for ref in cmds.ls(type='reference'):
            if ref != 'sharedReferenceNode':
                cmds.file(importReference=True, referenceNode=ref)

        for joint in cmds.ls(type='joint'):
            try:
                cmds.getAttr('%s.UE_Skeleton' % joint)
            except ValueError:
                continue

            namespace = ':'+':'.join(joint.split(':')[:-1])
            char = joint.split(':')[0]

            instance.data['message'] = {
                'stage': task['stage'],
                'source': '{path}/{project}_{tag}_{name}_{char}_anm.fbx'.format(**locals()),
                'target': '/Game/%s' % task['path'].split(';')[1],
                'skeleton': char
            }

            cmds.select(joint, r=True)

            if namespace != ':':
                cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

            mel.eval('FBXExportAnimationOnly -v false;')
            mel.eval('FBXExportApplyConstantKeyReducer -v true;')
            mel.eval('FBXExportBakeComplexStart -v %s;' % (mint - 5))
            mel.eval('FBXExportBakeComplexEnd -v %s;' % maxt)
            mel.eval('FBXExportBakeComplexStep -v 1;')
            mel.eval('FBXExportBakeResampleAnimation -v true;')
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
            mel.eval('FBXExport -f "%s" -s' % instance.data['message']['source'])

            samkit.ue_command(instance.data['message'])

        samkit.open_file(task, True)

        try:
            instance.data['message'] = {
                'stage': 'cam',
                'source': '{path}/{project}_{tag}_{name}_MainCam_S{mins}_E{maxs}.fbx'.format(**locals()),
                'target': '/Game/%s' % task['path'].split(';')[1],
                'skeleton': None
            }

            cmds.select('MainCam', r=True)
            mel.eval('FBXExportCameras -v true;')
            mel.eval('FBXExport -f "%s" -s' % instance.data['message']['source'])

            samkit.ue_command(instance.data['message'])

        except ValueError:
            pass
