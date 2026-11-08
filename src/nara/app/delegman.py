from ..plug import Plug
from ..utils import parse

class Delegman(Plug):

    addToApp=False

    def setup(self):
        super().setup()
        self.m_agents={}

    def add(self, obj):
        for fname in obj.__dir__():
            func = getattr(obj, fname, None)
            has_delegate = getattr(func, "hasDelegate", None)
            if has_delegate:
                tag = getattr(func, "deleg", "")
                deleg=parse.parse_deleg(tag)
                for data in deleg:
                    data['functor']=func
                self.addAgent(**data)

    def addAgent(
            self, 
            mode='any', 
            submode='any', 
            view='any', 
            subview='any',
            action=None,
            model='any',
            submodel='any',
            functor=None,
            ):
        if not mode in self.m_agents:
            self.m_agents[mode]={}
        modes=self.m_agents[mode]
        if not submode in modes:
            modes[submode]={}
        submodes=modes[submode]
        if not view in submodes:
            submodes[view]={}
        views=submodes[view]
        if not subview in views:
            views[subview]={}
        subviews=views[subview]
        # views[subview][action]=functor
        if not model in subviews:
            subviews[model]={}
        models=subviews[model]
        if not submodel in models:
            models[submodel]={}
        models[submodel][action]=functor

    def getAgent(
            self, 
            mode='any', 
            submode='any', 
            view='any', 
            subview='any',
            model='any',
            submodel='any',
            action='any', 
            delegate='action', 
            view_approach='super',
            subview_approach='super',
            model_approach='super',
            submodel_approach='super',
            ):
        if delegate=='mode':
            return self.m_agents.get(mode, {})
        elif delegate=='submode':
            modes=self.getAgent(mode=mode, delegate='mode')
            return modes.get(submode, {})
        elif delegate=='view':
            submodes=self.getAgent(mode, submode, delegate='submode')
            if view is None or type(view)==str:
                return submodes.get(view, {})
            else: 
                if view_approach=='own':
                    view_name=view.__class__.__name__
                    return submodes.get(view_name, {})
                elif view_approach=='super':
                    all_views={}
                    for klass in view.__class__.__mro__:
                        view_name=klass.__name__
                        views=submodes.get(view_name, {})
                        all_views.update(views)
                    return all_views
                elif view_approach=='manager':
                    all_views={}
                    manager=view.manager()
                    while manager:
                        name=manager.__class__.__name__
                        views=submodes.get(name, {})
                        all_views.update(views)
                        if not manager: break
                        manager=manager.manager()
                    return all_views
        elif delegate=='subview':
            views=self.getAgent(mode, submode, view, delegate='view')
            if subview is None or type(subview)==str:
                return views.get(subview, {})
            else: 
                if subview_approach=='own':
                    view_name=subview.__class__.__name__
                    return views.get(view_name, {})
                elif subview_approach=='super':
                    all_views={}
                    for klass in subview.__class__.__mro__:
                        view_name=klass.__name__
                        views=views.get(view_name, {})
                        all_views.update(views)
                    return all_views
                elif subview_approach=='manager':
                    all_views={}
                    manager=view.manager()
                    while manager:
                        name=manager.__class__.__name__
                        views=submodes.get(name, {})
                        all_views.update(views)
                        if not manager: break
                        manager=manager.manager()
                    return all_views
        elif delegate=='model':
            subviews=self.getAgent(mode, submode, view, subview, delegate='subview')
            if model is None or type(model)==str:
                return subviews.get(model, {})
            else: 
                if model_approach=='own':
                    model_name=model.__class__.__name__
                    return subviews.get(model_name, {})
                elif model_approach=='super':
                    all_models={}
                    for klass in model.__class__.__mro__:
                        model_name=klass.__name__
                        models=subviews.get(model_name, {})
                        all_models.update(models)
                    return all_models
        elif delegate=='submodel':
            models=self.getAgent(mode, submode, view, subview, model, delegate='model')
            if submodel is None or type(submodel)==str:
                return models.get(submodel, {})
            else: 
                if submodel_approach=='own':
                    submodel_name=submodel.__class__.__name__
                    return models.get(submodel_name, {})
                elif submodel_approach=='super':
                    all_models={}
                    for klass in submodel.__class__.__mro__:
                        submodel_name=klass.__name__
                        models=models.get(submodel_name, {})
                        all_models.update(models)
                    return all_models
        elif delegate=='action':
            subviews=self.getAgent(mode, submode, view, subview, model, submodel, delegate='submodel')
            return subviews.get(action, {})
        return {}

    def delegate(
            self, 
            mode='any', 
            submode='any', 
            view='any', 
            subview='any',
            model='any',
            submodel='any',
            action='any', 
            view_approach='super',
            subview_approach='super',
            model_approach='super',
            submodel_approach='super',
            delegate='action',
            data={},
            add_fields=['view', 'subview', 'model', 'submodel', 'action'],
            ):
        functor=self.getAgent(
                mode=mode, 
                submode=submode, 
                view=view, 
                subview=subview,
                model=model,
                submodel=submodel,
                action=action, 
                delegate=delegate,
                view_approach=view_approach,
                subview_approach=subview_approach,
                model_approach=model_approach,
                submodel_approach=submodel_approach
                )
        if functor and delegate=='action':
            if add_fields:
                for field in add_fields:
                    if not field in data:
                        if field=='mode':
                            data[field]=mode
                        elif field=='submode':
                            data[field]=submode
                        elif field=='action':
                            data[field]=action
                        elif field=='view':
                            data[field]=view
                        elif field=='subview':
                            data[field]=subview
                        elif field=='model':
                            data[field]=model
                        elif field=='submodel':
                            data[field]=submodel
            return functor(**data)
        return functor
