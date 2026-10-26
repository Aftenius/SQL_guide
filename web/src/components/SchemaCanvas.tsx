import { useEffect, useRef } from "react";
import rough from "roughjs";

export type SketchMode = "tables" | "join" | "group";

const ink = "#262626";
const blue = "rgba(186, 230, 253, 0.45)";
const green = "rgba(187, 247, 208, 0.45)";

export function SchemaCanvas({ mode }: { mode: SketchMode }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const parent = canvas?.parentElement;
    if (!canvas || !parent) return;

    const draw = () => {
      const width = parent.clientWidth;
      const height = parent.clientHeight;
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(width, 1) * ratio;
      canvas.height = Math.max(height, 1) * ratio;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.clearRect(0, 0, width, height);
      paint(rough.canvas(canvas), context, width, mode);
    };

    draw();
    const fontsReady = document.fonts.ready.then(draw);
    const observer = new ResizeObserver(draw);
    observer.observe(parent);
    return () => {
      void fontsReady.then(() => undefined);
      observer.disconnect();
    };
  }, [mode]);

  return <canvas ref={canvasRef} className="h-full w-full" aria-hidden="true" />;
}

function paint(
  pen: ReturnType<typeof rough.canvas>,
  context: CanvasRenderingContext2D,
  width: number,
  mode: SketchMode,
) {
  const cardWidth = Math.min(190, Math.max(120, width * 0.4));
  const left = 16;
  const top = 22;
  const right = Math.max(width - cardWidth - 16, left + cardWidth + 24);
  drawTable(pen, context, left, top, cardWidth, "users", ["id", "name", "age", "city"], blue);
  drawTable(pen, context, right, top, cardWidth, "orders", ["id", "user_id", "item", "amount"], green);
  if (mode === "join") drawJoin(pen, context, left + cardWidth, right, top);
  if (mode === "group") {
    context.font = "600 14px 'IBM Plex Sans', sans-serif";
    context.fillStyle = "#44403c";
    context.fillText("одна строка на группу", left, 196);
  }
}

function drawTable(
  pen: ReturnType<typeof rough.canvas>,
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  title: string,
  fields: string[],
  fill: string,
) {
  pen.rectangle(x, y, width, 150, {
    roughness: 1.5,
    stroke: ink,
    strokeWidth: 2,
    fill,
    fillStyle: "hachure",
  });
  pen.line(x, y + 32, x + width, y + 32, { stroke: ink, strokeWidth: 1.5 });
  context.font = "600 14px 'IBM Plex Sans', sans-serif";
  context.fillStyle = "#1c1917";
  context.fillText(title, x + 12, y + 22);
  context.font = "12px 'IBM Plex Mono', monospace";
  context.fillStyle = "#44403c";
  fields.forEach((field, index) => {
    context.fillText(field, x + 12, y + 54 + index * 22);
  });
}

function drawJoin(
  pen: ReturnType<typeof rough.canvas>,
  context: CanvasRenderingContext2D,
  fromX: number,
  toX: number,
  top: number,
) {
  const start: [number, number] = [fromX - 4, top + 54];
  const end: [number, number] = [toX + 4, top + 76];
  const bend: [number, number] = [(start[0] + end[0]) / 2, start[1] - 28];
  pen.curve([start, bend, end], { roughness: 1.6, stroke: "#b91c1c", strokeWidth: 2 });
  context.font = "600 12px 'IBM Plex Sans', sans-serif";
  context.fillStyle = "#7f1d1d";
  context.fillText("JOIN", bend[0] - 18, bend[1] + 4);
}
