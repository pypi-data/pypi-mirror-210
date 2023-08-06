import imageio

from dizoo.box2d.lunarlander.config.lunarlander_cont_dqn_vqvae_ensemble_generation_config import main_config, \
    create_config
from ding.entry import serial_pipeline_dqn_vqvae_visualize
from ding.entry import collect_episodic_demo_data, eval
import torch
import copy
import torch
from torch.utils.data import DataLoader
from ding.torch_utils import to_ndarray, to_list, to_tensor
from ding.config import read_config, compile_config
from ding.utils.data import create_dataset
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os


def train(args):
    # config = [main_config, create_config]
    config = [copy.deepcopy(main_config), copy.deepcopy(create_config)]
    input_cfg = config
    if isinstance(input_cfg, str):
        cfg, create_cfg = read_config(input_cfg)
    else:
        cfg, create_cfg = input_cfg
    create_cfg.policy.type = create_cfg.policy.type + '_command'
    cfg = compile_config(cfg, seed=args.seed, auto=True, create_cfg=create_cfg)

    # TODO(pu)
    cfg.policy.model_path = '/Users/puyuan/code/DI-engine/data_lunarlander/dqn_sbh_ensemble20_obs0_noema_smallnet_k8_upc50_crlw1_seed1_3M/ckpt/iteration_190000.pth.tar',
    cfg.policy.collect.data_path = '/Users/puyuan/code/DI-engine/data_lunarlander_visualize/dqn_sbh_ensemble20_obs0_noema_smallnet_k8_upc50_crlw1_seed1_3M/iter-190000_collect_in_seed2/data_iter-190000_1eps.pkl'
    visualize_path = '/Users/puyuan/code/DI-engine/data_lunarlander_visualize/dqn_sbh_ensemble20_obs0_noema_smallnet_k8_upc50_crlw1_seed1_3M/iter-190000_collect_in_seed2/'
    original_gif_path = '/Users/puyuan/code/DI-engine/data_lunarlander_visualize/dqn_sbh_ensemble20_obs0_noema_smallnet_k8_upc50_crlw1_seed1_3M/iter-190000_collect_in_seed2/LunarLanderContinuous-v2_episode_0.gif'
    processed_frames_path = '/Users/puyuan/code/DI-engine/data_lunarlander_visualize/dqn_sbh_ensemble20_obs0_noema_smallnet_k8_upc50_crlw1_seed1_3M/iter-190000_collect_in_seed2/'

    # Dataset
    dataset = create_dataset(cfg)
    print('num_episodes: ', dataset.__len__())
    # print(dataset.__getitem__(0))
    # print(dataset.__getitem__(0)[0]['action'])
    # print([len(dataset.__getitem__(i)) for i in range(dataset.__len__())])

    # episodes_len = np.array([len(dataset.__getitem__(i)) for i in range(dataset.__len__())])
    # print('episodes_len', episodes_len)
    # index_of_len1000 = np.argwhere(episodes_len == 1000).reshape(-1)
    # return_of_len1000 = torch.stack([torch.stack(
    #     [dataset.__getitem__(episode)[i]['reward'] for i in range(dataset.__getitem__(episode).__len__())], axis=0).sum(
    #     0) for episode in list(index_of_len1000)], axis=0)
    # print('return_of_len1000', return_of_len1000)
    # stacked action of the first collected episode

    episode0_obs = torch.stack(
        [dataset.__getitem__(0)[i]['obs'] for i in range(dataset.__getitem__(0).__len__())], axis=0)

    episode0_actions = torch.stack(
        [dataset.__getitem__(0)[i]['action'] for i in range(dataset.__getitem__(0).__len__())], axis=0)
    episode0_rewards = torch.stack(
        [dataset.__getitem__(0)[i]['reward'] for i in range(dataset.__getitem__(0).__len__())], axis=0)

    episode0_q_value = torch.stack(
        [to_tensor(dataset.__getitem__(0)[i]['q_value']) for i in range(dataset.__getitem__(0).__len__())],
        axis=0)

    # episode0_mapping = torch.stack(
    #     [to_tensor(dataset.__getitem__(0)[i]['_mapping']) for i in range(dataset.__getitem__(0).__len__())],
    #     axis=0)

    episode0_latent_actions = torch.stack(
        [dataset.__getitem__(0)[i]['latent_action'] for i in range(dataset.__getitem__(0).__len__())], axis=0)

    # print(episode0_rewards.max(), episode0_rewards.min(), episode0_rewards.mean(), episode0_rewards.std())
    # print(episode0_actions.max(0), episode0_actions.min(0), episode0_actions.mean(0), episode0_actions.std(0))

    def display_frames_as_gif(frames: list, path: str) -> None:
        imageio.mimsave(path, frames, fps=20)

    gif = imageio.get_reader(original_gif_path, '.gif')

    # Here's the number you're looking for
    number_of_frames = len(gif)
    print('episode_length:', number_of_frames)
    print('episode_return:', episode0_rewards.sum())
    processed_frames = []

    # process <number_of_frames> frames
    # serial_pipeline_dqn_vqvae_visualize([copy.deepcopy(main_config), copy.deepcopy(create_config)], seed=1,
    #                                         max_env_step=int(3e6), obs=episode0_obs, name_suffix='lunarlander_obs0_crlw1_k8',
    #                                         visualize_path=visualize_path, number_of_frames=number_of_frames)

    serial_pipeline_dqn_vqvae_visualize([copy.deepcopy(main_config), copy.deepcopy(create_config)], seed=1,
                                        max_env_step=int(3e6), obs=episode0_obs,
                                        name_suffix='lunarlander_obs0_crlw1_k8',
                                        visualize_path=visualize_path, number_of_frames=number_of_frames)
    for timestep, frame in enumerate(gif):
        # generate latent mapping img
        # process one frame once
        # name_suffix = f'lunarlander_obs0_crlw1_k8_seed1_t{timestep}_best'
        # serial_pipeline_dqn_vqvae_visualize([copy.deepcopy(main_config), copy.deepcopy(create_config)], seed=1,
        #                                     max_env_step=int(3e6), obs=episode0_obs[timestep], name_suffix=name_suffix,
        #                                     visualize_path=visualize_path)

        # each frame is a numpy matrix
        # print(frame.shape)
        # fig, ax = plt.subplots(figsize=(3, 2))

        fig = plt.figure(figsize=(15, 15))
        fig.tight_layout()
        ax1 = plt.subplot(2, 2, 1)
        plt.imshow(frame)

        obs = [round(i, 4) for i in episode0_obs[timestep].tolist()]
        reward = [round(i, 4) for i in episode0_rewards[timestep].tolist()]

        text_0 = f"{timestep}"
        text_1 = f"{obs[:4]}"
        text_2 = f"{obs[-4:]}"
        text_3 = f"{reward}"

        ax1.text(0, 0, text_0, fontsize=10, color="r", horizontalalignment='left', verticalalignment='top')
        ax1.text(0, 50, text_1, fontsize=10, color="r", horizontalalignment='left', verticalalignment='top')
        ax1.text(0, 100, text_2, fontsize=10, color="r", horizontalalignment='left', verticalalignment='top')
        ax1.text(0, 150, text_3, fontsize=10, color="r", horizontalalignment='left', verticalalignment='top')

        plt.subplot(2, 2, 2)
        barlist = plt.bar(range(8), episode0_q_value[timestep], fc='g')
        barlist[int(episode0_latent_actions[timestep])].set_color('r')
        plt.xlabel('Latent Action')
        plt.ylabel('Q Value')
        # plt.title(' Histogram')
        plt.grid(True)

        plt.subplot(2, 2, 3)
        plt.axis('off')
        img_mapping = plt.imread(
            visualize_path + f'latent_mapping_lunarlander_obs0_crlw1_k8_t{timestep}.png')
        plt.imshow(img_mapping)

        plt.subplot(2, 2, 4)
        plt.axis('off')
        img_mapping = plt.imread(
            visualize_path + f'latent_action_decoding_lunarlander_obs0_crlw1_k8_t{timestep}.png')
        plt.imshow(img_mapping)

        # plt.show()

        # If we haven't already shown or saved the plot, then we need to
        # draw the figure first...
        fig.canvas.draw()

        # Now we can save it to a numpy array.
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        # data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.float32)
        processed_frame = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.clf()
        plt.close('all')

        processed_frames.append(processed_frame)
        print('frame:', timestep)
        # if timestep == 1:
        #     break

    path = os.path.join(processed_frames_path, 'lunarlander_t-obs-rew_q-value_mapping_latent-decoding.gif')
    display_frames_as_gif(processed_frames, path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', '-s', type=int, default=0)
    args = parser.parse_args()

    train(args)
