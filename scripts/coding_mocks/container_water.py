"""Mock coding interview (~20 min): Container with most water."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the i-th line are i and height i. Find two lines that together with the x axis form a container with the most water. Return the maximum amount of water a container can store. Width is the difference of indices.'))

    d.append(("candidate",
        'Restating. Maximize min of height i height j times j minus i over i less than j. Clarifying. Non negative heights? n less than two? Return area only? Need indices?'))

    d.append(("interviewer",
        'Non negative. If fewer than two lines return zero. Area only. Indices not required.'))

    d.append(("candidate",
        'Naive: try all pairs O of n squared. Improved two pointers: left at zero, right at n minus one. Compute area, track best. Move the pointer at the shorter height inward, because width shrinks and the only hope is a taller limiting height. If equal, move either side with a consistent rule. This examines O of n candidate edges and is the standard optimal for this problem.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because O of n versus O of n squared matters at scale, and because the move shorter rule is a classic correctness story interviewers listen for. Randomly moving pointers is not enough.'))

    d.append(("interviewer",
        'State the correctness intuition for moving the shorter side.'))

    d.append(("candidate",
        'Suppose height left is less or equal height right. Any pair using left with a closer right has smaller width and height at most height left, so area is strictly less than the current area with the far right. Thus left can be discarded. Symmetric if right is shorter.'))

    d.append(("interviewer",
        'Hand walk heights one eight six two five four eight three seven at a high level.'))

    d.append(("candidate",
        'Start at ends, compute areas, move shorter each time, track best. The classic optimum is forty nine. Offline I verify with a brute force oracle on this fixture.'))

    d.append(("interviewer",
        'Hand walk one two one.'))

    d.append(("candidate",
        'Ends area two. Later pairs area at most one. Best two.'))

    d.append(("interviewer",
        'Width bug: plus one or not?'))

    d.append(("candidate",
        'Width is right minus left, not plus one. Two lines at indices zero and one with height one each store area one.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function max area height. If length less than two return zero. left zero right n minus one best zero. While left less than right: best equals max best and min heights times right minus left. If height left less than height right: left plus one else right minus one. Return best. Load bearing: move shorter. Load bearing: width index delta.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'n less than two zero. All zeros. Strictly increasing. Two elements. Equal tall ends. Classic forty nine fixture.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test two lines. test classic. test zeros. test equal heights. Optional random compare to brute force for n up to twenty.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Time O of n. Extra space O of one.'))

    d.append(("interviewer",
        'Why not sort?'))

    d.append(("candidate",
        'Sorting destroys positions required for width. Never sort for this problem.'))

    d.append(("interviewer",
        'Relation to trapping rain water?'))

    d.append(("candidate",
        'Different problem about total trapped cells; do not mix algorithms.'))

    d.append(("interviewer",
        'Relation to largest rectangle in histogram?'))

    d.append(("candidate",
        'Also different; uses stack. I name the distinction.'))

    d.append(("interviewer",
        'Equal heights: move left or right?'))

    d.append(("candidate",
        'Either is fine if consistent; some move both. Area already counted at current width.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I write max area with two pointers and best.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I implement the while loop with area update and move shorter.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I test two lines, classic, zeros. I compare to brute force helper on the classic list.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I speak O of n O of one space and stop.'))

    d.append(("interviewer",
        'Reviewer moved the taller pointer and some tests pass. Response?'))

    d.append(("candidate",
        'Lucky fixtures. I explain the proof and fix to move shorter. I add a case where moving taller fails.'))

    d.append(("interviewer",
        'Language without big ints for area?'))

    d.append(("candidate",
        'Use sixty four bit for the product in C like languages. Python ints are fine.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'Container with most water: two pointers at the ends, area is min height times index width, always move the shorter pointer, O of n time O of one space. Naive all pairs is the contrast. Not trap rain water and not histogram. Tests include tiny arrays and the classic fixture.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'Technique clinic: geometric meaning of area formula.'))

    d.append(("candidate",
        'Two vertical lines and the x axis form a rectangle of water that cannot be taller than the shorter line or water spills. Width is horizontal distance between indices. Area is that product. Diagonals and slopes do not matter in this problem; it is not a continuous integral, it is discrete index geometry.'))

    d.append(("interviewer",
        'Clinic: why starting at maximum width is a good greedy seed.'))

    d.append(("candidate",
        'Maximum width is unique at the ends. Any better area must compensate smaller width with larger min height. Two pointers explore that trade space systematically by discarding the side that cannot improve, rather than randomly sampling pairs.'))

    d.append(("interviewer",
        'Clinic: full proof again slower.'))

    d.append(("candidate",
        'Take left right with height left less or equal height right. Consider any k between them. Area left k is at most height left times k minus left. Because k minus left is less than right minus left, that area is less than height left times right minus left which is the current area. Therefore no better pair uses this left with any inner right. Advance left. Symmetric argument if right is the strictly shorter line. When equal, either side may be advanced because each is a limiting height.'))

    d.append(("interviewer",
        'Clinic: implement brute force oracle in words for tests.'))

    d.append(("candidate",
        'best zero. for i in range n: for j in range i plus one n: best max with min height i height j times j minus i. return best. Use for n less equal fifty against the two pointer function on random heights.'))

    d.append(("interviewer",
        'Clinic: trap rain water contrast with numbers.'))

    d.append(("candidate",
        'Elevation one zero one traps one unit in the middle. Container with most water on the same array uses the two ones width two area one, same number coincidentally but different definition. Trap rain sums water above each index. Different code paths. I refuse to mix.'))

    d.append(("interviewer",
        'Clinic: largest rectangle in histogram contrast.'))

    d.append(("candidate",
        'Histogram uses every bar as height of a rectangle extending left right until shorter bars, usually monotonic stack. Container problem only picks two lines. If I start coding stack here I am solving the wrong problem.'))

    d.append(("interviewer",
        'Clinic: equal height long plateau.'))

    d.append(("candidate",
        'Algorithm still O of n. Areas decrease as width shrinks if heights stay equal. Best often at widest equal pair which is considered early when pointers are at ends if ends are tall, or later if tall equals appear inside after moves.'))

    d.append(("interviewer",
        'Clinic: what you say if interviewer asks for the pair of indices as well.'))

    d.append(("candidate",
        'I keep argmax left right when I update best. Same algorithm. Return indices plus area or just indices per A P I.'))

    d.append(("interviewer",
        'Final pseudocode recitation.'))

    d.append(("candidate",
        'left zero right n minus one best zero. while left less right: update best with min height times width. if left height less than right height left plus one else right minus one. return best.'))

    d.append(("interviewer",
        'Minute summary.'))

    d.append(("candidate",
        'Most water container is two pointers from the ends moving the shorter line inward. Area is min height times index width. Linear time constant space. Prove by discarding the shorter line. Not trap rain and not histogram. Test with oracle on small n.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Max area formed by two lines: min height times index distance. Two pointers from ends, move shorter.'))

    d.append(("interviewer",
        'Why move shorter.'))

    d.append(("candidate",
        'Width shrinks either way. The shorter limits height. Any pair using the shorter with a closer partner is worse than current. Discard shorter.'))

    d.append(("interviewer",
        'Naive.'))

    d.append(("candidate",
        'All pairs quadratic. Fine as oracle for tests, not as ship solution.'))

    d.append(("interviewer",
        'Width formula.'))

    d.append(("candidate",
        'Right minus left not plus one. Two adjacent unit lines area equals the min height.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I maximize water between two vertical lines on an index axis. Area is min of the two heights times the distance between indices. I place pointers at both ends and repeatedly move the shorter pointer inward while tracking the best area. This is linear time and constant extra space. I am not solving trapping rain water or histogram largest rectangle.'))

    d.append(("interviewer",
        'Proof sketch thirty seconds.'))

    d.append(("candidate",
        'Shorter left with any inner right has smaller width and height at most left height, so smaller area than left with far right. Advance left. Symmetric for right.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Two elements, zeros, classic forty nine fixture, equal heights, random versus brute for small n.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Two pointers move shorter, width index delta, O of n, not trap rain, offline code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Max area formed by two lines: min height times index distance. Two pointers from ends, move shorter.'))

    d.append(("interviewer",
        'Why move shorter.'))

    d.append(("candidate",
        'Width shrinks either way. The shorter limits height. Any pair using the shorter with a closer partner is worse than current. Discard shorter.'))

    d.append(("interviewer",
        'Naive.'))

    d.append(("candidate",
        'All pairs quadratic. Fine as oracle for tests, not as ship solution.'))

    d.append(("interviewer",
        'Width formula.'))

    d.append(("candidate",
        'Right minus left not plus one. Two adjacent unit lines area equals the min height.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I maximize water between two vertical lines on an index axis. Area is min of the two heights times the distance between indices. I place pointers at both ends and repeatedly move the shorter pointer inward while tracking the best area. This is linear time and constant extra space. I am not solving trapping rain water or histogram largest rectangle.'))

    d.append(("interviewer",
        'Proof sketch thirty seconds.'))

    d.append(("candidate",
        'Shorter left with any inner right has smaller width and height at most left height, so smaller area than left with far right. Advance left. Symmetric for right.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Two elements, zeros, classic forty nine fixture, equal heights, random versus brute for small n.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Two pointers move shorter, width index delta, O of n, not trap rain, offline code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Max area formed by two lines: min height times index distance. Two pointers from ends, move shorter.'))

    d.append(("interviewer",
        'Why move shorter.'))

    d.append(("candidate",
        'Width shrinks either way. The shorter limits height. Any pair using the shorter with a closer partner is worse than current. Discard shorter.'))

    d.append(("interviewer",
        'Naive.'))

    d.append(("candidate",
        'All pairs quadratic. Fine as oracle for tests, not as ship solution.'))

    d.append(("interviewer",
        'Width formula.'))

    d.append(("candidate",
        'Right minus left not plus one. Two adjacent unit lines area equals the min height.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I maximize water between two vertical lines on an index axis. Area is min of the two heights times the distance between indices. I place pointers at both ends and repeatedly move the shorter pointer inward while tracking the best area. This is linear time and constant extra space. I am not solving trapping rain water or histogram largest rectangle.'))

    d.append(("interviewer",
        'Proof sketch thirty seconds.'))

    d.append(("candidate",
        'Shorter left with any inner right has smaller width and height at most left height, so smaller area than left with far right. Advance left. Symmetric for right.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Two elements, zeros, classic forty nine fixture, equal heights, random versus brute for small n.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Two pointers move shorter, width index delta, O of n, not trap rain, offline code AI off.'))

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
        'Speed recap. Two pointers. Move shorter. Width index delta. O of n. Code AI off.'))

    return d
