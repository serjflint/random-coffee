import collections
import pathlib
import random
import string
import time

USERS_COUNT = 1000
FILES_COUNT = 100
USERNAME_LENGTH = 100
SLEEP = 0
HISTORY_DIR = pathlib.Path(__file__).parent.parent / 'history'
global_descriptors = []


def get_random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=USERNAME_LENGTH))


def main():
    users = {get_random_name() + str(idx) for idx in range(USERS_COUNT)}

    user_pools = {user: users - {user} for user in users}
    repeats = collections.Counter()

    for idx in range(FILES_COUNT):
        file_path = HISTORY_DIR / f'{idx}.txt'
        stream = open(file_path, 'w', encoding='utf-8')
        global_descriptors.append(stream)
        time.sleep(SLEEP)
        write_pairs(idx, stream, users, user_pools, repeats)
    most_repeats = [b for _, b in repeats.most_common(3)]
    print('Most repeats:', most_repeats)


def write_pairs(idx, stream, users, user_pools, repeats):
    current_users = list(users)
    random.shuffle(current_users)

    # prefer bigger pools here to exhaust all pools in the end
    current_users.sort(key=lambda x: len(user_pools[x]), reverse=True)

    smallest_pool_size, biggest_pools_size = len(user_pools[current_users[0]]), len(user_pools[current_users[-1]])
    dlq = []  # users that couldn't form a pair with anyone in the current pool

    while len(current_users) > 1:
        left_user = current_users[0]
        current_users.remove(left_user)
        choices = user_pools[left_user].intersection(current_users)
        if not choices:
            dlq.append(left_user)
            continue
        right_user = random.choice(list(choices))
        stream.write(f'{left_user},{right_user}\n')
        current_users.remove(right_user)
        user_pools[left_user].remove(right_user)
        user_pools[right_user].remove(left_user)

    dlq += current_users
    random.shuffle(dlq)
    print(
        idx,
        "users couldn't form a pair:",
        len(dlq),
        'with pools:',
        smallest_pool_size,
        biggest_pools_size,
        len(repeats),
    )

    for left_user, right_user in zip(dlq[::2], dlq[1::2], strict=False):
        stream.write(f'{left_user},{right_user}\n')
        if right_user not in user_pools[left_user]:
            repeats[left_user, right_user] += 1
        if left_user not in user_pools[right_user]:
            repeats[right_user, left_user] += 1
        user_pools[left_user].discard(right_user)
        user_pools[right_user].discard(left_user)
    # stream.close()


if __name__ == '__main__':
    main()
