from viggocore.common.subsystem import operation, manager


class Create(operation.Create):

    def pre(self, **kwargs):
        kwargs['rg_insc_est'] = self.manager.validar_rg_inc_est(**kwargs)
        return super().pre(**kwargs)


class Update(operation.Update):

    def do(self, session, **kwargs):
        kwargs['rg_insc_est'] = self.manager.validar_rg_inc_est(**kwargs)
        return super().do(session, **kwargs)


class Manager(manager.Manager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)

    def validar_rg_inc_est(self, **kwargs):
        rg_insc_est = kwargs.get('rg_insc_est', None)
        if rg_insc_est is not None and len(rg_insc_est.strip()) == 0:
            rg_insc_est = None
        return rg_insc_est
