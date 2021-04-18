"""
场景 Demo.
"""

import sys
sys.path.append('../')

from sim import Scenario, Uav, Jammer, Radar


def print_scene(scene):
    """ 打印场景信息. """
    tt = scene.clock_info()
    print('{:.2f}'.format(tt[0]))

    if uav := scene.find('uav-1'):
        if uav.is_active():
            print('  uav : {} - {}'.format(uav.position, uav.velocity))

    if jammer := scene.find('jammer-1'):
        if jammer.power_on:
            print('  jammer : on')


def render_scene(scene):
    """ 渲染场景. """
    # painter.render(scene)
    pass


def switch_jammer(scene):
    """ 定时开关干扰机. """
    if jammer := scene.find('jammer-1'):
        t, _ = scene.clock_info()
        if abs(t - 7.0) < 0.01:
            jammer.power_on = True
        if abs(t - 11.0) < 0.01:
            jammer.power_on = False


def main():
    scene = Scenario(end=40)
    scene.step_handlers.append(print_scene)
    scene.step_handlers.append(render_scene)
    scene.step_handlers.append(switch_jammer)

    scene.add(Jammer(name='jammer-1', pos=[0, 0]))
    scene.add(Uav(name='uav-1', tracks=[[0, 0], [10, 10]], two_way=True))

    scene.reset()
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
