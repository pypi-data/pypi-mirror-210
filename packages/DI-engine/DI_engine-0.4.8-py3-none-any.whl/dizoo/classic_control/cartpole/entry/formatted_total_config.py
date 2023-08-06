from easydict import EasyDict

main_config = dict(
    env=dict(
        manager=dict(
            episode_num=float('inf'),
            max_retry=1,
            step_timeout=60,
            auto_reset=True,
            reset_timeout=60,
            retry_waiting_time=0.1,
            cfg_type='BaseEnvManagerDict',
        ),
        collector_env_num=8,
        evaluator_env_num=5,
        n_evaluator_episode=5,
        stop_value=195,
    ),
    policy=dict(
        model=dict(
            obs_shape=4,
            action_shape=2,
            encoder_hidden_size_list=[64, 64, 128],
            critic_head_hidden_size=128,
            actor_head_hidden_size=128,
        ),
        learn=dict(
            learner=dict(
                train_iterations=1000000000,
                dataloader=dict(num_workers=0, ),
                hook=dict(
                    load_ckpt_before_run='',
                    log_show_after_iter=100,
                    save_ckpt_after_iter=10000,
                    save_ckpt_after_run=True,
                ),
                cfg_type='BaseLearnerDict',
            ),
            multi_gpu=False,
            update_per_collect=6,
            batch_size=64,
            learning_rate=0.001,
            value_weight=0.5,
            entropy_weight=0.01,
            clip_ratio=0.2,
            adv_norm=False,
            ignore_done=False,
        ),
        collect=dict(
            collector=dict(
                deepcopy_obs=False,
                transform_obs=False,
                collect_print_freq=100,
                cfg_type='SampleCollectorDict',
            ),
            unroll_len=1,
            discount_factor=0.9,
            gae_lambda=0.95,
            n_sample=128,
        ),
        other=dict(
            replay_buffer=dict(
                type='naive',
                replay_buffer_size=1000,
                deepcopy=False,
                enable_track_used_data=False,
                cfg_type='NaiveReplayBufferDict',
            ),
        ),
        cuda=False,
        on_policy=True,
        priority=False,
        priority_IS_weight=False,
        nstep_return=False,
        nstep=3,
        cfg_type='PPOPolicyDict',
    ),
)
main_config = EasyDict(main_config)
main_config = main_config
create_config = dict(
    env=dict(),
    env_manager=dict(cfg_type='BaseEnvManagerDict', ),
    policy=dict(type='dqn'),
)
create_config = EasyDict(create_config)
create_config = create_config
