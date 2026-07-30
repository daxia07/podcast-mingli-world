"""Mock coding interview (~20 min): Merge intervals."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. Given an array of intervals where intervals i equals start i comma end i, merge all overlapping intervals and return an array of the non overlapping intervals that cover all the intervals in the input. Treat intervals as closed on integers so touching endpoints merge.'))

    d.append(("candidate",
        'Restating. Produce the minimal set of disjoint intervals covering the same range union. Clarifying. Inclusive ends? Touch merge? Sorted input? Empty? Start always less or equal end?'))

    d.append(("interviewer",
        'Closed ints, touch merges, input may be unsorted, empty returns empty, start less or equal end guaranteed.'))

    d.append(("candidate",
        'Naive: repeatedly find any overlapping pair and merge until stable. Messy complexity. Better: sort by start ascending. Initialize current as a copy of the first interval. For each next interval, if next start is less or equal current end, set current end to max of ends; else emit current and start a new current. Emit the last current. Linear after sort.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because sorting makes a single forward scan correct and O of n log n is the standard optimal offline merge. Calendar and ledger range problems reuse this subroutine constantly.'))

    d.append(("interviewer",
        'Hand walk one three, two six, eight ten, fifteen eighteen.'))

    d.append(("candidate",
        'Current one three merges with two six to one six. Eight starts new. Fifteen starts new. Result one six, eight ten, fifteen eighteen.'))

    d.append(("interviewer",
        'Hand walk unsorted five ten, one three, two six.'))

    d.append(("candidate",
        'Sort to one three, two six, five ten. Merge to one ten.'))

    d.append(("interviewer",
        'Contained two four inside one ten.'))

    d.append(("candidate",
        'Start inside, end max stays ten. Contained absorbed.'))

    d.append(("interviewer",
        'Touch one two and two three.'))

    d.append(("candidate",
        'Two less or equal two, merge to one three. Touch policy load bearing for closed intervals.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function merge intervals. If empty return empty. Sort by start. merged list. current copy of first. For iv in rest: if iv start less or equal current end: current end equals max ends else append current and current equals copy iv. Append current. Return merged. Load bearing: sort first. Load bearing: max end. Load bearing: less or equal for touch.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'Empty. Single. No overlaps. All merge to one. Contained. Touching. Unsorted. Negative times if allowed by product.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test classic. test touching. test contained. test unsorted. test empty single. Optional property: union coverage equals via brute on small sets.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Time O of n log n dominated by sort. Space O of n for output. Linear if input already sorted and you trust that.'))

    d.append(("interviewer",
        'Insert interval follow up.'))

    d.append(("candidate",
        'Walk before, merge through overlap, after. Same merge primitive.'))

    d.append(("interviewer",
        'Meeting rooms can attend all?'))

    d.append(("candidate",
        'Different: detect any overlap count, not merge output. Related sort by start.'))

    d.append(("interviewer",
        'Half open intervals.'))

    d.append(("candidate",
        'Touch may not merge. Policy must match domain.'))

    d.append(("interviewer",
        'Why copy intervals?'))

    d.append(("candidate",
        'Avoid mutating caller input when editing ends.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I sort a shallow copy by start.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I scan merging into current and merged list.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I test classic, touch, contained, unsorted.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I speak O of n log n and stop.'))

    d.append(("interviewer",
        'Candidate forgot sort and used example that was pre sorted. Risk?'))

    d.append(("candidate",
        'Hidden bug on unsorted tests. Always sort unless guaranteed. I add an unsorted fixture.'))

    d.append(("interviewer",
        'Interval trees?'))

    d.append(("candidate",
        'For dynamic online queries. Offline full list merge is sort scan.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'Merge intervals by sorting on start then scanning, merging when next start is less or equal current end using max end. Touch merges for closed integers. O of n log n. Tests cover classic, touch, contained, unsorted. Foundation for calendar and range union tasks.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'Technique clinic: why sorting is essential.'))

    d.append(("candidate",
        'Without order, any interval might overlap any other, suggesting quadratic checks. Sorting by start means when you process intervals left to right, the only interval you need to consider merging with is the current open merged segment. Past emitted segments end before the current start, so they cannot overlap future intervals with larger starts. That structural fact makes one pass enough.'))

    d.append(("interviewer",
        'Clinic: formalize non overlap of emitted segments.'))

    d.append(("candidate",
        'When you emit current and start a new one, the new start is greater than the emitted end. Future intervals have starts at least the new start after sort, so greater than the emitted end. Hence no future merge can reach back into emitted segments. Safety of irrevocable emit is guaranteed by the sort.'))

    d.append(("interviewer",
        'Clinic: inclusive versus exclusive ends with numbers.'))

    d.append(("candidate",
        'Closed one two and two three overlap at two and merge if less or equal. Half open one two and two three touch but do not share points, often kept separate. Product domain decides. Coding interviews usually use closed integers and merge on less or equal. I restate policy before coding.'))

    d.append(("interviewer",
        'Clinic: negative timestamps and zero length.'))

    d.append(("candidate",
        'If start equals end, a point interval still merges when another covers that point under closed rules. Negative starts are fine if order is numeric sort. I do not assume positive.'))

    d.append(("interviewer",
        'Clinic: in place merge attempts.'))

    d.append(("candidate",
        'You can write merged intervals into the front of a sorted list with a write pointer. Tricky under pressure. I prefer a new list for clarity unless memory is constrained. Clarity wins interviews.'))

    d.append(("interviewer",
        'Clinic: calendar free time outline.'))

    d.append(("candidate",
        'Gather all busy intervals from all people, merge them, then gaps between merged busy ranges are free. Merge is the key subroutine. I mention this if the interviewer pivots to scheduling.'))

    d.append(("interviewer",
        'Clinic: insert interval phases.'))

    d.append(("candidate",
        'Phase one push every interval ending before new starts. Phase two merge all that overlap the new interval into one new. Phase three push the rest. Works on already sorted disjoint lists in linear time without resorting everything.'))

    d.append(("interviewer",
        'Clinic: testing coverage equality idea.'))

    d.append(("candidate",
        'For small integer universes, mark covered points by brute force from input and from output, compare bitsets. Heavy but strong. Simpler: hand fixtures for contained touch unsorted.'))

    d.append(("interviewer",
        'Final pseudocode recitation.'))

    d.append(("candidate",
        'sort by start. current first. for each next if overlaps merge max end else push current and reset current. push last. return.'))

    d.append(("interviewer",
        'Minute summary.'))

    d.append(("candidate",
        'Merge intervals sorts by start then scans merging on overlap or touch with max end. Linear after sort. Policy on touching matters. Foundation for range unions in scheduling and ledgers. Tests must include unsorted and contained cases.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Merge overlapping closed intervals into minimal disjoint list. Sort by start, scan, merge on less or equal with max end.'))

    d.append(("interviewer",
        'Why sort.'))

    d.append(("candidate",
        'Makes one forward pass correct. Emitted segments cannot be reached by later larger starts.'))

    d.append(("interviewer",
        'Touch policy.'))

    d.append(("candidate",
        'Closed integers merge when next start less or equal current end. Half open might differ. I restate.'))

    d.append(("interviewer",
        'Hand walk unsorted.'))

    d.append(("candidate",
        'Sort first. Then merge chain. Contained intervals absorbed by max end.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'Given intervals start end, I return merged non overlapping coverage. I sort by start. I keep a current interval and either extend its end when the next overlaps or touches, or I push current and replace it. Time n log n from sort. This is the offline merge used in calendars and range unions.'))

    d.append(("interviewer",
        'Insert interval contrast.'))

    d.append(("candidate",
        'Already sorted disjoint list plus one new: push before, merge middle, push after. Linear without full resort if input guaranteed sorted disjoint.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Classic, touching, contained, unsorted, empty, single.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sort scan merge max end, touch merges, O of n log n, offline code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Merge overlapping closed intervals into minimal disjoint list. Sort by start, scan, merge on less or equal with max end.'))

    d.append(("interviewer",
        'Why sort.'))

    d.append(("candidate",
        'Makes one forward pass correct. Emitted segments cannot be reached by later larger starts.'))

    d.append(("interviewer",
        'Touch policy.'))

    d.append(("candidate",
        'Closed integers merge when next start less or equal current end. Half open might differ. I restate.'))

    d.append(("interviewer",
        'Hand walk unsorted.'))

    d.append(("candidate",
        'Sort first. Then merge chain. Contained intervals absorbed by max end.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'Given intervals start end, I return merged non overlapping coverage. I sort by start. I keep a current interval and either extend its end when the next overlaps or touches, or I push current and replace it. Time n log n from sort. This is the offline merge used in calendars and range unions.'))

    d.append(("interviewer",
        'Insert interval contrast.'))

    d.append(("candidate",
        'Already sorted disjoint list plus one new: push before, merge middle, push after. Linear without full resort if input guaranteed sorted disjoint.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Classic, touching, contained, unsorted, empty, single.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sort scan merge max end, touch merges, O of n log n, offline code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Merge overlapping closed intervals into minimal disjoint list. Sort by start, scan, merge on less or equal with max end.'))

    d.append(("interviewer",
        'Why sort.'))

    d.append(("candidate",
        'Makes one forward pass correct. Emitted segments cannot be reached by later larger starts.'))

    d.append(("interviewer",
        'Touch policy.'))

    d.append(("candidate",
        'Closed integers merge when next start less or equal current end. Half open might differ. I restate.'))

    d.append(("interviewer",
        'Hand walk unsorted.'))

    d.append(("candidate",
        'Sort first. Then merge chain. Contained intervals absorbed by max end.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'Given intervals start end, I return merged non overlapping coverage. I sort by start. I keep a current interval and either extend its end when the next overlaps or touches, or I push current and replace it. Time n log n from sort. This is the offline merge used in calendars and range unions.'))

    d.append(("interviewer",
        'Insert interval contrast.'))

    d.append(("candidate",
        'Already sorted disjoint list plus one new: push before, merge middle, push after. Linear without full resort if input guaranteed sorted disjoint.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Classic, touching, contained, unsorted, empty, single.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Sort scan merge max end, touch merges, O of n log n, offline code AI off.'))

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
        'Speed recap. Sort by start. Merge overlap or touch. Max end. O of n log n. Code AI off.'))

    return d
