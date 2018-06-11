"""
This code was slightly modified from the baselines/baselines/deepq/experiment/train_cartpole.py in order to use 
a different evaluation method. In order to run, simply replace the original code with this code 
in the original directory.
"""
import gym

from baselines import deepq

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--env', help='environment ID', default='CartPole-v0')
parser.add_argument('--seed', help='RNG seed', type=int, default=0)
parser.add_argument('--prioritized', type=int, default=0)
parser.add_argument('--prioritized-replay-alpha', type=float, default=0.6)
parser.add_argument('--double_q', type=int, default=0)
parser.add_argument('--mode', choices=['train', 'test'], default='train')
parser.add_argument('--dueling', type=int, default=0)
parser.add_argument('--nb_train_steps', type=int, default=100000)
parser.add_argument('--buffer_size', type=int, default=50000)
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--nb_step_warmup', type=int, default = 1000)
parser.add_argument('--epoch_steps', type=int, default = 1000)
parser.add_argument('--target_update_freq', type=int, default=500) # This should be smaller than epoch_steps
parser.add_argument('--nb_step_bound',type=int, default = None)
parser.add_argument('--learning_rate', type=float, default=1e-3)
parser.add_argument('--gamma', type=float, default=.99)
parser.add_argument('--log_dir', type=str, default='.')
parser.add_argument('--eps_max', type=float, default=0.1)
parser.add_argument('--eps_min', type=float, default=.02)
parser.add_argument('--device', type=str, default='/gpu:0')
parser.add_argument('--alg', choices=['adfq','adfq-v2'], default='adfq')
parser.add_argument('--record',type=int, default=0)
parser.add_argument('--gpu_memory',type=float, default=1.0)

args = parser.parse_args()

def callback(lcl, _glb):
    # stop training if reward exceeds 199
    is_solved = lcl['t'] > 100 and sum(lcl['episode_rewards'][-101:-1]) / 100 >= 199
    return is_solved


def train():
    directory = os.path.join(args.log_dir, '_'.join([args.env, datetime.datetime.now().strftime("%m%d%H%M")]))
    if not os.path.exists(directory):
            os.makedirs(directory)
    else:
            ValueError("The directory already exists...", directory)
    json.dump(vars(args), open(os.path.join(directory, 'learning_prop.json'), 'w'))

    env = gym.make(args.env)

    with tf.device(args.device):
        model = deepq.models.mlp([64])
        act, records = deepq.learn(
            env,
            q_func=model,
            lr=args.learning_rate,
            max_timesteps=args.nb_train_steps,
            buffer_size=args.buffer_size,
            exploration_fraction=0.1,
            exploration_final_eps=0.02,
            print_freq=10,
            checkpoint_freq=args.epoch_steps,
            learning_starts=args.nb_step_warmup,
            gamma = args.gamma,
            callback=None,#callback,
            env_name=args.env,
            epoch_steps = args.epoch_steps,
            gpu_memory=args.gpu_memory,
            save_dir=directory,
            double_q = args.double_q,
            nb_step_bound=args.nb_step_bound,
        )
        print("Saving model to model.pkl")
        act.save(os.path.join(args.log_dir,"model.pkl"))
    plot(records)
        
def test():
    env = gym.make(args.env)
    act = deepq.load(os.path.join(args.log_dir, "model.pkl"))

    while True:
        obs, done = env.reset(), False
        episode_rew = 0
        while not done:
            env.render()
            obs, rew, done, _ = env.step(act(obs[None])[0])
            episode_rew += rew
        print("Episode reward", episode_rew)

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
    if args.mode == 'train':
        train()
    elif args.mode =='test':
        test()
