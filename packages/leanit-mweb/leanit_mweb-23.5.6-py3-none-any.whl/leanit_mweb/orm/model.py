from __future__ import annotations

import asyncio
import logging
import threading
from functools import partial

from opentelemetry import  context

from leanit_mweb import YugabytedbThreadPool
from leanit_mweb.orm.fields import Field
from leanit_mweb.utils import camelCaseToSnakeCase

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Dict, TypeVar

if TYPE_CHECKING:
    pass

T = TypeVar('T', bound='Model')

class Model:
    _db: YugabytedbThreadPool = None
    _table = None
    _pk = None

    fields: Dict[str, Field] = {}

    def __init__(self, **kwargs):
        self._created = False
        # shows the difference between the initial values and the current values
        # {"name": ("old name", "new name")}
        self._diff = {}

        # dict of initial values
        self._init_values = kwargs

        # set attributes
        for field_name, field_instance in self.fields.items():
            value = kwargs.get(field_name)
            if value is not None:
                py_value = field_instance.from_db(value)
                setattr(self, field_name, py_value)
            else:
                default_value = field_instance.get_default()
                setattr(self, field_name, default_value)
                self._init_values[field_name] = default_value

    @classmethod
    def create(cls, **kwargs) -> "cls":
        insert_doc = {}

        for field_name, field_instance in cls.fields.items():
            if value := kwargs.get(field_name):
                insert_doc[field_name] = field_instance.to_db(value)
            else:
                value = field_instance.get_default()
                if value is not None:
                    insert_doc[field_name] = value
                    # logger.debug(f"field_name: {field_name}, value: {value}")

        instance = cls(**insert_doc)

        sql = f"INSERT INTO \"{cls._table}\" ({','.join(insert_doc.keys())}) VALUES ({','.join(['%s'] * len(insert_doc))})"
        # logger.debug(f"SQL: {sql}")

        instance.on_pre_create()

        thread_name = threading.current_thread().name
        if thread_name.startswith("yuga"):
            # we are already in the thread pool, just execute
            cls._db.submit_sql(sql, tuple(insert_doc.values()))
        else:
            # schedule in thread pool
            cls._db.execute(sql, tuple(insert_doc.values()))
        instance._created = True
        instance.on_post_create()

        return instance

    @classmethod
    async def create_async(cls, **kwargs) -> "cls":
        """
        Async wrapper for create
        :return:
        """
        callable = partial(cls.create, **kwargs)
        return await asyncio.get_event_loop().run_in_executor(cls._db, callable)

    @classmethod
    def delete_all(cls, **kwargs):
        """
        Delete all rows in the table
        :return:
        """
        where_clause = " AND ".join([f"{field_name} = %s" for field_name in kwargs.keys()])
        sql = f"DELETE FROM \"{cls._table}\" WHERE {where_clause}"
        # cls._db.submit_sql(query, tuple(kwargs.values()))

        tracing_context = context.get_current()
        cls._db.execute(sql, tuple(kwargs.values()), tracing_context)

    async def delete_async(self):
        """
        Async wrapper for delete
        :return:
        """
        pk_values = [getattr(self, pk) for pk in self._pk]
        if not all(pk_values):
            raise ValueError("Primary key value(s) not set for this instance")
        where_clause = " AND ".join([f"{pk} = %s" for pk in self._pk])
        query = f"DELETE FROM \"{self._table}\" WHERE {where_clause}"

        # for tracing context to thread
        tracing_context = context.get_current()

        return await asyncio.get_event_loop().run_in_executor(self._db, self._db.submit_sql, query, pk_values, tracing_context)

    @classmethod
    def get(cls, _only=None, **kwargs) -> T:
        result = cls.filter(_only=_only, _limit=1, **kwargs)
        if result:
            return result[0]
        else:
            return None
    @classmethod
    async def get_async(cls, _only=None, **kwargs) -> T:
        result = await cls.filter_async(_only=_only, _limit=1, **kwargs)
        if result:
            return result[0]
        else:
            return None

    from typing import Dict, List, TypeVar

    T = TypeVar('T', bound='Model')

    @classmethod
    def get_or_create(cls: T, query: Dict[str, any], defaults: Dict[str, any]) -> T:
        """
        This method takes two dictionaries as arguments. The first one is used to query the database,
        and the second one is used to create the object if it does not exist.

        :param query: A dictionary containing the query parameters.
        :param defaults: A dictionary containing the default values for creating a new object.
        :return: An instance of the Model.

        Example usage:

        author = Author.get_or_create(
            query={"tenant_id": 1, "id": 1},
            defaults={"name": "John Doe", "email": "john.doe@example.com"}
        )
        """
        results = cls.filter(**query)
        if results:
            return results[0]
        else:
            create_doc = query.copy()
            create_doc.update(defaults)

            new_object = cls.create(**create_doc)
            # new_object.save()
            return new_object

    @classmethod
    def filter(cls, _only=None, **kwargs):
        field_names = [*cls.fields.keys()]

        sql, values = cls._get_select_query_and_values(_only=field_names, **kwargs)
        # logger.debug(f"SQL: {sql}")

        result = []

        tracing_context = context.get_current()
        rows = cls._db.execute(sql, values, tracing_context)
        for row in rows:
            instance = cls(**dict(zip(field_names, row)))
            instance._created = True

            result.append(instance)

        return result

    @classmethod
    async def filter_async(cls, _only=None, _limit=None, **kwargs):
        field_names = [*cls.fields.keys()]

        sql, values = cls._get_select_query_and_values(_only=field_names, _limit=_limit, **kwargs)

        result = []

        tracing_context = context.get_current()

        rows = await asyncio.get_event_loop().run_in_executor(cls._db, cls._db.submit_sql, sql, values, tracing_context)
        for row in rows:
            instance = cls(**dict(zip(field_names, row)))
            instance._created = True

            result.append(instance)

        return result

    @classmethod
    def _get_select_query_and_values(cls, _only=None, _limit=None, **kwargs):
        operators = {
            "gt": ">",
            "lt": "<",
            "gte": ">=",
            "lte": "<=",
            "ne": "!="
        }
        conditions = []
        values = []
        for key, value in kwargs.items():
            if "__" in key:
                column, op = key.split("__")
                op = operators[op]
            else:
                column = key
                op = "="
            conditions.append(f"{column}{op}%s")
            values.append(value)
        conditions = " AND ".join(conditions)
        if _only:
            columns = ",".join(_only)
        else:
            columns = "*"
        query = f"SELECT {columns} from \"{cls._table}\" where {conditions}"
        if _limit:
            query += f" LIMIT {_limit}"
        return [query, values]

    @classmethod
    def _initialize(cls):
        # initialize fields, this is required
        # otherwise the fields are getting written into the same dict of the parent class
        # Model.fields
        cls.fields = {}

        for field_name, field_instance in cls.__dict__.items():
            if isinstance(field_instance, Field):
                cls.fields[field_name] = field_instance
                field_instance.name = field_name

        if not cls._table:
            # camel cast to snake case with under score
            cls._table = camelCaseToSnakeCase(cls.__name__)

        from leanit_mweb import db
        cls._db = db

        # check for primary key
        if not cls._pk:
            raise Exception(f"Primary key `_pk` not defined for '{cls.__name__}'")
        if type(cls._pk) == str:
            cls._pk = [cls._pk]

    def __str__(self):
        result = f"{self.__class__.__name__}("
        for field_name, field_instance in self.fields.items():
            result += f"{field_name}={getattr(self, field_name)},"
        result += ")"
        return result

    def save(self, tracing_context=None):
        if tracing_context:
            context.attach(tracing_context)

        self._diff = {}

        if self._created:
            # update
            update_doc = {}

            for field_name, old_value in self._init_values.items():
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    update_doc[field_name] = new_value
                    self._diff[field_name] = (old_value, new_value)
                    # update init values
                    self._init_values[field_name] = new_value

            if not update_doc:
                # nothing to update, do not fire update events
                return

            self.on_pre_update()

            if update_doc:
                sql, values = self._get_update_query_and_values(update_doc)

                # logger.debug(f"SQL: {sql}")

                self._db.execute(sql, values, tracing_context)

            self.on_post_update()

        else:
            # create
            create_doc = {}
            for field_name, field_instance in self.fields.items():
                value = getattr(self, field_name)
                if value is not None and not isinstance(value, Field):
                    create_doc[field_name] = value

            self.create(**create_doc)
            self._created = True

        # ensure that the diff is empty
        self._diff = {}

    async def save_async(self):
        """
        Async wrapper for save
        :return:
        """
        tracing_context = context.get_current()
        await asyncio.get_event_loop().run_in_executor(self._db, self.save, tracing_context)

    def _get_update_query_and_values(self, update_doc: Dict):
        set_values = []
        set_args = []
        for key, value in update_doc.items():
            set_values.append(f"{key}=%s")
            set_args.append(value)
        set_values = ",".join(set_values)

        where_values = []
        where_args = []
        for key in self._pk:
            where_values.append(f"{key}=%s")
            where_args.append(getattr(self, key))
        where_values = " AND ".join(where_values)

        query = f"UPDATE \"{self._table}\" SET {set_values} WHERE {where_values}"
        args = set_args + where_args
        return [query, args]

    def on_pre_create(self):
        pass

    def on_post_create(self):
        pass

    def on_pre_update(self):
        pass

    def on_post_update(self):
        pass

    def on_pre_delete(self):
        pass

    def on_post_delete(self):
        pass

    def reload(self, _limit=None):
        where_clause = " AND ".join([f"{field_name} = %s" for field_name in self._pk])
        values = [getattr(self, field_name) for field_name in self._pk]
        if _limit:
            fields = _limit
        else:
            fields = self.fields.keys()

        select_fields = ",".join(fields)

        query = f"SELECT {select_fields} FROM \"{self._table}\" WHERE {where_clause} LIMIT 1"

        tracing_context = context.get_current()
        result = self._db.execute(query, values, tracing_context)

        if not result:
            raise RuntimeError(f"Record not found for {self._table} with {self._pk} = {values}")

        row = result[0]
        for i, field_name in enumerate(fields):
            setattr(self, field_name, row[i])

    @classmethod
    def upsert(cls: T, query: Dict[str, any], update: Dict[str, any]) -> T:
        """
        This method takes two dictionaries as arguments. The first one is used to query the database,
        and the second one is used to update the object if it exists.

        :param query: A dictionary containing the query parameters.
        :param update: A dictionary containing the values to update.
        :return: An instance of the Model.

        Example usage:

        author = Author.upsert(
            query={"tenant_id": 1, "id": 1},
            update={"name": "Jane Doe", "email": "jane.doe@example.com"}
        )
        """
        results = cls.filter(**query)
        if results:
            obj = results[0]
            for key, value in update.items():
                setattr(obj, key, value)
            obj.save()
            return obj

    def to_dict(self) -> Dict[str, any]:
        result = {}
        for field_name, field_instance in self.fields.items():
            result[field_name] = getattr(self, field_name)
        return result
