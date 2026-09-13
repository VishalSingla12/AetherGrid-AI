# Project Journal

**Name:** Sparsh Verma
**Roll No.:** 1024240011
**Course:** UCS503P – Software Engineering
**Project:** AetherGrid AI – An Autonomous Logistics and Emergency-Dispatch Simulation
**Presented to:** Dr. Zeelani
**Institute:** Thapar Institute of Engineering and Technology

---

### August 4, 2026

We locked in the project idea yesterday, and today I went back through it on my own to make sure I actually believed in it before we committed - a dispatch simulation combining routing, assignment and learning. What sold me was that it's not really about inventing a new algorithm, it's about integrating a handful of known ones correctly, which felt like a more honest scope for a semester project than something flashier.

### August 16, 2026

Wrote Part 2 of the proposal - aim, objectives, proposed solution. Forcing myself to write twelve concrete objectives was more useful than I expected; it made us actually commit to which algorithm goes where (Dijkstra for the ETA matrix, A* for live routing, Hungarian for assignment, GA for multi-drop logistics, Q-learning for repositioning) instead of leaving it fuzzy and having to sort it out later mid-code.

### August 18, 2026

Started the use case diagram. Spent a while deciding whether the "Scenario Lab" person injecting hazards and the "Dispatcher" watching the dashboard should be the same actor or two - went with two, since their goals with the system are genuinely different even if it's the same physical user in our demo.

### August 21, 2026

Revised the use case diagram after looking at it fresh - "close road" and "inject hazard" were cluttering the diagram as separate use cases when they're really the same interaction with different parameters, so I merged them under one "inject scenario event" use case with an extend relationship to the base dispatch flow.

### September 7, 2026

ER diagram day. The one thing I kept getting wrong on paper first was treating ASSIGNMENT as a plain relationship between VEHICLE and REQUEST - it needed to be its own associative entity because it carries its own attributes (cost, timestamp) that don't belong to either vehicle or request alone. Once I saw it that way, BATCH_WINDOW, ROUTE and INCIDENT all slotted in cleanly around it.

### September 11, 2026

Wrote Prototype Documentation Part 2 (the AI layer and the web layer), then switched over to code and built the cost-field update logic - congestion, weather multiplier, hazard penalty, the works. Had to double check the formula against what I'd written in the ER diagram notes to make sure the two didn't quietly drift apart.

### September 13, 2026

Poked at edge cases in the cost function before the demo - specifically what happens when congestion and a hazard both apply to the same edge at once. Confirmed they combine correctly (multiplicative congestion, additive hazard) rather than one silently overriding the other, which is exactly what the report claims but I hadn't actually verified in code until today.

### September 14, 2026

Mid-term demo. I mostly fielded questions about the cost model since that's what I'd been deep in all week. The one thing I want to be clearer about next time is that the deadline penalty in the assignment cost is a soft penalty, not a hard constraint - a couple of people in the room read it as a hard cutoff and I had to backtrack and explain.

