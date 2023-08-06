from viggocore.common import subsystem
from viggoparceiro.subsystem.parceiro import resource, manager

subsystem = subsystem.Subsystem(resource=resource.Parceiro,
                                manager=manager.Manager)
