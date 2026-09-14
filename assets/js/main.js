/**
 * AETHERGRID AI — MAIN KINEMATICS & SCROLL ORCHESTRATION
 * Built according to awwwards-orchestrator directive & 12 Iron Invariants
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check for reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Register GSAP Plugins
  gsap.registerPlugin(ScrollTrigger);

  // ------------------------------------------------------------------------
  // 1. Lenis Smooth Scroll Setup
  // ------------------------------------------------------------------------
  let lenis = null;
  if (!prefersReducedMotion && typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothTouch: false,
    });

    // Invariant #3: Named callback for ticker cleanup
    function lenisRaf(time) {
      lenis.raf(time * 1000);
    }
    gsap.ticker.add(lenisRaf);
    gsap.ticker.lagSmoothing(0);

    // Sync Lenis scroll with ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);
  }

  // ------------------------------------------------------------------------
  // 2. Signature Move: Dynamic Transit-Line SVG Generator
  // ------------------------------------------------------------------------
  const svgWrap = document.querySelector('.transit-svg');
  let transitPath = null;
  let stationNodes = [];

  function setupTransitLine() {
    if (!svgWrap || window.innerWidth < 768) return;

    // Remove existing
    svgWrap.querySelectorAll('.transit-track-line, .transit-active-line, .station-node').forEach(el => el.remove());
    stationNodes = [];

    const scenes = [
      document.querySelector('#scene-1'),
      document.querySelector('#scene-2'),
      document.querySelector('#scene-3'),
      document.querySelector('#scene-4'),
      document.querySelector('#scene-5')
    ].filter(Boolean);

    if (scenes.length < 2) return;

    const coords = [];
    const w = window.innerWidth;
    const h = window.innerHeight;

    // Define 5 key anchor points across the screen for the continuous transit threading
    const anchors = [
      { x: w * 0.82, y: h * 0.45 },
      { x: w * 0.48, y: h * 0.52 },
      { x: w * 0.22, y: h * 0.48 },
      { x: w * 0.75, y: h * 0.55 },
      { x: w * 0.50, y: h * 0.65 }
    ];

    let d = `M ${anchors[0].x} ${anchors[0].y}`;
    for (let i = 1; i < anchors.length; i++) {
      const prev = anchors[i - 1];
      const curr = anchors[i];
      const cp1x = prev.x;
      const cp1y = prev.y + (curr.y - prev.y) * 0.5;
      const cp2x = curr.x;
      const cp2y = prev.y + (curr.y - prev.y) * 0.5;
      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${curr.x} ${curr.y}`;
    }

    // Create or update background dashed track
    let track = svgWrap.querySelector('.transit-track-line');
    if (!track) {
      track = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      track.setAttribute('class', 'transit-track-line');
      svgWrap.appendChild(track);
    }
    track.setAttribute('d', d);

    // Create or update active animated stroke line
    if (!transitPath) {
      transitPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      transitPath.setAttribute('class', 'transit-active-line');
      transitPath.setAttribute('stroke', 'url(#tg1)');
      svgWrap.appendChild(transitPath);
    }
    transitPath.setAttribute('d', d);

    const length = transitPath.getTotalLength();
    transitPath.style.strokeDasharray = `${length}`;
    if (!transitPath.style.strokeDashoffset) {
      transitPath.style.strokeDashoffset = `${length}`;
    }

    // Update or create station nodes
    svgWrap.querySelectorAll('.station-node').forEach(el => el.remove());
    stationNodes = [];
    anchors.forEach((pt, idx) => {
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('class', `station-node station-node--${idx + 1}`);
      circle.setAttribute('cx', pt.x);
      circle.setAttribute('cy', pt.y);
      circle.setAttribute('r', '6');
      svgWrap.appendChild(circle);
      stationNodes.push(circle);
    });

    if (stationNodes[0]) stationNodes[0].classList.add('active');
  }

  setupTransitLine();
  window.addEventListener('resize', () => {
    setupTransitLine();
  });

  // ------------------------------------------------------------------------
  // 3. Responsive GSAP MatchMedia Orchestration (Invariant #11)
  // ------------------------------------------------------------------------
  const mm = gsap.matchMedia();

  // Helper for numeric counter animation
  function animateCounter(el, target, isDecimal, duration = 1.2) {
    const obj = { val: 0 };
    gsap.to(obj, {
      val: target,
      duration: duration,
      ease: 'power2.out',
      onUpdate: () => {
        if (isDecimal) {
          el.textContent = obj.val.toFixed(1);
        } else {
          el.textContent = Math.round(obj.val).toLocaleString();
        }
      }
    });
  }

  // DESKTOP PIPELINE ( >= 768px )
  mm.add('(min-width: 768px)', () => {
    if (prefersReducedMotion) {
      // Set all elements to final visible state immediately
      gsap.set('.lm__i', { y: '0%' });
      gsap.set('.hero-sub, .info-panel, .stat-card, .algo-col, .inv-card, .link-card', { opacity: 1, x: 0, y: 0, scale: 1 });
      document.querySelectorAll('.stat-card__num').forEach(el => {
        el.textContent = parseInt(el.dataset.target, 10).toLocaleString();
      });
      document.querySelectorAll('.metric__num').forEach(el => {
        el.textContent = el.dataset.decimal ? parseFloat(el.dataset.target).toFixed(1) : el.dataset.target;
      });
      document.querySelectorAll('.wf-bar__fill').forEach(el => {
        el.style.height = el.dataset.cov + '%';
      });
      return;
    }

    // Global Transit-Line Scroll Scrub
    if (transitPath) {
      const totalLen = transitPath.getTotalLength();
      ScrollTrigger.create({
        trigger: document.body,
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.5,
        onUpdate: (self) => {
          const progress = self.progress;
          transitPath.style.strokeDashoffset = `${totalLen * (1 - progress)}`;
          
          // Switch gradient color along the path
          if (progress < 0.35) {
            transitPath.setAttribute('stroke', 'url(#tg1)');
          } else if (progress < 0.7) {
            transitPath.setAttribute('stroke', 'url(#tg2)');
          } else {
            transitPath.setAttribute('stroke', 'url(#tg3)');
          }

          // Activate station dots sequentially
          const stationIdx = Math.floor(progress * stationNodes.length);
          stationNodes.forEach((node, i) => {
            if (i <= stationIdx) {
              node.classList.add('active');
            } else {
              node.classList.remove('active');
            }
          });
        }
      });
    }

    // ----------------------------------------------------------------------
    // SCENE 1 — THRESHOLD
    // ----------------------------------------------------------------------
    const s1 = document.querySelector('#scene-1');
    const s1Title = s1.querySelectorAll('.hero-title .lm__i');
    const s1Sub = s1.querySelector('.hero-sub');
    const s1Grid = s1.querySelector('.scene__bg-grid');
    const s1Crease = s1.querySelector('.scene__crease');

    // Entrance timeline
    const s1Tl = gsap.timeline({ delay: 0.1 });
    s1Tl.fromTo(s1Title, 
      { y: '110%' }, 
      { y: '0%', duration: 1.1, ease: 'expo.out', stagger: 0.09 }
    )
    .fromTo(s1Sub, 
      { opacity: 0, y: 30 }, 
      { opacity: 1, y: 0, duration: 0.8, ease: 'power4.out' }, 
      '-=0.7'
    )
    .fromTo(s1Grid, 
      { scale: 1.15, opacity: 0.06 }, 
      { scale: 1.0, opacity: 0.1, duration: 1.4, ease: 'expo.out' }, 
      '-=1.0'
    );

    // Pinned scrub timeline (120vh)
    gsap.timeline({
      scrollTrigger: {
        trigger: s1,
        start: 'top top',
        end: '+=120%',
        pin: true,
        pinSpacing: true,
        anticipatePin: 1,
        scrub: 1.2
      }
    })
    .to('.hero-text', { y: '-8vh', ease: 'none' }, 0)
    .to(s1Grid, { y: '-12vh', ease: 'none' }, 0)
    .to(s1Crease, { opacity: 0, scaleX: 0, ease: 'none' }, 0);


    // ----------------------------------------------------------------------
    // SCENE 2 — EXPOSITION (Graph Engine)
    // ----------------------------------------------------------------------
    const s2 = document.querySelector('#scene-2');
    const s2Cards = s2.querySelectorAll('.stat-card');
    const s2Info = s2.querySelector('.info-panel');
    let s2Counted = false;

    // Rest states
    gsap.set(s2Cards, {
      opacity: 0,
      x: '-8%',
      rotateZ: (i) => (i % 2 === 0 ? -1.5 : 1.5)
    });
    gsap.set(s2Info, { opacity: 0, scale: 0.95 });

    const s2Tl = gsap.timeline({
      scrollTrigger: {
        trigger: s2,
        start: 'top top',
        end: '+=200%',
        pin: true,
        pinSpacing: true,
        anticipatePin: 1,
        scrub: 1.5,
        onUpdate: (self) => {
          if (self.progress > 0.08 && !s2Counted) {
            s2Counted = true;
            s2.querySelectorAll('.stat-card__num').forEach(el => {
              const target = parseInt(el.dataset.target, 10);
              animateCounter(el, target, false, 1.4);
            });
          }
        }
      }
    });

    s2Tl.to(s2Cards, {
      opacity: 1,
      x: '0%',
      rotateZ: 0,
      stagger: 0.12,
      ease: 'expo.out'
    }, 0)
    .to(s2Info, {
      opacity: 1,
      scale: 1,
      ease: 'power4.out'
    }, 0.1)
    .to(s2Cards, {
      y: (i) => `${-2 - i * 1.5}vh`,
      ease: 'none'
    }, 0.5);


    // ----------------------------------------------------------------------
    // SCENE 3 — CLIMAX (Pathfinding Wavefront)
    // ----------------------------------------------------------------------
    const s3 = document.querySelector('#scene-3');
    const s3Compare = s3.querySelector('.algo-compare');
    const s3Bars = s3.querySelectorAll('.wf-bar__fill');
    const s3Metrics = s3.querySelectorAll('.metric');
    let s3Counted = false;

    gsap.set(s3Compare, { opacity: 0, scale: 0.9, y: '5vh' });
    gsap.set(s3Metrics, { opacity: 0, y: 20 });

    const s3Tl = gsap.timeline({
      scrollTrigger: {
        trigger: s3,
        start: 'top top',
        end: '+=250%',
        pin: true,
        pinSpacing: true,
        anticipatePin: 1,
        scrub: 1.5,
        onUpdate: (self) => {
          if (self.progress > 0.35 && !s3Counted) {
            s3Counted = true;
            s3.querySelectorAll('.metric__num').forEach(el => {
              const isDec = el.dataset.decimal === 'true';
              const target = parseFloat(el.dataset.target);
              animateCounter(el, target, isDec, 1.2);
            });
          }
        }
      }
    });

    s3Tl.to(s3Compare, {
      opacity: 1,
      scale: 1.0,
      y: '0vh',
      ease: 'expo.out'
    }, 0)
    .fromTo(s3.querySelectorAll('.algo-col__name .lm__i'),
      { y: '110%' },
      { y: '0%', duration: 0.8, stagger: 0.1, ease: 'expo.out' },
      0.1
    )
    .to(s3Bars[0], { height: '100%', ease: 'power2.out' }, 0.1)
    .to(s3Bars[1], { height: '21.3%', ease: 'power2.out' }, 0.2) // 78.7% pruned
    .to(s3Bars[2], { height: '100%', ease: 'power2.out' }, 0.3)
    .to(s3Metrics, {
      opacity: 1,
      y: 0,
      stagger: 0.1,
      ease: 'power3.out'
    }, 0.4)
    .to(s3Compare, {
      scale: 0.98,
      ease: 'none'
    }, 0.7);


    // ----------------------------------------------------------------------
    // SCENE 4 — DECELERATION (Invariant Observatory)
    // ----------------------------------------------------------------------
    const s4 = document.querySelector('#scene-4');
    const s4Cards = s4.querySelectorAll('.inv-card');

    gsap.set(s4Cards, {
      opacity: 0,
      scale: 0.92,
      rotateZ: (i) => (i % 2 === 0 ? -2 : 2)
    });

    const s4Tl = gsap.timeline({
      scrollTrigger: {
        trigger: s4,
        start: 'top top',
        end: '+=180%',
        pin: true,
        pinSpacing: true,
        anticipatePin: 1,
        scrub: 1.2
      }
    });

    s4Tl.to(s4Cards, {
      opacity: 1,
      scale: 1.0,
      rotateZ: 0,
      stagger: 0.1,
      ease: 'expo.out'
    }, 0)
    .to(s4Cards, {
      y: (i) => (i >= 3 ? '-3vh' : '-1.5vh'),
      ease: 'none'
    }, 0.3)
    .to(s4.querySelectorAll('.inv-card[data-status="specified"]'), {
      opacity: 0.45,
      ease: 'none'
    }, 0.65);


    // ----------------------------------------------------------------------
    // SCENE 5 — CLOSURE (Dispatch Terminal)
    // ----------------------------------------------------------------------
    const s5 = document.querySelector('#scene-5');
    const s5ManifestRows = s5.querySelectorAll('.manifest__row');
    const s5LinkCards = s5.querySelectorAll('.link-card');

    gsap.set(s5LinkCards, { opacity: 0, x: '15%' });

    const s5Tl = gsap.timeline({
      scrollTrigger: {
        trigger: s5,
        start: 'top top',
        end: '+=100%',
        pin: true,
        pinSpacing: true,
        anticipatePin: 1,
        scrub: 1.0
      }
    });

    s5Tl.fromTo(s5ManifestRows,
      { opacity: 0, y: 15 },
      { opacity: 1, y: 0, stagger: 0.08, ease: 'expo.out' },
      0
    )
    .to(s5LinkCards, {
      opacity: 1,
      x: '0%',
      stagger: 0.15,
      ease: 'power4.out'
    }, 0.2)
    .to('.manifest', { y: '-3vh', ease: 'none' }, 0.5)
    .to('.link-cards', { y: '-1.5vh', ease: 'none' }, 0.5);

  });


  // MOBILE PIPELINE ( < 768px — Invariant #11: Native unpinned flow )
  mm.add('(max-width: 767px)', () => {
    // Entrance for hero
    gsap.fromTo('.hero-title .lm__i',
      { y: '110%' },
      { y: '0%', duration: 0.9, ease: 'expo.out', stagger: 0.08 }
    );
    gsap.fromTo('.hero-sub',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', delay: 0.3 }
    );

    // Scroll-triggered batch reveals
    const sections = document.querySelectorAll('.scene');
    sections.forEach(sec => {
      ScrollTrigger.create({
        trigger: sec,
        start: 'top 75%',
        once: true,
        onEnter: () => {
          // Trigger counters if in Scene 2
          if (sec.id === 'scene-2') {
            sec.querySelectorAll('.stat-card__num').forEach(el => {
              animateCounter(el, parseInt(el.dataset.target, 10), false, 1.2);
            });
          }
          // Trigger wavefront & metrics if in Scene 3
          if (sec.id === 'scene-3') {
            sec.querySelectorAll('.wf-bar__fill').forEach(el => {
              el.style.height = el.dataset.cov + '%';
            });
            sec.querySelectorAll('.metric__num').forEach(el => {
              const isDec = el.dataset.decimal === 'true';
              animateCounter(el, parseFloat(el.dataset.target), isDec, 1.2);
            });
          }
        }
      });
    });
  });


  // ------------------------------------------------------------------------
  // 4. Interactive Tactile Micro-Interactions (Springs & 3D Tilts)
  // ------------------------------------------------------------------------
  // Invariant card 3D tilt
  const invCards = document.querySelectorAll('.inv-card');
  invCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      const rotX = -(y / (rect.height / 2)) * 4;
      const rotY = (x / (rect.width / 2)) * 4;
      gsap.to(card, {
        rotateX: rotX,
        rotateY: rotY,
        transformPerspective: 800,
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    card.addEventListener('mouseleave', () => {
      gsap.to(card, {
        rotateX: 0,
        rotateY: 0,
        duration: 0.6,
        ease: 'power2.out'
      });
    });
  });

  // Magnetic button effects for .magnetic-btn
  const magneticBtns = document.querySelectorAll('.magnetic-btn');
  magneticBtns.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const dx = (e.clientX - rect.left - rect.width / 2) * 0.25;
      const dy = (e.clientY - rect.top - rect.height / 2) * 0.25;
      gsap.to(btn, {
        x: Math.max(-12, Math.min(12, dx)),
        y: Math.max(-12, Math.min(12, dy)),
        duration: 0.3,
        ease: 'power2.out'
      });
    });

    btn.addEventListener('mouseleave', () => {
      gsap.to(btn, {
        x: 0,
        y: 0,
        duration: 0.6,
        ease: 'elastic.out(1, 0.4)'
      });
    });
  });

  // ------------------------------------------------------------------------
  // 5. Shared Resource Preview Dock & Carousel Subsystem
  // ------------------------------------------------------------------------
  const allDockCloseHandlers = [];

  function closeAllDocks(exceptDockId = null) {
    allDockCloseHandlers.forEach(({ id, closeFn }) => {
      if (id !== exceptDockId) closeFn();
    });
  }

  function initPreviewDockSystem(cfg) {
    const wrap = document.getElementById(cfg.wrapId);
    const dock = document.getElementById(cfg.dockId);
    const trigger = document.getElementById(cfg.triggerId);
    const modal = document.getElementById(cfg.modalId);
    const modalIframe = document.getElementById(cfg.modalIframeId);
    const modalClose = document.getElementById(cfg.modalCloseId);
    const modalBackdrop = document.getElementById(cfg.modalBackdropId);
    const expandBtn = document.getElementById(cfg.expandBtnId);
    const launchBtn = document.getElementById(cfg.launchBtnId);
    const prevBtn = document.getElementById(cfg.prevBtnId);
    const nextBtn = document.getElementById(cfg.nextBtnId);
    const track = document.getElementById(cfg.trackId);
    const subscrollFill = document.getElementById(cfg.subscrollFillId);
    const activeNum = document.getElementById(cfg.activeNumId);
    const activeTitle = document.getElementById(cfg.activeTitleId);
    const statusDot = document.getElementById(cfg.statusDotId);
    const movsContainer = document.getElementById(cfg.movsContainerId);
    const endBackBtn = document.getElementById(cfg.endBackBtnId);
    const newtabLink = document.getElementById(cfg.newtabLinkId);

    let currentIdx = 0;
    let hoverTimer = null;
    let isHoveringTrigger = false;
    let isHoveringDock = false;
    const decks = cfg.decks || [];

    function showDock() {
      clearTimeout(hoverTimer);
      closeAllDocks(cfg.dockId);
      if (dock) {
        dock.classList.add('is-active');
        dock.setAttribute('aria-hidden', 'false');
      }
    }

    function scheduleHideDock() {
      clearTimeout(hoverTimer);
      hoverTimer = setTimeout(() => {
        if (!isHoveringTrigger && !isHoveringDock && dock) {
          dock.classList.remove('is-active');
          dock.setAttribute('aria-hidden', 'true');
        }
      }, 1000);
    }

    function hideImmediate() {
      clearTimeout(hoverTimer);
      isHoveringTrigger = false;
      isHoveringDock = false;
      if (dock) {
        dock.classList.remove('is-active');
        dock.setAttribute('aria-hidden', 'true');
      }
    }

    allDockCloseHandlers.push({ id: cfg.dockId, closeFn: hideImmediate });

    if (wrap && dock) {
      wrap.addEventListener('mouseenter', () => {
        isHoveringTrigger = true;
        showDock();
      });

      wrap.addEventListener('mouseleave', () => {
        isHoveringTrigger = false;
        scheduleHideDock();
      });

      dock.addEventListener('mouseenter', () => {
        isHoveringDock = true;
        showDock();
      });

      dock.addEventListener('mouseleave', () => {
        isHoveringDock = false;
        scheduleHideDock();
      });
    }

    function triggerBoundaryBounce(direction) {
      if (!track) return;
      const currentTranslate = -(currentIdx * 100);
      const nudge = direction === 'next' ? -2.5 : 2.5;
      track.style.transition = 'transform 0.15s ease';
      track.style.transform = `translateX(${currentTranslate + nudge}%)`;
      setTimeout(() => {
        track.style.transition = 'transform 0.45s cubic-bezier(0.16, 1, 0.3, 1)';
        track.style.transform = `translateX(${currentTranslate}%)`;
      }, 150);
    }

    function goToDeck(index) {
      if (!track || decks.length <= 1) {
        if (track) triggerBoundaryBounce(index > 0 ? 'next' : 'prev');
        return;
      }
      const maxIdx = decks.length - 1;

      if (index < 0) {
        triggerBoundaryBounce('prev');
        return;
      }
      if (index > maxIdx) {
        triggerBoundaryBounce('next');
        return;
      }

      currentIdx = index;
      const active = decks[currentIdx];

      track.style.transform = `translateX(-${currentIdx * 100}%)`;

      if (subscrollFill) {
        const pct = Math.round(((currentIdx + 1) / decks.length) * 100);
        subscrollFill.style.width = `${pct}%`;
      }

      if (newtabLink && active.url && active.url !== '#') {
        newtabLink.href = active.url;
      }

      if (activeNum && active.num) activeNum.textContent = active.num;
      if (activeTitle && active.title) activeTitle.textContent = active.title;

      if (statusDot) {
        if (active.isEmpty) {
          statusDot.style.background = 'var(--amber-gold)';
          statusDot.style.boxShadow = '0 0 0 2px rgba(179, 128, 36, 0.2)';
        } else if (active.isEnd) {
          statusDot.style.background = 'var(--cinnabar-red)';
          statusDot.style.boxShadow = '0 0 0 2px rgba(210, 73, 30, 0.2)';
        } else {
          statusDot.style.background = 'var(--celadon-jade)';
          statusDot.style.boxShadow = '0 0 0 2px rgba(47, 91, 70, 0.2)';
        }
      }

      if (prevBtn) prevBtn.disabled = (currentIdx === 0);
      if (nextBtn) nextBtn.disabled = (currentIdx === maxIdx);

      if (movsContainer && active.movs) {
        movsContainer.innerHTML = '';
        active.movs.forEach((m, idx) => {
          const span = document.createElement('span');
          span.className = 'ppt-mov';
          if (active.isEmpty) {
            if (idx === 0) span.className = 'ppt-mov demo-mov--standby';
          } else if (!active.isEnd && idx === 0) {
            span.style.color = 'var(--celadon-jade)';
            span.style.fontWeight = '700';
            span.style.background = 'var(--celadon-light)';
          } else if (active.isEnd && idx === 0) {
            span.style.color = 'var(--cinnabar-red)';
            span.style.fontWeight = '700';
            span.style.background = 'rgba(210, 73, 30, 0.08)';
          }
          span.textContent = m;
          movsContainer.appendChild(span);
        });
      }
    }

    if (endBackBtn) {
      endBackBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        goToDeck(0);
      });
    }

    let wheelCooldown = false;
    if (dock) {
      dock.addEventListener('wheel', (e) => {
        e.preventDefault();
        if (wheelCooldown) return;

        const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
        if (delta > 18) {
          goToDeck(currentIdx + 1);
          wheelCooldown = true;
          setTimeout(() => { wheelCooldown = false; }, 360);
        } else if (delta < -18) {
          goToDeck(currentIdx - 1);
          wheelCooldown = true;
          setTimeout(() => { wheelCooldown = false; }, 360);
        }
      }, { passive: false });

      let touchStartX = 0;
      dock.addEventListener('touchstart', (e) => {
        if (e.touches.length > 0) touchStartX = e.touches[0].clientX;
      }, { passive: true });

      dock.addEventListener('touchend', (e) => {
        if (e.changedTouches.length > 0) {
          const touchEndX = e.changedTouches[0].clientX;
          const diffX = touchEndX - touchStartX;
          if (diffX < -40) {
            goToDeck(currentIdx + 1);
          } else if (diffX > 40) {
            goToDeck(currentIdx - 1);
          }
        }
      }, { passive: true });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        goToDeck(currentIdx - 1);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        goToDeck(currentIdx + 1);
      });
    }

    function openModal(e, deckIndex = currentIdx) {
      if (e) e.preventDefault();
      if (!modal) return;

      const deck = decks[deckIndex] || decks[0];
      if (deck && deck.isEmpty) {
        showToast('Live Demo environment is scheduled for Phase Two deployment.');
        return;
      }
      if (deck && deck.isEnd) return;

      modal.hidden = false;
      void modal.offsetWidth;
      modal.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      if (lenis) lenis.stop();

      if (trigger) trigger.setAttribute('aria-expanded', 'true');

      if (modalIframe && deck && deck.url && deck.url !== '#') {
        if (!modalIframe.src || modalIframe.src === 'about:blank' || !modalIframe.src.includes(deck.url)) {
          modalIframe.src = deck.url;
        }
      }

      const modalTabBtn = modal.querySelector('.ppt-modal__tab-btn');
      if (modalTabBtn && deck && deck.url && deck.url !== '#') {
        modalTabBtn.href = deck.url;
      }

      const modalTitle = modal.querySelector('.ppt-modal__title');
      if (modalTitle && deck && deck.modalTitle) {
        modalTitle.textContent = deck.modalTitle;
      }

      const modalBadge = modal.querySelector('.ppt-modal__badge');
      if (modalBadge && deck && deck.modalBadge) {
        modalBadge.textContent = deck.modalBadge;
      }

      setTimeout(() => {
        modalClose?.focus();
      }, 100);
    }

    function closeModal() {
      if (!modal || modal.hidden) return;

      modal.classList.remove('is-open');
      document.body.style.overflow = '';
      if (lenis) lenis.start();

      if (trigger) {
        trigger.setAttribute('aria-expanded', 'false');
        trigger.focus();
      }

      setTimeout(() => {
        modal.hidden = true;
      }, 350);
    }

    if (expandBtn) {
      expandBtn.addEventListener('click', (e) => openModal(e, currentIdx));
    }
    if (launchBtn) {
      launchBtn.addEventListener('click', (e) => openModal(e, currentIdx));
    }

    if (cfg.triggerSelector) {
      document.querySelectorAll(cfg.triggerSelector).forEach(el => {
        el.addEventListener('click', (e) => {
          const idx = parseInt(el.getAttribute(cfg.triggerDataAttr || 'data-deck-trigger'), 10) || 0;
          openModal(e, idx);
        });
        el.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const idx = parseInt(el.getAttribute(cfg.triggerDataAttr || 'data-deck-trigger'), 10) || 0;
            openModal(e, idx);
          }
        });
      });
    }

    if (modalClose) {
      modalClose.addEventListener('click', closeModal);
    }
    if (modalBackdrop) {
      modalBackdrop.addEventListener('click', closeModal);
    }

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal && !modal.hidden) {
        closeModal();
      }
    });

    return {
      goToDeck,
      openModal,
      closeModal,
      showDock,
      hideImmediate
    };
  }

  // ------------------------------------------------------------------------
  // A. Documentation Deck Registry & Initialization
  // ------------------------------------------------------------------------
  const docsDecks = [
    {
      num: '01',
      total: '02',
      title: 'SYSTEM DESIGN REPORT REV 1.0',
      modalTitle: 'AetherGrid AI — System Design Report (Rev 0.1.0)',
      modalBadge: 'SPECIFICATION AEG-RPT-001',
      url: 'Project_Proposal_&_ppt/project_proposal_1.pdf',
      movs: ['Problem Space', 'G_t Topology', 'Cost Model', 'Invariants', 'Verification'],
      isEnd: false
    },
    {
      num: '02',
      total: '02',
      title: 'DYNAMIC COST PRICING SPECIFICATION',
      modalTitle: 'AetherGrid AI — Dynamic Cost Pricing & Traversal Engine',
      modalBadge: 'CORE ENGINE SPECIFICATION',
      url: 'docs/CostPricingdocs.pdf',
      movs: ['System Arch', 'Edge Pricing', 'Weather Impedance', 'Anti-Flapping', 'Traversal Engine'],
      isEnd: false
    },
    {
      num: '02',
      total: '02',
      title: "THAT'S THE END OF THE ROAD",
      url: 'docs/CostPricingdocs.pdf',
      movs: ['Phase One Active', '2 Documents Linked', 'Terminal Horizon'],
      isEnd: true
    }
  ];

  const docsController = initPreviewDockSystem({
    wrapId: 'docs-card-wrap',
    dockId: 'docs-preview',
    triggerId: 'docs-trigger',
    modalId: 'docs-modal',
    modalIframeId: 'docs-modal-iframe',
    modalCloseId: 'docs-modal-close',
    modalBackdropId: 'docs-modal-backdrop',
    expandBtnId: 'docs-preview-expand-btn',
    launchBtnId: 'docs-launch-btn',
    prevBtnId: 'docs-prev-btn',
    nextBtnId: 'docs-next-btn',
    newtabLinkId: 'docs-newtab-link',
    trackId: 'docs-carousel-track',
    subscrollFillId: 'docs-subscroll-fill',
    activeNumId: 'docs-active-num',
    activeTitleId: 'docs-active-title',
    statusDotId: 'docs-status-dot',
    movsContainerId: 'docs-movements-container',
    endBackBtnId: 'docs-end-back-btn',
    triggerSelector: '[data-doc-trigger]',
    triggerDataAttr: 'data-doc-trigger',
    decks: docsDecks
  });

  // ------------------------------------------------------------------------
  // B. Presentation Deck Registry & Initialization
  // ------------------------------------------------------------------------
  const pptDecks = [
    {
      num: '01',
      total: '02',
      title: 'CONCERTO DAY ONE',
      modalTitle: 'AetherGrid AI — Autonomous Fleet & Emergency Dispatch',
      modalBadge: 'CONCERTO DECK',
      url: 'Project_Proposal_&_ppt/project_ppt.html',
      movs: ['Ouverture', 'Esposizione', 'Sviluppo', 'Rondò', 'Coda'],
      isEnd: false
    },
    {
      num: '02',
      total: '02',
      title: 'PHASE 01 ARCHITECTURAL DEFENSE',
      modalTitle: 'AetherGrid AI — Autonomous Urban Dispatch Architecture (Phase 01 Defense)',
      modalBadge: 'PHASE 01 DEFENSE',
      url: 'docs/phase01.html',
      movs: ['Overture', 'Topology & I1', 'Cost Physics', 'Algo Ledger', 'Lab Exhibits'],
      isEnd: false
    },
    {
      num: '02',
      total: '02',
      title: "THAT'S THE END OF THE ROAD",
      url: 'docs/phase01.html',
      movs: ['Phase One Active', '2 Decks Linked', 'Terminal Horizon'],
      isEnd: true
    }
  ];

  const pptController = initPreviewDockSystem({
    wrapId: 'presentation-card-wrap',
    dockId: 'ppt-preview',
    triggerId: 'presentation-trigger',
    modalId: 'ppt-modal',
    modalIframeId: 'ppt-modal-iframe',
    modalCloseId: 'ppt-modal-close',
    modalBackdropId: 'ppt-modal-backdrop',
    expandBtnId: 'ppt-preview-expand-btn',
    launchBtnId: 'ppt-launch-btn',
    prevBtnId: 'ppt-prev-btn',
    nextBtnId: 'ppt-next-btn',
    newtabLinkId: 'ppt-newtab-link',
    trackId: 'ppt-carousel-track',
    subscrollFillId: 'ppt-subscroll-fill',
    activeNumId: 'ppt-active-num',
    activeTitleId: 'ppt-active-title',
    statusDotId: 'ppt-status-dot',
    movsContainerId: 'ppt-movements-container',
    endBackBtnId: 'ppt-end-back-btn',
    triggerSelector: '[data-deck-trigger]',
    triggerDataAttr: 'data-deck-trigger',
    decks: pptDecks
  });

  // ------------------------------------------------------------------------
  // C. Live Demo Deck Registry & Initialization (Empty for now)
  // ------------------------------------------------------------------------
  const demoDecks = [
    {
      num: '00',
      total: '00',
      title: 'SIMULATION STANDBY (EMPTY)',
      url: '#',
      movs: ['Simulation Offline', 'WebSocket Inactive', 'Phase 2 Scheduled'],
      isEnd: true,
      isEmpty: true
    }
  ];

  const demoController = initPreviewDockSystem({
    wrapId: 'demo-card-wrap',
    dockId: 'demo-preview',
    triggerId: 'demo-trigger',
    modalId: 'demo-modal',
    modalIframeId: 'demo-modal-iframe',
    modalCloseId: 'demo-modal-close',
    modalBackdropId: 'demo-modal-backdrop',
    expandBtnId: 'demo-preview-expand-btn',
    launchBtnId: 'demo-launch-btn',
    prevBtnId: 'demo-prev-btn',
    nextBtnId: 'demo-next-btn',
    trackId: 'demo-carousel-track',
    subscrollFillId: 'demo-subscroll-fill',
    activeTitleId: 'demo-active-title',
    statusDotId: 'demo-status-dot',
    movsContainerId: 'demo-movements-container',
    decks: demoDecks
  });

  // Dedicated handlers for Live Demo trigger and standby buttons
  const demoTrigger = document.getElementById('demo-trigger');
  if (demoTrigger) {
    demoTrigger.addEventListener('click', (e) => {
      e.preventDefault();
      showToast('Live Demo simulation environment is scheduled for Phase Two deployment.');
    });
  }

  const demoBenchBtn = document.getElementById('demo-bench-btn');
  if (demoBenchBtn) {
    demoBenchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      showToast("Run 'python3 -m Aether.cli benchmark' in terminal for headless simulation.");
    });
  }

  // Placeholder links toast notification
  document.querySelectorAll('[data-placeholder]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const title = link.querySelector('.link-card__title')?.textContent || 'Resource';
      showToast(`${title} will be linked in future release.`);
    });
  });

  function showToast(msg) {
    let toast = document.querySelector('.site-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'site-toast';
      Object.assign(toast.style, {
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        backgroundColor: '#1A1A1A',
        color: '#F9F7F1',
        padding: '12px 20px',
        borderRadius: '2px',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '11px',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
        boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        zIndex: '9999',
        opacity: '0',
        transform: 'translateY(16px)',
        transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      });
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(16px)';
    }, 2400);
  }
});
