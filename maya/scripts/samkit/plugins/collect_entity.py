import pyblish.api


class EntityCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder

    def process(self, context):
        import samkit

        task = samkit.get_context()
        context.set_data('label', task['path'].split(';')[0])
        instance = context.create_instance(task['entity'])
        instance.data['family'] = task['stage']
        instance.data['pathSrc'] = samkit.get_source_path(task)
        instance.data['pathDat'] = samkit.get_data_path(task)
