import collections
import os
import pathlib
import random

USERS_COUNT = 10000
FILES_COUNT = 100
USERNAME_LENGTH = 100
HISTORY_DIR = pathlib.Path(__file__).parent.parent / 'history'


def get_random_hex(idx: int):
    rand = os.urandom(USERNAME_LENGTH).hex()
    return f'{rand}_{idx}'[-USERNAME_LENGTH:]


def main():
    users = [get_random_hex(idx) for idx in range(USERS_COUNT)]

    user_pools = {user: set() for user in users}
    repeats = collections.Counter()

    for idx in range(FILES_COUNT):
        file_path = HISTORY_DIR / f'{idx}.txt'
        with file_path.open('w') as stream:
            write_pairs(idx, stream, users, user_pools, repeats)
    most_repeats = [b for _, b in repeats.most_common(3)]
    print('Most repeats:', most_repeats)


def write_pairs(idx, stream, users, user_pools, repeats):
    users.sort(key=lambda x: len(user_pools[x]), reverse=False)
    current_users = set(users)

    pointer = 0
    left_user = users[pointer]

    smallest_pool_size, biggest_pools_size = len(user_pools[users[0]]), len(user_pools[users[-1]])
    dlq = []  # users that couldn't form a pair with anyone in the current pool

    while len(current_users) > 1:
        while pointer < len(users) and left_user not in current_users:
            pointer += 1
            left_user = users[pointer]
        current_users.remove(left_user)
        choices = current_users - user_pools[left_user]
        if not choices:
            dlq.append(left_user)
            continue
        right_user = choices.pop()
        stream.write(f'{left_user},{right_user}\n')
        current_users.remove(right_user)
        user_pools[left_user].add(right_user)
        user_pools[right_user].add(left_user)

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
        if right_user in user_pools[left_user]:
            repeats[left_user, right_user] += 1
        if left_user in user_pools[right_user]:
            repeats[right_user, left_user] += 1
        user_pools[left_user].add(right_user)
        user_pools[right_user].add(left_user)


if __name__ == '__main__':
    main()
