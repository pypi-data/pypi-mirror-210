from ding.bonus import PPOF

if __name__ == "__main__":
    # lunarlander_discrete
    # agent = PPOF(env='lunarlander_discrete', exp_name='lunarlander_discrete_demo')
    # agent.train(step=int(1e5))
    # lunarlander_continuous
    # agent = PPOF(env='lunarlander_continuous', exp_name='lunarlander_continuous_demo')
    # agent.train(step=int(1e5))
    # rocket landing
    # agent = PPOF(env='rocket_landing', exp_name='rocket_landing_demo')
    # agent.train(step=int(5e6), debug=True)
    # drone fly
    # agent = PPOF(env='drone_fly', exp_name='drone_fly_demo')
    # agent.train(step=int(1e7), debug=False)
    # hybrid_moving
    agent = PPOF(env='hybrid_moving', exp_name='hybrid_moving_demo')
    agent.train(step=int(1e5))
    # agent.deploy()
    # agent.deploy(enable_save_replay=True)
    # agent.collect_data(n_sample=100)
    # agent.batch_evaluate(env_num=4, n_evaluator_episode=8)
