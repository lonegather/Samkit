import pyblish.api


class SkinSkeletonValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder + 0.01
    label = 'Detect influences'
    families = ['skn']

    def process(self, instance):
        from maya import cmds

        joints = []
        for shape in cmds.ls(type='mesh'):
            skin = cmds.listConnections(shape, d=False, t='skinCluster')
            if not skin:
                continue
            for joint in cmds.listConnections(skin, d=False, t='joint') or list():
                if joint not in joints:
                    joints.append(joint)

        instance.data['joints'] = joints
        assert len(joints), 'No skin found.'


class SkinRootValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder + 0.02
    label = 'Valid Skeleton Root'
    families = ['skn']

    def process(self, instance):
        from pprint import pprint
        pprint(instance.data)


class SkinExtractor(pyblish.api.InstancePlugin):

    order = pyblish.api.ExtractorOrder
    label = 'Export FBX Data'
    families = ['skn']

    def process(self, instance):
        import os
        from maya import cmds, mel

        name = instance.data['name']
        path = instance.data['pathDat'].replace('\\', '/')
        if not os.path.exists(path):
            os.makedirs(path)

        mel.eval('FBXExportAnimationOnly -v false;')
        mel.eval('FBXExportAxisConversionMethod convertAnimation;')
        mel.eval('FBXExportCameras -v false;')
        mel.eval('FBXExportEmbeddedTextures -v true;')
        mel.eval('FBXExportFileVersion -v FBX201400;')
        mel.eval('FBXExportGenerateLog -v false;')
        mel.eval('FBXExportLights -v false;')
        mel.eval('FBXExportQuaternion -v quaternion;')
        mel.eval('FBXExportReferencedAssetsContent -v true;')
        mel.eval('FBXExportScaleFactor 10.0;')
        mel.eval('FBXExportShapes -v true;')
        mel.eval('FBXExportSkeletonDefinitions -v true;')
        mel.eval('FBXExportSkins -v true;')
        mel.eval('FBXExportSmoothingGroups -v true;')
        mel.eval('FBXExportSmoothMesh -v true;')
        mel.eval('FBXExportTangents -v true;')
        mel.eval('FBXExportUpAxis z;')
        mel.eval('FBXExportUseSceneName -v true;')


