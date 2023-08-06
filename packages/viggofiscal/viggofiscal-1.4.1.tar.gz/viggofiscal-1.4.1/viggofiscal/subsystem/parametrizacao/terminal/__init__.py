from viggocore.common import subsystem
from viggofiscal.subsystem.parametrizacao.terminal \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.Terminal,
                                manager=manager.Manager)
