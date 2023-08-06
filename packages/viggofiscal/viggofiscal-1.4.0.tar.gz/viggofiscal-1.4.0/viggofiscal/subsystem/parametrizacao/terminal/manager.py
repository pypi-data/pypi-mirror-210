from viggocore.common.subsystem import operation
from viggocore.common import manager


class Create(operation.Create):

    def do(self, session, **kwargs):
        super().do(session=session, **kwargs)

        self.manager.remover_users_de_outros_terminais(
            terminal=self.entity, session=session)

        return self.entity


class Update(operation.Update):

    def do(self, session, **kwargs):
        self.entity = super().do(session=session, **kwargs)

        self.manager.remover_users_de_outros_terminais(
            terminal=self.entity, session=session)

        return self.entity


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.create = Create(self)
        self.update = Update(self)

    def remover_users_de_outros_terminais(self, terminal, session):
        user_ids = terminal.get_user_id_dos_operadores()
        query = """
            DELETE FROM terminal_operador
            WHERE terminal_id <> \'{terminal_id}\' AND
                user_id in {user_ids};
        """
        query = query.format(
            terminal_id=terminal.id,
            user_ids=str(user_ids).replace('[', '(').replace(']', ')'))
        session.execute(query)
