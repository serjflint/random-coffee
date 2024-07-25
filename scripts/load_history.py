import os
import os.path

meetings = {}
users = set()
statuses = set()


def read_status():
    return ('done' * 100)[-4:]


for file in os.listdir('history'):
    with open(os.path.join('history', file)) as stream:
        for line in stream:
            left_user, right_user = line.strip().split(',')
            if left_user not in meetings:
                meetings[left_user] = []
            if right_user not in meetings:
                meetings[right_user] = []
            left_meeting, right_meeting = (right_user, read_status()), (left_user, read_status())
            meetings[left_user].append((right_user, read_status()))
            meetings[right_user].append((left_user, read_status()))

            users.add(id(left_user))
            users.add(id(right_user))
            statuses.add(id(left_meeting[1]))
            statuses.add(id(right_meeting[1]))

print(len(users), len(statuses), len(meetings))
