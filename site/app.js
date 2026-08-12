/* Mingli Podcast — player-first app with solution boards */
(function () {
  "use strict";

  var SHOW_META = {
    "coding-prep": {
      title: "Coding Prep",
      mono: "CP",
      desc: "Think-aloud coding for Airwallex screens. Pair with tutor deep drills.",
    },
    "coding-youtube": {
      title: "Coding YouTube",
      mono: "YT",
      desc: "Audio-first NeetCode walkthroughs. Pair with Coding Prep + app drills.",
    },
    "system-design": {
      title: "System Design",
      mono: "SD",
      desc: "Architecture think-alouds, concepts, and design walkthroughs.",
    },
    "awx-10min-speeches": {
      title: "AWX 10-Min Speeches",
      mono: "AW",
      desc: "Agenda monologues for Airwallex system design prep.",
    },
    "airwallex-domain": {
      title: "Airwallex Domain",
      mono: "AX",
      desc: "Domain-specific mock interviews.",
    },
    "sd-mock-interviews": {
      title: "SD Mock Interviews",
      mono: "MK",
      desc: "Two-voice system design mocks.",
    },
    "sd-youtube": {
      title: "SD YouTube",
      mono: "SY",
      desc: "Curated video-derived design episodes.",
    },
    "sd-think-aloud": {
      title: "SD Think-Aloud",
      mono: "TA",
      desc: "Long-form design reasoning.",
    },
    "sd-estimation": {
      title: "SD Estimation",
      mono: "ES",
      desc: "Back-of-envelope estimation practice.",
    },
    "sd-deep-dive": {
      title: "SD Deep Dive",
      mono: "DD",
      desc: "Deep concept episodes.",
    },
    "interview-prep": {
      title: "Interview English",
      mono: "EN",
      desc: "Daily English patterns and frameworks.",
    },
    "interview-support": {
      title: "Interview Support",
      mono: "QA",
      desc: "Self-intro and Q&A practice.",
    },
  };

  var ICON_PLAY =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="6 3 20 12 6 21 6 3"/></svg>';
  var ICON_PAUSE =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="4" width="5" height="16" rx="1"/><rect x="14" y="4" width="5" height="16" rx="1"/></svg>';

  var FEATURED_SHOWS = ["coding-prep", "coding-youtube", "system-design"];

  var SHOW_ORDER = [
    "coding-prep",
    "coding-youtube",
    "system-design",
    "sd-mock-interviews",
    "awx-10min-speeches",
    "airwallex-domain",
    "sd-youtube",
    "sd-think-aloud",
    "sd-estimation",
    "sd-deep-dive",
    "interview-prep",
    "interview-support",
  ];

  var episodes = [];
  var playlists = [];
  var solutions = {};
  var queue = [];
  var queuePos = -1;
  var current = null;
  var solutionsOn = false;
  var speeds = [1, 1.25, 1.5, 0.85];
  var speedIdx = 0;
  var finished = loadJSON("pod_finished", {});
  var progress = loadJSON("pod_progress", {});

  var audio = document.getElementById("audio");

  function loadJSON(k, d) {
    try {
      return JSON.parse(localStorage.getItem(k) || "null") || d;
    } catch (e) {
      return d;
    }
  }
  function saveJSON(k, v) {
    try {
      localStorage.setItem(k, JSON.stringify(v));
    } catch (e) {}
  }

  function toast(m) {
    var t = document.getElementById("toast");
    t.textContent = m;
    t.classList.add("on");
    setTimeout(function () {
      t.classList.remove("on");
    }, 2200);
  }

  function fmt(s) {
    if (!isFinite(s) || s < 0) s = 0;
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }

  function hourGreet() {
    var h = new Date().getHours();
    var line =
      h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
    return "<strong>" + line + "</strong>Interview prep audio";
  }

  function monoFor(id) {
    var m = showMeta(id);
    if (m.mono) return m.mono;
    var t = (m.title || id || "??").replace(/[^A-Za-z0-9]/g, "");
    return (t.slice(0, 2) || "??").toUpperCase();
  }

  function artHtml(id) {
    return '<span class="mono">' + esc(monoFor(id)) + "</span>";
  }

  function epShowId(ep) {
    if (ep.playlist) return ep.playlist;
    if (ep.playlist_ids && ep.playlist_ids.length) {
      // Prefer coding / system-design when multi-tagged
      var ids = ep.playlist_ids;
      if (ids.indexOf("coding-youtube") >= 0) return "coding-youtube";
      if (ids.indexOf("coding-prep") >= 0) return "coding-prep";
      if (ids.indexOf("system-design") >= 0) return "system-design";
      return ids[0];
    }
    var tip = String(ep.tip_id || "");
    var theme = String(ep.theme || "");
    if (tip.indexOf("system-design") >= 0 || theme.indexOf("sd-") === 0)
      return "system-design";
    if (theme.indexOf("yt-coding") === 0 || theme.indexOf("yt-coding-") >= 0)
      return "coding-youtube";
    if (tip.indexOf("coding") >= 0 || theme.indexOf("coding") >= 0)
      return "coding-prep";
    if (theme.indexOf("mock") >= 0) return "sd-mock-interviews";
    if (theme.indexOf("awx") >= 0) return "awx-10min-speeches";
    return "interview-prep";
  }

  // The manifest is the show registry (content/shows.json -> playlists). The
  // SHOW_META and SHOW_ORDER constants below are now only fallbacks for shows
  // the manifest doesn't describe — a new show must not require an app.js edit,
  // which is exactly why the AWS AI Practitioner show rendered nowhere.
  function adoptShowsFromManifest() {
    var ordered = [];

    playlists.forEach(function (p) {
      var existing = SHOW_META[p.id] || {};
      SHOW_META[p.id] = {
        title: p.title || existing.title || p.id,
        mono: p.mono || existing.mono ||
          (String(p.id).replace(/[^A-Za-z0-9]/g, "").slice(0, 2) || "??").toUpperCase(),
        desc: p.description || existing.desc || "",
        icon: p.icon || existing.icon || "",
        featured: p.featured != null ? !!p.featured : !!existing.featured,
      };
      ordered.push({
        id: p.id,
        // Shows without an explicit order keep their old hardcoded position.
        order: p.order != null ? p.order : 100 + Math.max(SHOW_ORDER.indexOf(p.id), 0),
      });
    });

    if (!ordered.length) return;

    ordered.sort(function (a, b) {
      return a.order - b.order;
    });
    SHOW_ORDER = ordered.map(function (o) {
      return o.id;
    });

    var pinned = ordered
      .filter(function (o) {
        return SHOW_META[o.id] && SHOW_META[o.id].featured;
      })
      .map(function (o) {
        return o.id;
      });
    if (pinned.length) FEATURED_SHOWS = pinned;
  }

  function showMeta(id) {
    return (
      SHOW_META[id] || {
        title: id,
        mono: (String(id || "??").replace(/[^A-Za-z0-9]/g, "").slice(0, 2) || "??").toUpperCase(),
        icon: "🎵",
        desc: "",
      }
    );
  }

  function episodesForShow(showId) {
    var pl = null;
    for (var i = 0; i < playlists.length; i++) {
      if (playlists[i].id === showId) {
        pl = playlists[i];
        break;
      }
    }
    var byId = {};
    var list = [];
    if (pl && pl.episode_ids && pl.episode_ids.length) {
      list = episodes.filter(function (ep) {
        return pl.episode_ids.indexOf(ep.id) !== -1 && !ep.archived;
      });
      list.sort(function (a, b) {
        return pl.episode_ids.indexOf(a.id) - pl.episode_ids.indexOf(b.id);
      });
      list.forEach(function (ep) {
        byId[ep.id] = true;
      });
    }
    // Also include episodes that tag this show (unshelves SD eps missing from ids)
    episodes.forEach(function (ep) {
      if (ep.archived || byId[ep.id]) return;
      if (epShowId(ep) === showId) {
        list.push(ep);
        byId[ep.id] = true;
      }
    });
    return list;
  }

  function epSrc(ep) {
    return (
      ep.file_url ||
      ep.audio_url ||
      (ep.filename ? "/episodes/" + ep.filename : "")
    );
  }

  function hasBoard(ep) {
    return !!(ep && solutions[String(ep.id)]);
  }

  // ——— tabs ———
  function switchTab(name) {
    document.querySelectorAll(".tab").forEach(function (t) {
      t.classList.toggle("on", t.dataset.tab === name);
    });
    document.querySelectorAll(".bottom-nav .nav-item").forEach(function (b) {
      b.classList.toggle("on", b.dataset.tab === name);
    });
    document.getElementById("showDetail").hidden = true;
    if (name === "home") renderHome();
    if (name === "library") renderLibrary("shows");
    if (name === "search") document.getElementById("searchInput").focus();
  }

  document.getElementById("bottomNav").addEventListener("click", function (e) {
    var btn = e.target.closest(".nav-item");
    if (!btn) return;
    switchTab(btn.dataset.tab);
  });

  // ——— render home ———
  function renderHome() {
    document.getElementById("greet").innerHTML = hourGreet();

    var cont = document.getElementById("continueCard");
    var resumeId = progress.lastId;
    var resumeEp = resumeId
      ? episodes.filter(function (e) {
          return e.id === resumeId;
        })[0]
      : null;
    if (resumeEp && progress[String(resumeId)] > 5) {
      var dur = progress[String(resumeId) + "_dur"] || 0;
      var pos = progress[String(resumeId)] || 0;
      var pct = dur > 0 ? Math.min(100, (pos / dur) * 100) : 10;
      cont.hidden = false;
      cont.innerHTML =
        '<div class="k">Continue listening</div><div class="t">' +
        esc(resumeEp.title) +
        '</div><div class="s">' +
        esc(showMeta(epShowId(resumeEp)).title) +
        (hasBoard(resumeEp) ? " · Solution board" : "") +
        '</div><div class="bar"><i style="width:' +
        pct +
        '%"></i></div>';
      cont.onclick = function () {
        playEpisode(resumeEp, pos);
      };
    } else {
      cont.hidden = true;
    }

    var row = document.getElementById("showRow");
    var html = "";
    // Featured shows come from the manifest (shows.json "featured": true),
    // falling back to the original three.
    FEATURED_SHOWS.forEach(function (id) {
      var eps = episodesForShow(id);
      if (!eps.length && id === "system-design") {
        // Unshelve: still show SD if any episode maps via tip/theme
        eps = episodes.filter(function (ep) {
          return !ep.archived && epShowId(ep) === "system-design";
        });
      }
      if (!eps.length && !SHOW_META[id]) return;
      var m = showMeta(id);
      var pl = playlists.filter(function (p) {
        return p.id === id;
      })[0];
      var title = (pl && pl.title) || m.title;
      var cls =
        "show-card featured" +
        (id === "system-design" ? " sd" : "") +
        (id === "coding-youtube" ? " yt" : "");
      html +=
        '<div class="' +
        cls +
        '" data-show="' +
        escAttr(id) +
        '"><div class="art">' +
        artHtml(id) +
        '</div><div class="n">' +
        esc(title) +
        '</div><div class="c">' +
        Math.max(eps.length, (pl && pl.episode_ids && pl.episode_ids.length) || 0) +
        " episodes</div></div>";
    });
    var order = SHOW_ORDER.slice();
    playlists.forEach(function (p) {
      if (order.indexOf(p.id) === -1) order.push(p.id);
    });
    order.forEach(function (id) {
      if (id === "coding-prep" || id === "coding-youtube" || id === "system-design") return;
      var eps = episodesForShow(id);
      if (!eps.length && !SHOW_META[id]) return;
      var m = showMeta(id);
      var title = (playlists.filter(function (p) {
        return p.id === id;
      })[0] || {}).title || m.title;
      html +=
        '<div class="show-card" data-show="' +
        escAttr(id) +
        '"><div class="art">' +
        artHtml(id) +
        '</div><div class="n">' +
        esc(title) +
        '</div><div class="c">' +
        eps.length +
        " episodes</div></div>";
    });
    row.innerHTML = html || '<div class="empty">No shows yet</div>';
    row.querySelectorAll(".show-card").forEach(function (el) {
      el.addEventListener("click", function () {
        openShow(el.dataset.show);
      });
    });

    var featured = episodes
      .filter(function (e) {
        return !e.archived;
      })
      .slice()
      .sort(function (a, b) {
        return (b.id || 0) - (a.id || 0);
      })
      .slice(0, 12);
    // put coding-prep / coding-youtube first among featured
    featured.sort(function (a, b) {
      function rank(ep) {
        var s = epShowId(ep);
        if (s === "coding-prep") return 0;
        if (s === "coding-youtube") return 1;
        return 2;
      }
      var ac = rank(a);
      var bc = rank(b);
      if (ac !== bc) return ac - bc;
      return (b.id || 0) - (a.id || 0);
    });
    renderEpList(document.getElementById("featuredList"), featured.slice(0, 8));
  }

  function renderEpList(el, list) {
    if (!list.length) {
      el.innerHTML = '<div class="empty">Nothing here</div>';
      return;
    }
    el.innerHTML = list
      .map(function (ep) {
        var board = hasBoard(ep);
        var done = !!finished[String(ep.id)];
        return (
          '<div class="ep-card' +
          (board ? " has-sheet" : "") +
          (done ? " done" : "") +
          '" data-id="' +
          ep.id +
          '">' +
          '<div class="ep-num">' +
          (done ? "✓" : ep.id) +
          "</div>" +
          '<div class="ep-body"><div class="ep-title">' +
          esc(ep.title) +
          '</div><div class="ep-meta">' +
          esc(showMeta(epShowId(ep)).title) +
          " · " +
          (ep.duration || "—") +
          "</div>" +
          (board
            ? '<span class="ep-badge">Solution board</span>'
            : "") +
          "</div>" +
          '<button type="button" class="ep-play" data-play="' +
          ep.id +
          '" aria-label="Play">' +
          ICON_PLAY +
          "</button></div>"
        );
      })
      .join("");
    el.querySelectorAll(".ep-card").forEach(function (card) {
      card.addEventListener("click", function (e) {
        if (e.target.closest(".ep-play")) return;
        var ep = byId(+card.dataset.id);
        if (ep) playEpisode(ep);
      });
    });
    el.querySelectorAll(".ep-play").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var ep = byId(+btn.dataset.play);
        if (ep) playEpisode(ep);
      });
    });
  }

  function byId(id) {
    for (var i = 0; i < episodes.length; i++) {
      if (episodes[i].id === id) return episodes[i];
    }
    return null;
  }

  // ——— library ———
  function renderLibrary(mode) {
    document.querySelectorAll("#libSeg .seg-btn").forEach(function (b) {
      b.classList.toggle("on", b.dataset.lib === mode);
    });
    var el = document.getElementById("libraryList");
    if (mode === "finished") {
      var list = episodes.filter(function (e) {
        return finished[String(e.id)];
      });
      renderEpList(el, list);
      return;
    }
    var html = "";
    var order = SHOW_ORDER.slice();
    playlists.forEach(function (p) {
      if (order.indexOf(p.id) === -1) order.push(p.id);
    });
    order.forEach(function (id) {
      var eps = episodesForShow(id);
      if (!eps.length) return;
      var m = showMeta(id);
      var pl = playlists.filter(function (p) {
        return p.id === id;
      })[0];
      html +=
        '<div class="lib-row" data-show="' +
        escAttr(id) +
        '"><div class="lib-art">' +
        artHtml(id) +
        '</div><div class="lib-info"><div class="lib-name">' +
        esc((pl && pl.title) || m.title) +
        '</div><div class="lib-sub">' +
        eps.length +
        " episodes</div></div></div>";
    });
    el.innerHTML = html || '<div class="empty">No shows</div>';
    el.querySelectorAll(".lib-row").forEach(function (row) {
      row.addEventListener("click", function () {
        openShow(row.dataset.show);
      });
    });
  }

  document.getElementById("libSeg").addEventListener("click", function (e) {
    var b = e.target.closest(".seg-btn");
    if (!b) return;
    renderLibrary(b.dataset.lib);
  });

  // ——— show detail ———
  function openShow(id) {
    var m = showMeta(id);
    var pl = playlists.filter(function (p) {
      return p.id === id;
    })[0];
    var eps = episodesForShow(id);
    document.getElementById("showDetail").hidden = false;
    document.getElementById("showArt").innerHTML = artHtml(id);
    document.getElementById("showName").textContent =
      (pl && pl.title) || m.title;
    document.getElementById("showDesc").textContent =
      (pl && pl.description) || m.desc || "";
    document.getElementById("showTitle").textContent =
      (pl && pl.title) || m.title;
    renderEpList(document.getElementById("showEpisodes"), eps);
    document.getElementById("showPlayAll").onclick = function () {
      if (!eps.length) return;
      queue = eps.slice();
      queuePos = 0;
      playEpisode(queue[0]);
    };
    document.getElementById("showQueueAll").onclick = function () {
      queue = queue.concat(eps);
      toast("Queued " + eps.length + " episodes");
      updateQueueUI();
    };
  }

  document.getElementById("showBack").onclick = function () {
    document.getElementById("showDetail").hidden = true;
  };

  // ——— search ———
  document.getElementById("searchInput").addEventListener("input", function () {
    var q = this.value.trim().toLowerCase();
    var el = document.getElementById("searchResults");
    if (!q) {
      el.innerHTML = '<div class="empty">Search episodes and solution boards</div>';
      return;
    }
    var hits = episodes.filter(function (ep) {
      var blob = (
        ep.title +
        " " +
        (ep.description || "") +
        " " +
        (ep.subtitle || "") +
        " " +
        epShowId(ep)
      ).toLowerCase();
      var board = solutions[String(ep.id)];
      if (board) {
        blob +=
          " " +
          board.title +
          " " +
          board.problem +
          " " +
          board.sections
            .map(function (s) {
              return s.title + " " + s.body.join(" ");
            })
            .join(" ");
      }
      return blob.indexOf(q) !== -1;
    });
    renderEpList(el, hits.slice(0, 30));
  });

  // ——— playback ———
  function playEpisode(ep, startAt) {
    if (!ep) return;
    current = ep;
    var src = epSrc(ep);
    if (!src) {
      toast("No audio for this episode");
      return;
    }

    // ensure in queue
    var qi = -1;
    for (var i = 0; i < queue.length; i++) {
      if (queue[i].id === ep.id) {
        qi = i;
        break;
      }
    }
    if (qi < 0) {
      queue = [ep].concat(queue);
      queuePos = 0;
    } else {
      queuePos = qi;
    }

    audio.src = src;
    audio.load();
    var resume = startAt != null ? startAt : progress[String(ep.id)] || 0;
    if (resume > 5) {
      audio.addEventListener(
        "loadedmetadata",
        function onMeta() {
          audio.currentTime = Math.min(resume, (audio.duration || resume) - 1);
          audio.removeEventListener("loadedmetadata", onMeta);
        }
      );
    }
    audio
      .play()
      .then(function () {
        updatePlayButtons(true);
      })
      .catch(function () {
        toast("Tap play to start audio");
        updatePlayButtons(false);
      });

    progress.lastId = ep.id;
    saveJSON("pod_progress", progress);

    openPlayer(true);
    updatePlayerChrome();
    updateMini();
    updateQueueUI();

    // player-ui.js picks this up to load chapters, the transcript and
    // lock-screen metadata. Kept as an event so app.js has no dependency on it.
    try {
      window.dispatchEvent(new CustomEvent("episode:change", { detail: ep }));
    } catch (e) {}
    if (solutionsOn) {
      if (hasBoard(ep)) renderSolutions(ep);
      else {
        solutionsOn = false;
        applySolutionsMode();
        toast("No solution board for this episode yet");
      }
    }
  }

  function openPlayer(full) {
    document.getElementById("mini").hidden = false;
    document.getElementById("app").classList.add("has-mini");
    if (full) {
      document.getElementById("playerFull").hidden = false;
    }
  }

  function closePlayer() {
    document.getElementById("playerFull").hidden = true;
  }

  function updatePlayerChrome() {
    if (!current) return;
    var m = showMeta(epShowId(current));
    document.getElementById("playerShowName").textContent = m.title;
    document.getElementById("playerTitle").textContent = current.title;
    document.getElementById("playerSub").textContent =
      (current.subtitle || m.title) +
      (current.duration ? " · " + current.duration : "");
    document.getElementById("playerArt").innerHTML = artHtml(epShowId(current));
    document.getElementById("miniTitle").textContent = current.title;
    var canSol = hasBoard(current);
    document.getElementById("solHint").hidden = canSol;
    document.getElementById("btnSolutions").disabled = !canSol;
    document.getElementById("btnSolutions").classList.toggle("disabled", !canSol);
  }

  function updateMini() {
    document.getElementById("mini").hidden = !current;
    document.getElementById("app").classList.toggle("has-mini", !!current);
  }

  function updatePlayButtons(playing) {
    var main = document.getElementById("btnPlay");
    var mini = document.getElementById("miniPlay");
    main.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
    main.classList.toggle("playing", !!playing);
    main.setAttribute("aria-label", playing ? "Pause" : "Play");
    mini.innerHTML = playing ? ICON_PAUSE : ICON_PLAY;
    mini.setAttribute("aria-label", playing ? "Pause" : "Play");
  }

  function togglePlay() {
    if (!current) return;
    if (audio.paused) {
      audio.play().then(function () {
        updatePlayButtons(true);
      });
    } else {
      audio.pause();
      updatePlayButtons(false);
    }
  }

  audio.addEventListener("timeupdate", function () {
    if (!current || !audio.duration) return;
    var pct = audio.currentTime / audio.duration;
    document.getElementById("seek").value = Math.floor(pct * 1000);
    document.getElementById("tCur").textContent = fmt(audio.currentTime);
    document.getElementById("tDur").textContent = fmt(audio.duration);
    document.getElementById("miniFill").style.width = pct * 100 + "%";
    progress[String(current.id)] = audio.currentTime;
    progress[String(current.id) + "_dur"] = audio.duration;
    progress.lastId = current.id;
    if (Math.floor(audio.currentTime) % 3 === 0) saveJSON("pod_progress", progress);
  });

  audio.addEventListener("ended", function () {
    if (current) {
      finished[String(current.id)] = true;
      saveJSON("pod_finished", finished);
      progress[String(current.id)] = 0;
      saveJSON("pod_progress", progress);
    }
    playNext();
  });

  audio.addEventListener("play", function () {
    updatePlayButtons(true);
  });
  audio.addEventListener("pause", function () {
    updatePlayButtons(false);
  });

  document.getElementById("seek").addEventListener("input", function () {
    if (!audio.duration) return;
    audio.currentTime = (this.value / 1000) * audio.duration;
  });

  document.getElementById("btnPlay").onclick = togglePlay;
  document.getElementById("miniPlay").onclick = function (e) {
    e.stopPropagation();
    togglePlay();
  };
  document.getElementById("miniOpen").onclick = function () {
    openPlayer(true);
  };
  document.getElementById("playerClose").onclick = closePlayer;
  document.getElementById("btnBack15").onclick = function () {
    audio.currentTime = Math.max(0, audio.currentTime - 15);
  };
  document.getElementById("btnFwd15").onclick = function () {
    audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 15);
  };
  document.getElementById("btnNext").onclick = playNext;
  document.getElementById("miniNext").onclick = function (e) {
    e.stopPropagation();
    playNext();
  };
  document.getElementById("btnPrev").onclick = playPrev;

  document.getElementById("btnSpeed").onclick = function () {
    speedIdx = (speedIdx + 1) % speeds.length;
    audio.playbackRate = speeds[speedIdx];
    this.textContent = speeds[speedIdx] + "×";
  };

  function playNext() {
    if (queuePos < queue.length - 1) {
      queuePos++;
      playEpisode(queue[queuePos], 0);
    } else {
      updatePlayButtons(false);
      toast("Queue finished");
    }
  }
  function playPrev() {
    if (audio.currentTime > 3) {
      audio.currentTime = 0;
      return;
    }
    if (queuePos > 0) {
      queuePos--;
      playEpisode(queue[queuePos], 0);
    }
  }

  function updateQueueUI() {
    document.getElementById("queueCount").textContent = String(queue.length);
    var list = document.getElementById("queueList");
    list.innerHTML = queue
      .map(function (ep, i) {
        return (
          '<div class="queue-item' +
          (i === queuePos ? " now" : "") +
          '" data-qi="' +
          i +
          '">' +
          (i === queuePos ? "Now · " : i + 1 + ". ") +
          esc(ep.title) +
          "</div>"
        );
      })
      .join("");
    list.querySelectorAll(".queue-item").forEach(function (row) {
      row.addEventListener("click", function () {
        queuePos = +row.dataset.qi;
        playEpisode(queue[queuePos], 0);
      });
    });
  }

  document.getElementById("queueToggle").onclick = function () {
    var list = document.getElementById("queueList");
    list.hidden = !list.hidden;
  };

  // ——— solutions ———
  function applySolutionsMode() {
    var panel = document.getElementById("solutionsPanel");
    var full = document.getElementById("playerFull");
    var btn = document.getElementById("btnSolutions");
    panel.hidden = !solutionsOn;
    full.classList.toggle("sol-on", solutionsOn);
    btn.classList.toggle("on", solutionsOn);
    document.getElementById("btnSolutionsOff").classList.toggle("on", solutionsOn);
    document.getElementById("btnSolutionsOff").textContent = solutionsOn
      ? "ON"
      : "OFF";
  }

  function renderSolutions(ep) {
    var board = solutions[String(ep.id)];
    if (!board) return;
    var tabs = document.getElementById("solTabs");
    var body = document.getElementById("solBody");
    tabs.innerHTML = board.sections
      .map(function (s, i) {
        return (
          '<button type="button" class="sol-tab' +
          (i === 0 ? " on" : "") +
          '" data-si="' +
          i +
          '">' +
          esc(s.title) +
          "</button>"
        );
      })
      .join("");

    function showSection(idx) {
      tabs.querySelectorAll(".sol-tab").forEach(function (t, i) {
        t.classList.toggle("on", i === idx);
      });
      var s = board.sections[idx];
      body.innerHTML =
        '<div class="sol-section"><h3>' +
        esc(s.title) +
        "</h3><ul>" +
        s.body
          .map(function (line) {
            return "<li>" + esc(line) + "</li>";
          })
          .join("") +
        "</ul></div>" +
        // also list all for free browse
        board.sections
          .map(function (sec, j) {
            if (j === idx) return "";
            return (
              '<div class="sol-section" id="sol-sec-' +
              j +
              '"><h3>' +
              esc(sec.title) +
              "</h3><ul>" +
              sec.body
                .map(function (line) {
                  return "<li>" + esc(line) + "</li>";
                })
                .join("") +
              "</ul></div>"
            );
          })
          .join("");
    }

    showSection(0);
    tabs.querySelectorAll(".sol-tab").forEach(function (t) {
      t.addEventListener("click", function () {
        showSection(+t.dataset.si);
        body.scrollTop = 0;
      });
    });

    var tutor = document.getElementById("solTutor");
    if (board.tutorPath) {
      tutor.hidden = false;
      tutor.href = "https://learn.mingli.world" + board.tutorPath;
    } else {
      tutor.hidden = true;
    }
  }

  document.getElementById("btnSolutions").onclick = function () {
    if (!current || !hasBoard(current)) {
      document.getElementById("solHint").hidden = false;
      toast("No solution board for this episode yet");
      return;
    }
    solutionsOn = !solutionsOn;
    applySolutionsMode();
    if (solutionsOn) renderSolutions(current);
  };
  document.getElementById("btnSolutionsOff").onclick = function () {
    solutionsOn = false;
    applySolutionsMode();
  };

  // ——— logout ———
  function logout() {
    fetch("/api/logout", { method: "POST" }).finally(function () {
      location.reload();
    });
  }
  document.getElementById("btnLogout").onclick = logout;
  document.getElementById("btnLogout2").onclick = logout;

  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function escAttr(s) {
    return esc(s).replace(/'/g, "&#39;");
  }

  // ——— boot ———
  Promise.all([
    fetch("/manifest.json").then(function (r) {
      return r.json();
    }),
    fetch("/solutions.json")
      .then(function (r) {
        return r.ok ? r.json() : {};
      })
      .catch(function () {
        return {};
      }),
  ])
    .then(function (pair) {
      var d = pair[0];
      solutions = pair[1] || {};
      episodes = (d.episodes || []).map(function (ep) {
        if (!ep.file_url) {
          ep.file_url =
            ep.audio_url ||
            (ep.filename ? "/episodes/" + ep.filename : "");
        }
        return ep;
      });
      var rawPl = d.playlists || {};
      playlists = Array.isArray(rawPl)
        ? rawPl
        : Object.keys(rawPl).map(function (k) {
            var p = rawPl[k];
            p.id = k;
            p.title = p.title || p.name || k;
            return p;
          });
      adoptShowsFromManifest();
      renderHome();
    })
    .catch(function () {
      toast("Failed to load podcast data");
    });
})();
