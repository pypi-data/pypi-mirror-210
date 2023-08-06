from __future__ import annotations

import base64
import logging
import os
import sys
from collections import defaultdict
from datetime import timedelta, datetime
from os.path import isabs, abspath
from pprint import pprint

import yaml
from fastapi import FastAPI, Depends, HTTPException
from jose import jwt, JWTError

from leanit_mweb.jinja_template import Jinja2Templates
from leanit_mweb.jinja_template.loaders import FileSystemLoader
from leanit_mweb.utils import merge_dict


from leanit_mweb.yuga import YugabytedbThreadPool
from starlette import status

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Dict, Annotated, Any

if TYPE_CHECKING:
    from leanit_mweb.orm.model import Model

config: Dict = None
db: YugabytedbThreadPool = None
loader: FileSystemLoader = None
templates: Jinja2Templates = None

# auth
secret_key = None
algorithm = None
pwd_context = None
access_token_expire_minutes = None
oauth2_scheme = None
auth_user_model = None

app = None

class App(FastAPI):

    def __init__(self, app_root: str, enable_static=False):
        global config, app
        app = self

        self.app_root = app_root

        config = self.config = self._read_config()

        super().__init__()

        if enable_static:
            # mount static files
            from leanit_mweb.staticfiles import StaticFiles
            self.mount("/static", StaticFiles(directory=f"{app_root}/static"), name="static")

    def enable_auth(self, user_model):
        """
        :param user_model: Model class for user
        :type user_model: Model
        :return:
        """
        global secret_key, algorithm, pwd_context, access_token_expire_minutes, oauth2_scheme, auth_user_model

        # user_model
        auth_config = self.config.get("auth", {})

        secret_key = auth_config.get("secret_key", None)
        if not secret_key:
            logger.error("No secret key found in config (auth.secret_key)")
            exit(1)

        algorithm = auth_config.get("algorithm", "HS256")
        access_token_expire_minutes = auth_config.get("access_token_expire_minutes", 30)

        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
        oauth2_scheme = oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        auth_user_model = user_model

    def enable_db(self):
        global db

        db_config = config["db"]
        pool_config = db_config.get("pool", {})
        db = YugabytedbThreadPool(
            min_workers=pool_config.get("min_workers", 1),
            max_workers=pool_config.get("max_workers", 10),
        )
        db.migrate(migration_dir=f"{self.app_root}/migrations")

        # get all subclasses of Model
        from leanit_mweb.orm.model import Model
        # initialize all models
        for cls in Model.__subclasses__():  # type: Model
            cls._initialize()

        # initialize objects
        init_objects = db_config.get("init_objects", [])
        if init_objects:
            def _handle_object(obj_cls, query: Dict, obj_attributes: Dict):
                obj = obj_cls.get(**query)
                if obj:
                    # update object
                    for key, value in obj_attributes.items():
                        setattr(obj, key, value)
                    obj.save()
                else:
                    # create object
                    obj = obj_cls.create(**obj_attributes)

            batches = defaultdict(list)

            counter = 1
            for obj in init_objects:
                obj_type = obj["type"]
                logger.info(f"[init-objects] ({counter}/{len(init_objects)}) {obj_type}")
                obj_attributes = obj["attributes"]

                # obj_type is a string with the fully qualified name of the class, e.g. "incloud_auth.models.User", import it
                try:
                    module_name, class_name = obj_type.rsplit(".", 1)
                except ValueError as e:
                    raise RuntimeError(f"Infalid object type for init object ({counter}): {obj_type}")

                module = __import__(module_name, fromlist=[class_name])
                obj_cls: Model = getattr(module, class_name)

                primary_key_field_names = obj_cls._pk
                # dict of primary key values, like {"id": 4}
                query: Dict[str, Any] = {attribute_name: obj_attributes[attribute_name] for attribute_name in
                                         primary_key_field_names}

                batch_id: int = obj.get("batch", counter)
                batches[batch_id].append(
                    (_handle_object, obj_cls, query, obj_attributes)
                )

                # submit to thread pool, so that it can be executed in parallel
                # db.submit(_handle_object, obj_cls, query, obj_attributes)
                counter += 1

            batch_ids = [*batches.keys()]
            batch_ids.sort()

            for batch_id in batch_ids:
                batch = batches[batch_id]
                logger.info(f"[init-objects] starting batch {batch_id} with {len(batch)} items")

                # schedule all functions in this batch
                futures = []
                for func, *args in batch:
                    futures.append(db.submit(func, *args))

                # wait for all futures to finish
                for future in futures:
                    future.result()

                logger.info(f"[init-objects] batch {batch_id} finished")

    def enable_tracing(self):
        tracing_config = config.get("tracing", {})
        if not tracing_config.get("enabled", False):
            logger.info("Tracing is disabled")
            return

        try:
            service_name = tracing_config["service_name"]
        except KeyError:
            logger.error("No service name found in config (tracing.service_name)")
            exit(1)

        try:
            tracing_endpoint = tracing_config["endpoint"]
        except KeyError:
            logger.error("No endpoint found in config (tracing.endpoint)")
            exit(1)

        exporter_headers = {}

        username = tracing_config.get("username", None)
        password = tracing_config.get("password", None)

        if username and password:
            base64_creds = base64.b64encode(f'{username}:{password}'.encode()).decode()
            exporter_headers['authorization'] = f'Basic {base64_creds}'

        from opentelemetry.sdk.resources import Resource
        resource = Resource(attributes={"service.name": service_name})

        # set the tracer provider
        from opentelemetry.sdk.trace import TracerProvider
        tracer_provider = TracerProvider(resource=resource)
        from opentelemetry import trace
        trace.set_tracer_provider(tracer_provider)

        # no batching as we are using Grafana Agent which does the batching for us
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from grpc import Compression
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=tracing_endpoint,
                    insecure=tracing_config.get("insecure", False),
                    headers=exporter_headers,
                    compression=Compression.Gzip,
                ),
                # represents the maximum queue size for the data export of the
                max_queue_size=int(tracing_config.get("max_queue_size", 2048)), # default is 2048
                # represents the maximum batch size for the data export
                # puts this many spans in one batch, must be less than or equal to max_queue_size
                max_export_batch_size=int(tracing_config.get("max_export_batch_size", 512)), # default is 512
                # represents the delay interval between two consecutive exports
                schedule_delay_millis=int(tracing_config.get("schedule_delay_millis", 5000)), # default is 5000
                # represents the maximum allowed time to export data
                export_timeout_millis=int(tracing_config.get("export_timeout_millis", 30000)), # default is 30000
            )
        )

        trace_debug = tracing_config.get("debug", False)
        if trace_debug:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            tracer_provider.add_span_processor(
                SimpleSpanProcessor(ConsoleSpanExporter())
            )

        # instrument fastapi
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(self, tracer_provider=tracer_provider)

        # instrument aiohttp
        import aiohttp
        from opentelemetry.instrumentation.aiohttp_client import (
            AioHttpClientInstrumentor
        )

        # Enable instrumentation
        AioHttpClientInstrumentor().instrument()

    def initialize(self):
        # do your initialization here
        pass

    def _is_unittest_run(self) -> bool:
        """
        sys.argv:

        run by pycharm:
            ['/snap/pycharm-professional/333/plugins/python/helpers/pycharm/_jb_pytest_runner.py', 'test_healthz.py::test_register']
        """
        command = sys.argv[0]
        if command.endswith("_jb_pytest_runner.py"):
            return True
        return False

    def _read_config(self) -> Dict:
        config_data = {}

        # check if this is a unittest run
        if self._is_unittest_run():
            config_profile = "unittest"
        else:
            # not a unittest run
            config_profile = os.environ.get("CONFIG_PROFILE", "default")

        config_dir = f"{self.app_root}/etc/{config_profile}"

        config_files = os.listdir(config_dir)
        # ensure that config files are read in alphabetical order
        config_files.sort()

        for config_file in config_files:
            # only read .yml and .yaml files
            if not config_file.endswith(".yml") and not config_file.endswith(".yaml"):
                continue
            config_file_abs = f"{config_dir}/{config_file}"

            logger.info(f"Reading config from {config_file_abs}")

            # read yaml config
            with open(config_file_abs, "r") as f:
                sub_config = yaml.safe_load(f)
                if sub_config:
                    merge_dict(source=sub_config, destination=config_data)

        return config_data

    def setup(self) -> None:
        super().setup()

        if "db" in config:
            self.enable_db()

        global loader, templates
        loader = FileSystemLoader(f"{self.app_root}/templates")
        templates = Jinja2Templates(directory=f"{self.app_root}/templates", loader=loader)

        if "tracing" in config:
            self.enable_tracing()

        self.initialize()
