class DBSessionStore:
    pass


class AHSSessionStore(DBSessionStore):

    def create_model_instance(self, data):

        session_data = super().create_model_instance(data)
        return session_data

