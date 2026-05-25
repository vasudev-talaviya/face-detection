/**
 * Scanner Page — Face detection and attendance scanning.
 * Composes: useCamera, useToast hooks + CameraPreview, CameraControls,
 * DetectionResult, FaceGrid, Loader3D, ToastContainer components.
 */
import { useState, useEffect, useCallback } from "react";
import { ScanLine, Upload } from "lucide-react";
import { useCamera } from "../../hooks";
import { useToast } from "../../hooks";
import { scanAttendance, submitAttendance, listUsers } from "../../services/api";
import { Loader3D, ToastContainer } from "../../components/common";
import { CameraPreview, CameraControls } from "../../components/camera";
import { DetectionResult, FaceGrid } from "../../components/scanner";

export default function Scanner() {
  const camera = useCamera({ facingMode: "user", width: 640, height: 480 });
  const toast = useToast();

  const [loading, setLoading] = useState(false);
  const [autoScan, setAutoScan] = useState(false);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [registeredUsers, setRegisteredUsers] = useState([]);
  const [corrections, setCorrections] = useState({});

  // Fetch registered users for the correction dropdown
  useEffect(() => {
    listUsers()
      .then((r) => setRegisteredUsers(r.data || []))
      .catch(() => {});
  }, []);

  // ── Scan ──
  // Note: toast.clearToast/setError are stable refs (useState setters + useCallback),
  // so they don't need to be in the dependency array.
  const scan = useCallback(
    async (imageData) => {
      setLoading(true);
      toast.clearToast();
      setCorrections({});
      try {
        const res = await scanAttendance(imageData);
        setResult(res.data);
      } catch (e) {
        toast.setError(e.message);
      } finally {
        setLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const handleCapture = useCallback(() => {
    const frame = camera.captureFrame();
    if (frame) scan(frame);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scan]);

  const handleUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => scan(reader.result);
    reader.readAsDataURL(file);
  };

  // ── Auto Scan Loop ──
  useEffect(() => {
    let timeoutId;
    if (autoScan && camera.streaming && !loading) {
      timeoutId = setTimeout(() => {
        handleCapture();
      }, 1500);
    }
    return () => clearTimeout(timeoutId);
  }, [autoScan, camera.streaming, loading, handleCapture]);

  // ── Corrections ──
  const handleCorrection = (idx, field, value) => {
    setCorrections((prev) => ({
      ...prev,
      [idx]: { ...prev[idx], [field]: value },
    }));
  };

  // ── Submit ──
  const handleSubmit = async () => {
    if (!result?.faces?.length) return;
    setSubmitting(true);
    toast.clearToast();
    try {
      const entries = result.faces.map((face, i) => {
        const correction = corrections[i];
        const corrected =
          correction?.user_id &&
          correction.user_id !== (face.user_id || "");
        const selectedUser = registeredUsers.find(
          (u) => u.id === correction?.user_id
        );
        return {
          user_id: correction?.user_id || face.user_id || null,
          final_name: corrected
            ? selectedUser?.name || face.name || "Unknown"
            : face.name || "Unknown",
          original_prediction: face.name || null,
          confidence: face.confidence || 0,
          was_corrected: corrected,
          face_box: face.box || null,
        };
      });
      const res = await submitAttendance(entries);
      toast.setMsg(res.message || "Attendance submitted!");
    } catch (e) {
      toast.setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStartCamera = () => {
    camera.startCamera();
    setResult(null);
    toast.clearToast();
  };

  const faces = result?.faces || [];
  const fileRef = { current: null };

  return (
    <div className="space-y-6 fade-in">
      {/* Controls */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
          <ScanLine className="w-5 h-5 text-primary" />
          Face Scanner
        </h2>
        <p className="text-xs opacity-50 mb-5">
          Scan faces from camera or upload an image to mark attendance
        </p>

        <div className="flex flex-wrap gap-3 mb-4">
          <CameraControls
            streaming={camera.streaming}
            loading={loading}
            onStart={handleStartCamera}
            onStop={camera.stopCamera}
            onCapture={handleCapture}
            autoScan={{ enabled: autoScan, onChange: setAutoScan }}
            startLabel="Start Camera"
            captureLabel="Capture & Scan"
          />

          <button
            className="btn btn-secondary btn-sm gap-2"
            onClick={() => fileRef.current?.click()}
            disabled={loading}
          >
            <Upload className="w-4 h-4" /> Upload Image
          </button>
          <input
            ref={(el) => (fileRef.current = el)}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleUpload}
          />
        </div>

        {/* Video preview */}
        <CameraPreview
          webcamRef={camera.webcamRef}
          streaming={camera.streaming}
          videoConstraints={camera.videoConstraints}
          error={camera.error}
          onUserMediaError={camera.onUserMediaError}
          showAutoScanIndicator={loading && autoScan}
        />

        {/* Loading overlay */}
        {loading && !autoScan && <Loader3D text="Analyzing faces..." />}
      </div>

      {/* Annotated image */}
      <DetectionResult annotatedImage={result?.annotated_image} />

      {/* Detected faces */}
      <FaceGrid
        faces={faces}
        corrections={corrections}
        onCorrection={handleCorrection}
        registeredUsers={registeredUsers}
        submitting={submitting}
        onSubmit={handleSubmit}
        onReset={() => {
          setResult(null);
          setCorrections({});
          toast.clearToast();
        }}
      />

      {/* Toasts */}
      <ToastContainer
        error={toast.error}
        msg={toast.msg}
        onClearError={() => toast.setError("")}
        onClearMsg={() => toast.setMsg("")}
      />
    </div>
  );
}
