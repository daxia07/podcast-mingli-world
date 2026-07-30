"""Mock coding interview (~20 min): FX arbitrage via Bellman-Ford on −log rates."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. About twenty minutes. Two voices. No AI. Ear only first play. Pause second. Shadow third.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. One coding problem. Python fine. No AI. This pairs with best rate conversion but focuses on arbitrage detection. Clarify, design, hand walk, pseudocode, corners, complexity. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead.'))

    d.append(("interviewer",
        'Here is the problem. You are given a list of directed FX rates as triples: from currency, to currency, rate, meaning one unit of from converts to rate units of to. I want to know whether an arbitrage cycle exists: a cycle of currencies where multiplying the rates along the cycle yields a product strictly greater than one, so you can increase money by walking the cycle. Return true if such a cycle exists, false otherwise. You may also sketch how to recover one cycle if time allows. What questions do you have?'))

    d.append(("candidate",
        'Restating. Graph nodes are currencies. Directed edge from A to B with weight related to rate A to B. Arbitrage means a cycle whose rate product is greater than one. Clarifying. Are rates always positive? Can both A to B and B to A appear? Self loops? Disconnected currencies? Empty edge list? Should I assume I can start with any currency, meaning I need to detect a positive product cycle anywhere, not only reachable from one source? Do you want only a boolean, or also the cycle list of currencies? Float precision: use a small epsilon?'))

    d.append(("interviewer",
        'Rates positive. Bidirectional pairs may appear as two edges. No need to invent missing reverse edges. Disconnected components possible. Boolean is enough for the main API; cycle recovery is a bonus. Use careful floats with a tiny epsilon if needed. Explain the log transform before code.'))

    d.append(("candidate",
        'Naive approach. Enumerate cycles and multiply rates. Exponential and messy. Better. Transform the problem to a standard graph algorithm. Take the natural log. Product of rates greater than one if and only if sum of log rates is greater than zero. For shortest path algorithms we usually detect negative cycles. So use edge weight equal to negative log of rate. Then a cycle with product of rates greater than one becomes a cycle with sum of weights negative. Bellman Ford detects negative cycles. Why not Dijkstra? Dijkstra cannot handle negative weights and does not detect negative cycles. Why not only BFS on unweighted structure? Rates matter. Product framing: this is the arbitrage check you add after best path conversion with Dijkstra on negative log for maximum product path. I will still implement Bellman Ford carefully including a virtual source or multi source init so disconnected parts are covered.'))

    d.append(("interviewer",
        'Walk the math on a tiny cycle. U S D to E U R rate two, E U R to U S D rate zero point six. Is that arbitrage?'))

    d.append(("candidate",
        'Product two times zero point six equals one point two greater than one, yes arbitrage. Logs: log two plus log zero point six greater than zero. Weights negative log rate: negative log two plus negative log zero point six equals negative log of one point two which is negative. Negative cycle, Bellman Ford should report true. If reverse rate were zero point five, product one, not arbitrage. If reverse zero point four, product zero point eight less than one, no arbitrage, weights sum positive on that cycle.'))

    d.append(("interviewer",
        'Describe algorithm steps in full words including why a dummy source helps.'))

    d.append(("candidate",
        'Build list of edges as from, to, weight equals negative math log rate. Collect all currency nodes. Distance map init to zero for every node, or equivalently add a dummy source with zero weight edges to every node and init only dummy to zero others to infinity then relax. Initializing all distances to zero is a common interview form: it is like every node is reachable with zero cost start, so any negative cycle anywhere can propagate. Then relax all edges n times where n is number of nodes: for each edge, if distance to is greater than distance from plus weight, update distance to. After n minus one rounds, do one more pass: if any edge can still relax, a negative cycle exists, return true. Else false. Load bearing: weight is negative log rate, not log rate alone, if we want greater product to map to negative cycle. Load bearing: positive rates only so log is defined.'))

    d.append(("interviewer",
        'Full word pseudocode.'))

    d.append(("candidate",
        'Function has arbitrage rates list. If rates empty return false. Import math. Nodes set. Edges list. For each from to rate in rates: if rate less or equal zero raise. Add from and to to nodes. Append edge from to weight negative math log rate. N equals number of nodes. Dist equals map every node to zero. For iteration in range n minus one: for each edge if dist to greater than dist from plus weight plus tiny negative guard optional: dist to equals dist from plus weight. For each edge in a final pass: if dist to greater than dist from plus weight: return true. Return false. Optionally track predecessor on updates to reconstruct a cycle when final pass finds a relaxable edge by walking pred n times to enter the cycle then loop until repeat.'))

    d.append(("interviewer",
        'Hand walk two node arbitrage and two node non arbitrage quickly.'))

    d.append(("candidate",
        'Arbitrage two and zero point six as above, final pass still relaxes, true. Non arbitrage two and zero point four: product zero point eight, weights sum positive, after settling no further relax, false. Three hop cycle with product greater than one also eventually creates a negative cycle in the transformed graph even if no two hop arb exists.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Bellman Ford is O of n times m for n currencies and m rate edges. Space O of n plus m. For interview sized FX graphs this is fine. If m is huge, still the standard tool for negative cycle detection.'))

    d.append(("interviewer",
        'Corners and tests.'))

    d.append(("candidate",
        'Empty rates false. Single edge no cycle false. Two edge product greater than one true. Two edge product less than one false. Three currency arb true. Disconnected other currencies with no cycle still false if no neg cycle. Zero or negative rate raises. Self loop rate greater than one is arb true. Self loop rate less than one false. Precision near product one: document epsilon or exact fractions if rates were rational; floats with a small tolerance on the final comparison may be needed.'))

    d.append(("interviewer",
        'How does this relate to best conversion path Dijkstra?'))

    d.append(("candidate",
        'Best rate path maximizes product of rates, equivalent to minimize sum of negative log rates, which is Dijkstra when no negative cycles, meaning no arbitrage. If arbitrage exists, best product is unbounded by looping. So production converters often check arbitrage or forbid cycles. Same weight transform, different algorithm and question.'))

    d.append(("interviewer",
        'Why not Floyd Warshall?'))

    d.append(("candidate",
        'Floyd can detect negative cycles via negative diagonal after run, O of n cubed. Fine for tiny currency sets. Bellman Ford is the usual teaching answer for negative cycle detection with sparse edges O of n m. I can mention both; I implement Bellman Ford.'))

    d.append(("interviewer",
        'Simulate coding narration.'))

    d.append(("candidate",
        'I write has arbitrage. Build edges with weight negative log. Dist all zero. Relax n minus one times. Final pass return true on improvement. Tests for product one point two true and zero point eight false and empty false.'))

    d.append(("interviewer",
        'Continue.'))

    d.append(("candidate",
        'If true negatives fail, I check the sign of the log weight. A common bug is using log rate without the negative, which flips the meaning. I fix and re-run.'))

    d.append(("interviewer",
        'Bonus cycle recovery in words only.'))

    d.append(("candidate",
        'Keep predecessor on relax. From a vertex that still relaxes on the nth pass, walk predecessor n steps to guarantee you are on a cycle, then walk until you repeat to collect the cycle. Map back to currencies. I only code this if time remains after boolean is green.'))

    d.append(("interviewer",
        'One minute summary.'))

    d.append(("candidate",
        'Arbitrage means a cycle with rate product greater than one. Transform weight to negative log rate so that becomes a negative cycle. Bellman Ford with distances initialized to zero relaxes n minus one rounds then checks for another relax. True if negative cycle exists. O of n m time. Empty and non cyclic graphs false. Positive rates only. Same transform as best path Dijkstra, but Dijkstra cannot detect these cycles. Tests pin two node arb and non arb. Follow up: reconstruct cycle, epsilon policy.'))

    d.append(("interviewer",
        'Production note?'))

    d.append(("candidate",
        'Real books use bid ask spreads so naive mid rates can show phantom arb. Interview uses clean mid rates. I would mention spreads if the conversation goes production.'))

    d.append(("interviewer",
        'Hand walk three currency arbitrage. U S D to E U R one point zero, E U R to G B P one point zero, G B P to U S D one point two.'))

    d.append(("candidate",
        'Product one times one times one point two equals one point two greater than one. Negative log weights sum to negative log one point two less than zero. Bellman Ford should return true. No two edge cycle may be arb if reverses are poor; the three cycle still is. Good test that we are not only checking mutual pairs.'))

    d.append(("interviewer",
        'What if the graph has a negative cycle not reachable from some nodes? Does all zero init still find it?'))

    d.append(("candidate",
        'Initializing all distances to zero is equivalent to connecting a virtual source to all nodes with zero weight edges. Any negative cycle in any component can be detected. If I only ran from one source with inf init, I could miss a cycle elsewhere. For global arbitrage boolean, all zero or dummy source is correct.'))

    d.append(("interviewer",
        'Recover a cycle in more detail.'))

    d.append(("candidate",
        'On the nth pass, when edge u v can relax, set start to v. Then for i in range n: start equals pred start, to walk into a cycle. Then walk from start following pred until you return to start, collecting nodes. Reverse if needed for the edge direction story. Careful with pred init none. Only bonus after boolean works.'))

    d.append(("interviewer",
        'Floating point log instability near one.'))

    d.append(("candidate",
        'Product extremely close to one may misclassify. Production might use scaled integer logs or rational products with care. Interview: use math log on positive floats and a tiny epsilon on the relax comparison if needed. I document sensitivity.'))

    d.append(("interviewer",
        'Can S P F A or queue based Bellman Ford replace the n rounds?'))

    d.append(("candidate",
        'Yes for speed on some graphs, with care about negative cycle detection termination. Classic n rounds is clearer in interviews and hard to get wrong on termination conditions. I stick to classic unless performance is the point.'))

    d.append(("interviewer",
        'Arbitrage with fees on each edge.'))

    d.append(("candidate",
        'Effective rate becomes rate times one minus fee fraction. Use that in the log weight. Structure unchanged. If fees are fixed absolute amounts, product form breaks and the model changes more deeply.'))

    d.append(("interviewer",
        'Why shortest path language when we care about money increase?'))

    d.append(("candidate",
        'Because the log transform converts multiplicative gain into additive path weight. Negative cycle in the additive graph is multiplicative gain in the money graph. It is a dictionary between two equivalent problems.'))

    d.append(("interviewer",
        'Implementer bug: using log base ten versus natural log.'))

    d.append(("candidate",
        'Any base works because it only scales weights by a positive constant and preserves sign of sums. Negative cycle detection is invariant to positive scaling of all weights. Base choice does not matter; the negative sign in front of log does.'))

    d.append(("interviewer",
        'Connect back to the best rate converter mock.'))

    d.append(("candidate",
        'Best path uses Dijkstra on negative log when no arb. If has arbitrage returns true, best product is unbounded if cycles allowed. A complete FX toolkit: add rate, best convert, has arbitrage. I mention the suite without coding all three unless asked.'))

    d.append(("interviewer",
        'Simulate coding. Imports and function signature.'))

    d.append(("candidate",
        'Import math. Function has arbitrage rates where rates is a list of triples from currency to currency rate. Return bool. I validate each rate greater than zero.'))

    d.append(("interviewer",
        'Build graph structures next.'))

    d.append(("candidate",
        'Nodes set. Edges list of tuples u v w. For each triple append edge with w equals negative math log rate and add both currencies to nodes. If not nodes return false. n equals len nodes. dist equals open brace node colon zero for node in nodes close brace.'))

    d.append(("interviewer",
        'Relaxation loops.'))

    d.append(("candidate",
        'For underscore in range n minus one: for u v w in edges: if dist v greater than dist u plus w: dist v equals dist u plus w. Then for u v w in edges: if dist v greater than dist u plus w: return true. Return false.'))

    d.append(("interviewer",
        'Tests.'))

    d.append(("candidate",
        'Arb two and zero point six true. Non arb two and zero point four false. Three hop one one one point two true. Empty false. Self loop one point one true. Self loop zero point nine false.'))

    d.append(("interviewer",
        'Bug: everything returns true. Diagnosis path.'))

    d.append(("candidate",
        'I forgot the negative on log, or I used log of one over rate incorrectly doubled. I print weights on a known non arb cycle and check sum positive. Fix sign. Re-run.'))

    d.append(("interviewer",
        'Bug: three hop arb returns false.'))

    d.append(("candidate",
        'Too few relax rounds, or nodes count wrong because I used m edges as n. n must be number of currencies. Fix and re-run three hop.'))

    d.append(("interviewer",
        'How you draw this on a whiteboard in thirty seconds.'))

    d.append(("candidate",
        'Nodes currencies, arrows rates, write w equals minus log r on edges, say negative cycle means arb, Bellman Ford n rounds plus check.'))

    d.append(("interviewer",
        'Risk of treating phantom arb from mid prices again.'))

    d.append(("candidate",
        'I restate bid ask caveat in one sentence if interviewer is senior markets. Still code mids as given.'))

    d.append(("interviewer",
        'Priority with five minutes left.'))

    d.append(("candidate",
        'Boolean green on two node and three hop tests. Sign of weight correct. Spoken O of n m. Cycle recovery only if already green and time left.'))

    d.append(("interviewer",
        'Technique clinic: derive the log transform again from first principles.'))

    d.append(("candidate",
        'We care about product of rates along a cycle. Products become sums under logarithm because log of a product is sum of logs. Product greater than one if and only if sum of logs greater than zero. Shortest path algorithms detect negative cycles more often than positive cycles in textbooks, so we multiply the sum by negative one: use weights equal to negative log rate. Then product greater than one becomes sum of weights less than zero, a negative cycle. Any base of log works because it multiplies all weights by the same positive constant and preserves the sign of sums.'))

    d.append(("interviewer",
        'Clinic: show the algebra on rates two and zero point six.'))

    d.append(("candidate",
        'Product one point two. log product positive. Sum of log rates positive. Sum of negative log rates negative. Negative cycle true. For rates two and zero point four product zero point eight, sum of negative logs positive on that cycle, not a negative cycle from that loop alone.'))

    d.append(("interviewer",
        'Clinic: dummy source versus all zero distances.'))

    d.append(("candidate",
        'Adding a dummy source with zero weight edges to every node and running Bellman Ford from the dummy makes every node reachable. Initializing all distances to zero is equivalent for negative cycle detection because it is as if every node starts with a free zero cost token. Either approach detects a negative cycle anywhere. Single source with infinity init can miss cycles in other components.'))

    d.append(("interviewer",
        'Clinic: relation to best conversion Dijkstra in one clear contrast.'))

    d.append(("candidate",
        'Best conversion seeks a path with maximum product of rates between two currencies, equivalent to minimum sum of negative log weights, which Dijkstra can solve when no negative cycles exist. Arbitrage detection asks whether any negative cycle exists anywhere. If yes, unlimited money by looping, and best product is unbounded if cycles allowed in the path. Same weight transform, different questions and algorithms.'))

    d.append(("interviewer",
        'Clinic: implementer checklist before submit.'))

    d.append(("candidate",
        'Positive rates only. Weight negative log. n is number of currencies not edges. Relax n minus one times then check. Tests two node arb, two node non arb, three hop arb, empty, self loop. Spoken complexity O of n m. Optional cycle recovery only after boolean green.'))

    d.append(("interviewer",
        'Minute summary for muscle memory.'))

    d.append(("candidate",
        'FX arbitrage is a negative cycle after weighting edges by negative log of rate. Bellman Ford detects it. Product greater than one maps to negative weight sum. O of n m. Dijkstra cannot do this job. Phantom arb from mid prices is a production caveat. Code the boolean first.'))

    d.append(("narrator",
        'Speed recap. Arbitrage cycle product greater than one. Weight negative log rate. Bellman Ford negative cycle. Init dist zero. O of n m. Not Dijkstra. Sign of log is the classic bug. Code AI off after listen.'))

    return d
