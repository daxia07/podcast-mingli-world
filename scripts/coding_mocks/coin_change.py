"""Mock coding interview (~20 min): Coin change."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. You are given an integer array coins representing coin denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. You may assume you have an infinite number of each kind of coin. If that amount cannot be made, return negative one.'))

    d.append(("candidate",
        'Restating. Unbounded knapsack minimum count to exact amount. Clarifying. Amount zero? Empty coins? Coins unsorted? Return count only not combination? Greedy allowed?'))

    d.append(("interviewer",
        'Amount zero returns zero. Empty coins with positive amount is impossible. Coins positive unsorted. Count only. Greedy is not assumed correct for arbitrary denominations.'))

    d.append(("candidate",
        'Naive recursion exponential. Greedy largest first fails on some systems. Correct: bottom up D P. best of a is min coins for exact a. best zero zero. best other init infinity. For value from one to amount: for each coin if coin less or equal value, best value min with best value minus coin plus one. End: if best amount infinite return negative one else best amount. B F S on remainders also finds minimum count as shortest path.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because arbitrary denominations make greedy wrong, and D P is the standard linear in amount times coin types solution interviewers expect, with a clear greedy counterexample you can state.'))

    d.append(("interviewer",
        'Greedy trap: coins one three four amount six.'))

    d.append(("candidate",
        'Greedy takes four plus two ones total three. Optimal two threes total two. D P returns two. I always mention this if greedy comes up.'))

    d.append(("interviewer",
        'Hand walk coins one two five amount eleven.'))

    d.append(("candidate",
        'D P builds up; eleven becomes three, for example two fives and one one. Return three.'))

    d.append(("interviewer",
        'Impossible: coins two amount three.'))

    d.append(("candidate",
        'Odd amount with only even coin. best three stays infinity. Return negative one.'))

    d.append(("interviewer",
        'Why sentinel amount plus one works?'))

    d.append(("candidate",
        'With coin values at least one you never need more than amount coins. amount plus one is larger than any feasible answer.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function coin change coins amount. If amount zero return zero. inf equals amount plus one. best list of inf, best zero equals zero. For v in one to amount: for c in coins: if c less equal v: best v equals min best v and best v minus c plus one. Return best amount if less than inf else negative one. Load bearing: exact amount. Load bearing: not greedy.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'Amount zero. Empty coins. Single coin divides. Impossible. Greedy trap six. Large coin greater than amount skipped. Order of coins irrelevant.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test eleven equals three. test three with two equals negative one. test six with one three four equals two. test amount zero. test empty coins positive amount.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Time O of amount times number of coin types. Space O of amount. Reconstruct combination as follow up with parent pointers.'))

    d.append(("interviewer",
        'Combination count sister problem?'))

    d.append(("candidate",
        'Different D P and loop order story. Do not mix with min count.'))

    d.append(("interviewer",
        'B F S approach?'))

    d.append(("candidate",
        'Shortest path on remainders; valid alternative.'))

    d.append(("interviewer",
        'When greedy works?'))

    d.append(("candidate",
        'Canonical coin systems; not general. Need proof or stick to D P.'))

    d.append(("interviewer",
        'Reconstruct coins?'))

    d.append(("candidate",
        'Store chosen coin at each value when improving best; walk back from amount.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I allocate best array with inf and best zero zero.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write double loop updates.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I return conditional negative one. Tests include greedy trap and impossible.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I speak O of amount times coins and stop.'))

    d.append(("interviewer",
        'Bug used slash slash floor thinking for something else; here wrong answer is greedy.'))

    d.append(("candidate",
        'I delete greedy path, keep D P, re-run trap test.'))

    d.append(("interviewer",
        'Amount huge memory?'))

    d.append(("candidate",
        'Array size issue; mention B F S or special math. Interview amounts usually moderate.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'Fewest coins for amount with unbounded denominations uses bottom up D P min of best remainder plus one. Not greedy; trap six with four three one. Impossible returns negative one. Amount zero returns zero. Time O of amount times coin types. Tests pin trap and impossible cases.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'Technique clinic: optimal substructure statement.'))

    d.append(("candidate",
        'If an optimal solution for amount uses a coin c as one of the coins, then the rest of the coins form an optimal solution for amount minus c. Therefore the minimum count for amount is one plus the minimum over coins c of the minimum count for amount minus c when those subamounts are feasible. That recurrence is exactly the D P transition. Base amount zero needs zero coins. Unreachable amounts stay at infinity.'))

    d.append(("interviewer",
        'Clinic: why order of coin loops matters for counting combinations but not for min count the same way.'))

    d.append(("candidate",
        'When counting the number of combinations, treating sequences as the same combination requires careful loop order so you do not count permutations separately. For minimum number of coins, taking min of plus one is order agnostic in the standard complete knapsack style updates as long as you use the updated or prior layer correctly. I still implement the common amount outer coin inner for min coins and I do not claim combination count code without re deriving it.'))

    d.append(("interviewer",
        'Clinic: draw the D P array growth for coins two three amount seven.'))

    d.append(("candidate",
        'Index zero through seven. best zero is zero. one inf. two one. three one. four two via two plus two. five two via two plus three. six two via three plus three. seven three via two plus previous five or three plus four. Return three. Example seven equals two plus two plus three.'))

    d.append(("interviewer",
        'Clinic: B F S layer meaning.'))

    d.append(("candidate",
        'Layer zero is amount remaining amount at start. Each edge subtracts a coin. First time you reach remainder zero, the depth is the min coins. Visited remainders prevent reprocessing. This is shortest path in an unweighted graph of remainders. Equivalent answer to D P.'))

    d.append(("interviewer",
        'Clinic: greedy works on some systems proof sketch awareness.'))

    d.append(("candidate",
        'Canonical coin systems have structural properties that greedy choice is safe. U S coins are often cited. Arbitrary sets do not. Interview rule: unless told canonical, use D P and keep the counterexample ready.'))

    d.append(("interviewer",
        'Clinic: reconstruct coins for amount eleven with one two five.'))

    d.append(("candidate",
        'While updating best v from best v minus c plus one, set choice v equals c. Then from amount walk choice, subtract, collect coins until zero. One possible result five five one. Useful follow up after count is correct.'))

    d.append(("interviewer",
        'Clinic: floating money mistake.'))

    d.append(("candidate",
        'This problem is integer amounts. Real money should use integer minor units not floats. I mention if the interviewer frames coins as currency.'))

    d.append(("interviewer",
        'Clinic: very large amount with few coins math.'))

    d.append(("candidate",
        'If coins are huge and amount huge, D P memory hurts. Frobenius coin problem for two coprime coins has formulas but general many coins is hard. Interview stays on D P.'))

    d.append(("interviewer",
        'Final pseudocode recitation.'))

    d.append(("candidate",
        'best zero zero others inf. for v one to amount for each coin if coin less equal v best v min with best v minus coin plus one. return best amount or negative one if inf.'))

    d.append(("interviewer",
        'Minute summary.'))

    d.append(("candidate",
        'Coin change fewest coins is unbounded knapsack D P with min of remainder plus one. Not greedy on arbitrary denominations. Impossible to negative one. Time amount times coin types. Tests include the six with four three one trap and impossible odd amounts with even coins.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Fewest coins to make amount with unlimited each denomination. D P min of remainder plus one. Impossible negative one.'))

    d.append(("interviewer",
        'Greedy trap.'))

    d.append(("candidate",
        'Coins one three four amount six: greedy three coins, optimal two. Always D P for general sets.'))

    d.append(("interviewer",
        'Recurrence.'))

    d.append(("candidate",
        'best amount equals min over coins of best amount minus coin plus one, with best zero zero and unreachable inf.'))

    d.append(("interviewer",
        'Complexity.'))

    d.append(("candidate",
        'Time amount times coin types. Space amount.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I need the minimum number of coins to reach an exact amount with infinite supply of each coin type. I build an array best where best of value is that minimum for that value. I initialize best zero to zero and others to a large sentinel. I try every coin at every value. If I cannot make the amount I return negative one. I refuse pure greedy unless the coin system is proven canonical. My first tests are eleven with one two five equals three, three with only two equals negative one, and six with one three four equals two.'))

    d.append(("interviewer",
        'B F S alternative.'))

    d.append(("candidate",
        'Shortest path on remainders, each coin an edge. Same min count.'))

    d.append(("interviewer",
        'Reconstruct.'))

    d.append(("candidate",
        'Store choice coin when improving best, walk back from amount.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Min coin D P not greedy, O of amount times coins, trap test green, code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Fewest coins to make amount with unlimited each denomination. D P min of remainder plus one. Impossible negative one.'))

    d.append(("interviewer",
        'Greedy trap.'))

    d.append(("candidate",
        'Coins one three four amount six: greedy three coins, optimal two. Always D P for general sets.'))

    d.append(("interviewer",
        'Recurrence.'))

    d.append(("candidate",
        'best amount equals min over coins of best amount minus coin plus one, with best zero zero and unreachable inf.'))

    d.append(("interviewer",
        'Complexity.'))

    d.append(("candidate",
        'Time amount times coin types. Space amount.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I need the minimum number of coins to reach an exact amount with infinite supply of each coin type. I build an array best where best of value is that minimum for that value. I initialize best zero to zero and others to a large sentinel. I try every coin at every value. If I cannot make the amount I return negative one. I refuse pure greedy unless the coin system is proven canonical. My first tests are eleven with one two five equals three, three with only two equals negative one, and six with one three four equals two.'))

    d.append(("interviewer",
        'B F S alternative.'))

    d.append(("candidate",
        'Shortest path on remainders, each coin an edge. Same min count.'))

    d.append(("interviewer",
        'Reconstruct.'))

    d.append(("candidate",
        'Store choice coin when improving best, walk back from amount.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Min coin D P not greedy, O of amount times coins, trap test green, code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Fewest coins to make amount with unlimited each denomination. D P min of remainder plus one. Impossible negative one.'))

    d.append(("interviewer",
        'Greedy trap.'))

    d.append(("candidate",
        'Coins one three four amount six: greedy three coins, optimal two. Always D P for general sets.'))

    d.append(("interviewer",
        'Recurrence.'))

    d.append(("candidate",
        'best amount equals min over coins of best amount minus coin plus one, with best zero zero and unreachable inf.'))

    d.append(("interviewer",
        'Complexity.'))

    d.append(("candidate",
        'Time amount times coin types. Space amount.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I need the minimum number of coins to reach an exact amount with infinite supply of each coin type. I build an array best where best of value is that minimum for that value. I initialize best zero to zero and others to a large sentinel. I try every coin at every value. If I cannot make the amount I return negative one. I refuse pure greedy unless the coin system is proven canonical. My first tests are eleven with one two five equals three, three with only two equals negative one, and six with one three four equals two.'))

    d.append(("interviewer",
        'B F S alternative.'))

    d.append(("candidate",
        'Shortest path on remainders, each coin an edge. Same min count.'))

    d.append(("interviewer",
        'Reconstruct.'))

    d.append(("candidate",
        'Store choice coin when improving best, walk back from amount.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Min coin D P not greedy, O of amount times coins, trap test green, code AI off.'))

    d.append(("interviewer",
        'We still have room for deliberate practice. Answer as in a real interview with complete sentences.'))

    d.append(("candidate",
        'Understood. I will keep restating the contract, naming the naive approach, naming the improved approach, walking an example, giving pseudocode, listing tests, and stating complexity before I claim done.'))

    d.append(("interviewer",
        'What does good clarifying sound like under time pressure?'))

    d.append(("candidate",
        'Three to six questions that change the design: input guarantees, return types, edge policies like empty input, and whether mutation is allowed. I avoid twenty trivial questions. Then I commit and design.'))

    d.append(("interviewer",
        'What does bad clarifying sound like?'))

    d.append(("candidate",
        'Silence then coding, or only asking questions that do not affect the algorithm. Or arguing style guides for five minutes. I will not do that.'))

    d.append(("interviewer",
        'Narrate how you use the last five minutes of a thirty minute block.'))

    d.append(("candidate",
        'I freeze features. I write or re-run the highest value tests. I restate complexity. I clean names if something is confusing on screen share. I do not open a second hard follow up unless the core is green.'))

    d.append(("interviewer",
        'How do you handle a bug found by the interviewer?'))

    d.append(("candidate",
        'I thank them, restate the failing case, form a hypothesis, fix the smallest place, re-run the mental test, and continue. I do not rewrite from scratch unless the approach is wrong.'))

    d.append(("interviewer",
        'How do you speak complexity without hand waving?'))

    d.append(("candidate",
        'I name the dominant loops or data structure costs, say expected versus worst if hashing, and name extra memory. I connect big O to the actual code lines I wrote.'))

    d.append(("interviewer",
        'How do you keep financial or product framing honest?'))

    d.append(("candidate",
        'One or two sentences max linking the toy problem to a real system, then back to the algorithm. I do not bluff market microstructure I do not know.'))

    d.append(("interviewer",
        'Final offline homework instruction to yourself.'))

    d.append(("candidate",
        'After this audio, blank file, no AI, implement from memory, run tests, then compare to a reference only after green or after twenty five minutes of struggle with a written fork plan.'))

    d.append(("narrator",
        'Speed recap. Min coin D P. Not greedy. O of amount times coins. Code AI off.'))

    return d
