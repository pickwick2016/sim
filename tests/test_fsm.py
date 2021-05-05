import unittest

from sim.fsm import FSM


def s0_act(fsm, evt):
    return None


def s0_handle(fsm, evt):
    if evt == 'a':
        return fsm.states[1]
    return fsm.current_state


def s1_act(fsm, evt):
    print('s1 in action')
    return None


def s1_handle(fsm, evt):
    if evt == 'a':
        return fsm.states[2]
    if evt == 'b':
        return fsm.states[0]
    return fsm.current_state


def s2_act(fsm, evt):
    return None


def s2_handle(fsm, evt):
    if evt == 'a':
        return fsm.states[0]
    if evt == 'b':
        return fsm.states[1]
    return fsm.current_state


def run(fsm: FSM, evts) -> list:
    fsm.reset()
    rets = [fsm.current_state]
    for evt in evts:
        fsm.handle(evt)
        rets.append(fsm.current_state)
    return rets


class TestFSM(unittest.TestCase):
    """ 测试有限状态机. """

    def test_simple_fsm(self):
        states = ['s0', 's1', 's2']
        evts = ['a', 'a', 'b']
        states_out = ['s0', 's1', 's2', 's1']

        # 方法1
        handlers = [s0_handle, s1_handle, s2_handle]  # 每个状态处理包括：动作+转移
        fsm = FSM(states=states, handlers=handlers)
        rets = run(fsm, evts)
        self.assertEqual(rets, states_out)

        handlers = {'s0': s0_handle, 's1': s1_handle, 's2': s2_handle}
        fsm = FSM(states=states, handlers=handlers)
        rets = run(fsm, evts)
        self.assertEqual(rets, states_out)

        handlers = {'s0': s0_handle, 's1': s1_handle}
        fsm = FSM(states=states, handlers=handlers)
        rets = run(fsm, evts)
        self.assertNotEqual(rets, states_out)

        # 方法2
        transitions = {
            's0': [('a', 's1'), ],
            's1': [('a', 's2'), ('b', 's0')],
            's2': [('a', 's0'), ('b', 's1')], }
        fsm = FSM(states=states, transitions=transitions)
        rets = run(fsm, evts)
        self.assertEqual(rets, states_out)

        # 方法3
        handlers = {'s1': s1_act}
        transitions = {
            's0': [('a', 's1'), ],
            's1': [('a', 's2'), ('b', 's0')],
            's2': [('a', 's0'), ('b', 's1')], }
        fsm = FSM(states=states, handlers=handlers, transitions=transitions)
        rets = run(fsm, evts)
        self.assertEqual(rets, states_out)

        # 方法4
        handlers = {'s1': s1_act, 's2': s2_handle}
        transitions = {
            's0': [('a', 's1'), ],
            's1': [('a', 's2'), ('b', 's0')], }
        fsm = FSM(states=states, handlers=handlers, transitions=transitions)
        rets = run(fsm, evts)
        self.assertEqual(rets, states_out)
        
