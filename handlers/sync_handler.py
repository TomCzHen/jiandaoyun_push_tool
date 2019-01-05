from log import logger
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


class Handler:
    def __init__(self, engine, **kwargs):
        self._engine = engine
        self._config = kwargs
        self.__metadata = MetaData()
        self._users_schema = UserSchema(many=True)
        self._departments_schema = DepartmentSchema(many=True)

    @property
    def config(self):
        return self._config

    def handle(self, users, departments):

        users_data = self._users_schema.load(users).data
        departments_data = self._departments_schema.load(departments).data
        relationships_data = []
        for user in users:
            for department in user['departments']:
                data = dict()
                data['department_id'] = department
                data['user_id'] = user['_id']
                relationships_data.append(data)
        try:
            self._sync_to_database(users=users_data, departments=departments_data, relationships=relationships_data)
        except Exception as error:
            logger.error('同步数据出错', exc_info=True)
            raise error
        else:
            logger.info(f'同步用户数据 [{len(users)}] 条，部门数据 [{len(departments)}] 条。')

    def _sync_to_database(self, users, departments, relationships):
        users_table = self._init_users_table()
        departments_table = self._init_departments_table()
        relationships_table = self._init_relationships_table()

        conn = self._engine.connect()
        trans = conn.begin()
        try:
            conn.execute(relationships_table.delete())
            conn.execute(users_table.delete())
            conn.execute(departments_table.delete())

            conn.execute(users_table.insert(), users)
            conn.execute(departments_table.insert(), departments)
            conn.execute(relationships_table.insert(), relationships)
        except Exception as error:
            trans.rollback()
            raise error
        else:
            trans.commit()
        finally:
            conn.close()

    def _init_users_table(self):
        table = Table(
            self.config["users_table"],
            self.__metadata,
            Column('id', String(32), primary_key=True),
            Column('name', String(32), index=True),

        )
        table.create(self._engine, checkfirst=True)
        return table

    def _init_departments_table(self):
        table = Table(
            self.config["departments_table"],
            self.__metadata,
            Column('id', String(32), primary_key=True),
            Column('parent_id', String(32), index=True),
            Column('name', String(32), index=True)
        )
        table.create(self._engine, checkfirst=True)
        return table

    def _init_relationships_table(self):
        table = Table(
            self.config["relationships_table"],
            self.__metadata,
            Column('department_id', String(32), ForeignKey(f'{self.config["departments_table"]}.id')),
            Column('user_id', String(32), ForeignKey(f'{self.config["users_table"]}.id')),
        )
        table.create(self._engine, checkfirst=True)
        return table
