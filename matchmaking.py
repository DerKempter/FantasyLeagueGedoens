import random

menschis = ["A-L", "Kempter", "Jonas", "Laurin", "Markus", "Simon"]


def generate_matchups(humans):
    week1 = []
    week2 = []
    week3 = []
    week4 = []
    week5 = []
    weeks = [week1, week2, week3, week4, week5]
    for i in range(0, 5):
        taken = []
        while len(weeks[i]) != 3:
            r = random.randint(0, 5)
            s = random.randint(0, 5)
            if r is not s and humans[r] not in taken and humans[s] not in taken and (humans[r], humans[s]) not in weeks[i] and (humans[s], humans[r]) not in weeks[i]:
                if i == 0:
                    weeks[i].append((humans[r], humans[s]))
                    taken.append(humans[r])
                    taken.append(humans[s])
                    # print(r, s)
                else:
                    breaker = False
                    for k in range(0, i):
                        if (humans[r], humans[s]) in weeks[k] or (humans[s], humans[r]) in weeks[k]:
                            breaker = True
                            break
                    if not breaker:
                        weeks[i].append((humans[r], humans[s]))
                        taken.append(humans[r])
                        taken.append(humans[s])
                        # print(r, s)
    return weeks


wochen = generate_matchups(menschis)

for week in wochen:
    print("new week")
    print(week)
