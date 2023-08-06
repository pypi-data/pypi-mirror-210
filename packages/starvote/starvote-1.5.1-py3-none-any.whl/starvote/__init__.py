#!/usr/bin/env python3

__doc__ = "A simple STAR vote tabulator"

__version__ = "1.5.1"

__all__ = [
    'Bloc_STAR',
    'BLOC_STAR',
    'main',
    'Poll',
    'ElectoralSystem',
    'Proportional_STAR',
    'Reweighted_Range',
    'RRV',
    'STAR',
    'STAR_PR',
    'UnbreakableTieError',
    ]

import builtins
import enum
import math

try:
    from enum import global_enum
except ImportError:
    def global_enum(fn):
        return fn

class UnbreakableTieError(ValueError):
    def __init__(self, description, *candidates):
        super().__init__(description)
        self.candidates = tuple(candidates)


@global_enum
class ElectoralSystem(enum.Enum):
    STAR = 1
    Bloc_STAR = 2
    Proportional_STAR = 3
    Reweighted_Range = 4

STAR = ElectoralSystem.STAR
# permit old capitalized name, FOR NOW
Bloc_STAR = BLOC_STAR = ElectoralSystem.Bloc_STAR
Proportional_STAR = STAR_PR = ElectoralSystem.Proportional_STAR
Reweighted_Range = RRV = ElectoralSystem.Reweighted_Range


