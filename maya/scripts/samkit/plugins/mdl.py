import pyblish.api


'''
{'family': u'mdl',
 'name': u'Bobo',
 'pathDat': u'P:\\TEMPLATE\\UE\\asset\\CH\\Bobo',
 'pathSrc': u'P:\\TEMPLATE\\asset\\CH\\Bobo\\Bobo_mdl.ma',
 'time': '2019-07-05 16:04:19'}
'''


class ModelTypeValidator(pyblish.api.InstancePlugin):
    """
    Geometry should only be poly mesh.
    """

    order = pyblish.api.ValidatorOrder + 0.01
    label = 'Validate Model Type'
    families = ['mdl']

    def process(self, instance):
        from maya import cmds

        assert cmds.ls(geometry=True), 'No geometry found.'

        for shape in cmds.ls(geometry=True):
            assert cmds.objectType(shape) == 'mesh', '"%s" is NOT a mesh' % shape


class ModelTransformValidator(pyblish.api.InstancePlugin):
    """
    Geometry should have the scale value of 1.0 and rotation value of 0.0.
    """

    order = pyblish.api.ValidatorOrder + 0.02
    label = 'Validate Model Scale'
    families = ['mdl']

    def process(self, instance):
        from maya import cmds

        for shape in cmds.ls(type='mesh'):
            for transform in cmds.listRelatives(shape, allParents=True):
                for sv in cmds.xform(transform, q=True, scale=True, ws=True):
                    assert sv == 1.0, 'Global scale of "%s" is NOT 1.0' % transform
                for rv in cmds.xform(transform, q=True, rotation=True, ws=True):
                    assert rv == 0.0, 'Global rotation of "%s" is NOT 0.0' % transform


class ModelUVSetValidator(pyblish.api.InstancePlugin):
    """
    Geometry should have only one UVSet.
    """

    order = pyblish.api.ValidatorOrder + 0.03
    label = 'Validate Model UVSet'
    families = ['mdl']

    def process(self, instance):
        from maya import cmds

        for shape in cmds.ls(type='mesh'):
            assert len(cmds.polyUVSet(shape, q=True, auv=True)) <= 1, '"%s" has multiply UVSets.' % shape


class ModelHistoryValidator(pyblish.api.InstancePlugin):
    """
    Geometry should have no history.
    """

    order = pyblish.api.ValidatorOrder + 0.03
    label = 'Validate Model History'
    families = ['mdl']

    def process(self, instance):
        from maya import cmds

        for shape in cmds.ls(type='mesh'):
            assert not cmds.listConnections(shape, d=False), '"%s" has construction history.' % shape


class ModelExtractor(pyblish.api.InstancePlugin):

    order = pyblish.api.ExtractorOrder
    label = 'Export FBX Data'
    families = ['mdl']

    def process(self, instance):
        import os
        from maya import cmds, mel

        name = instance.data['name']
        path = instance.data['pathDat'].replace('\\', '/')
        if not os.path.exists(path):
            os.makedirs(path)

        selection_list = []
        for shape in cmds.ls(type='mesh'):
            for transform in cmds.listRelatives(shape, allParents=True):
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
        mel.eval('FBXExportScaleFactor 10.0;')
        mel.eval('FBXExportShapes -v true;')
        mel.eval('FBXExportSkeletonDefinitions -v false;')
        mel.eval('FBXExportSkins -v false;')
        mel.eval('FBXExportSmoothingGroups -v true;')
        mel.eval('FBXExportSmoothMesh -v true;')
        mel.eval('FBXExportTangents -v true;')
        mel.eval('FBXExportUpAxis z;')
        mel.eval('FBXExportUseSceneName -v true;')
        mel.eval('FBXExport -f "{path}/{name}_mdl.fbx" -s'.format(**locals()))
