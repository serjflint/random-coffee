import collections
import enum
import functools
import pathlib
import sys


class Enum(enum.Enum):
    done = 'done'


HISTORY_DIR = pathlib.Path(__file__).parent.parent / 'history'

meetings = collections.defaultdict(list)
users = set()
statuses = set()


def read_status():
    return ('done' * 100)[-4:]


@functools.lru_cache(maxsize=100000)
def cheap_cache(s: str) -> str:
    return s


for file in sorted(HISTORY_DIR.glob('*.txt')):
    with file.open('r') as stream:
        for line in stream:
            left_user, right_user = line.strip().split(',')
            left_user, right_user = cheap_cache(left_user), cheap_cache(right_user)
            left_meeting, right_meeting = (right_user, Enum(read_status())), (left_user, Enum(read_status()))
            meetings[left_user].append(left_meeting)
            meetings[right_user].append(right_meeting)

            users.add(id(left_user))
            users.add(id(right_user))
            statuses.add(id(left_meeting[1]))
            statuses.add(id(right_meeting[1]))

print(len(users), len(statuses), len(meetings))
