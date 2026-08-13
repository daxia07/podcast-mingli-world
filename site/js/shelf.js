/* shelf.js — shelving episodes and shows, and the swipe gesture maths.
 *
 * Two independent pieces of state, both local to this device:
 *
 *   pod_shelved      { episodeId: 1 }  episodes you swiped away
 *   pod_shows_shown  { showId: 1 }     shows archived in the manifest that you
 *                                      have chosen to see again here
 *
 * The second one matters: shows are archived server-side in content/shows.json,
 * which needs a deploy to change. Keeping a local override means the Airwallex
 * back-catalogue can be brought back from the phone, without a release, and
 * without the archive decision being reversed for good.
 *
 * Everything below is pure except the localStorage read/write, so the gesture
 * thresholds and the visibility rules are unit-tested in tests/test_shelf.mjs.
 */
(function (global) {
  'use strict';

  var KEY_EPISODES = 'pod_shelved';
  var KEY_SHOWS = 'pod_shows_shown';

  // Gesture thresholds, in pixels of horizontal travel.
  var REVEAL_AT = 56;      // past this, the action button stays open
  var COMMIT_AT = 160;     // past this, a full swipe acts immediately
  var VELOCITY_COMMIT = 1.1; // px/ms — a fast flick commits from a short drag
  var SLOP = 10;           // below this it is a tap, not a swipe

  function read(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || '{}') || {};
    } catch (e) {
      return {};
    }
  }
  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {}
  }

  // ——— episode shelf ———

  function shelvedEpisodes() { return read(KEY_EPISODES); }

  function isShelved(id) { return !!shelvedEpisodes()[String(id)]; }

  function setShelved(id, on) {
    var map = shelvedEpisodes();
    if (on) map[String(id)] = 1;
    else delete map[String(id)];
    write(KEY_EPISODES, map);
    return on;
  }

  function shelvedCount() { return Object.keys(shelvedEpisodes()).length; }

  // ——— show overrides ———

  function shownShows() { return read(KEY_SHOWS); }

  function isShowRestored(showId) { return !!shownShows()[String(showId)]; }

  function setShowRestored(showId, on) {
    var map = shownShows();
    if (on) map[String(showId)] = 1;
    else delete map[String(showId)];
    write(KEY_SHOWS, map);
    return on;
  }

  /** Should this show appear in the app?
   *  Archived in the manifest, unless restored locally. */
  function showVisible(playlist) {
    if (!playlist) return false;
    if (!playlist.archived) return true;
    return isShowRestored(playlist.id);
  }

  /** Should this episode appear in a browsing list?
   *  Hidden when shelved locally, or when its show is archived and not restored. */
  function episodeVisible(ep, playlistsById) {
    if (!ep) return false;
    if (isShelved(ep.id)) return false;

    var playlist = playlistsById && playlistsById[ep.playlist];
    if (playlist && playlist.archived && !isShowRestored(ep.playlist)) return false;

    // Episodes carry their own archived flag too, set from the show they belong
    // to. Honour it, but let a local restore win.
    if (ep.archived && !isShowRestored(ep.playlist)) return false;

    return true;
  }

  // ——— gesture ———

  /** What a drag should do when the finger lifts.
   *
   *  Returns 'closed' | 'open' | 'commit'. Only leftward travel counts, so a
   *  horizontal scroll to the right never arms the action.
   */
  function swipeDecision(dx, velocity, wasOpen) {
    var travel = -dx;                       // leftward is positive here
    var speed = velocity == null ? 0 : -velocity;

    if (travel >= COMMIT_AT) return 'commit';
    if (speed >= VELOCITY_COMMIT && travel >= REVEAL_AT) return 'commit';
    if (travel >= REVEAL_AT) return 'open';

    // An open row needs a deliberate push back to the right to close.
    if (wasOpen && travel > -REVEAL_AT / 2) return 'open';
    return 'closed';
  }

  /** Is this movement a swipe rather than a tap or a vertical scroll? */
  function isHorizontalSwipe(dx, dy) {
    return Math.abs(dx) > SLOP && Math.abs(dx) > Math.abs(dy) * 1.4;
  }

  /** How far to translate the row during a drag, with resistance past the
   *  reveal point so it feels anchored rather than loose. */
  function dragOffset(dx) {
    if (dx >= 0) return Math.min(dx * 0.25, 24); // rightward: rubber band only
    var travel = -dx;
    if (travel <= REVEAL_AT) return -travel;
    return -(REVEAL_AT + (travel - REVEAL_AT) * 0.55);
  }

  global.Shelf = {
    isShelved: isShelved,
    setShelved: setShelved,
    shelvedEpisodes: shelvedEpisodes,
    shelvedCount: shelvedCount,
    isShowRestored: isShowRestored,
    setShowRestored: setShowRestored,
    shownShows: shownShows,
    showVisible: showVisible,
    episodeVisible: episodeVisible,
    swipeDecision: swipeDecision,
    isHorizontalSwipe: isHorizontalSwipe,
    dragOffset: dragOffset,
    REVEAL_AT: REVEAL_AT,
    COMMIT_AT: COMMIT_AT
  };
})(typeof window !== 'undefined' ? window : globalThis);
