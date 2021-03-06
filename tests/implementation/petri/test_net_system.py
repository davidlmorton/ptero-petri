from .helpers.net_test import NetTest
from ptero_petri.implementation import rom
from ptero_petri.implementation.petri.actions.merge import BasicMergeAction
from ptero_petri.implementation.petri.net import Net
from ptero_petri.implementation.petri.net import ForeignTokenError
from ptero_petri.implementation.petri.net import PlaceNotFoundError
from ptero_petri.implementation.petri.transitions.basic import BasicTransition
from unittest import main


class TestNet(NetTest):

    def setUp(self):
        NetTest.setUp(self)
        self.token = self.create_simple_token()

    def create_simple_token(self, data=None):
        color_group = self.net.add_color_group(size=1)
        return self.net.create_token(color_group.begin, color_group.idx, data)

    def test_put_token_place_not_found(self):
        self.assertRaises(PlaceNotFoundError, self.net.put_token, 0, self.token)

    def test_put_foreign_token(self):
        othernet = Net.create(self.conn, "net2")
        othernet.add_place("home")
        self.assertRaises(ForeignTokenError, othernet.put_token, 0, self.token)

    def test_put_token(self):
        self.net.add_place("start")

        self.assertEqual(0, len(self.net.color_marking))
        self.assertEqual(0, len(self.net.group_marking))

        token_idx = self.token.index.value
        color = self.token.color.value
        color_group_idx = self.token.color_group_idx.value

        place_idx = 0
        color_key = self.net.marking_key(color, place_idx)
        group_key = self.net.marking_key(color_group_idx, place_idx)

        rv = self.net.put_token(place_idx, self.token)

        self.assertEqual(0, rv)
        expected_color_marking = {color_key: token_idx}
        self.assertEqual(expected_color_marking, self.net.color_marking.value)
        self.assertEqual({group_key: 1}, self.net.group_marking.value)

        # make sure putting the same token is idempotent
        rv = self.net.put_token(place_idx, self.token)
        self.assertEqual(0, rv)
        self.assertEqual(expected_color_marking, self.net.color_marking.value)
        self.assertEqual({group_key: 1}, self.net.group_marking.value)

        # make sure putting a new token is an error
        new_token = self.net.create_token(color=color,
                                          color_group_idx=color_group_idx)

        rv = self.net.put_token(place_idx, new_token)
        self.assertEqual(-1, rv)
        self.assertEqual(expected_color_marking, self.net.color_marking.value)
        self.assertEqual({group_key: 1}, self.net.group_marking.value)

    def test_notify_place_no_token(self):
        home = self.net.add_place("home")
        place_idx = home.index.value

        color = 0
        self.net.notify_place(place_idx, color)

        self.assertRaises(rom.NotInRedisError, getattr,
                          home.first_token_timestamp, "value")

    def test_notify_place_wrong_color(self):
        home = self.net.add_place("home")
        place_idx = home.index.value

        self.net.put_token(place_idx, self.token)
        color = self.token.color.value

        self.net.notify_place(place_idx, color + 1)

        self.assertRaises(rom.NotInRedisError, getattr,
                          home.first_token_timestamp, "value")

    def test_delete(self):
        self.net.add_place('p')
        trans = self.net.add_transition(BasicTransition)
        BasicMergeAction.create(self.conn, key=trans.action_key)
        cg = self.net.add_color_group(3)
        self.net.create_token(cg.begin, cg.idx)

        self.net.delete()
        print list(self.net.associated_iterkeys_for_attribute('place'))
        print [i for i in self.net.associated_iterkeys()]

        self.assertEqual([], self.conn.keys())

    def test_expire(self):
        self.net.add_place('p')
        trans = self.net.add_transition(BasicTransition)
        BasicMergeAction.create(self.conn, key=trans.action_key)
        cg = self.net.add_color_group(3)
        self.net.create_token(cg.begin, cg.idx)

        associated_keys = []
        for key in self.net.associated_iterkeys():
            associated_keys.append(key)
        self.assertTrue(len(associated_keys) > 0)

        self.net.expire(0)

        for key in associated_keys:
            self.assertFalse(self.conn.exists(key))

        for key in self.conn.keys('*'):
            self.assertFalse(self.conn.exists(key))


if __name__ == "__main__":
    main()
