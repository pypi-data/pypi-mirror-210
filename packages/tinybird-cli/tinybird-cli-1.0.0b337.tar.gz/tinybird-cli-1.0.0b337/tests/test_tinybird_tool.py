from typing import Any, Dict, Iterable, Optional
import tornado
import uuid
from unittest.mock import patch

from tinybird.cli import cli
from click.testing import CliRunner
from tinybird.syncasync import sync_to_async
from tinybird.tokens import scopes
from tinybird.user import User, UserAccount, Users
from tinybird.ch import ch_table_details_async
from .views.base_test import BaseTest, TBApiProxyAsync
from .utils import CsvIO


class TinybirdToolBaseTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Here we are going to avoid calling setup_redis_client as it already setup in conftest
        cls.patch_setup_redis = patch('tinybird.cli.setup_redis_client')
        cls.patch_setup_redis.start()

    @classmethod
    def tearDownClass(cls):
        cls.patch_setup_redis.stop()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.runner = CliRunner()
        self.tinybird_tool = cli
        self.runner.invoke = sync_to_async(self.runner.invoke, thread_sensitive=False)
        self.workspace = Users.get_by_id(self.WORKSPACE_ID)
        self.user_account = UserAccount.get_by_id(self.USER_ID)
        self.user_admin_token = UserAccount.get_token_for_scope(self.user_account, scopes.AUTH)
        self.admin_token = Users.get_token_for_scope(self.workspace, scopes.ADMIN_USER)
        self.user_token = self.user_account.get_token_for_scope(scopes.AUTH)
        self.workspace_admin_token = Users.get_token_for_scope(self.workspace, scopes.ADMIN)
        self.tb_api_proxy_async = TBApiProxyAsync(self)

    def tearDown(self) -> None:
        super().tearDown()

    async def _tinybird_tool(
        self,
        args: Optional[Iterable[str]] = None,
        input: Optional[str] = None,
        env: Optional[Dict[str, Any]] = None,
        replace_new_line: bool = True,
        assert_exit_code: int = 0
    ) -> str:
        """Calls the tinybird_tool entry point with the `args` passed.

           Also:
           - Allows to pass an `input` string, in case you need to interactively
           control the operation.
           - Allows to pass a custom dict with environment variables in `env`.
           - `replace_new_line` controls how you get the resulting output.
           - `assert_exit_code` indicates the expected exit code for the process
             (0 by default)
        """

        result = await self.runner.invoke(self.tinybird_tool, args, input, env, catch_exceptions=False)
        self.assertEqual(result.exit_code, assert_exit_code, result.stdout_bytes.decode("utf-8"))

        res = result.stdout_bytes.decode("utf-8")
        return res.replace('\n', '') if replace_new_line else res


class TestPopulateAndExchange(TinybirdToolBaseTest):

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    async def _setup(self):
        self.ds_name = f"ds_to_populate_and_exchange_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        await self.tb_api_proxy_async.create_datasource(
            self.workspace_admin_token,
            self.ds_name,
            schema,
            engine_params={'engine': 'MergeTree', 'engine_partition_key': 'd'}
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(self.ds_name)
        await self.tb_api_proxy_async.append_data_to_datasource(self.workspace_admin_token, self.ds_name, CsvIO(
            '12345,1.0,2023-01-01 10:00:00',
            '12346,2.0,2023-01-02 10:00:00',
        ))
        self.wait_for_datasource_replication(self.workspace, self.datasource)

        self.ds_tmp = f"ds_tmp_to_populate_and_exchange_{uuid.uuid4().hex}"
        schema = "uid UInt8, q Float64, v String, d DateTime"
        await self.tb_api_proxy_async.create_datasource(
            self.workspace_admin_token,
            self.ds_tmp,
            schema,
            engine_params={'engine': 'MergeTree', 'engine_partition_key': 'toDate(d)'}
        )
        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource_tmp = self.workspace.get_datasource(self.ds_tmp)
        self.wait_for_datasource_replication(self.workspace, self.datasource_tmp)

    @tornado.testing.gen_test
    async def test_happy_path(self):
        await self._setup()

        output = await self._tinybird_tool(["populate-and-exchange-datasource", self.workspace.id, "--datasource", self.datasource.name,
                                            "--datasource-tmp", self.datasource_tmp.name, "--reference-time-column", "d",
                                            "--reference-time-value", "2023-05-17 10:00:00", "--populate-timeout", "300", "--yes"])
        self.assertIn('Populate finished', output, output)
        self.assertIn('Swapped', output, output)
        self.assertIn('dropped', output, output)

        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(self.ds_name)
        self.wait_for_datasource_replication(self.workspace, self.datasource)
        self.datasource_tmp = self.workspace.get_datasource(self.ds_tmp)
        self.wait_for_datasource_replication(self.workspace, self.datasource_tmp)

        count_ds_name = await self._query(self.workspace_admin_token, f"select count() from {self.ds_name}")
        count_ds_tmp_name = await self._query(self.workspace_admin_token, f"select count() from {self.ds_tmp}")
        self.assertEqual(count_ds_name, 2)
        self.assertEqual(count_ds_tmp_name, 2)

        details = await ch_table_details_async(self.datasource.id, self.workspace.database_server, database=self.workspace.database)
        details_tmp = await ch_table_details_async(self.datasource_tmp.id, self.workspace.database_server, database=self.workspace.database)
        self.assertEqual(details.partition_key, 'toDate(d)')
        self.assertEqual(details_tmp.partition_key, 'd')

    @tornado.testing.gen_test
    async def test_dry_run(self):
        await self._setup()

        output = await self._tinybird_tool(["populate-and-exchange-datasource", self.workspace.id, "--datasource", self.datasource.name,
                                            "--datasource-tmp", self.datasource_tmp.name, "--reference-time-column", "d",
                                            "--reference-time-value", "2023-05-17 10:00:00", "--populate-timeout", "300", "--dry-run", "--yes"])
        self.assertIn("DRY RUN", output, output)

        self.workspace = User.get_by_id(self.workspace.id)
        self.datasource = self.workspace.get_datasource(self.ds_name)
        self.wait_for_datasource_replication(self.workspace, self.datasource)
        self.datasource_tmp = self.workspace.get_datasource(self.ds_tmp)
        self.wait_for_datasource_replication(self.workspace, self.datasource_tmp)

        count_ds_name = await self._query(self.workspace_admin_token, f"select count() from {self.ds_name}")
        count_ds_tmp_name = await self._query(self.workspace_admin_token, f"select count() from {self.ds_tmp}")
        self.assertEqual(count_ds_name, 2)
        self.assertEqual(count_ds_tmp_name, 0)

        details = await ch_table_details_async(self.datasource.id, self.workspace.database_server, database=self.workspace.database)
        details_tmp = await ch_table_details_async(self.datasource_tmp.id, self.workspace.database_server, database=self.workspace.database)
        self.assertEqual(details.partition_key, 'd')
        self.assertEqual(details_tmp.partition_key, 'toDate(d)')

    @tornado.testing.gen_test
    async def test_no_workspace(self):
        await self._setup()

        output = await self._tinybird_tool(["populate-and-exchange-datasource", "unkown workspacee", "--datasource", self.datasource.name,
                                            "--datasource-tmp", self.datasource_tmp.name, "--reference-time-column", "d",
                                            "--reference-time-value", "2023-05-17 10:00:00", "--populate-timeout", "300", "--yes"])
        self.assertIn("doesn't exists", output, output)
