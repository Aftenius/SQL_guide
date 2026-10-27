import { describe, expect, it } from "vitest";

import { tracks } from "./catalog";
import { lessonBody } from "./lessonBodies";

describe("lessonBody", () => {
  it("gives every lesson a lecture that can be read on its own", () => {
    for (const track of tracks) {
      for (const lesson of track.lessons) {
        const body = lessonBody(track.slug, lesson.slug);
        expect(body?.paragraphs.length, `${track.slug}/${lesson.slug}`).toBeGreaterThanOrEqual(3);
        expect(body?.syntax?.length, `${track.slug}/${lesson.slug}`).toBeGreaterThan(0);
        expect(body?.prompt.length, `${track.slug}/${lesson.slug}`).toBeGreaterThan(0);
      }
    }
  });
});
