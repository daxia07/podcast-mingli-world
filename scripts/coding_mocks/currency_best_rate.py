"""Mock coding interview (~20 min): Currency best rate — problem segment only."""


def build():
    d = []

    d.append(("narrator",
        'Coding mock interview. Currency best rate conversion. Problem segment only. About twenty minutes. Two voices. No AI. Listen, pause, answer, then shadow.'))

    d.append(("interviewer",
        'Hi. One coding problem. No AI tools. Clarify before code. We will go deep on approach, pseudocode, corners, and complexity. Ready?'))

    d.append(("candidate",
        'Ready.'))

    d.append(("interviewer",
        'Build a currency converter. Input rates are triples: from currency, to currency, and a positive multiplier rate. Implement convert amount from currency to currency. Support direct rates and multi hop paths, for example US dollars to euros to pounds. If from equals to, return the amount unchanged after normal rounding. If no path exists, fail with a clear error. When multiple paths exist, choose the best product of rates, not merely any path or fewest hops. Round the final fiat amount to two decimal places. What do you need to know?'))

    d.append(("candidate",
        'Restating. Currencies are nodes in a directed graph. Edges multiply amounts by rates. I must maximize the product along a path, then scale and round. Questions. Are edges only as provided, or should I invent reverse edges as one over rate? Are rates guaranteed positive? Approximate graph size? Round each hop or only at the end? Are negative amounts valid? May I keep an adjacency list in memory?'))

    d.append(("interviewer",
        'Only listed directions, no automatic reverse. Positive rates. About fifty currencies and a few hundred edges. Round only at the end. Negative amounts are invalid. Adjacency list is fine.'))

    d.append(("candidate",
        'Naive approach: enumerate all simple paths and keep the maximum product. Correct on tiny graphs, exponential and hard to get right under cycles. Wrong popular approach: BFS for fewest hops. Fewest hops is the wrong objective because a longer path can have a better product. Example intuition: a bad direct rate can lose to two good hops. Correct approach: maximize product of positive edge weights. Standard transform: set weight to negative log of rate. Then minimize path weight using Dijkstra, valid because weights are positive when rates are positive. Product equals e to the minus distance to the target. Output equals round amount times product to two decimals. Same currency short circuits without running search.'))

    d.append(("interviewer",
        'Why not start with Bellman Ford?'))

    d.append(("candidate",
        'Bellman Ford supports negative weights and can detect negative cycles. After the log transform, a negative cycle corresponds to arbitrage, a loop whose rate product exceeds one. If the task is only best conversion and we assume we do not need arbitrage detection yet, Dijkstra is enough and typically faster. I will mention Bellman Ford if you ask for arbitrage as a follow up.'))

    d.append(("interviewer",
        'Hand walk dollars, euros, pounds with concrete rates.'))

    d.append(("candidate",
        'Edges: dollars to euros one point one, euros to pounds zero point nine, dollars to pounds direct zero point nine five. Two hop product is one point one times zero point nine equals zero point nine nine. Direct is zero point nine five. Best is two hop. One hundred dollars becomes ninety nine units before formatting as ninety nine point zero zero if exact. Identity: convert ten dollars to dollars yields ten point zero zero. If yen never appears, dollars to yen raises no path.'))

    d.append(("interviewer",
        'Walk Dijkstra state changes on that graph at a high level.'))

    d.append(("candidate",
        'Start dollars distance zero. Relax euros with weight negative log one point one. Relax pounds with weight negative log zero point nine five. When processing euros, candidate distance to pounds is negative log one point one plus negative log zero point nine, which is negative log of zero point nine nine. That improves on the direct edge, so pounds updates. Final product exp of minus distance equals zero point nine nine.'))

    d.append(("interviewer",
        'Full word pseudocode for add rate and convert.'))

    d.append(("candidate",
        'Class Currency Converter with graph map from currency to list of neighbor and rate pairs. Method add rate from currency, to currency, rate. If rate less or equal zero, raise invalid rate. Append the edge. Method convert amount, from currency, to currency. If amount less than zero, raise invalid amount. If from equals to, return round amount to two decimals. Run Dijkstra with negative log weights from from currency. If to is unreachable, raise no path error including both currency codes. Product equals exp of minus distance to target. Return round amount times product to two decimals. Dijkstra details: distance map default infinity, distance start zero, priority queue of distance and node. While queue not empty, pop best. Skip stale heap entries when popped distance is worse than recorded. For each edge, weight equals negative log rate, candidate equals distance plus weight, update neighbor if better. Load bearing lines: stale skip, positive rate guard, maximize product via minimize negative log.'))

    d.append(("interviewer",
        'Corner cases and tests.'))

    d.append(("candidate",
        'Identity same currency. Single direct edge. Multi hop strictly better than direct. No path error. Invalid zero or negative rate on add. Negative amount rejected. Disconnected currency. Self loop edge if present should not break Dijkstra. Tests use a hard coded micro graph, no network calls. I would assert multi hop wins with a tight expected value within floating tolerance, and assert rounding to two places on a chosen case.'))

    d.append(("interviewer",
        'Floating point concerns?'))

    d.append(("candidate",
        'Log and exp can introduce tiny numeric error. For interview scale and two decimal fiat, it is usually acceptable if we round only at the end. In production pricing I would discuss decimal types, integer pips, and audited rate tables. I state that limitation rather than hiding it.'))

    d.append(("interviewer",
        'If rates change online, what about caching?'))

    d.append(("candidate",
        'convert can always recompute on the current graph. If convert is extremely hot, cache best product per pair and invalidate on any add rate or remove rate. I would not build the cache until profiling says I need it.'))

    d.append(("interviewer",
        'Reachability only pre check?'))

    d.append(("candidate",
        'BFS or DFS on edge existence ignoring magnitudes except positivity. Same adjacency list, method has path, separate from convert.'))

    d.append(("interviewer",
        'Arbitrage follow up in one short design speech.'))

    d.append(("candidate",
        'Bellman Ford on negative log weights for V minus one relaxations, then one more pass. If any edge still relaxes on a node reachable from the source, a negative cycle exists, which means a multiplicative loop greater than one.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Dijkstra per convert is on the order of edges plus vertices log vertices with a binary heap. Space for adjacency lists and distance maps. Fifty currencies is small, so clarity beats micro optimization.'))

    d.append(("interviewer",
        'If you must return the path for debugging, how?'))

    d.append(("candidate",
        'Keep a parent map from currency to previous currency during Dijkstra. Walk from target back to source and reverse. convert can ignore path; a debug helper returns the currency list.'))

    d.append(("interviewer",
        'Five minutes left on the problem. Priorities?'))

    d.append(("candidate",
        'Implement convert, identity, multi hop wins, and no path tests. Do not build a full treasury platform.'))

    d.append(("interviewer",
        'Live you would type next. Offline, implement from blank without AI using the three currency example as tests.'))

    d.append(("candidate",
        'I will write the multi hop better than direct test first, then Dijkstra.'))

    d.append(("interviewer",
        'What is the difference between rate and weight in your Dijkstra?'))

    d.append(("candidate",
        'Rate multiplies money. Weight is negative log rate used only inside the shortest path math.'))

    d.append(("interviewer",
        'Why not maximize sum of rates?'))

    d.append(("candidate",
        'Sums of rates are meaningless for conversion. Products compose along hops.'))

    d.append(("interviewer",
        'What if two paths have equal product?'))

    d.append(("candidate",
        'Either is fine for value. I may break ties by fewer hops or lexicographic path if product asks, but I will not invent that unless required.'))

    d.append(("interviewer",
        'How do you name errors?'))

    d.append(("candidate",
        'Invalid rate, invalid amount, and no path, as explicit types or clear messages.'))

    d.append(("interviewer",
        'Would you use A star?'))

    d.append(("candidate",
        'No benefit here without a special heuristic. Dijkstra is enough.'))

    d.append(("interviewer",
        'What if the graph is disconnected into regions?'))

    d.append(("candidate",
        'convert fails when target not reachable from source even if both nodes exist somewhere.'))

    d.append(("interviewer",
        'Can self loops with rate less than one matter?'))

    d.append(("candidate",
        'They should not improve distance in the log graph when rates are positive and less than one; Dijkstra still fine.'))

    d.append(("interviewer",
        'How do you explain this to someone who only knows BFS?'))

    d.append(("candidate",
        'We still traverse a graph, but the score is product of edge rates, so we change edge weights with logs and run Dijkstra.'))

    d.append(("interviewer",
        'What regression test catches BFS mistaken for best rate?'))

    d.append(("candidate",
        'The dollars euros pounds fixture where multi hop beats direct.'))

    d.append(("interviewer",
        'What is the first line you write in the editor?'))

    d.append(("candidate",
        'Probably the class shell and add rate, then a failing test for identity.'))

    d.append(("interviewer",
        'Let us simulate the implementation phase. Narrate the code you would type in order, as if I am watching your editor. Full words, no silent typing.'))

    d.append(("candidate",
        'I create converter.py. I import math and heapq. Class Currency Converter with graph dict defaulting to empty lists via setdefault.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Method add rate from currency, to currency, rate. If rate less or equal zero raise Value Error invalid rate. Graph setdefault from currency list append tuple to currency and rate.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Method convert amount from currency to currency. If amount less than zero raise. If from equals to return round amount to two decimals. Then I call an internal method best product from currency to currency.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'best product runs Dijkstra. Dist dict starts empty, I will treat missing as infinity. I push heap with pair zero and from currency. Dist from currency equals zero. While heap: pop distance and node. If distance greater than dist get node infinity, continue stale. For each neighbor rate in graph get node empty: weight equals negative math log rate. Candidate equals distance plus weight. If candidate less than dist get neighbor infinity: dist neighbor equals candidate, push heap candidate neighbor.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'After the loop, if to currency not in dist raise Key Error or custom No Path Error. Product equals math exp of minus dist to currency. Return round amount times product two decimals.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write tests with the three currency graph. Assert convert one hundred dollars to pounds equals round one hundred times zero point nine nine two decimals. Assert identity. Assert no path to yen raises. Assert add rate zero raises.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'If tests show direct path winning incorrectly, I debug the relax order and stale skip. If floating noise appears, I compare with almost equal tolerance then still round output for API.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I stop without caching and without arbitrage unless asked. I restate complexity edges plus vertices log vertices.'))

    d.append(("interviewer",
        'Good. Pause. Any compile time or test failure you anticipate?'))

    d.append(("interviewer",
        'Narrate a second implementation pass as if refactoring for clarity after green tests. What do you rename or extract?'))

    d.append(("candidate",
        'I extract a private method relax edges for node to keep Dijkstra readable. I rename variables to from currency and to currency everywhere. I introduce a tiny Edge named tuple with to currency and rate. I keep convert thin: validate, identity, best product, multiply, round.'))

    d.append(("interviewer",
        'Speak the validation layer again slowly.'))

    d.append(("candidate",
        'add rate rejects non positive rates. convert rejects negative amounts. identity returns rounded amount. missing path raises a dedicated error. I never return zero amount as a silent failure for no path because zero can be a valid converted value in other systems and is ambiguous.'))

    d.append(("interviewer",
        'Compare your approach to Floyd Warshall for all pairs.'))

    d.append(("candidate",
        'Floyd Warshall can compute best products among all pairs after a similar log transform or by maximizing products carefully. With only fifty nodes it could work, but for single query convert Dijkstra is enough and easier to explain. If the API becomes many pair queries with rare rate updates, all pairs precompute is worth discussing.'))

    d.append(("interviewer",
        'What invariant should always hold after add rate?'))

    d.append(("candidate",
        'Every edge in the adjacency list has a strictly positive rate, and convert either returns a finite rounded number or raises a documented error, never hangs.'))

    d.append(("interviewer",
        'Minute summary as if closing the problem.'))

    d.append(("candidate",
        'Directed currency graph, best multiplicative path via negative log Dijkstra, identity short circuit, no automatic reverse edges, round once, explicit no path error. Tests pin multi hop better than direct. Complexity edges plus vertices log vertices. Arbitrage would be Bellman Ford later.'))

    d.append(("interviewer",
        'Production tomorrow differences?'))

    d.append(("candidate",
        'Decimal or integer minor units for money, audited rate feed, cache invalidation, and monitoring on conversion failures. Algorithm core can stay.'))

    d.append(("interviewer",
        'Why exp minus distance recovers the product?'))

    d.append(("candidate",
        'Because distance sums negative logs, so minus distance is sum of logs, exp of that is the product of rates.'))

    d.append(("interviewer",
        'What heap operations do you rely on?'))

    d.append(("candidate",
        'Push and pop min distance. Stale entries are skipped by comparing to the dist map.'))

    d.append(("interviewer",
        'How do you test rounding?'))

    d.append(("candidate",
        'Choose amounts and rates that produce a known two decimal result and assert equality on the rounded value.'))

    d.append(("interviewer",
        'What if from currency is unknown but to exists?'))

    d.append(("candidate",
        'Unknown from means no outgoing edges, distance stays only at start if start missing from graph. I ensure start is inserted with dist zero even if it has no edges, then to unreachable raises no path.'))

    d.append(("interviewer",
        'Should convert mutate the graph?'))

    d.append(("candidate",
        'No. convert is read only. Only add rate mutates.'))

    d.append(("interviewer",
        'How do you document assumptions in code?'))

    d.append(("candidate",
        'Module docstring: positive rates, directed edges, best product, round half to even language default.'))

    d.append(("interviewer",
        'What is your first failing test message you want to see?'))

    d.append(("candidate",
        'Something like expected ninety nine point zero zero got ninety five point zero zero if BFS style bug appears.'))

    d.append(("interviewer",
        'How do you handle a rate update from one point one to one point two?'))

    d.append(("candidate",
        'add rate could append a second edge or replace. I would prefer replace semantics for a pair and mention both options to the interviewer.'))

    d.append(("interviewer",
        'Is replace or multi edge better?'))

    d.append(("candidate",
        'For F X mid market usually one rate per pair direction. Replace is cleaner. Multi edges would require policy.'))

    d.append(("interviewer",
        'Final line before coding offline?'))

    d.append(("candidate",
        'I will implement adjacency list and the multi hop regression test first.'))

    d.append(("interviewer",
        'I want one more end to end spoken rehearsal. Pretend I just asked you to begin coding. Speak the next five minutes of what you would do without pausing for me much, but still structured.'))

    d.append(("candidate",
        'I create the file and imports math and heapq. I sketch Currency Converter with an empty graph dict. I implement add rate with validation so bad rates fail fast. I write three tests before Dijkstra: identity, no path, and the multi hop better than direct fixture with dollars euros pounds. I implement convert identity branch and the raise for negative amount so early tests can pass partially. I implement best product Dijkstra with dist map and heap, including the stale entry skip because that bug is classic. I wire convert to multiply amount by exp of minus distance and round to two decimals. I run tests. If multi hop fails I print dist values for pounds via both paths and fix the weight sign, a common mistake if someone uses log without the negative. I add a quick comment that reverse edges are not invented. I state complexity out loud and list follow ups arbitrage and caching without coding them. I stop when the three core tests and one rounding test are green.'))

    d.append(("interviewer",
        'What mistake with log signs would show up as multi hop never winning?'))

    d.append(("candidate",
        'If I minimize log rate without the negative, I am optimizing the wrong direction and products get scrambled. The safe phrase I remember is maximize product, minimize negative log rate.'))

    d.append(("interviewer",
        'Repeat the load bearing phrase once more for muscle memory.'))

    d.append(("candidate",
        'Maximize product of rates by minimizing the sum of negative log rates with Dijkstra, then exp of minus distance recovers the product.'))

    d.append(("narrator",
        'Speed recap. Best product not fewest hops. Negative log plus Dijkstra. No automatic reverse. Round once at end. Corners: identity, multi hop wins, no path, bad rate, negative amount. Arbitrage is Bellman Ford later. Shadow the candidate, then code with AI off.'))

    return d
