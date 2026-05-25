/**
 * DetectionResult — Displays the annotated detection image.
 *
 * @param {string} annotatedImage - Base64 image data
 */
import { CheckCircle2 } from "lucide-react";

export default function DetectionResult({ annotatedImage }) {
  if (!annotatedImage) return null;

  return (
    <div className="glass-card p-4 fade-in">
      <h3 className="font-semibold mb-3 flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4 text-success" />
        Detection Result
      </h3>
      <img
        src={annotatedImage}
        alt="Annotated detection"
        className="w-full rounded-xl border border-base-content/10"
      />
    </div>
  );
}
