"""Mock coding interview (~20 min): Two Sum."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. Given an array of integers nums and an integer target, return the indices of the two numbers such that they add up to target. You may assume that each input has exactly one solution in the main cut, and you may not use the same element twice. Return the answer in any order. This is a hash map classic. Treat it as a real screen: clarity, correctness, and complexity matter.'))

    d.append(("candidate",
        'Restating. Find two different indices i and j with nums i plus nums j equals target. Clarifying questions. Is exactly one solution guaranteed? What if none or many in variants? Are negatives and zeros allowed? Duplicates allowed? May I mutate the array? Should I return values or indices? Is the array sorted?'))

    d.append(("interviewer",
        'Exactly one solution for the main cut; still say what you would do if none. Negatives and zeros allowed. Duplicates allowed. Prefer not to destroy indices. Return indices. Array is not necessarily sorted.'))

    d.append(("candidate",
        'Naive approach: nested loops over i and j greater than i, check sums, return when found. Time O of n squared, space O of one. Improved: one pass hash map from value to index. For each index j with value x, need equals target minus x. If need is in the map, return the stored index and j. Else store x to j. Look up before you write so you never pair an element with itself. Sorting plus two pointers works if you keep original indices in pairs, at O of n log n, but the hash one pass is the expected optimal for unsorted input.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because interviews often set n large enough that quadratic times out, and because the map pattern transfers to many pairing problems in payments and matching. The improved approach is still short enough to code cleanly under pressure.'))

    d.append(("interviewer",
        'Hand walk nums two, seven, eleven, fifteen, target nine. Speak the map after every step.'))

    d.append(("candidate",
        'Start map empty. j zero value two, need seven, miss, store two to zero. j one value seven, need two, hit at zero, return zero and one. Stop. Classic.'))

    d.append(("interviewer",
        'Hand walk nums three, three, target six. Show duplicates.'))

    d.append(("candidate",
        'j zero value three, need three, miss, store three to zero. j one value three, need three, hit at zero, indices differ, return zero and one. Lookup before overwrite is why this works.'))

    d.append(("interviewer",
        'Hand walk nums three, two, four, target six.'))

    d.append(("candidate",
        'Store three to zero. Store two to one. At four, need two, hit at one, return one and two.'))

    d.append(("interviewer",
        'What breaks if you write to the map before looking up the complement?'))

    d.append(("candidate",
        'A single value equal to half the target can pair with itself. Example one element three target six would falsely succeed. Always check need in map first, then assign current.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function two sum nums target returns a list of two indices. Pseudocode: map empty. For j from zero to n minus one: x equals nums j, need equals target minus x. If need in map return map need and j. Map x equals j. If loop ends under a none variant return empty or raise. Load bearing: lookup before assign. Load bearing: store indices not only a seen set when indices are required.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'Empty array none. Single element none. Two elements success. Negatives. Zeros with target zero. Duplicates. Large n. Exactly one solution assumed in main tests. If none, empty list in variant.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test classic nine. test three three six. test zeros. test negatives. test order of indices either permutation accepted. Optional slow oracle on random small arrays.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Expected O of n time and O of n space for the map. I do not claim adversarial hash worst cases unless asked; interview standard is expected linear.'))

    d.append(("interviewer",
        'Variant: return true or false whether a pair exists.'))

    d.append(("candidate",
        'Same idea with a set of seen values. Still look up complement before insert.'))

    d.append(("interviewer",
        'Variant: sorted array only.'))

    d.append(("candidate",
        'Two pointers left right in O of n time O of one space. Different constraint. I name both tools and pick based on sortedness.'))

    d.append(("interviewer",
        'Variant: return all pairs without duplicate pairs.'))

    d.append(("candidate",
        'Different problem. Needs careful multiset counting or sort unique. I treat as follow up, not a silent change to one pair code.'))

    d.append(("interviewer",
        'Where does this pattern show up in fintech style tasks?'))

    d.append(("candidate",
        'Matching two ledger legs, finding two fee components that fill a budget, indexing by amount to find complements. Map from value to identity is the reusable muscle.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I create two_sum.py and define two sum with nums and target.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I create an empty dict named seen. I loop j and x via enumerate.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I compute need equals target minus x. If need in seen I return seen need and j. Otherwise seen x equals j.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write tests for classic, duplicates, zeros, negatives. I run until green. I speak expected O of n.'))

    d.append(("interviewer",
        'A reviewer says just use nested loops, it is clearer. Your response?'))

    d.append(("candidate",
        'Clear brute force is a fine first sentence. Shipping quadratic on large n is not. I keep brute force as the naive contrast and ship the map.'))

    d.append(("interviewer",
        'How long should this take in a real warm up?'))

    d.append(("candidate",
        'About fifteen minutes including tests, not half the interview. Clock management matters if a harder scenario follows.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'I solve two sum with a one pass value to index map. For each value I look for target minus value already seen, else I store the index. Lookup before store prevents self pairing. Naive double loop is O of n squared. Expected time O of n, space O of n. Tests cover the classic nine case, duplicate threes, zeros, and negatives. Follow ups include sorted two pointers and all pairs.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'We will use remaining time as a technique clinic so this episode is worth a full listen. Explain the difference between storing values in a set versus value to index in a map, slowly.'))

    d.append(("candidate",
        'If the problem only asks whether a pair exists, a set of previously seen values is enough because the answer is boolean. When the problem asks for indices, the set forgets where the value lived. The map from value to index remembers a position so you can return it. If multiple indices share a value, one stored index is enough for a single pair answer as long as you look up before writing the current index. If you needed every index of a value, you would store lists. Choosing set versus map is really choosing what payload the problem requires, not a random preference.'))

    d.append(("interviewer",
        'Walk a whiteboard teaching script you would use for a junior.'))

    d.append(("candidate",
        'I write the array on a line with indices under it. I draw an empty box labeled seen. I point to the first number and say I have not seen its partner yet so I put the number in the box with its index. I move to the next number, compute target minus this number out loud, and look in the box. If the partner is there I circle both indices and stop. If not I add this number to the box. The story is always have I already seen my partner. That story is the algorithm.'))

    d.append(("interviewer",
        'Now criticize a wrong solution that sorts the array then uses two pointers without tracking indices.'))

    d.append(("candidate",
        'Sorting finds two values that sum to target quickly but destroys the original positions unless you sort pairs of value and index together. If the interviewer asked for indices, sorting values alone is incomplete. If they asked only for the values, sorted two pointers is excellent. Matching the return type is part of correctness. I would rewrite as list of pairs sorted by value, then two pointers, then return the stored original indices.'))

    d.append(("interviewer",
        'Complexity comparison spoken as you would at end of block.'))

    d.append(("candidate",
        'Brute force time quadratic space constant. Hash map time expected linear space linear. Sort pairs time n log n space linear if copying pairs. I pick hash map for unsorted index return. I can implement sort pairs if hash structures were forbidden.'))

    d.append(("interviewer",
        'Edge case clinic: target zero with mixture of positives negatives and zeros.'))

    d.append(("candidate",
        'Possible pairs include zero with zero if two zeros exist, or three with negative three. The same complement logic holds because need equals target minus x works for negatives. Tests should include zero zero target zero and three negative three target zero. I never assume all positives.'))

    d.append(("interviewer",
        'Edge case clinic: integer overflow in other languages when computing need.'))

    d.append(("candidate",
        'In Python integers expand. In languages with fixed width, target minus x might overflow. Interview Python ignores this. In production C plus plus I might cast carefully or use sixty four bit. One sentence awareness is enough live.'))

    d.append(("interviewer",
        'Testing clinic: differential testing idea.'))

    d.append(("candidate",
        'Write a brute force pair finder for n up to a few hundred. Generate random small arrays with a planted pair, run both algorithms, compare index pairs for sum correctness. This catches self pair bugs and off by one returns. I do this if time remains after primary tests.'))

    d.append(("interviewer",
        'Communication clinic: what to say first after hearing the problem.'))

    d.append(("candidate",
        'I restate in one or two sentences, ask whether one solution is guaranteed, ask about negatives and duplicates, then propose naive quadratic and improved linear map, then hand walk, then code. That order scores process points even before perfect code.'))

    d.append(("interviewer",
        'Failure mode clinic: you return indices in reverse order of what a hidden test expects.'))

    d.append(("candidate",
        'Problem says any order. If a grader is strict, I check the problem statement. For Airwallex style human interviews any order is fine. I mention any order when I return.'))

    d.append(("interviewer",
        'Transfer clinic: two sum design in a stream of payments where you cannot store all.'))

    d.append(("candidate",
        'Exact two sum over an unbounded stream needs more product constraints, like only looking back window of time. That becomes a windowed map with eviction, combining two sum with sliding window ideas. I would reclarify rather than force full history map in memory forever.'))

    d.append(("interviewer",
        'Final drill: without looking at code, recite pseudocode once more.'))

    d.append(("candidate",
        'Empty map. For each index and value, need is target minus value, if need in map return stored index and current index, else map value to current index. Done.'))

    d.append(("interviewer",
        'Minute summary again for muscle memory.'))

    d.append(("candidate",
        'Two sum uses a one pass hash map from value to index. Look for the complement before storing the current value. That prevents self pairing and returns indices in expected linear time. Brute force is the quadratic contrast. Tests must include duplicates and negatives. This is warm up map muscle for harder scenario problems.'))

    d.append(("interviewer",
        'Shadow practice. I will prompt stages; answer in full candidate voice. Stage: restate.'))

    d.append(("candidate",
        'I need two different indices whose values sum to the target. Exactly one solution is assumed. I will use a hash map from value to index in one pass.'))

    d.append(("interviewer",
        'Stage: naive versus better.'))

    d.append(("candidate",
        'Naive nested loops check all pairs in quadratic time. Better stores seen values to indices and looks up the complement target minus current in expected constant time per element, overall expected linear time.'))

    d.append(("interviewer",
        'Stage: hand walk two seven eleven fifteen target nine.'))

    d.append(("candidate",
        'See two, store index zero. See seven, need two, found at zero, return zero and one.'))

    d.append(("interviewer",
        'Stage: self pair trap.'))

    d.append(("candidate",
        'If I store before lookup, a lone four with target eight might return the same index twice. Lookup before store fixes it. Two fours with target eight correctly returns two indices.'))

    d.append(("interviewer",
        'Stage: tests.'))

    d.append(("candidate",
        'Classic nine, three three six, zero four three zero, negatives. Complexity expected linear time linear space.'))

    d.append(("interviewer",
        'Stage: implementation order.'))

    d.append(("candidate",
        'Write function, empty dict, enumerate loop, lookup then store, tests, run green, stop.'))

    d.append(("interviewer",
        'Another full restate for audio muscle memory. Pretend brand new problem read.'))

    d.append(("candidate",
        'Array of ints and a target. Return indices of two numbers adding to target. Not the same element twice. I clarify uniqueness of solution, duplicates, negatives, and that I need indices not values. I choose one pass hash map of value to index, looking up target minus value before inserting the current value. Brute force double loop is the fallback explanation. Complexity expected O of n time and O of n space. I will encode the classic example as my first test.'))

    d.append(("interviewer",
        'Explain map memory layout as if drawing.'))

    d.append(("candidate",
        'Each key is a number from the array. Each value is the last index where I saw it, or the first if I choose not to overwrite. Boxes fill as I scan left to right. When complement hits, I draw an arrow from current index back to the boxed index.'))

    d.append(("interviewer",
        'What if interviewer forbids hash maps?'))

    d.append(("candidate",
        'I sort a list of pairs value and original index, then two pointers moving on values, return original indices when sum matches. Time n log n. I state tradeoff.'))

    d.append(("interviewer",
        'Closing shadow: one minute pitch.'))

    d.append(("candidate",
        'One pass map, complement lookup before insert, expected linear, tests for duplicates and negatives, ready to code offline without AI.'))

    d.append(("narrator",
        'Speed recap. Two sum indices. Complement in map. Lookup before write. Expected O of n. Classic tests. Replay, then code AI off for thirty minutes.'))

    return d