class Poll:
    def __init__(self, electoral_system=STAR, *, seats=1, maximum_score=5):
        self.electoral_system = electoral_system
        self.seats = seats
        self.maximum_score = maximum_score

        self.candidates = {}
        self.ballots = []

        if electoral_system == STAR:
            if seats != 1:
                raise ValueError("seats must be 1 when using STAR electoral system")
        else:
            if seats == 1:
                raise ValueError("seats must be > 1 when using {str(electoral_system).rpartition('.'')[2]} electoral system")

    def add_candidate(self, name):
        self.candidates[name] = 0

    def add_ballot(self, ballot):
        for candidate, score in ballot.items():
            assert isinstance(score, int)
            assert 0 <= score <= self.maximum_score, f"score {score} not in the range 0..{self.maximum_score}"
            if candidate not in self.candidates:
                self.add_candidate(candidate)
            self.candidates[candidate] += score
        self.ballots.append(ballot)

    @staticmethod
    def compute_widths(ballots, scores):
        # scores should be an array of [score, candidate] iterables.
        candidate_width = -1
        largest_score = -1
        largest_average = -1
        ballots_count = len(ballots)
        for score, candidate in scores:
            candidate_width = max(candidate_width, len(candidate))
            largest_score = max(largest_score, score)
            average = score / ballots_count
            largest_average = max(largest_average, average)
        score_width = math.floor(math.log10(largest_score)) + 1
        average_width = math.floor(math.log10(largest_average)) + 1  # .xx
        return candidate_width, score_width, average_width

    # of these 2 candidates, which is preferred?
    # used for the automatic runoff, and to resolve
    # two-way ties in the score round.
    @staticmethod
    def preference(ballots, candidate0, candidate1, *, when=None, print=None):
        scores = [ [0, candidate0], [0, candidate1] ]
        for ballot in ballots:
            score0 = ballot.get(candidate0, 0)
            score1 = ballot.get(candidate1, 0)
            if score0 > score1:
                scores[0][0] += 1
            elif score1 > score0:
                scores[1][0] += 1
        scores.sort()

        no_preference = len(ballots) - (scores[0][0] + scores[1][0])
        scores.insert(0, [no_preference, "No preference"])

        if print:
            candidate_width, score_width, average_width = Poll.compute_widths(ballots, scores)
            for score, candidate in reversed(scores):
                print(f"  {candidate:<{candidate_width}} -- {score:>{score_width}}")

        if scores[1][0] == scores[2][0]:
            raise UnbreakableTieError(f"two-way tie during {when} between {candidate0} and {candidate1}", candidate0, candidate1)
        winner = scores[2][1]

        return winner


    def print_rankings(self, ballots, rankings, print):
        candidate_width, score_width, average_width = self.compute_widths(ballots, rankings)
        total_average_width = average_width + 3
        ballots_count = len(ballots)

        # are the scores all ints?
        for score, candidate in rankings:
            int_score = int(score)
            if int_score != score:
                score_format = f"{score_width}.3f"
                total_score_width = score_width + 4
                break
        else:
            score_format = score_width
            total_score_width = score_width

        for score, candidate in reversed(rankings):
            average = score / ballots_count
            average = f"{average:>1.2f}"
            score = f"{score:>{score_format}}"
            print(f"  {candidate:<{candidate_width}} -- {score:>{total_score_width}} (average {average:>{total_average_width}})")

    def _rrv(self, ballots, candidates, *, print=None):
        # Suggested by Tim Peters as an alternative to Proportional STAR;
        # a score-based proportional electoral system that doesn't throw away ballots.
        # https://rangevoting.org/RRV.html
        # https://rangevoting.org/RRVr.html

        C = self.maximum_score
        weight = 1.0 # aka C/C
        weighted_ballots = [ [b, C, weight] for b in ballots ]
        winners = []

        for polling_round in range(1, self.seats + 1):
            if print:
                print(f"[Reweighted Range {polling_round}]")
            # zero out candidate votes
            for candidate in candidates:
                candidates[candidate] = 0

            for t in weighted_ballots:
                ballot, sum, weight = t
                for candidate, score in ballot.items():
                    if score:
                        score *= weight
                        candidates[candidate] += score

            rankings = [(score, candidate) for candidate, score in candidates.items()]
            rankings.sort()

            if print:
                self.print_rankings(ballots, rankings, print)

            winning_score, winner = rankings[-1]
            if (len(rankings) > 1) and (rankings[-2][0] == winning_score):
                tied_candidates = [c for s, c in rankings if s == winning_score]
                raise UnbreakableTieError("Tie between {len(tied_candidates)} candidates in round {polling_round}", *tied_candidates)

            if print:
                print(f"[Winner {polling_round}]")
                print(f"  {winner}")

            winners.append(winner)
            assert winner in candidates
            del candidates[winner]
            if len(winners) == self.seats:
                break

            for t in weighted_ballots:
                ballot, C_plus_scores, weight = t
                score = ballot.get(winner, 0)
                if score:
                    del ballot[winner]
                    C_plus_scores += score
                    weight = C / C_plus_scores
                    t[1] = C_plus_scores
                    t[2] = weight

        return winners


    def _proportional_result(self, ballots, candidates, *, print=None):
        winners = []

        # Floordiv so hare_quota is an integer.
        # If there would have been a fraction,
        # it just means the last round's hare quota
        # would be one more.
        #   e.g. 100 voters, 3 seats, you'd use 33, 33, and 34.
        # But we don't need to bother with the Hare quota
        # during the last round.
        # So we can just ignore the fraction completely.
        hare_quota = len(ballots) // self.seats

        if print:
            print(f"  Hare quota is {hare_quota}.")

        for polling_round in range(1, self.seats+1):
            rankings = [(score, candidate) for candidate, score in candidates.items()]
            rankings.sort()
            if print:
                print(f"[Score round {polling_round}]")
                remaining = " remaining" if polling_round > 1 else ""
                print(f"  {len(ballots)}{remaining} ballots.")
                self.print_rankings(ballots, rankings, print)

            round_winners = [t[1] for t in rankings if t[0] == rankings[-1][0]]
            if len(round_winners) > 2:
                raise UnbreakableTieError(f"{len(round_winners)}-way tie in round {polling_round}", *round_winners)
            if len(round_winners) == 2:
                if print:
                    print(f"[Tie-breaker preference round {polling_round}]")
                winner = self.preference(ballots, *round_winners, when=f"score round {polling_round}", print=print)
            else:
                assert len(round_winners) == 1
                winner = round_winners.pop()

            # we need to allocate voters to the winner,
            # do the hare quota thing, etc.
            # for simplicity of implementation, we're only going to handle
            # one winner here.  if we reached here and there were multiple
            # tied winners, we'll process the other winners in future
            # iterations of the loop.  doing them one at a time won't
            # affect the outcome.

            winners.append(winner)
            if print:
                print(f"[Winner round {polling_round}]")
                print(f"  {winner}")
            if len(winners) == self.seats:
                return winners

            del candidates[winner]

            # gonna iterate.
            # remove hare quota voters, possibly fractionally.
            if print:
                print(f"[Allocating voters round {polling_round}]")

            quota = hare_quota
            all_supporters = [ballot for ballot in ballots if ballot.get(winner, 0)]
            all_supporters.sort(key=lambda ballot: ballot[winner])

            while all_supporters:
                # find highest score.
                # note that this might not be an integer!
                # after the first scoring round, it's likely there will be non-integer votes.
                score = all_supporters[-1][winner]

                tranche = [ballot for ballot in all_supporters if ballot[winner] == score]
                tranche_count = len(tranche)

                assert all_supporters[-tranche_count][winner] == score
                assert (len(all_supporters) == tranche_count) or (all_supporters[-(tranche_count + 1)][winner] != score)
                del all_supporters[-tranche_count:]

                unallocated_ballots = [ballot for ballot in ballots if ballot.get(winner, 0) != score]

                if print:
                    print(f"  Quota remaining {quota}.")
                    print(f"    Allocating {tranche_count} voters at score {score}.")
                if tranche_count <= quota:
                    quota -= tranche_count
                    ballots = unallocated_ballots
                    if not quota:
                        break
                    continue

                # this tranche has more supporters than we need to fill the quota.
                # reduce every supporter's vote by the surplus, then keep them in play.
                weight_reduction_ratio = 1 - (quota / tranche_count)
                if print:
                    print(f"    This would take us over quota, so handling fractional surplus.")
                    print(f"    Allocating {(1 - weight_reduction_ratio) * 100:2.2f}% of these ballots.")
                    print(f"    Multiplying these ballot's scores by {weight_reduction_ratio:2.6f}, then keeping them unallocated.")
                for ballot in tranche:
                    del ballot[winner]
                    for candidate, vote in ballot.items():
                        adjusted_vote = vote * weight_reduction_ratio
                        candidates[candidate] += (adjusted_vote - vote)
                        ballot[candidate] = adjusted_vote

                unallocated_ballots.extend(tranche)

                ballots = unallocated_ballots
                break

            for ballot in ballots:
                if winner in ballot:
                    del ballot[winner]


        raise RuntimeError("shouldn't reach here")



    def result(self, *, print=None):
        winners = []
        candidates = self.candidates
        ballots = self.ballots

        if not candidates:
            raise ValueError("no candidates")

        if self.electoral_system == STAR:
            if print:
                print("[STAR]")
            if len(candidates) == 1:
                winners = list(candidates)
                winner = winners[0]
                if print:
                    print("  Only one candidate, returning winner {winner}!")
                return winner
            round_text_format = ""
        else:
            if print:
                if self.electoral_system == BLOC_STAR:
                    print("[BLOC STAR]")
                elif self.electoral_system == Proportional_STAR:
                    print("[Proportional STAR]")
                else:
                    print("[Reweighted Range]")
                print(f"  {self.seats} seats.")
            if len(candidates) <= self.seats:
                raise ValueError(f"not enough candidates, need {self.seats}, have {len(candidates)}")
            if len(candidates) == self.seats:
                print(f"  Have exactly {self.seats} candidates, all candidates are winners!")
                return list(candidates)
            # we're gonna modify ballots, so, make copies
            ballots = [dict(b) for b in ballots]
            candidates = dict(candidates)
            round_text_format = " {polling_round}"

        if self.electoral_system == Proportional_STAR:
            return self._proportional_result(ballots, candidates, print=print)

        if self.electoral_system == Reweighted_Range:
            return self._rrv(ballots, candidates, print=print)

        for polling_round in range(1, self.seats+1):
            candidates_count = len(candidates)
            ballots_count = len(ballots)
            assert candidates_count

            round_text = round_text_format.format(polling_round=polling_round)

            if print:
                print(f"[Score round{round_text}]")

            # score round
            rankings = [(score, candidate) for candidate, score in candidates.items()]
            rankings.sort()

            if print:
                self.print_rankings(ballots, rankings, print)

            top_two = rankings[-2:]
            if candidates_count > 2:
                if (rankings[-3][0] == rankings[-2][0]):
                    if rankings[-2][0] == rankings[-1][0]:
                        candidates = [r[1] for r in rankings[-3:]]
                        description = ", ".join(candidates)
                        first_two, comma, last_one = description.rpartition(",")
                        description = f"{first_two}{comma} and{last_one}"
                        raise UnbreakableTieError(f"unbreakable three-way tie for first in score round{round_text} between " + description, *candidates)
                    if (candidates_count > 3) and (rankings[-4][0] == rankings[-3][0]):
                        candidates = ([r[1] for r in rankings[-4:-1]])
                        description = ", ".join(candidates)
                        first_two, comma, last_one = description.rpartition(",")
                        description = f"{first_two}{comma} and{last_one}"
                        raise UnbreakableTieError(f"unbreakable three-way tie for second in score round{round_text} between " + description, *candidates)
                    if print:
                        print(f"[Resolving two-way tie between second and third in score round{round_text}]")
                    preferred = self.preference(ballots, rankings[-3][1], rankings[-2][1], print=print, when="preference runoff between second and third in score round")
                    if top_two[0][1] != preferred:
                        top_two[0] = rankings[-3]
            if print:
                print(f"[Automatic runoff round{round_text}]")

            try:
                winner = self.preference(ballots, top_two[0][1], top_two[1][1], print=print, when=f"automatic runoff round{round_text}")
            except UnbreakableTieError:
                if print:
                    print(f"[Resolving two-way tie in automatic runoff round{round_text}]")
                    self.print_rankings(ballots, top_two, print)

                if top_two[0][0] > top_two[1][0]:
                    winner= top_two[0][1]
                elif top_two[1][0] > top_two[0][0]:
                    winner = top_two[1][1]
                else:
                    raise UnbreakableTieError(f"unbreakable tie between {top_two[0][1]} and {top_two[1][1]} in automatic runoff round{round_text}", top_two[0][1], top_two[1][1])
            if (self.seats != 1) and print:
                print(f"[Winner round{round_text}]")
                print(f"  {winner}")
            winners.append(winner)

            if self.seats > 1:
                for b in ballots:
                    if winner in b:
                        del b[winner]
                assert winner in candidates
                del candidates[winner]

        if self.electoral_system == STAR:
            assert len(winners) == 1
            return winner

        assert len(winners) == self.seats
        return winners


