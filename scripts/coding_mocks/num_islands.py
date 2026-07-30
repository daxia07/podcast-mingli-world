"""Mock coding interview (~20 min): Number of islands."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We will spend this block on a single coding problem, roughly the way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. Clarify requirements, explain approach, hand walk an example, give full word pseudocode, cover corners and complexity, then narrate implementation. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. Given an m by n two d binary grid which represents a map of one as land and zero as water, return the number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are surrounded by water. Four way connectivity only.'))

    d.append(("candidate",
        'Restating. Count connected components of land cells under four neighbor adjacency. Clarifying. May I mutate the grid? Diagonal connections? Empty grid? Chars or ints for zero one?'))

    d.append(("interviewer",
        'Mutation allowed. Four directions only not eight. Empty returns zero. Chars one and zero are fine.'))

    d.append(("candidate",
        'Approach is standard graph traversal rather than a false naive. Iterate each cell. On land, increment count and flood fill mark all reachable land via D F S or B F S, setting cells to water or using visited. Each flood is one island. Time O of rows times cols. Union find is an alternative with more code.'))

    d.append(("interviewer",
        'Why is the improved approach worth the extra structure?'))

    d.append(("candidate",
        'Because interviewers want to see you map a grid to an implicit graph and write a clean flood without leaking connectivity mistakes. This pattern underpins many grid problems.'))

    d.append(("interviewer",
        'Hand walk a small two island mental grid.'))

    d.append(("candidate",
        'Top left land blob flood as island one. Separated land elsewhere flood as island two. Water never increments. Count two.'))

    d.append(("interviewer",
        'All land one by three grid.'))

    d.append(("candidate",
        'First cell starts flood of entire grid. Count one. No second increment.'))

    d.append(("interviewer",
        'Checker pattern of lands not diagonal connected.'))

    d.append(("candidate",
        'With four connectivity each land is its own island if only diagonals touch. Eight connectivity would differ. Restate four.'))

    d.append(("interviewer",
        'Why mark visited when enqueue in B F S?'))

    d.append(("candidate",
        'Prevent the same land from entering the queue many times from different neighbors, which wastes time and can blow memory.'))

    d.append(("interviewer",
        'Describe the API you will implement, then full word pseudocode.'))

    d.append(("candidate",
        'Function num islands grid. If not grid return zero. r c dimensions. Def sink i j: if out of bounds or water return; set water; sink four neighbors. count zero. For each cell if land: count plus one; sink. Return count. Load bearing: increment then flood. Load bearing: four deltas only.'))

    d.append(("interviewer",
        'Walk corner cases one by one.'))

    d.append(("candidate",
        'Empty zero. All water zero. All land one. Single cell. Border lands. Two islands fixture. Large island recursion depth concern.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test all water. test all land. test two islands. test single. Optional iterative stack version test same results.'))

    d.append(("interviewer",
        'Complexity, precise.'))

    d.append(("candidate",
        'Time O of r c. Space O of r c worst recursion or queue. Iterative stack avoids Python recursion limits on huge islands.'))

    d.append(("interviewer",
        'Eight connected?'))

    d.append(("candidate",
        'Only if problem says so. Add diagonal deltas.'))

    d.append(("interviewer",
        'Max area of island?'))

    d.append(("candidate",
        'Return size from flood, track max.'))

    d.append(("interviewer",
        'Union find sketch.'))

    d.append(("candidate",
        'Union right and down neighbors of lands, count parents of lands.'))

    d.append(("interviewer",
        'Surrounded regions family?'))

    d.append(("candidate",
        'Same flood tools, different starts and marks.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left. What do you do?'))

    d.append(("candidate",
        'I do not start a harder follow up. I lock the tests we named, restate complexity, and keep the code readable. Working correct code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Simulate the implementation phase. Narrate what you type in order as if I watch your editor.'))

    d.append(("candidate",
        'I write dimensions and sink helper with four deltas.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write nested loops with count and sink.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I test fixtures. If recursion depth concerns me I rewrite sink iterative.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I speak O of r c and stop.'))

    d.append(("interviewer",
        'Bug counts land cells not islands.'))

    d.append(("candidate",
        'Forgot flood mark; every land increments. Fix mark whole component.'))

    d.append(("interviewer",
        'Bug off by one on borders.'))

    d.append(("candidate",
        'Bounds checks before grid access. Add border land tests.'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute.'))

    d.append(("candidate",
        'Number of islands counts connected land components with four way flood fill D F S or B F S. Mark visited by mutating to water. O of cells time. Tests cover all water, all land, multi island. Iterative flood if recursion is risky. Not eight connected unless asked.'))

    d.append(("interviewer",
        'What would you do differently if this shipped tomorrow versus interview code?'))

    d.append(("candidate",
        'I would add property tests or random differential checks against a slow oracle where feasible, metrics if it sits on a hot path, and clearer error types at A P I boundaries. The core algorithm stays the same.'))

    d.append(("interviewer",
        'Any open questions you would ask before calling the design final?'))

    d.append(("candidate",
        'Constraints on n, whether input is trusted, and which follow up variant product actually needs. Those change validation and A P I more than the core loop.'))

    d.append(("interviewer",
        'Technique clinic: grid as graph.'))

    d.append(("candidate",
        'Each cell is a vertex. Four way land to land adjacency defines edges. Water cells are absent vertices or vertices without edges. Islands are connected components among land vertices. Counting components is: iterate vertices, on unvisited land run D F S or B F S to mark the component, increment once per successful start. This is textbook graph traversal with an implicit edge function.'))

    d.append(("interviewer",
        'Clinic: choose D F S vs B F S vs union find for interviews.'))

    d.append(("candidate",
        'D F S recursive is shortest to type. B F S iterative is safe for large components. Union find shines when you already think in disjoint sets or online edge additions. I default to recursive D F S with a note I can convert to iterative stack if needed. All are O of cells for this static grid.'))

    d.append(("interviewer",
        'Clinic: mark order bugs.'))

    d.append(("candidate",
        'If you increment count for every land cell without flooding, you count cells not islands. If you flood but forget to mark the starting cell, you may infinite loop. If you mark after recursion instead of before, neighbors may reenter. Pattern: mark when you visit, then recurse neighbors.'))

    d.append(("interviewer",
        'Clinic: directions array style.'))

    d.append(("candidate",
        'I keep a list of four delta pairs one zero minus one zero zero one zero minus one. Loop deltas for clean code and fewer typos than four copy pasted blocks. Easy to extend to eight by adding diagonals if the problem changes.'))

    d.append(("interviewer",
        'Clinic: input types chars versus ints.'))

    d.append(("candidate",
        'Many problems use character one and zero. Compare to character one carefully not integer one. I check type in the first fixture. Mixing causes zero islands falsely.'))

    d.append(("interviewer",
        'Clinic: parallel flood thought experiment.'))

    d.append(("candidate",
        'You could start floods from multiple seeds with care not to double count using atomics on marks, but that is not interview scope. Sequential scan is expected. I avoid over engineering.'))

    d.append(("interviewer",
        'Clinic: related problems list quickly.'))

    d.append(("candidate",
        'Max area of island, perimeter of island, surrounded regions, walls and gates, pacific atlantic water flow, number of closed islands. All flood or multi source B F S variants. Learning islands unlocks the family.'))

    d.append(("interviewer",
        'Clinic: complexity constants.'))

    d.append(("candidate",
        'Each cell is written to water at most once and read a constant number of times from neighbors. So time linear in cells even with four neighbor checks. Space linear worst case for stack or queue.'))

    d.append(("interviewer",
        'Final pseudocode recitation.'))

    d.append(("candidate",
        'count zero. for each cell if land count plus one and sink component. sink marks water and recurses four neighbors with bounds checks. return count.'))

    d.append(("interviewer",
        'Minute summary.'))

    d.append(("candidate",
        'Number of islands is connected component count on a grid graph with four connectivity. Flood fill each unvisited land and increment once. Linear in cells. Mutation or visited both fine. Do not use eight connectivity unless asked. Tests all water all land multi island.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Count four connected land components in a grid. Flood fill each unvisited land and increment once.'))

    d.append(("interviewer",
        'Graph view.'))

    d.append(("candidate",
        'Cells vertices, four land edges, components are islands. D F S or B F S marks a component.'))

    d.append(("interviewer",
        'Mutation.'))

    d.append(("candidate",
        'Setting land to water marks visited. Allowed here. Otherwise use visited matrix.'))

    d.append(("interviewer",
        'Four not eight.'))

    d.append(("candidate",
        'Diagonals do not connect unless problem says eight. Wrong connectivity is a silent bug.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I receive a grid of land and water. I count islands where land connects up down left right. I scan every cell. When I find land I add one to the count and flood fill to mark the whole connected land mass so I will not count it again. Time linear in the number of cells. I can write recursive D F S or iterative B F S. I will test all water, all land, and a multi island fixture.'))

    d.append(("interviewer",
        'Recursion limit.'))

    d.append(("candidate",
        'Huge single island may blow Python recursion. Iterative stack flood is safer. Same marks.'))

    d.append(("interviewer",
        'Related family.'))

    d.append(("candidate",
        'Max area island, surrounded regions, walls gates. Same flood tools.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Flood fill components four ways, O of cells, tests multi island, code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Count four connected land components in a grid. Flood fill each unvisited land and increment once.'))

    d.append(("interviewer",
        'Graph view.'))

    d.append(("candidate",
        'Cells vertices, four land edges, components are islands. D F S or B F S marks a component.'))

    d.append(("interviewer",
        'Mutation.'))

    d.append(("candidate",
        'Setting land to water marks visited. Allowed here. Otherwise use visited matrix.'))

    d.append(("interviewer",
        'Four not eight.'))

    d.append(("candidate",
        'Diagonals do not connect unless problem says eight. Wrong connectivity is a silent bug.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I receive a grid of land and water. I count islands where land connects up down left right. I scan every cell. When I find land I add one to the count and flood fill to mark the whole connected land mass so I will not count it again. Time linear in the number of cells. I can write recursive D F S or iterative B F S. I will test all water, all land, and a multi island fixture.'))

    d.append(("interviewer",
        'Recursion limit.'))

    d.append(("candidate",
        'Huge single island may blow Python recursion. Iterative stack flood is safer. Same marks.'))

    d.append(("interviewer",
        'Related family.'))

    d.append(("candidate",
        'Max area island, surrounded regions, walls gates. Same flood tools.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Flood fill components four ways, O of cells, tests multi island, code AI off.'))

    d.append(("interviewer",
        'Shadow arc. Restate.'))

    d.append(("candidate",
        'Count four connected land components in a grid. Flood fill each unvisited land and increment once.'))

    d.append(("interviewer",
        'Graph view.'))

    d.append(("candidate",
        'Cells vertices, four land edges, components are islands. D F S or B F S marks a component.'))

    d.append(("interviewer",
        'Mutation.'))

    d.append(("candidate",
        'Setting land to water marks visited. Allowed here. Otherwise use visited matrix.'))

    d.append(("interviewer",
        'Four not eight.'))

    d.append(("candidate",
        'Diagonals do not connect unless problem says eight. Wrong connectivity is a silent bug.'))

    d.append(("interviewer",
        'Full restate memory.'))

    d.append(("candidate",
        'I receive a grid of land and water. I count islands where land connects up down left right. I scan every cell. When I find land I add one to the count and flood fill to mark the whole connected land mass so I will not count it again. Time linear in the number of cells. I can write recursive D F S or iterative B F S. I will test all water, all land, and a multi island fixture.'))

    d.append(("interviewer",
        'Recursion limit.'))

    d.append(("candidate",
        'Huge single island may blow Python recursion. Iterative stack flood is safer. Same marks.'))

    d.append(("interviewer",
        'Related family.'))

    d.append(("candidate",
        'Max area island, surrounded regions, walls gates. Same flood tools.'))

    d.append(("interviewer",
        'Closing pitch.'))

    d.append(("candidate",
        'Flood fill components four ways, O of cells, tests multi island, code AI off.'))

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
        'Speed recap. Flood each unvisited land. Four directions. O of r c. Code AI off.'))

    return d
