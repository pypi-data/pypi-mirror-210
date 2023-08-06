import fcntl
from functools import wraps
import sqlite3
from hashlib import sha1
from typing import Callable, List, Optional
from uuid import uuid4

from .loggers import logger

__all__ = ['mock_context', 'is_mock_mode', 'mock_node_id', 'mock_nodes']


_VERSION = 'v1'
_MOCK_DB = f'.mock_{_VERSION}.db'
_FILE_LOCK = '.alphamed.lock'
_mock_conn: sqlite3.Connection = None
_mock_cur: sqlite3.Cursor = None


def _lock_execute(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with open(_FILE_LOCK, 'w') as fl:
            try:
                fcntl.flock(fl, fcntl.LOCK_EX)
                return func(*args, **kwargs)
            finally:
                fcntl.flock(fl, fcntl.LOCK_UN)
    return wrapper


@_lock_execute
def _init_mock_db():
    _mock_cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id    INTEGER   PRIMARY KEY  AUTOINCREMENT,
            target         CHAR(50)  NOT NULL,
            message_title  CHAR(50)  NOT NULL,
            content        TEXT      NOT NULL,
            message_time   INT       NOT NULL,
            channel        CHAR(20)  NOT NULL,
            task_id        CHAR(50)  NOT NULL
        )
        '''
    )
    _mock_cur.execute('CREATE INDEX IF NOT EXISTS contract_task_id ON contracts (task_id);')
    _mock_cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS contract_consume_cursors (
            cursor_id    INT       PRIMARY KEY,
            node_id      CHAR(50)  NOT NULL,
            cursor       INT       NOT NULL
        )
        '''
    )
    _mock_cur.execute('CREATE INDEX IF NOT EXISTS cursor_node_id ON contract_consume_cursors (node_id);')
    _mock_cur.connection.commit()


class mock_context:

    __mock_mode = False
    __nodes = []
    __node_id = None

    def __init__(self,
                 clean: bool = False,
                 id: str = None,
                 nodes: List[str] = None) -> None:
        """Set running context into mock mode.

        Args:
            clean:
                Whether to clean all historical data, and begin from a very clean.
            id:
                A unique ID of the node this process mocks. If not specified, a random
                one will be assigned each time.
            nodes:
                The ID list of ALL node which take part in this mock task. If specified,
                query_nodes returns this list, otherwise it returns an empty list.
                It's all right to use all FAKE ID values but they must not be duplicate.
        """
        assert isinstance(clean, bool), f'clean must be a bool value instead of `{clean}`.'
        assert id is None or isinstance(id, str), f'id must be a str value instead of `{id}`.'
        assert (
            nodes is None or (isinstance(nodes, list)
                              and all(isinstance(_node, str) for _node in nodes))
        ), f'nodes must be a str list instead of `{nodes}`.'

        self.clean = clean
        self.id = id or str(uuid4())
        self.nodes = nodes

    def __enter__(self):
        mock_context._mock_context__mock_mode = True
        if self.nodes:
            mock_context._mock_context__nodes = self.nodes
        else:
            logger.warn('Without specifying nodes, query_nodes returns an empty list.')
        mock_context._mock_context__node_id = self.id

        global _mock_conn
        global _mock_cur
        _mock_conn = sqlite3.connect(_MOCK_DB, check_same_thread=False)
        _mock_conn.row_factory = sqlite3.Row
        _mock_cur = _mock_conn.cursor()
        _init_mock_db()

        if self.clean:
            _mock_cur.execute('DELETE FROM contract_consume_cursors WHERE 1=1')
            _mock_cur.execute('DELETE FROM contracts WHERE 1=1')
            _mock_cur.connection.commit()
        self._init_contract_cursor(node_id=self.id)

    @_lock_execute
    def _init_contract_cursor(self, node_id: str):
        is_exist = _mock_cur.execute(
            'SELECT 1 FROM contract_consume_cursors WHERE node_id=?',
            (node_id,)
        ).fetchone()
        if is_exist is None:
            _mock_cur.execute(
                '''
                INSERT INTO contract_consume_cursors (node_id, cursor)
                VALUES (?, ?)
                ''',
                (node_id, 0)
            )
            _mock_cur.connection.commit()

    def __exit__(self, *exc):
        mock_context._mock_context__mock_mode = False
        mock_context._mock_context__nodes = []
        mock_context._mock_context__node_id = None

        global _mock_conn
        global _mock_cur
        _mock_conn = None
        _mock_cur = None


def is_mock_mode():
    return mock_context._mock_context__mock_mode


def mock_nodes():
    return mock_context._mock_context__nodes


def mock_node_id():
    return mock_context._mock_context__node_id


@_lock_execute
def _put_mock_contract(targets: List[str],
                       message_title: str,
                       content: str,
                       message_time: int,
                       channel: str,
                       task_id: str) -> str:
    _mock_cur.executemany(
        '''
        INSERT INTO contracts (target, message_title, content, message_time, channel, task_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        [(_target, message_title, content, message_time, channel, task_id) for _target in targets]
    )
    _mock_cur.connection.commit()
    max_id = _mock_cur.execute(
        'SELECT MAX(contract_id) FROM contracts'
    ).fetchone()['MAX(contract_id)']
    return sha1(str(max_id).encode()).hexdigest()


@_lock_execute
def _get_mock_contract(node_id: str, channel: str, task_id: str) -> Optional[str]:
    cursor = _mock_cur.execute(
        'SELECT cursor FROM contract_consume_cursors WHERE node_id=?', (node_id,)
    ).fetchone()['cursor']
    contract = _mock_cur.execute(
        '''
        SELECT contract_id, content
        FROM contracts
        WHERE contract_id>:cursor
        AND task_id=:task_id
        AND target=:node_id
        AND channel=:channel
        ORDER BY contract_id
        ''',
        {'cursor': cursor, 'node_id': node_id, 'channel': channel, 'task_id': task_id}
    ).fetchone()
    if contract is None:
        return None

    new_cursor = contract['contract_id']
    _mock_cur.execute(
        'UPDATE contract_consume_cursors SET cursor=:new_cursor WHERE node_id=:node_id',
        {'new_cursor': new_cursor, 'node_id': node_id}
    )
    _mock_cur.connection.commit()
    return contract['content']
