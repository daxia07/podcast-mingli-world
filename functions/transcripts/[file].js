// GET /transcripts/:file — WebVTT transcript from R2.
//
// Public: RSS <podcast:transcript> points here, and the in-app transcript panel
// fetches it. See functions/chapters/[file].js for the shared handler.

import { serveArtifact } from '../chapters/[file].js';

export async function onRequest(context) {
  return serveArtifact(context, 'transcripts', 'text/vtt; charset=utf-8');
}
