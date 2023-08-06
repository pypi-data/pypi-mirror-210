from unittest import IsolatedAsyncioTestCase
from ..context import ctx
from ..config import DatabaseConfig
from ..cache import TraceCache, SimpleCache


class MongoMockTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if not ctx.initialised:
            from ..baseapp import BaseApp
            app = BaseApp(".")
            app.initialise()
        ctx.db.reconfigure(DatabaseConfig(), mock=True)

        # aiomcache conflicts with async tests as it seems to run
        # in its own async loop. This leads to "got Future attached to a different loop"
        # errors.
        #
        # Since mongo tests do not use memcached explicitly we override
        # all caches to avoid using MemcachedCache
        ctx._cache_l1 = TraceCache()
        ctx._cache_l2 = SimpleCache()
