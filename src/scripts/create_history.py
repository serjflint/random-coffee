import collections
import pathlib
import random
import string

USERS_COUNT = 1000
USERNAME_LENGTH = 10
HISTORY_DIR = pathlib.Path(__file__).parent.parent.parent / 'history'

users = {''.join(random.sample(string.ascii_lowercase, USERNAME_LENGTH)) + str(idx) for idx in range(USERS_COUNT)}

user_pools = {user: users - {user} for user in users}
repeats = collections.Counter()

for idx in range(len(users)):
    file_path = HISTORY_DIR / f'{idx}.txt'
    with file_path.open('w') as stream:
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
        if dlq:
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


print('Total repeats:', repeats.most_common(3))
