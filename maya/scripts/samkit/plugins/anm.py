import pyblish.api


class AnimationCharacterCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder + 0.11
    label = 'Collect Influences'
    families = ['anm']

    def process(self, context):
        from maya import cmds

        context.data['references'] = []
        for ref in cmds.ls(type='reference'):
            context.data['references'].append({
                'node': ref,
                'namespace': cmds.referenceQuery(ref, namespace=True),
                'filename': cmds.referenceQuery(ref, filename=True),
            })


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
        path_dir = instance.data['pathDat'].replace('\\', '/')
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        for ref in instance.context.data['references']:
            namespace = ref['namespace']
            path = ref['filename']
            node = ref['node']
            root = cmds.ls(':'.join([namespace, 'Root']))
            selection_list = [root]
            for shape in cmds.ls(type='mesh'):
                if namespace not in shape:
                    continue
                for transform in cmds.listRelatives(shape, allParents=True):
                    # cmds.parent(transform, world=True)
                    selection_list.append(transform)

            cmds.select(selection_list, r=True)

            mel.eval('FBXExportAnimationOnly -v true;')
            mel.eval('FBXExportAxisConversionMethod convertAnimation;')
            mel.eval('FBXExportCameras -v false;')
            mel.eval('FBXExportEmbeddedTextures -v false;')
            mel.eval('FBXExportFileVersion -v FBX201400;')
            mel.eval('FBXExportGenerateLog -v false;')
            mel.eval('FBXExportLights -v false;')
            mel.eval('FBXExportQuaternion -v quaternion;')
            mel.eval('FBXExportReferencedAssetsContent -v true;')
            mel.eval('FBXExportScaleFactor 1.0;')
            mel.eval('FBXExportShapes -v false;')
            mel.eval('FBXExportSkeletonDefinitions -v true;')
            mel.eval('FBXExportSkins -v false;')
            mel.eval('FBXExportSmoothingGroups -v false;')
            mel.eval('FBXExportSmoothMesh -v false;')
            mel.eval('FBXExportTangents -v true;')
            mel.eval('FBXExportUpAxis z;')
            mel.eval('FBXExportUseSceneName -v true;')
            mel.eval('FBXExport -f "{path_dir}/{name}_skn.fbx" -s'.format(**locals()))
