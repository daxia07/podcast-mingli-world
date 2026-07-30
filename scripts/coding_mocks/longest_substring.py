"""Mock coding interview (~20 min): Longest substring without repeat."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. Given a string s, find the length of the longest substring without repeating characters. Substring means contiguous characters. Return the length only.'))

    d.append(("candidate",
        'Restating. Maximum length of a contiguous window where all characters are unique. Clarifying. Empty string? Case sensitive? Unicode? Return length only or the string too? May I use O of alphabet extra space?'))

    d.append(("interviewer",
        'Empty returns zero. Case sensitive. Treat Python characters as units. Length only. O of alphabet or O of n space is fine.'))

    d.append(("candidate",
        'Naive: check all O of n squared substrings with a set per window, or expand from each left until conflict. Improved: sliding window. Move right from zero to n minus one. Maintain left so s left through s right is unique. Use a map from character to last index. When s right was seen at an index greater or equal left, set left to that index plus one. Update last index of s right to right. Track max of right minus left plus one. Alternatively maintain a set and shrink left while conflict. Both are O of n.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because pure O of n is expected and the window invariant is a core interview pattern that transfers to stream windows and at most k distinct problems. It is still compact to implement.'))

    d.append(("interviewer",
        'Hand walk a b c a b c b b. Speak left, right, best.'))

    d.append(("candidate",
        'Expand to a b c best three. Next a conflicts, left moves to one, window b c a length three. Continue as in the classic; best remains three. Final answer three.'))

    d.append(("interviewer",
        'Hand walk a b b a carefully with the last index method.'))

    d.append(("candidate",
        'a then b best two. Second b conflicts, left moves past previous b. Then a: previous a is before left so do not jump backward; window becomes b a length two. Answer two. The forward only left move is load bearing.'))

    d.append(("interviewer",
        'Hand walk p w w k e w which answers three.'))

    d.append(("candidate",
        'p w best two. Second w shrinks to w. Then k e builds w k e length three. Final w conflicts and window becomes k e w length three. Best three.'))

    d.append(("interviewer",
        'What is the window invariant in one sentence?'))

    d.append(("candidate",
        'After each step, every character in the closed range left to right appears once, and best stores the max length of any valid window seen so far.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function length of longest substring s. last empty dict, left zero, best zero. For right, ch in enumerate s: if ch in last and last ch greater or equal left: left equals last ch plus one. last ch equals right. best equals max best and right minus left plus one. Return best. Load bearing: left never decreases. Load bearing: substring not subsequence.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'Empty zero. Single one. All unique n. All same one. abba two. Classic three. pwwkew three. Spaces and punctuation count as characters.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test empty, single, all same, abcabcbb, abba, pwwkew, dvdf equals three. Those pin left jump logic.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Time O of n. Space O of min of n and alphabet for the map.'))

    d.append(("interviewer",
        'Variant at most k distinct characters.'))

    d.append(("candidate",
        'Sliding window with frequency map and distinct counter; shrink while distinct greater than k. Same skeleton.'))

    d.append(("interviewer",
        'Set based implementation tradeoff.'))

    d.append(("candidate",
        'More incremental removals when left jumps far; still amortized O of n. Last index jumps in one assignment.'))

    d.append(("interviewer",
        'Binary search on length alternative.'))

    d.append(("candidate",
        'Check whether any window of length L is unique, O of n log n. Correct but more code than linear window.'))

    d.append(("interviewer",
        'Common bug with last index?'))

    d.append(("candidate",
        'Setting left to last plus one even when last is outside the window, which can move left backward. Guard with last greater or equal left, or left equals max left and last plus one.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I define the function with last dict, left, best.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write the for right loop with conflict update, last assign, best update.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I add tests empty, abba, classic three, pwwkew. I fix left jump if abba fails.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I speak O of n and stop.'))

    d.append(("interviewer",
        'Someone confuses substring and subsequence. How do you correct course?'))

    d.append(("candidate",
        'I redefine: contiguous required, so window algorithms apply. Longest unique subsequence would be a different count of distinct characters if order free, which is not this problem.'))

    d.append(("interviewer",
        'Time left: what do you skip?'))

    d.append(("candidate",
        'I skip k distinct and minimum window substring follow ups until base tests are green.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'Longest substring without repeating characters via sliding window and last seen indices. Expand right, advance left past prior occurrence, track max length. O of n time. Tests include classic three, abba, and pwwkew. Not a subsequence problem. Follow ups include at most k distinct.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'Technique clinic: derive the sliding window from the definition of substring uniqueness.'))

    d.append(("candidate",
        'A substring is defined by two ends left and right. Uniqueness means no character appears twice inside. If I only increase right, I may introduce a duplicate. Then I must increase left until the duplicate is gone. If I process right in increasing order and always repair left minimally, every right is processed once and left only moves forward, giving linear time. The max over all valid windows is the answer. That derivation prevents memorizing code without understanding.'))

    d.append(("interviewer",
        'Clinic: compare last index map versus frequency map versus set.'))

    d.append(("candidate",
        'Set answers membership: is this char inside the window. Frequency map counts occurrences and supports at most k distinct generalizations. Last index map answers where did this char last appear so I can jump left in one step. For pure no repeats, set or last index both work. I pick last index for jump efficiency and clear code, or set if I want a simple mental model of adding and removing.'))

    d.append(("interviewer",
        'Clinic: prove left never needs to move backward.'))

    d.append(("candidate",
        'Suppose left moved backward. The window would include characters already excluded for a previous right, and uniqueness for a larger right would not require re including them because any window ending at the new right that starts earlier than current left would include the conflict that forced left forward. Formally people use the argument that the minimal valid left is non decreasing in right. In practice I code left equals max of left and candidate which enforces non decrease.'))

    d.append(("interviewer",
        'Clinic hand walk d v d f which answers three.'))

    d.append(("candidate",
        'd best one. v window d v best two. second d: last d at zero, left becomes one, window v d length two. f extends v d f length three. Best three. This catches bugs that clear the entire window to empty on each conflict.'))

    d.append(("interviewer",
        'Clinic: subsequence confusion with an example.'))

    d.append(("candidate",
        'In a b c a, longest unique substring length three a b c. Longest unique subsequence can also pick a b c. In a a a, substring length one, and unique subsequence length one. The algorithms differ more on problems like longest increasing subsequence which is not a window problem. I say contiguous out loud every time.'))

    d.append(("interviewer",
        'Clinic: alphabet optimization.'))

    d.append(("candidate",
        'If characters are lowercase English only, last index array of size twenty six initialized to negative one can replace a hash map. For general Unicode, dict is correct. I implement dict unless constraints scream lowercase.'))

    d.append(("interviewer",
        'Clinic: how you would explain a bug to the interviewer when abba fails.'))

    d.append(("candidate",
        'I say I think left jumped backward because I assigned left to last plus one without checking last is inside the window. I fix with a guard, re-run abba, expect two, continue. Calm debug narration scores points.'))

    d.append(("interviewer",
        'Clinic: streaming version of the problem.'))

    d.append(("candidate",
        'If characters arrive as a stream and I must output the best length so far online, the same window state works: update on each new char and emit best. If I must emit the best substring content, I also store argmax start length. Memory is the window map.'))

    d.append(("interviewer",
        'Clinic: related problem minimum window substring containing all of t.'))

    d.append(("candidate",
        'Harder. Need need counts of required characters and a deficit counter. Expand right to satisfy, shrink left while satisfied, track min length. Same expand shrink skeleton, heavier state. I only open that door if asked.'))

    d.append(("interviewer",
        'Final pseudocode recitation.'))

    d.append(("candidate",
        'last map, left zero, best zero. for right char enumerate: if char seen inside window left equals last plus one. last equals right. best max with window length. return best.'))

    d.append(("interviewer",
        'Minute summary for muscle memory.'))

    d.append(("candidate",
        'Longest substring without repeating characters is a sliding window. Expand right, move left past previous occurrence, track max length. Linear time. Tests abba classic pwwkew. Contiguous not subsequence. Pattern transfers to other window problems.'))

    d.append(("interviewer",
        'Shadow practice full arc. Restate.'))

    d.append(("candidate",
        'Longest contiguous substring length with all unique characters. Empty is zero. Case sensitive. Sliding window with last seen index map.'))

    d.append(("interviewer",
        'Naive versus better.'))

    d.append(("candidate",
        'Naive checks many substrings quadratic. Better expands right, moves left past previous occurrence of the new character, tracks max length, linear time.'))

    d.append(("interviewer",
        'Hand walk abba.'))

    d.append(("candidate",
        'Build ab length two. Second b moves left. Final a does not jump left backward because previous a is outside window. Answer two.'))

    d.append(("interviewer",
        'Invariant.'))

    d.append(("candidate",
        'Window left to right always unique after each repair. Best is max length seen. Left only moves forward.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Empty, all same, classic abcabcbb three, abba two, pwwkew three, dvdf three.'))

    d.append(("interviewer",
        'Full restate again for memory.'))

    d.append(("candidate",
        'I am asked for the length of the longest substring without repeating characters. Substring is contiguous. I use a sliding window. As right advances over each character, if that character last appeared inside the window I move left to last index plus one. I update the last index and the best length. Time O of n space O of alphabet. I will not solve subsequence by mistake.'))

    d.append(("interviewer",
        'Set version in one breath.'))

    d.append(("candidate",
        'While right char in set remove left char and advance left, then add right char, update best with set size.'))

    d.append(("interviewer",
        'Bug narration abba wrong answer three.'))

    d.append(("candidate",
        'Left jumped backward reintroducing an earlier a. Fix max left with last plus one. Re-test abba equals two.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sliding window unique chars, left forward only, linear, classic tests green, code offline AI off.'))

    d.append(("interviewer",
        'Shadow practice full arc. Restate.'))

    d.append(("candidate",
        'Longest contiguous substring length with all unique characters. Empty is zero. Case sensitive. Sliding window with last seen index map.'))

    d.append(("interviewer",
        'Naive versus better.'))

    d.append(("candidate",
        'Naive checks many substrings quadratic. Better expands right, moves left past previous occurrence of the new character, tracks max length, linear time.'))

    d.append(("interviewer",
        'Hand walk abba.'))

    d.append(("candidate",
        'Build ab length two. Second b moves left. Final a does not jump left backward because previous a is outside window. Answer two.'))

    d.append(("interviewer",
        'Invariant.'))

    d.append(("candidate",
        'Window left to right always unique after each repair. Best is max length seen. Left only moves forward.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Empty, all same, classic abcabcbb three, abba two, pwwkew three, dvdf three.'))

    d.append(("interviewer",
        'Full restate again for memory.'))

    d.append(("candidate",
        'I am asked for the length of the longest substring without repeating characters. Substring is contiguous. I use a sliding window. As right advances over each character, if that character last appeared inside the window I move left to last index plus one. I update the last index and the best length. Time O of n space O of alphabet. I will not solve subsequence by mistake.'))

    d.append(("interviewer",
        'Set version in one breath.'))

    d.append(("candidate",
        'While right char in set remove left char and advance left, then add right char, update best with set size.'))

    d.append(("interviewer",
        'Bug narration abba wrong answer three.'))

    d.append(("candidate",
        'Left jumped backward reintroducing an earlier a. Fix max left with last plus one. Re-test abba equals two.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sliding window unique chars, left forward only, linear, classic tests green, code offline AI off.'))

    d.append(("interviewer",
        'Shadow practice full arc. Restate.'))

    d.append(("candidate",
        'Longest contiguous substring length with all unique characters. Empty is zero. Case sensitive. Sliding window with last seen index map.'))

    d.append(("interviewer",
        'Naive versus better.'))

    d.append(("candidate",
        'Naive checks many substrings quadratic. Better expands right, moves left past previous occurrence of the new character, tracks max length, linear time.'))

    d.append(("interviewer",
        'Hand walk abba.'))

    d.append(("candidate",
        'Build ab length two. Second b moves left. Final a does not jump left backward because previous a is outside window. Answer two.'))

    d.append(("interviewer",
        'Invariant.'))

    d.append(("candidate",
        'Window left to right always unique after each repair. Best is max length seen. Left only moves forward.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Empty, all same, classic abcabcbb three, abba two, pwwkew three, dvdf three.'))

    d.append(("interviewer",
        'Full restate again for memory.'))

    d.append(("candidate",
        'I am asked for the length of the longest substring without repeating characters. Substring is contiguous. I use a sliding window. As right advances over each character, if that character last appeared inside the window I move left to last index plus one. I update the last index and the best length. Time O of n space O of alphabet. I will not solve subsequence by mistake.'))

    d.append(("interviewer",
        'Set version in one breath.'))

    d.append(("candidate",
        'While right char in set remove left char and advance left, then add right char, update best with set size.'))

    d.append(("interviewer",
        'Bug narration abba wrong answer three.'))

    d.append(("candidate",
        'Left jumped backward reintroducing an earlier a. Fix max left with last plus one. Re-test abba equals two.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sliding window unique chars, left forward only, linear, classic tests green, code offline AI off.'))

    d.append(("narrator",
        'Speed recap. Sliding window unique chars. Left only forward. O of n. Code AI off after listen.'))

    return d
