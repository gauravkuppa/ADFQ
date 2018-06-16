"""
This code was modified from a OpenAI baseline code - baselines/baselines/deepq/experiments/run_atari.py 
"""

from baselines.common import set_global_seeds
from baselines.common.atari_wrappers import make_atari
from baselines import logger
from baselines import bench

import argparse
import models
import simple
import tensorflow as tf
import numpy as np
import os, datetime, json
from gym.wrappers import Monitor

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--env', help='environment ID', default='BreakoutNoFrameskip-v4')
parser.add_argument('--seed', help='RNG seed', type=int, default=0)
parser.add_argument('--prioritized', type=int, default=1)
parser.add_argument('--prioritized-replay-alpha', type=float, default=0.6)
parser.add_argument('--mode', choices=['train', 'test'], default='train')
parser.add_argument('--dueling', type=int, default=0)
parser.add_argument('--nb_train_steps', type=int, default=int(3*1e6))
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--nb_step_warmup', type=int, default = 10000)
parser.add_argument('--epoch_steps', type=int, default = 20000)
parser.add_argument('--nb_step_bound',type=int, default = 10000)
parser.add_argument('--target_update_freq', type=int, default=1000)
parser.add_argument('--learning_rate', type=float, default=0.00025)
parser.add_argument('--gamma', type=float, default=.99)
parser.add_argument('--log_dir', type=str, default='.')
parser.add_argument('--log_fname', type=str, default='model.pkl')
parser.add_argument('--buffer_size', type=int, default=10000)
parser.add_argument('--eps_max', type=float, default=0.1)
parser.add_argument('--eps_min', type=float, default=.01)
parser.add_argument('--init_mean', type =float, default=1.)
parser.add_argument('--init_sd', type=float, default=50.)
parser.add_argument('--device', type=str, default='/gpu:0')
parser.add_argument('--alg', choices=['adfq','adfq-v2'], default='adfq')
parser.add_argument('--act_policy', choices=['egreedy','bayesian'], default='egreedy')
parser.add_argument('--record',type=int, default=0)
parser.add_argument('--gpu_memory',type=float, default=1.0)
parser.add_argument('--varth', type=float,default=1e-5)
parser.add_argument('--noise', type=float,default=1e-5)

args = parser.parse_args()

def train():
    
    logger.configure()
    set_global_seeds(args.seed)

    directory = os.path.join(args.log_dir, '_'.join([args.env, datetime.datetime.now().strftime("%m%d%H%M")]))
    if not os.path.exists(directory):
            os.makedirs(directory)
    else:
            ValueError("The directory already exists...", directory)
    json.dump(vars(args), open(os.path.join(directory, 'learning_prop.json'), 'w'))

    env = make_atari(args.env)
    env = bench.Monitor(env, logger.get_dir())
    env = models.wrap_atari_dqn(env)

    if args.record == 1:
        env = Monitor(env, directory=directory)
    
    with tf.device(args.device):
        model = models.cnn_to_mlp(
            convs=[(32, 8, 4), (64, 4, 2), (64, 3, 1)],
            hiddens=[256],
            dueling=bool(args.dueling),
            init_mean = args.init_mean, 
            init_sd = args.init_sd,
        )

        act, records = simple.learn(
            env,
            q_func=model,
            lr=args.learning_rate,
            max_timesteps=args.nb_train_steps,
            buffer_size=args.buffer_size,
            exploration_fraction=args.eps_max,
            exploration_final_eps=args.eps_min,
            train_freq=4,
            print_freq=1000,
            checkpoint_freq=int(args.nb_train_steps/10),
            learning_starts=args.nb_step_warmup,
            target_network_update_freq=args.target_update_freq,
            gamma=0.99,
            prioritized_replay=bool(args.prioritized),
            prioritized_replay_alpha=args.prioritized_replay_alpha,
            env_name = args.env,
            epoch_steps = args.epoch_steps,
            alg = args.alg,
            noise = args.noise,
            gpu_memory = args.gpu_memory,
            varTH=args.varth,
            act_policy=args.act_policy,
            save_dir=directory,
            nb_step_bound = args.nb_step_bound, 
        )
        print("Saving model to model.pkl")
        act.save(os.path.join(args.log_dir,"model.pkl"))
    plot(records, directory)
    env.close()

def test():
    env = make_atari(args.env)
    env = models.wrap_atari_dqn(env)
    act = simple.load(os.path.join(args.log_dir, args.log_fname))
    if args.record:
        env = Monitor(env, directory=args.log_dir)

    while True:
        obs, done = env.reset(), False
        episode_rew = 0
        while not done:
            env.render()
            obs, rew, done, _ = env.step(act(obs[None])[0])
            episode_rew += rew
        print("Episode reward", episode_rew)

def plot(records, directory):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    m = len(records['q_mean'])
    x_vals = range(0 , args.epoch_steps*m, args.epoch_steps)
    
    f0, ax0 = plt.subplots(3, sharex=True, sharey=False)
    ax0[0].plot(x_vals, records['q_mean'])
    ax0[0].set_ylabel('Average Q means')

    ax0[1].plot(x_vals, np.log(records['q_sd']))
    ax0[1].set_ylabel('Log of Average Q SD')

    ax0[2].plot(x_vals, records['loss'])
    ax0[2].set_ylabel('Loss')
    ax0[2].set_xlabel('Learning Steps')

    f1, ax1 = plt.subplots()
    ax1.plot(x_vals, records['online_reward'])
    ax1.set_ylabel('Average recent 100 rewards')
    ax1.set_xlabel('Learning Steps')

    f2, ax2 = plt.subplots()
    m, ids25, ids75 = simple.iqr(np.array(records['test_reward']).T)
    ax2.plot(x_vals, m, color='b')
    ax2.fill_between(x_vals, list(ids75), list(ids25), facecolor='b', alpha=0.2)
    ax2.set_ylabel('Test Rewards')
    ax2.set_xlabel('Learning Steps')

    f0.savefig(os.path.join(directory, "result.png"))
    f1.savefig(os.path.join(directory, "online_reward.png"))
    f2.savefig(os.path.join(directory, "test_reward.png"))

if __name__ == '__main__':
    if args.mode == 'train':
        train()
    elif args.mode =='test':
        test()