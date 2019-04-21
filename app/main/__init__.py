# -*- coding: utf-8 -*-


def reset():
    from . import models
    
    tables = [
        models.Department, models.Role,
        models.Project, models.Edition, models.Genus, models.Tag,
        models.Entity, models.Stage, models.Status, models.Task
    ]
    
    for table in tables:
        for data in table.objects.all():
            data.delete()

    #Department
    for data in [
        {'name': u'global',    'info': u'统筹'},
        {'name': u'design',    'info': u'原画'},
        {'name': u'modeling',  'info': u'模型'},
        {'name': u'rigging',   'info': u'绑定'},
        {'name': u'animation', 'info': u'动画'},
        {'name': u'rendering', 'info': u'渲染'},
    ]: models.Department(**data).save()

    #Role
    for data in [
        {'name':'staff', 'info':u'制作人员'},
        {'name':'supervisor', 'info':u'组长'},
        {'name':'producer', 'info':u'制片'},
        {'name':'director', 'info':u'导演'},
        {'name':'administrator', 'info':u'管理员'},
    ]: models.Role(**data).save()
    
    #Project
    for data in [
        {'name':u'TEMPLATE', 'info':u'模板项目', 'url':u'file:///P:/TEMPLATE'},
    ]: models.Project(**data).save()
    
    #Edition
    for data in [
        {'name':u'work',    'url_head':u'work',    'url_history':u'history/work'   },
        {'name':u'publish', 'url_head':u'publish', 'url_history':u'history/publish'},
    ]: models.Edition(**data).save()
    
    #Genus
    for data in [
        {'name':'asset', 'info':u'资产', 'url':u'assets'},
        {'name':'shot',  'info':u'镜头', 'url':u'shots' },
        {'name':'batch', 'info':u'批次', 'url':u''      },
    ]: models.Genus(**data).save()
    
    #Tag
    prj = models.Project.objects.get(name='TEMPLATE')
    gns_batch = models.Genus.objects.get(name='batch')
    gns_asset = models.Genus.objects.get(name='asset')
    for data in [
        {'project': prj, 'genus': gns_batch, 'name': u'scene', 'info': u'场次', 'url': u''},
        {'project': prj, 'genus': gns_batch, 'name': u'episode', 'info': u'集数', 'url': u''},
        {'project': prj, 'genus': gns_asset, 'name': u'CH', 'info': u'角色', 'url': u'char'},
        {'project': prj, 'genus': gns_asset, 'name': u'PR', 'info': u'道具', 'url': u'prop'},
        {'project': prj, 'genus': gns_asset, 'name': u'SC', 'info': u'场景', 'url': u'scene'},
    ]: models.Tag(**data).save()
    
    #Stage
    gns_shot = models.Genus.objects.get(name='shot')
    for data in [
        {'project':prj, 'genus':gns_batch, 'name':u'script',      'info':u'剧本', 'path':u'{project}/{stage}/{entity}',               'url':u'scp'},
        {'project':prj, 'genus':gns_batch, 'name':u'storyboard',  'info':u'分镜', 'path':u'{project}/{stage}/{entity}',               'url':u'stb'},
        {'project':prj, 'genus':gns_batch, 'name':u'dubbing',     'info':u'配音', 'path':u'{project}/{stage}/{entity}',               'url':u'dub'},
        {'project':prj, 'genus':gns_asset, 'name':u'design',      'info':u'原画', 'path':u'{project}/{genus}/{tag}/{entity}/{stage}', 'url':u'dsn'},
        {'project':prj, 'genus':gns_asset, 'name':u'modeling',    'info':u'建模', 'path':u'{project}/{genus}/{tag}/{entity}/{stage}', 'url':u'mdl'},
        {'project':prj, 'genus':gns_asset, 'name':u'texture',     'info':u'贴图', 'path':u'{project}/{genus}/{tag}/{entity}/{stage}', 'url':u'txt'},
        {'project':prj, 'genus':gns_asset, 'name':u'shader',      'info':u'材质', 'path':u'{project}/{genus}/{tag}/{entity}/{stage}', 'url':u'shd'},
        {'project':prj, 'genus':gns_asset, 'name':u'skinning',    'info':u'蒙皮', 'path':u'{project}/{genus}/{tag}/{entity}',         'url':u'skn'},
        {'project':prj, 'genus':gns_asset, 'name':u'rigging',     'info':u'绑定', 'path':u'{project}/{genus}/{tag}/{entity}',         'url':u'rig'},
        {'project':prj, 'genus':gns_asset, 'name':u'preview',     'info':u'预览', 'path':u'{project}/{genus}/{tag}/{entity}/{stage}', 'url':u'prv'},
        {'project':prj, 'genus':gns_shot,  'name':u'layout',      'info':u'布局', 'path':u'{project}/{genus}/{stage}',                'url':u'lyt'},
        {'project':prj, 'genus':gns_shot,  'name':u'animation',   'info':u'动画', 'path':u'{project}/{genus}/{stage}',                'url':u'anm'},
        {'project':prj, 'genus':gns_shot,  'name':u'cfx',         'info':u'解算', 'path':u'{project}/{genus}/{stage}',                'url':u'cfx'},
        {'project':prj, 'genus':gns_shot,  'name':u'lighting',    'info':u'灯光', 'path':u'{project}/{genus}/{stage}',                'url':u'lgt'},
        {'project':prj, 'genus':gns_shot,  'name':u'rendering',   'info':u'渲染', 'path':u'{project}/{genus}/{stage}/{tag}/{entity}', 'url':u'rnd'},
        {'project':prj, 'genus':gns_shot,  'name':u'vfx',         'info':u'特效', 'path':u'{project}/{genus}/{stage}/{tag}/{entity}', 'url':u'vfx'},
        {'project':prj, 'genus':gns_shot,  'name':u'compositing', 'info':u'合成', 'path':u'{project}/{genus}/{stage}/{tag}/{entity}', 'url':u'cmp'},
    ]: models.Stage(**data).save()

    # Entity
    tag_eps = models.Tag.objects.get(name='episode', project=prj)
    tag_ch  = models.Tag.objects.get(name='CH', project=prj)
    for data in [
        {'tag':tag_eps, 'name':u'EP01',  'url':u'EP01' },
        {'tag':tag_ch,  'name':u'Danny', 'url':u'Danny'},
    ]: models.Entity(**data).save()
    
    #Status
    edt_work = models.Edition.objects.get(name='work')
    edt_publish = models.Edition.objects.get(name='publish')
    for data in [
        {'edition':edt_work,    'name':u'initialized', 'info':u'初始化'},
        {'edition':edt_work,    'name':u'assigned',    'info':u'已分配'},
        {'edition':edt_work,    'name':u'submitted',   'info':u'已提交'},
        {'edition':edt_publish, 'name':u'approved',    'info':u'已通过'},
        {'edition':edt_work,    'name':u'unapproved',  'info':u'未通过'},
        {'edition':edt_publish, 'name':u'expired',     'info':u'已过期'},
        {'edition':edt_publish, 'name':u'ignored',     'info':u'已忽略'},
    ]: models.Status(**data).save()
    
    #Task
    
    
    pass


if __name__ == "__main__":
    reset()
