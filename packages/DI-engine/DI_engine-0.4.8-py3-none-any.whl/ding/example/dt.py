import gym
from ditk import logging
from ding.model import DecisionTransformer
from ding.policy import DTPolicy
from ding.envs import DingEnvWrapper, BaseEnvManagerV2, SubprocessEnvManagerV2
from ding.utils.data import create_offline_dataset
from ding.config import compile_config
from ding.framework import task, ding_init
from ding.framework.context import OfflineRLContext
from ding.framework.middleware import interaction_evaluator, trainer, CkptSaver, offline_data_fetcher, offline_logger
from ding.utils import set_pkg_seed
from dizoo.classic_control.pendulum.config.pendulum_dt_config import main_config, create_config


def main():
    # If you don't have offline data, you need to prepare if first and set the data_path in config
    # For demostration, we also can train a RL policy (e.g. SAC) and collect some data
    logging.getLogger().setLevel(logging.INFO)
    main_config.env.train_data_path = 'pendulum_sac_data_generation/pendulum_expert.hdf5'
    cfg = compile_config(main_config, create_cfg=create_config, auto=True)
    ding_init(cfg)
    with task.start(ctx=OfflineRLContext()):
        #evaluator_env = SubprocessEnvManagerV2(
        #    env_fn=[lambda: PendulumEnv(cfg.env) for _ in range(cfg.env.evaluator_env_num)], cfg=cfg.env.manager
        #)
        evaluator_env = BaseEnvManagerV2(
            env_fn=[lambda: DingEnvWrapper(gym.make('Pendulum-v1')) for _ in range(cfg.env.evaluator_env_num)],
            cfg=cfg.env.manager
        )

        set_pkg_seed(cfg.seed, use_cuda=cfg.policy.cuda)

        dataset = create_offline_dataset(
            'traj', dataset_path=cfg.env.train_data_path, context_len=cfg.policy.context_len
        )
        model = DecisionTransformer(**cfg.policy.model)
        policy = DTPolicy(cfg.policy, model=model)

        #task.use(interaction_evaluator(cfg, policy.eval_mode, evaluator_env))
        task.use(offline_data_fetcher(cfg, dataset))
        task.use(trainer(cfg, policy.learn_mode))
        task.use(CkptSaver(policy, cfg.exp_name, train_freq=int(1e3)))
        task.use(offline_logger())
        task.run()


if __name__ == "__main__":
    main()
