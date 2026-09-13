# Project Journal

**Name:** Vishal Singla
**Roll No.:** 1024240009
**Course:** UCS503P – Software Engineering
**Project:** AetherGrid AI – An Autonomous Logistics and Emergency-Dispatch Simulation
**Presented to:** Dr. Zeelani
**Institute:** Thapar Institute of Engineering and Technology

---

### August 3, 2026

Kickoff day. Sparsh and I threw around three or four project ideas before landing on a dispatch/routing simulation - it appealed to me mainly because it let us actually implement algorithms from class (Dijkstra, A*, an assignment problem) instead of just discussing them. I put together the skeleton of the introduction PPT tonight: problem, why it's hard, what we're building. Named it AetherGrid AI.

### August 12, 2026

Drafting Part 1 of the proposal today - abstract, introduction and problem statement. I went back to my DAA notes on the Hungarian algorithm to make sure I described the assignment problem correctly (m x n cost matrix, minimize total cost, O(n³)) instead of hand-waving it. Also wrote the four sub-problems section - combinatorial assignment, changing road conditions, myopic dispatch, disruption handling - which ended up structuring most of the later report.

### August 19, 2026

Started this journal today, a bit late but better late than never. Also started the DFD diagram in parallel. Drawing the data flow from request generator → cost field → assignment → dashboard made me realize the simulation engine really needs to run independent of the web layer, not bolted to it. That distinction wasn't obvious to me until I tried to draw the boxes and arrows.

### August 23, 2026

Second pass on the DFD. Sparsh pointed out I'd merged hazards and road closures into one "environment" bubble, which was wrong since the report later treats them completely differently (a closure removes the edge, a hazard just raises its cost). Fixed it and it made the whole diagram read more sensibly.

### September 8, 2026

Moved to the activity diagram for the full simulation loop. Getting the fork/join around "vehicle executes route" vs "RL repositions idle vehicles" right took three redraws - I kept accidentally letting the RL branch look like it could interrupt an active dispatch, which is exactly what the design is supposed to prevent. Also wrote Prototype Documentation Part 1 covering the core engine assumptions (seeded, tick-based, deterministic).

### September 9, 2026

First real coding session. Built the road graph module for the prototype - nodes, edges, a basic cost function. Nothing fancy yet, just enough to prove the seeded run produces identical output twice, which was the one invariant I actually cared about getting right early.

### September 12, 2026

Ran internal tests before the demo. Found a bug where a hazard edge was being dropped from the graph like a closure instead of just getting a cost penalty - an easy mixup given how similar they look in the data, but exactly the kind of thing the DFD had already warned me about back in August. Fixed and re-tested.

### September 14, 2026

Mid-term demo. Walked the panel through the road graph and the cost-field update live. Biggest piece of feedback: make sure the Hungarian assignment stage stays visibly separate from RL repositioning in the next milestone - which is already how we'd planned Phase 4, so that was reassuring rather than a redirect.
