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
        path = instance.data['pathDat'].replace('\\', '/')

        if not os.path.exists(path):
            os.makedirs(path)

        for ref in instance.context.data['references']:
            namespace = ref['namespace']
            if namespace[-4:] != ':skn':
                continue
            
            char = namespace.split(':')[1]
            cmds.select(':'.join([namespace, 'Root']), r=True)

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
