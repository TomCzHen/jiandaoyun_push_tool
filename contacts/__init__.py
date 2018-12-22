from sqlalchemy import Table, Column, String, MetaData, ForeignKey
from marshmallow import Schema, fields


class DepartmentSchema(Schema):
    id = fields.Str(load_from='_id')
    parent_id = fields.Str()
    name = fields.Str()


class UserSchema(Schema):
    id = fields.Str(load_from='_id')
    name = fields.Str()
    departments = fields.List(fields.Str())


class SyncHandler:

    def __init__(self, engine, **kwargs):
        self._engine = engine
        self.departments_table = kwargs.get('departments_table')
        self.users_table = kwargs.get('users_table')
        self.relationships_table = kwargs.get('relationship_table')
        self.__metadata = MetaData()

    @property
    def users_table(self):
        return self._users_table

    @property
    def departments_table(self):
        return self._departments_table

    @property
    def relationships_table(self):
        return self._relationships_table

    @users_table.setter
    def users_table(self, table_name: str):
        self._users_table = Table(
            table_name,
            self.__metadata,
            Column('id', String(32), primary_key=True),
            Column('name', String(32), index=True),

        )

    @departments_table.setter
    def departments_table(self, table_name: str):
        self._departments_table = Table(
            table_name,
            self.__metadata,
            Column('id', String(32), primary_key=True),
            Column('parent_id', String(32), index=True),
            Column('name', String(32), index=True)
        )

    @relationships_table.setter
    def relationships_table(self, table_name: str):
        self._relationships_table = Table(
            table_name,
            self.__metadata,
            Column('department_id', String(32), ForeignKey(f'{self.departments_table.name}.id')),
            Column('user_id', String(32), ForeignKey(f'{self.users_table.name}.id')),
        )

    def sync(self, users: list, departments: list):
        users_schema = UserSchema(many=True)
        users = users_schema.load(users).data

        departments_schema = DepartmentSchema(many=True)
        departments = departments_schema.load(departments).data

        relationships = self._generate_relationships(users)

        conn = self._engine.connect()
        trans = conn.begin()
        try:
            conn.execute(self.relationships_table.delete())
            conn.execute(self.users_table.delete())
            conn.execute(self.departments_table.delete())

            conn.execute(self.users_table.insert(), users)
            conn.execute(self.departments_table.insert(), departments)
            conn.execute(self.relationships_table.insert(), relationships)
        except Exception as error:
            trans.rollback()
            raise error
        else:
            trans.commit()
        finally:
            conn.close()

    @staticmethod
    def _generate_relationships(users: list) -> list:
        relationships = []
        for user in users:
            for department in user['departments']:
                data = dict()
                data['department_id'] = department
                data['user_id'] = user['_id']
                relationships.append(data)

        return relationships
