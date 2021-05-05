"""
有限状态机.
"""

from typing import Optional, Dict, List, Iterable


class FSM:
    """ 有限状态机. """

    def __init__(self, states: Iterable, initial=None, handlers=None, transitions: Optional[Dict] = None):
        """ 初始化.

        :param states: 状态列表.  
        :param handlers: 函数列表或字典，其中元素是"状态处理/动作"函数.
            状态处理函数原型为 function(fsm, event) -> None
            动作函数原型为 function(fsm, event) -> next_state  
        :param transitions: 状态迁移表（字典）.
            典型用法是： {s0: [(evt1, s1), (evt2, s2), ...]}  
        :param initial: 初始状态，默认是状态列表第一个状态.
        """
        self._states = list([s for s in states])
        self._initial = initial
        self._handlers = self.__setup_handlers(handlers)
        self._transitions = transitions
        self._current_state = self._states[0]

    def __setup_handlers(self, handlers):
        """ 初始化状态处理/动作字典. """
        ret = {}
        if handlers is not None:
            if isinstance(handlers, dict):
                for k, v in handlers.items():
                    if k in self._states:
                        ret[k] = v
            else:
                for i, v in enumerate(handlers):
                    if i < len(self._states):
                        ret[self._states[i]] = v
        return ret

    def reset(self):
        """ 重置状态. """
        self._current_state = None
        if (self._initial is not None) and (self._initial in self._states):
            self.current_state = self._initial
        if self._current_state is None:
            self._current_state = self._states[0]

    @property
    def current_state(self):
        """ 当前状态. """
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        """ 设置当前状态. """
        if state not in self._states:
            raise ValueError()
        self._current_state = state

    @property
    def states(self):
        """ 获取状态列表. """
        return self._states

    def handle(self, event) -> None:
        """ 处理事件. 
        """
        if self.current_state in self._handlers:
            if handler := self._handlers[self._current_state]:
                next_state = handler(self, event)
                if next_state is not None:
                    self.current_state = next_state
                    return
        if (self._transitions is not None) and (self._current_state in self._transitions):
            transitions = self._transitions[self._current_state]
            for evt, next_state in transitions:
                if evt == event:
                    self.current_state = next_state
                    break
