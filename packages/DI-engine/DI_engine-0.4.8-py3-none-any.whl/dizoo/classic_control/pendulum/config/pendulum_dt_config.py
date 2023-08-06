from easydict import EasyDict
from copy import deepcopy

pendulum_dt_config = dict(
    exp_name='pendulum_dt_seed0',
    env=dict(
        env_id='pendulum-v1',
        evaluator_env_num=5,
        n_evaluator_episode=5,
        stop_value=-250,
        act_scale=True,
        train_data_path='placeholder',
    ),
    policy=dict(
        cuda=True,
        model=dict(
            state_dim=11,
            act_dim=3,
            continuous=True,
        ),
        context_len=20,
        batch_size=64,
        learning_rate=0.0001,
        rtg_target=-250,  # max target return to go
    ),
)

pendulum_dt_config = EasyDict(pendulum_dt_config)
main_config = pendulum_dt_config
pendulum_dt_create_config = dict(
    env=dict(
        type='pendulum',
        import_names=['dizoo.classic_control.pendulum.envs.pendulum_env'],
    ),
    env_manager=dict(type='subprocess'),
    policy=dict(type='dt'),
)
pendulum_dt_create_config = EasyDict(pendulum_dt_create_config)
create_config = pendulum_dt_create_config
# please run `ding/example/dt.py` with this config.
