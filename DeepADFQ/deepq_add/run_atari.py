"""
This code was slightly modified from the baselines/baselines/deepq/experiment/run_atari.py in order to use 
a different evaluation method. In order to run, simply replace the original code with this code 
in the original directory.
"""

from baselines import deepq
from baselines.common import set_global_seeds
from baselines import bench
import argparse
from baselines import logger
from baselines.common.atari_wrappers import make_atari
import tensorflow as tf
import datetime, json

from BRL.brl_util_new import iqr
import os

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--env', help='environment ID', default='BreakoutNoFrameskip-v4')
    parser.add_argument('--seed', help='RNG seed', type=int, default=0)
    parser.add_argument('--prioritized', type=int, default=1)
    parser.add_argument('--prioritized-replay-alpha', type=float, default=0.6)
    parser.add_argument('--dueling', type=int, default=0)
    parser.add_argument('--num_timesteps', type=int, default=int(3*1e6))
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--nb_steps_warmup', type=int, default = 10000)
    parser.add_argument('--epoch_steps', type=int, default = 20000)
    parser.add_argument('--target_update_freq', type=int, default=1000)
    parser.add_argument('--nb_step_bound',type=int, default = 10000)
    parser.add_argument('--learning_rate', type=float, default=0.00025)
    parser.add_argument('--gamma', type=float, default=.99)
    parser.add_argument('--log_dir', type=str, default='.')
    parser.add_argument('--buffer_size', type=int, default=10000)
    parser.add_argument('--eps_max', type=float, default=0.1)
    parser.add_argument('--eps_min', type=float, default=.01)
    parser.add_argument('--double_q', type=int, default=0)
    parser.add_argument('--device', type=str, default='/gpu:0')
    parser.add_argument('--record',type=int, default=0)
    parser.add_argument('--scope',type=str, default='deepq')
    parser.add_argument('--gpu_memory',type=float, default=1.0)

    args = parser.parse_args()
    logger.configure()
    set_global_seeds(args.seed)

    directory = datetime.datetime.now().strftime("%m%d%H%M")
    if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        ValueError("The directory already exists...", directory)
    json.dump(vars(args), open(os.path.join(directory, 'learning_prop.json'), 'w'))

    env = make_atari(args.env)
    env = bench.Monitor(env, logger.get_dir())
    env = deepq.wrap_atari_dqn(env)

    if args.record == 1:
        env = Monitor(env, directory=args.log_dir)
    with tf.device(args.device):
        model = deepq.models.cnn_to_mlp(
            convs=[(32, 8, 4), (64, 4, 2), (64, 3, 1)],
            hiddens=[256],
            dueling=bool(args.dueling),
        )

        act, records = deepq.learn(
            env,
            q_func=model,
            lr=args.learning_rate,
            max_timesteps=args.num_timesteps,
            buffer_size=args.buffer_size,
            exploration_fraction=args.eps_max,
            exploration_final_eps=args.eps_min,
            train_freq=4,
            print_freq=1000,
            checkpoint_freq=args.epoch_steps,
            learning_starts=args.nb_steps_warmup,
            target_network_update_freq=args.target_update_freq,
            gamma=0.99,
            prioritized_replay=bool(args.prioritized),
            prioritized_replay_alpha=args.prioritized_replay_alpha,
            env_name = args.env,
            epoch_steps = args.epoch_steps,
            gpu_memory = args.gpu_memory,
            double_q = args.double_q,
            directory=directory,
            nb_step_bound = args.nb_step_bound
        )

    env.close()
    plot(records)

def plot(records):
    import matplotlib.pyplot as plt
    x_vals = range(args.nb_step_warmup, args.nb_train_steps, args.epoch_steps)
    
    plt.figure(0)
    plt.plot(x_vals, records['q_mean'])
    plt.ylabel('Average Q means')
    plt.xlabel('Learning Steps')

    plt.figure(1)
    plt.plot(x_vals, np.log(records['q_sd']))
    plt.ylabel('Log of Average Q SD')
    plt.xlabel('Learning Steps')

    plt.figure(2)
    plt.plot(x_vals, records['online_reward'])
    plt.ylabel('Average recent 100 rewards')
    plt.xlabel('Learning Steps')

    plt.figure(3)
    plt.plot(x_vals, records['loss'])
    plt.ylabel('Loss')
    plt.xlabel('Learning Steps')

    plt.figure(4)
    m, ids25, ids75 = iqr(np.array(records['test_reward']).T)
    plt.plot(x_vals, m, color='b')
    plt.fill_between(x_vals, list(ids75), list(ids25), facecolor='b', alpha=0.2)
    plt.ylabel('Test Rewards')
    plt.xlabel('Learning Steps')

if __name__ == '__main__':
    main()