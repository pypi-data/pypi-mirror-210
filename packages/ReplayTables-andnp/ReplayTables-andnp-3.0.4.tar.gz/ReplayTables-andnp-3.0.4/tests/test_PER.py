import unittest
import pickle
import numpy as np
from typing import cast, NamedTuple

from ReplayTables.ReplayBuffer import EIDS
from ReplayTables.PER import PrioritizedReplay

class Data(NamedTuple):
    a: float
    b: int


class TestPER(unittest.TestCase):
    def test_simple_buffer(self):
        rng = np.random.default_rng(0)
        buffer = PrioritizedReplay(5, Data, rng)

        # on creation, the buffer should have no size
        self.assertEqual(buffer.size(), 0)

        # should be able to simply add and sample a single data point
        d = Data(a=0.1, b=1)
        buffer.add(d)
        self.assertEqual(buffer.size(), 1)
        samples, idxs, weights = buffer.sample(10)
        self.assertTrue(np.all(samples.b == 1))
        self.assertTrue(np.all(idxs == 0))
        self.assertTrue(np.all(weights == 0.2))

        # should be able to add a few more points
        for i in range(4):
            x = i + 2
            buffer.add(Data(a=x / 10, b=x))

        self.assertEqual(buffer.size(), 5)
        samples, idxs, weights = buffer.sample(1000)

        unique = np.unique(samples.b)
        unique.sort()

        self.assertTrue(np.all(unique == np.array([1, 2, 3, 4, 5])))

        # buffer drops the oldest element when over max size
        buffer.add(Data(a=0.6, b=6))
        self.assertEqual(buffer.size(), 5)

        samples, _, _ = buffer.sample(1000)
        unique = np.unique(samples.b)
        unique.sort()
        self.assertTrue(np.all(unique == np.array([2, 3, 4, 5, 6])))

    def test_priority_on_add(self):
        rng = np.random.default_rng(0)
        buffer = PrioritizedReplay(5, Data, rng)

        d = Data(a=0.1, b=1)
        buffer.add(d, priority=1)
        d = Data(a=0.2, b=2)
        buffer.add(d, priority=2)

        batch, _, _ = buffer.sample(128)

        b = np.sum(batch.b == 2)
        a = np.sum(batch.b == 1)

        self.assertEqual(b, 91)
        self.assertEqual(a, 37)

    def test_pickeable(self):
        rng = np.random.default_rng(0)
        buffer = PrioritizedReplay(5, Data, rng)

        for i in range(5):
            buffer.add(Data(i, 2 * i))

        ids = cast(EIDS, np.arange(5))
        buffer.update_priorities(ids, np.arange(5) + 1)

        byt = pickle.dumps(buffer)
        buffer2 = pickle.loads(byt)

        s, _, _ = buffer.sample(20)
        s2, _, _ = buffer2.sample(20)

        self.assertTrue(np.all(s.a == s2.a) and np.all(s.b == s2.b))
