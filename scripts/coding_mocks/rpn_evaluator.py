"""Mock coding interview (~20 min): RPN / postfix expression evaluator."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. Single coding problem for this block. Python is fine. No AI tools. Clarify, design, hand walk, full word pseudocode, corners, complexity. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead.'))

    d.append(("interviewer",
        'Here is the problem. We need a reverse Polish notation evaluator. You receive a list of tokens that already form a postfix expression. Tokens are integer numbers as strings, or one of the four operators: plus, minus, times, and divide. Evaluate the expression to a single integer result. Why this matters here: expression evaluation shows up in rule engines, fee formulas, and policy checkers that agents must execute deterministically. Functional requirements. Correct operator semantics including subtraction and division order. Clear error handling for invalid expressions. No use of language eval on raw strings. Non functional: readable structure and tests. What questions do you have?'))

    d.append(("candidate",
        'Restating. Input is a list of string tokens in reverse Polish notation. I evaluate with a stack. Numbers push. Operators pop operands, apply, push result. Final stack must hold exactly one value. Clarifying questions. Are tokens already split, so multi digit numbers arrive as one token? Integer only, or floats? For division, truncate toward zero as in many interview problems, or floor toward negative infinity? What should happen on divide by zero? Empty input? A single number with no operators? Unary minus, or only binary operators? Invalid tokens? May I raise exceptions for errors, or return a result type?'))

    d.append(("interviewer",
        'Tokens are already split strings. Integers only. Division truncates toward zero. Divide by zero is an error. Empty input is an error. Single number is valid and returns that number. No unary operators. Invalid tokens error. Raising a clear exception is fine for this cut. Choose a small public function or method.'))

    d.append(("candidate",
        'Naive approach. Convert postfix to infix with parentheses, then evaluate with a second parser. That is two systems and easy to get precedence wrong. Better approach. One left to right pass with a stack, which is the natural model for reverse Polish notation. For each token, if it is an operator, require at least two stack values, pop the right operand first then the left operand, apply the operator, push the result. If it is a number, parse integer and push. After all tokens, require exactly one value on the stack and return it. Product framing: this is a deterministic calculator for fee or limit expressions agents must not execute via Python eval. I will still hand walk subtraction and division carefully because pop order is the classic bug.'))

    d.append(("interviewer",
        'Why is pop order load bearing for minus and divide but not for plus and times?'))

    d.append(("candidate",
        'Plus and times are commutative, so swapping operands still yields the same number. Minus and divide are not. If the stack top is the right operand, I must pop right first, then left, then compute left operator right. If I pop left first by mistake, four divide two becomes two divide four. Tests will catch it only if they include non commutative ops.'))

    d.append(("interviewer",
        'Hand walk tokens: two, one, plus, three, times. Speak the stack after every token.'))

    d.append(("candidate",
        'Start empty. Token two: push two. Stack two. Token one: push one. Stack two, one. Token plus: pop one as right, pop two as left, two plus one equals three, push three. Stack three. Token three: push three. Stack three, three. Token times: pop three right, pop three left, three times three equals nine, push nine. Stack nine. End. Exactly one value, return nine. This is the classic example corresponding to open paren two plus one close paren times three.'))

    d.append(("interviewer",
        'Hand walk four, two, divide. Then hand walk four, two, minus.'))

    d.append(("candidate",
        'Four, two, divide. Push four, push two. Divide pops two then four, four divided by two equals two. Truncation not needed here. Four, two, minus. Push four, push two. Minus pops two then four, four minus two equals two. If pop order were wrong, both would flip to incorrect results.'))

    d.append(("interviewer",
        'Hand walk a division that needs toward zero truncation: seven, two, divide, and also negative seven as a single token if we allow signed integers, then two, divide.'))

    d.append(("candidate",
        'Seven, two, divide. Push seven push two, seven divided by two is three point five, truncate toward zero yields three. For negative seven and two, negative seven divided by two is negative three point five, toward zero yields negative three, not negative four. In Python three, integer divide with slash slash floors toward negative infinity, so I must not use slash slash blindly. I will use float division then int truncation toward zero, or an explicit helper that matches the contract. I will confirm signed tokens are allowed as single tokens like the string negative seven.'))

    d.append(("interviewer",
        'Signed integer tokens are allowed. Empty string tokens are invalid. Describe the API you will implement.'))

    d.append(("candidate",
        'Function eval r p n that takes a list of strings and returns an int. Internally I may use a set or map of operator callables. I raise Value Error with a clear message for stack underflow, leftover values, divide by zero, and invalid tokens. No class is required unless you want a reusable calculator object; a pure function is enough for this cut.'))

    d.append(("interviewer",
        'Full word pseudocode. Speak every branch.'))

    d.append(("candidate",
        'Function eval r p n tokens. If tokens is empty, raise invalid expression. Stack is an empty list. Operators is the set plus minus times divide, written as the characters. For each token in tokens: if token is an operator: if length of stack is less than two, raise stack underflow. Right equals pop stack. Left equals pop stack. If token is divide and right equals zero, raise divide by zero. Result equals apply left operator right with toward zero division for divide. Push result. Else: try parse token as integer, including optional leading minus for negatives. On parse failure raise invalid token. Push the integer. After the loop, if length of stack is not one, raise invalid expression leftover or missing values. Return pop stack. Load bearing: pop right then left. Load bearing: division policy toward zero. Load bearing: final single value check.'))

    d.append(("interviewer",
        'How do you implement toward zero division portably in Python?'))

    d.append(("candidate",
        'I compute int of left divided by right using true division then cast with int, because int of a float truncates toward zero in Python. I must ensure right is not zero before dividing. I avoid slash slash. I add a unit test for negative seven over two equals negative three so nobody refactors to floor division later.'))

    d.append(("interviewer",
        'Walk corner cases and expected behavior.'))

    d.append(("candidate",
        'Single number list returns that number. Simple add and multiply. Non commutative minus and divide. Divide by zero raises. Too many operators causes underflow. Too many numbers left on stack at end raises. Empty list raises. Invalid token like foo raises. Token that looks like a float one point five is invalid under integer only unless we extend later. Very large integers: Python ints are unbounded, fine here; other languages may need big int policy. Operator as first token underflows. Only operators underflows.'))

    d.append(("interviewer",
        'Name the unit tests before claiming done.'))

    d.append(("candidate",
        'test classic nine from two one plus three times. test four two divide equals two. test four two minus equals two. test seven two divide equals three. test negative seven two divide equals negative three. test divide by zero raises. test empty raises. test single number. test underflow too many operators. test leftover two numbers no operator. test invalid token. Those pin semantics without a full fuzz harness.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Time O of n for n tokens. Space O of n for the stack in the worst case of all numbers then operators later, or typically O of n. No nested loops.'))

    d.append(("interviewer",
        'Why not shunting yard?'))

    d.append(("candidate",
        'Shunting yard converts infix to postfix. Our input is already postfix. Using shunting yard would be solving a different problem and inviting precedence bugs we do not need.'))

    d.append(("interviewer",
        'I extend: support a modulo operator with the same binary stack discipline. How?'))

    d.append(("candidate",
        'Add modulo to the operator set and application map. Decide remainder sign policy up front and test it. Structure unchanged: still pop right then left. No rewrite of the stack loop.'))

    d.append(("interviewer",
        'Security: tokens come from a user facing formula builder. Anything to refuse?'))

    d.append(("candidate",
        'I never pass tokens to Python eval or exec. I only parse integers and apply a fixed operator set. That keeps the evaluator a pure calculator, not a code execution sandbox. If formulas grow, I still keep a whitelist of operators.'))

    d.append(("interviewer",
        'How does this relate to a fee rule engine at a payments company?'))

    d.append(("candidate",
        'Rules often compile to an intermediate form. Postfix or a small A S T is safer than storing Python snippets. Evaluating R P N is a thin deterministic backend for those rules, which is why interviewers like it for fintech and agent policy contexts.'))

    d.append(("interviewer",
        'You have a few minutes left after the happy path. What do you do?'))

    d.append(("candidate",
        'I lock tests for nine, non commutative ops, toward zero division, and divide by zero. I restate O of n. I do not add variables or functions to the language. Readable correct evaluator beats a half built expression language.'))

    d.append(("interviewer",
        'Simulate implementation. Narrate what you type in order.'))

    d.append(("candidate",
        'I create eval rpn.py. I define a function eval r p n tokens. I create an empty stack list. I define a set of operator strings. I may define a helper apply left op right that branches on the four operators and implements toward zero divide.'))

    d.append(("interviewer",
        'Continue. What next and why?'))

    d.append(("candidate",
        'I loop tokens. On operator I check length at least two, pop right, pop left, guard divide by zero, push apply. On non operator I parse int and push, wrapping parse errors as invalid token. After loop I assert length one and return the value.'))

    d.append(("interviewer",
        'Continue.'))

    d.append(("candidate",
        'I write tests first or immediately after for the nine case, four two minus, seven two divide, negative seven two divide, and divide by zero. I run until green. If minus is wrong I fix pop order. If negative division is wrong I remove slash slash.'))

    d.append(("interviewer",
        'Continue.'))

    d.append(("candidate",
        'I add empty, underflow, leftover, invalid token tests. I speak complexity O of n time and space. I stop.'))

    d.append(("interviewer",
        'One minute summary as at the end of a real block.'))

    d.append(("candidate",
        'I evaluate reverse Polish notation with a single stack pass. Numbers push. Operators pop right then left, apply, push. Division truncates toward zero without Python floor division. Errors for empty input, underflow, leftover values, divide by zero, and invalid tokens. No language eval. Tests cover the classic nine case, non commutative ops, signed division, and failure modes. Time O of n, space O of n. Follow ups include modulo and maybe floats with an explicit policy. Structure stays a pure function over a token list.'))

    d.append(("interviewer",
        'Production tomorrow: what changes?'))

    d.append(("candidate",
        'I would bound expression length, add structured error codes for the formula U I, and fuzz random valid postfix trees against a trusted calculator. I would still refuse arbitrary code execution.'))

    d.append(("interviewer",
        'Open product questions?'))

    d.append(("candidate",
        'Whether integers are decimal only or can be hex, whether we need big decimal money math instead of ints, and whether variables like amount appear later. Variables would push us toward an environment map, not a rewrite of the stack idea.'))

    d.append(("interviewer",
        'Walk tokens four, thirteen, five, divide, plus. Stack after every step.'))

    d.append(("candidate",
        'Push four. Push thirteen. Push five. Divide: pop five right, pop thirteen left, thirteen divided by five is two point six, toward zero yields two, push two. Stack four, two. Plus: pop two right, pop four left, four plus two equals six. Return six. This shows multi digit tokens and intermediate truncation before a later add.'))

    d.append(("interviewer",
        'What if the problem allowed multi digit numbers but tokens were a raw string without splits?'))

    d.append(("candidate",
        'That becomes a lexer problem first: scan digits into numbers, single character operators, reject spaces or handle them. I would separate tokenize from eval r p n. Mixing both in one loop is a common interview mess. For the stated problem, tokens are already split, so I refuse to re-lex unless asked.'))

    d.append(("interviewer",
        'Compare exception types versus a Result object for errors.'))

    d.append(("candidate",
        'Exceptions are fine in a coding block and keep the happy path clean. A Result with ok and error code is better at A P I boundaries for fee engines so callers do not catch broadly. I can sketch a small enum of error kinds: underflow, overflow values leftover, div zero, bad token. Implementation still one stack pass.'))

    d.append(("interviewer",
        'Property style tests you would add if time permits.'))

    d.append(("candidate",
        'Generate random expression trees, emit postfix, evaluate with my function, and compare to evaluating the tree with known semantics. That catches pop order bugs better than a handful of examples. I still keep the classic nine and signed division as regression pins.'))

    d.append(("interviewer",
        'If amount fields in payments used this evaluator, what integer policy would you demand?'))

    d.append(("candidate",
        'Money usually wants decimal or integer minor units, not silent float. For interview ints are fine. In production I would evaluate in integer minor units and define division policy with product and legal, not invent bankers rounding live. I say that out loud so the interviewer hears financial awareness without derailing the stack.'))

    d.append(("interviewer",
        'Show the apply helper in full words.'))

    d.append(("candidate",
        'Function apply left op right. If op is plus return left plus right. If minus return left minus right. If times return left times right. If divide: if right is zero raise. Quotient equals left divided by right using true division, return int of quotient for toward zero. Else raise unknown operator. Keeping apply separate makes the main loop readable on a shared screen.'))

    d.append(("interviewer",
        'Narrate a failing test you fix under time pressure.'))

    d.append(("candidate",
        'Test expects negative three for negative seven over two but gets negative four. I search for slash slash, replace with toward zero helper, re-run. Second fail: leftover two numbers returns a value instead of error. I add the final length equals one check. Green. Stop feature creeping.'))

    d.append(("interviewer",
        'How would you explain R P N to a product manager in two sentences?'))

    d.append(("candidate",
        'It is a way to write formulas that a machine evaluates with a stack and no parentheses ambiguity. We use it when agents or rule engines must compute fees without executing arbitrary code.'))

    d.append(("interviewer",
        'Last trap: token plus as the word plus versus the symbol. Your input uses symbols, correct?'))

    d.append(("candidate",
        'Yes, the four operator characters. If the problem used words I would map words to callables. I confirm the alphabet of tokens before coding.'))

    d.append(("narrator",
        'Speed recap. Problem: evaluate postfix tokens to one integer. Clarify: split tokens, ints, toward zero divide, errors on empty underflow leftover zero divide. Naive: convert to infix. Better: stack, pop right then left. Hand walk nine and non commutative ops. No Python eval. Tests pin division policy. O of n time and space. Replay, then code thirty minutes AI off.'))

    return d
