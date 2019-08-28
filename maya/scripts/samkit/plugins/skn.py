import pyblish.api


class SkinJointsCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder + 0.11
    label = 'Collect Influences'
    families = ['skn', 'rig']

    def process(self, context):
        from maya import cmds

        joints = []
        for shape in cmds.ls(type='mesh', noIntermediate=True):
            skin = cmds.listConnections(shape, d=False, t='skinCluster')
            if not skin:
                continue
            for joint in cmds.listConnections(skin, d=False, t='joint') or list():
                if joint not in joints:
                    joints.append(joint)
        context.data['joints'] = joints


class SkinSkeletonValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.39
    label = 'Detect influences'
    families = ['skn', 'rig']

    def process(self, instance):
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        assert len(instance.context.data['joints']), 'No skin found.'


class SkinRootValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.38
    label = 'Validate Skeleton Root'
    families = ['skn', 'rig']

    def process(self, instance):
        from maya import cmds
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        joints_influence = [joint for joint in instance.context.data['joints'] if 'Root' not in joint]
        joints_all = cmds.ls(type='joint')
        root = ''
        for joint in joints_all:
            if 'Root' in joint:
                root = joint
                break
        assert root, \
            'Root joint not found.'

        for rv in cmds.xform(root, q=True, rotation=True, ws=True):
            assert rv == 0.0, \
                'Global rotation of Root is NOT 0.0'

        for tv in cmds.xform(root, q=True, translation=True, ws=True):
            assert tv == 0.0, \
                'Global translation of Root is NOT 0.0'

        joints_children = cmds.listRelatives(root, allDescendents=True) or list()
        assert all(joint in joints_children for joint in joints_influence), \
            'Not all influences are under Root.'

    @staticmethod
    def fix():
        from maya import cmds

        for joint in cmds.ls(type='joint'):
            if 'Root' in joint:
                cmds.select(joint, r=True)
                return False

        cmds.select(cl=True)
        cmds.joint(name='Root')
        return True


class SkinScaleValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.37
    label = 'Validate Skeleton Scale'
    families = ['skn', 'rig']

    def process(self, instance):
        from maya import cmds
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        for joint in instance.context.data['joints']:
            for sv in cmds.xform(joint, q=True, scale=True, ws=True):
                sv_str = '%.2f' % sv
                assert sv_str == '1.00', \
                    'Global scale of %s is NOT 1.0' % joint

    @staticmethod
    def fix():
        from maya import cmds

        joints = []
        for shape in cmds.ls(type='mesh', noIntermediate=True):
            skin = cmds.listConnections(shape, d=False, t='skinCluster')
            if not skin:
                continue
            for joint in cmds.listConnections(skin, d=False, t='joint') or list():
                if joint not in joints:
                    joints.append(joint)

        for joint in joints:
            for sv in cmds.xform(joint, q=True, scale=True, ws=True):
                sv_str = '%.2f' % sv
                if sv_str != '1.00':
                    cmds.select(joint, r=True)
                    return False


class SkinHistoryValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.36
    label = 'Validate Skeleton History'
    families = ['skn', 'rig']

    def process(self, instance):
        from maya import cmds
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        for shape in cmds.ls(type='mesh', noIntermediate=True):
            for node in cmds.listConnections(shape, d=False) or list():
                assert cmds.objectType(node) in [
                    'skinCluster',
                    'objectSet',
                    'tweak',
                    'groupId',
                ], '%s has history other than SkinCluster or BlendShape.' % shape

    @staticmethod
    def fix():
        from maya import cmds

        for shape in cmds.ls(type='mesh', noIntermediate=True):
            for node in cmds.listConnections(shape, d=False) or list():
                if cmds.objectType(node) not in [
                    'skinCluster',
                    'objectSet',
                    'tweak',
                    'groupId',
                ]:
                    cmds.select(shape, r=True)
                    return False


class SkinBlendShapeValidator(pyblish.api.InstancePlugin):

    order = pyblish.api.ValidatorOrder - 0.35
    label = 'Validate Skin BlendShape'
    families = ['skn', 'rig']

    def process(self, instance):
        from maya import cmds
        import samkit

        task = instance.data['task']
        samkit.open_file(task)

        for shape in cmds.ls(type='mesh', noIntermediate=True):
            for obj in cmds.listConnections(shape, type='objectSet', d=False) or list():
                for bs in cmds.listConnections(obj, type='blendShape', d=False) or list():
                    assert not cmds.listConnections(bs, d=False), \
                        '%s\'s BlendShape must have NO history.' % shape

    @staticmethod
    def fix():
        from maya import cmds

        for shape in cmds.ls(type='mesh', noIntermediate=True):
            for obj in cmds.listConnections(shape, type='objectSet', d=False) or list():
                for bs in cmds.listConnections(obj, type='blendShape', d=False) or list():
                    if cmds.listConnections(bs, d=False):
                        cmds.select(shape, r=True)
                        return False


class SkinExtractor(pyblish.api.InstancePlugin):

    order = pyblish.api.ExtractorOrder
    label = 'Export FBX Data'
    families = ['skn', 'rig']

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

        root = cmds.ls('Root', type='joint')[0]
        # cmds.parent(root, world=True)

        selection_list = [root]
        for shape in cmds.ls(type='mesh', noIntermediate=True):
            for transform in cmds.listRelatives(shape, allParents=True):
                # cmds.parent(transform, world=True)
                selection_list.append(transform)

        cmds.select(selection_list, r=True)

        mel.eval('FBXExportAnimationOnly -v false;')
        mel.eval('FBXExportAxisConversionMethod convertAnimation;')
        mel.eval('FBXExportCameras -v false;')
        mel.eval('FBXExportEmbeddedTextures -v true;')
        mel.eval('FBXExportFileVersion -v FBX201400;')
        mel.eval('FBXExportGenerateLog -v false;')
        mel.eval('FBXExportLights -v false;')
        mel.eval('FBXExportQuaternion -v quaternion;')
        mel.eval('FBXExportReferencedAssetsContent -v true;')
        mel.eval('FBXExportScaleFactor 1.0;')
        mel.eval('FBXExportShapes -v true;')
        mel.eval('FBXExportSkeletonDefinitions -v true;')
        mel.eval('FBXExportSkins -v true;')
        mel.eval('FBXExportSmoothingGroups -v true;')
        mel.eval('FBXExportSmoothMesh -v true;')
        mel.eval('FBXExportTangents -v true;')
        mel.eval('FBXExportUpAxis z;')
        mel.eval('FBXExportUseSceneName -v true;')
        mel.eval('FBXExport -f "{path}/{name}_skn.fbx" -s'.format(**locals()))


