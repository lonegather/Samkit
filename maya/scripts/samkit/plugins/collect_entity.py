import pyblish.api


class EntityCollector(pyblish.api.ContextPlugin):

    order = pyblish.api.CollectorOrder

    def process(self, context):
        from samkit import get_context

        task = get_context()
        context.set_data('label', task['path'])
        instance = context.create_instance(task['entity'])
        instance.data['family'] = task['stage']
