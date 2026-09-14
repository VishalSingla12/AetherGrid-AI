html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherGrid Phase 1 — Kinematic Ledger</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Inter:wght@300;400;500;600&family=Roboto+Mono:wght@300;400&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --base: #FCFCF9;
            --ink: #0A1128;
            --flame: #FF4400;
            --azure: #0047FF;
            --font-display: 'Fraunces', serif;
            --font-body: 'Inter', sans-serif;
            --font-mono: 'Roboto Mono', monospace;
        }

        /* Lenis defaults */
        html.lenis, html.lenis body {
            height: auto;
        }
        .lenis.lenis-smooth {
            scroll-behavior: auto !important;
        }
        .lenis.lenis-smooth [data-lenis-prevent] {
            overscroll-behavior: contain;
        }
        .lenis.lenis-stopped {
            overflow: hidden;
        }
        .lenis.lenis-smooth iframe {
            pointer-events: none;
        }

        body {
            margin: 0;
            padding: 0;
            background-color: var(--base);
            color: var(--ink);
            font-family: var(--font-body);
            overflow-x: clip;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }

        h1, h2, h3, .display {
            font-family: var(--font-display);
            font-weight: 400;
            margin: 0;
            line-height: 0.9;
            letter-spacing: -0.03em;
        }
        
        .micro {
            font-family: var(--font-body);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.25em;
            opacity: 0.55;
        }

        .line-mask {
            overflow: hidden;
            display: inline-block;
            vertical-align: top;
        }
        
        .line-mask-inner {
            display: inline-block;
            transform: translateY(110%);
        }

        .scene-1 {
            position: relative;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 4vw;
            z-index: 10;
        }
        .overture-title {
            font-size: clamp(4rem, 10vw, 12rem);
            text-align: center;
            opacity: 0;
        }

        .scene-2 {
            position: relative;
            padding: 10vh 4vw;
            z-index: 20;
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 2vw;
        }
        .topo-stat {
            grid-column: span 4;
            clip-path: inset(0 0 100% 0);
        }
        .topo-stat:nth-child(2) { grid-column-start: 6; }
        .topo-stat:nth-child(3) { grid-column-start: 10; }
        .topo-number {
            font-size: clamp(3rem, 6vw, 7rem);
            font-family: var(--font-mono);
            color: var(--azure);
        }

        .scene-3 {
            position: relative;
            height: 100vh;
            z-index: 30;
            overflow: hidden;
        }
        .horizontal-container {
            display: flex;
            width: 400vw;
            height: 100%;
            align-items: center;
        }
        .horizontal-item {
            width: 100vw;
            padding: 0 5vw;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .horizontal-title {
            font-size: clamp(4rem, 12vw, 15rem);
            white-space: nowrap;
            will-change: transform;
        }
        .hairline {
            height: 1px;
            background: var(--ink);
            opacity: 0.12;
            width: 100%;
            margin: 4vh 0;
        }
        .algo-desc {
            max-width: 40vw;
            font-size: 1.25rem;
            line-height: 1.5;
        }

        .scene-4 {
            position: relative;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 40;
            background: var(--ink);
            color: var(--base);
        }
        .equation {
            font-family: var(--font-mono);
            font-size: clamp(2rem, 5vw, 6rem);
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5vw;
        }
        .eq-char {
            opacity: 0.1;
        }

        .scene-5 {
            position: relative;
            padding: 20vh 4vw;
            z-index: 50;
        }
        .proof-container {
            width: 100%;
            height: 80vh;
            overflow: hidden;
            transform: scale(1.2);
            transform-origin: center;
            position: relative;
        }
        .proof-image {
            width: 100%;
            height: 130%;
            object-fit: cover;
            position: absolute;
            top: -15%;
            left: 0;
        }
        .proof-caption {
            margin-top: 4vh;
            font-size: 1.1rem;
            line-height: 1.6;
            max-width: 30vw;
        }
        
        .accent-flame { color: var(--flame); }
    </style>
</head>
<body>
    <section class="scene-1">
        <h1 class="overture-title">
            <div class="line-mask"><span class="line-mask-inner">AETHERGRID</span></div><br>
            <div class="line-mask"><span class="line-mask-inner"><i class="accent-flame">KINEMATIC</i> LEDGER</span></div>
        </h1>
    </section>

    <section class="scene-2">
        <div class="topo-stat">
            <div class="micro">01 // OSM Nodes</div>
            <div class="topo-number" id="count-nodes">0</div>
            <p>Spatial vertices mapping intersections.</p>
        </div>
        <div class="topo-stat">
            <div class="micro">02 // Traversal Edges</div>
            <div class="topo-number" id="count-edges">0</div>
            <p>Directed paths governing routing logic.</p>
        </div>
        <div class="topo-stat">
            <div class="micro">03 // Phase</div>
            <div class="topo-number">01</div>
            <p>Architecture deployment.</p>
        </div>
    </section>

    <section class="scene-3">
        <div class="horizontal-container">
            <div class="horizontal-item">
                <div class="micro">01 // Engine</div>
                <h2 class="horizontal-title skew-elem">DIJKSTRA</h2>
                <div class="hairline"></div>
                <p class="algo-desc">Baseline priority queue exploration for uniform graphs. Guarantees optimal paths where edge weights remain strictly non-negative.</p>
            </div>
            <div class="horizontal-item">
                <div class="micro">02 // Engine</div>
                <h2 class="horizontal-title skew-elem">BELLMAN-FORD</h2>
                <div class="hairline"></div>
                <p class="algo-desc">Iterative relaxation spanning all edges $|V|-1$ times. Capable of handling negative weight anomalies in the grid.</p>
            </div>
            <div class="horizontal-item">
                <div class="micro">03 // Engine</div>
                <h2 class="horizontal-title skew-elem">FLOYD-WARSHALL</h2>
                <div class="hairline"></div>
                <p class="algo-desc">Dynamic programming matrix resolving all-pairs shortest paths. $O(|V|^3)$ complexity reserved for dense subgraph analysis.</p>
            </div>
            <div class="horizontal-item">
                <div class="micro">04 // Engine</div>
                <h2 class="horizontal-title skew-elem">A-STAR</h2>
                <div class="hairline"></div>
                <p class="algo-desc">Heuristic-driven spatial routing using Haversine estimation, converging faster on Euclidean targets while maintaining optimality.</p>
            </div>
        </div>
    </section>

    <section class="scene-4">
        <div class="equation">
            <span class="eq-char">C_{edge}</span>
            <span class="eq-char">=</span>
            <span class="eq-char">W_{base}</span>
            <span class="eq-char">+</span>
            <span class="eq-char">(\alpha</span>
            <span class="eq-char">\cdot</span>
            <span class="eq-char">T_{curr}</span>
            <span class="eq-char">+</span>
            <span class="eq-char">(1-\alpha)</span>
            <span class="eq-char">\cdot</span>
            <span class="eq-char">T_{prev})</span>
            <span class="eq-char">\times</span>
            <span class="eq-char">P_{surge}</span>
        </div>
    </section>

    <section class="scene-5">
        <div class="proof-container">
            <img class="proof-image" src="../assets/images/project_proposal_1_preview.png" alt="Proof of Work">
        </div>
        <div class="proof-caption">
            <div class="micro">Proof of Work</div>
            <p>Phase 1 architectural proposal and systemic requirements documentation. Authored by Vishal Singla & Sparsh Verma.</p>
        </div>
    </section>

    <script src="https://unpkg.com/@studio-freight/lenis@1.0.39/dist/lenis.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
    
    <script>
        gsap.registerPlugin(ScrollTrigger);

        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            direction: 'vertical',
            gestureDirection: 'vertical',
            smooth: true,
            mouseMultiplier: 1,
            smoothTouch: false,
            touchMultiplier: 2,
            infinite: false,
        });

        const tick = (t) => {
            lenis.raf(t * 1000);
        };
        gsap.ticker.add(tick);
        
        let mm = gsap.matchMedia();

        mm.add("(min-width: 768px)", () => {
            const tl1 = gsap.timeline();
            tl1.fromTo(".scene-1", 
                { opacity: 0 }, 
                { opacity: 1, duration: 2.0, ease: "power2.inOut" }
            );
            tl1.fromTo(".line-mask-inner",
                { y: "110%" },
                { y: "0%", duration: 1.4, ease: "power4.out", stagger: 0.08, clearProps: 'transform' },
                "-=1.5"
            );

            ScrollTrigger.create({
                trigger: ".scene-1",
                start: "top top",
                end: "+=100%",
                pin: true,
                pinSpacing: true
            });

            gsap.fromTo(".topo-stat",
                { clipPath: "inset(0 0 100% 0)" },
                { clipPath: "inset(0 0 0% 0)", duration: 1.2, ease: "power3.inOut", stagger: 0.2, clearProps: 'clipPath',
                  scrollTrigger: { trigger: ".scene-2", start: "top 60%" }
                }
            );
            
            gsap.fromTo({val: 0}, {val: 18912}, {
                val: 18912, duration: 3.5, ease: "expo.out",
                scrollTrigger: { trigger: ".scene-2", start: "top 60%" },
                onUpdate: function() { document.getElementById("count-nodes").innerText = Math.floor(this.targets()[0].val).toLocaleString(); }
            });
            gsap.fromTo({val: 0}, {val: 24164}, {
                val: 24164, duration: 3.5, ease: "expo.out",
                scrollTrigger: { trigger: ".scene-2", start: "top 60%" },
                onUpdate: function() { document.getElementById("count-edges").innerText = Math.floor(this.targets()[0].val).toLocaleString(); }
            });

            let horizontalTl = gsap.timeline({
                scrollTrigger: {
                    trigger: ".scene-3",
                    start: "top top",
                    end: "+=300%",
                    scrub: 1,
                    pin: true,
                    pinSpacing: true
                }
            });
            
            horizontalTl.fromTo(".horizontal-container",
                { x: "0%" },
                { x: "-300%", ease: "none" }
            );

            let proxy = { skew: 0 },
                skewSetter = gsap.quickSetter(".skew-elem", "skewX", "deg"),
                clamp = gsap.utils.clamp(-15, 15);

            ScrollTrigger.create({
                onUpdate: (self) => {
                    let skew = clamp(self.getVelocity() / -100);
                    if (Math.abs(skew) > Math.abs(proxy.skew)) {
                        proxy.skew = skew;
                        gsap.to(proxy, {skew: 0, duration: 0.8, ease: "power3", overwrite: true, onUpdate: () => skewSetter(proxy.skew)});
                    }
                }
            });

            gsap.fromTo(".eq-char",
                { opacity: 0.1 },
                { opacity: 1.0, ease: "none", stagger: 0.05,
                  scrollTrigger: {
                      trigger: ".scene-4",
                      start: "top top",
                      end: "+=200%",
                      scrub: 1,
                      pin: true,
                      pinSpacing: true
                  }
                }
            );

            gsap.fromTo(".proof-container",
                { scale: 1.2 },
                { scale: 1.0, duration: 1.8, ease: "expo.out", clearProps: 'transform',
                  scrollTrigger: { trigger: ".scene-5", start: "top 80%" }
                }
            );
            
            gsap.fromTo(".proof-image",
                { y: "-15%" },
                { y: "15%", ease: "none",
                  scrollTrigger: {
                      trigger: ".proof-container",
                      start: "top bottom",
                      end: "bottom top",
                      scrub: true
                  }
                }
            );
        });

        mm.add("(max-width: 767px)", () => {
            gsap.fromTo(".overture-title", {opacity: 0}, {opacity: 1, duration: 1});
            gsap.fromTo(".line-mask-inner", {y: "110%"}, {y: "0%", duration: 1, clearProps: 'transform'});
            document.getElementById("count-nodes").innerText = "18,912";
            document.getElementById("count-edges").innerText = "24,164";
            gsap.set(".horizontal-container", {width: "auto", flexWrap: "wrap", flexDirection: "column"});
            gsap.set(".horizontal-item", {width: "100%", padding: "5vh 5vw"});
            gsap.set(".eq-char", {opacity: 1});
        });

    </script>
</body>
</html>
"""

with open("docs/index.html", "w") as f:
    f.write(html_content)