def main(argv, print=None):
    import csv
    import os.path

    text = []
    if print is None:
        def print(*a, sep=" "):
            text.append(sep.join(str(o) for o in a))
        def flush_print():
            t = "\n".join(text)
            builtins.print(t)
    else:
        def flush_print(): pass

    def usage(s=None):
        if s:
            print(s)
            print()
        print("usage: starvote.py [-e|--electoral-system system] [-m|--maximum-score score] [-s|--seats seats] ballot.csv")
        print()
        print("Options:")
        print("  -e|--electoral-system specifies electoral system.  Supported systems are STAR (default), BLOC, STAR-PR, and RRV.")
        print("  -m|--maximum-score specifies the maximum score per vote, default 5.")
        print("  -s|--seats specifies number of seats, default 1.")
        print()
        print("ballot.csv is assumed to be in https://start.vote CSV format.")
        print()
        flush_print()
        return -1

    if not argv:
        return usage()

    electoral_system_map = {
        "STAR": STAR,
        None: STAR,

        "Bloc_STAR": Bloc_STAR,
        "Bloc": Bloc_STAR,
        # permit old capitalized names, FOR NOW
        "BLOC_STAR": Bloc_STAR,
        "BLOC": Bloc_STAR,

        "Proportional_STAR": Proportional_STAR,
        "STAR-PR": Proportional_STAR,

        "Reweighted_Range": Reweighted_Range,
        "RRV": Reweighted_Range,
    }

    electoral_system = None
    seats = None
    maximum_score = None

    csv_file = None

    value_waiting_for_oparg = None
    extraneous_args = []

    allow_options = True

    for arg in argv:

        if value_waiting_for_oparg:
            option, name = value_waiting_for_oparg
            if name == "electoral_system":
                electoral_system = electoral_system_map.get(arg)
                if electoral_system is None:
                    return usage(f"unknown electoral system {arg}")
            elif name == "seats":
                seats = int(arg)
            elif name == "maximum_score":
                maximum_score = int(arg)
            else:
                raise RuntimeError(f"unknown value waiting for oparg {value_waiting_for_oparg!r}")
            value_waiting_for_oparg = None
            continue

        if allow_options:
            if arg.startswith("-e=") or arg.startswith("--electoral-system="):
                if electoral_system is not None:
                    return usage("electoral system specified twice")
                e = arg.partition('=')[2]
                electoral_system = electoral_system_map.get(e, None)
                if electoral_system is None:
                    return usage(f"unknown electoral system {e}")
                continue
            if arg in ("-e", "--electoral-system"):
                if electoral_system is not None:
                    return usage("electoral system specified twice")
                value_waiting_for_oparg = (arg, "electoral_system")
                continue

            if arg.startswith("-s=") or arg.startswith("--seats="):
                if seats is not None:
                    return usage("seats specified twice")
                seats = int(arg.partition('='))
                continue
            if arg in ("-s", "--seats"):
                if seats is not None:
                    return usage("seats specified twice")
                value_waiting_for_oparg = (arg, "seats")
                continue

            if arg.startswith("-m=") or arg.startswith("--maximum-score="):
                if maximum_score is not None:
                    return usage("maximum score specified twice")
                maximum_score = int(arg.partition('='))
                continue
            if arg in ("-m", "--maximum-score"):
                if maximum_score is not None:
                    return usage("maximum score specified twice")
                value_waiting_for_oparg = (arg, "maximum_score")
                continue

            if arg == "--":
                allow_options = False
                continue

            if arg.startswith('-'):
                return usage(f"unknown option {arg}")

        if csv_file is None:
            csv_file = arg
            continue
        extraneous_args.append(arg)

    if extraneous_args:
        return usage("too many arguments: " + " ".join(extraneous_args))
    if value_waiting_for_oparg:
        option, name = value_waiting_for_oparg
        return usage(f"no argument specified for {option}")

    args = []
    kwargs = {}

    if electoral_system is not None:
        args.append(electoral_system)

    if seats is not None:
        kwargs["seats"] = seats

    if maximum_score is not None:
        kwargs["maximum_score"] = maximum_score

    if csv_file is None:
        return usage("no CSV file specified.")
    if not os.path.isfile(csv_file):
        return usage("invalid CSV file specified.")

    poll = Poll(*args, **kwargs)
    with open(csv_file, "rt") as f:
        reader = csv.reader(f)
        candidates = None
        for row in reader:
            # clip off voterid, date, and pollid
            row = row[3:]
            if candidates == None:
                candidates = row
                # for candidate in candidates:
                #     poll.add_candidate(candidate)
                continue
            ballot = {candidate: int(vote) for candidate, vote in zip(candidates, row)}
            poll.add_ballot(ballot)

    winner = None
    try:
        winner = poll.result(print=print)
    except UnbreakableTieError as e:
        if len(e.candidates) == 2:
            winner = f"Tie between {e.candidates[0]} and {e.candidates[1]}"
        else:
            candidates = list(e.candidates)
            last_candidate = candidates.pop()
            winner = f"Tie between {', '.join(candidates)}, and {last_candidate}"

        s = str(e)
        s = s[0].title() + s[1:]
        print(f"\n{s}!")
        print("")

    if isinstance(winner, str):
        print("[Winner]")
        print(f"  {winner}")
    else:
        print("[Winners]")
        for w in winner:
            print(f"  {w}")

    if text:
        flush_print()

    return 0
