/**
 * UsersList Page — User registration, management, and history.
 * Composes: useCamera, useToast hooks + CameraPreview, CameraControls,
 * RegistrationForm, UserCard, HistoryModal, ToastContainer components.
 */
import { useState, useEffect, useCallback } from "react";
import { Users, Loader2, Upload, Shield } from "lucide-react";
import { useCamera } from "../../hooks";
import { useToast } from "../../hooks";
import {
  listUsers,
  deleteUser,
  registerUser,
  detectFaces,
  updateUser,
  getUserHistory,
} from "../../services/api";
import { ToastContainer } from "../../components/common";
import { CameraPreview, CameraControls } from "../../components/camera";
import { RegistrationForm } from "../../components/users";
import { UserCard } from "../../components/users";
import { HistoryModal } from "../../components/users";

export default function UsersList() {
  const camera = useCamera({ facingMode: "user", width: 480, height: 360 });
  const toast = useToast();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Registration state
  const [regName, setRegName] = useState("");
  const [regLoading, setRegLoading] = useState(false);
  const [rawImage, setRawImage] = useState(null);
  const [previewImg, setPreviewImg] = useState(null);
  const fileRef = { current: null };

  // Edit state
  const [editUser, setEditUser] = useState(null);

  // History state
  const [historyUser, setHistoryUser] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listUsers();
      setUsers(res.data || []);
    } catch (e) {
      toast.setError(e.message);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // ── Delete ──
  const handleDelete = async (id, name) => {
    if (!confirm(`Delete user "${name}"?`)) return;
    try {
      await deleteUser(id);
      toast.setMsg(`Deleted "${name}"`);
      fetchUsers();
    } catch (e) {
      toast.setError(e.message);
    }
  };

  // ── Edit ──
  const handleEditClick = (u) => {
    setEditUser(u);
    setRegName(u.name);
    setRawImage(null);
    setPreviewImg(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleCancelEdit = () => {
    setEditUser(null);
    setRegName("");
    setRawImage(null);
    setPreviewImg(null);
  };

  // ── History ──
  const openHistoryModal = async (u) => {
    setHistoryUser(u);
    setHistoryData([]);
    document.getElementById("history_modal").showModal();
    setHistoryLoading(true);
    try {
      const res = await getUserHistory(u.id);
      setHistoryData(res.data?.records || []);
    } catch (e) {
      toast.setError(e.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  // ── Detect embedding from image ──
  const detectEmbedding = async (imageData) => {
    setRegLoading(true);
    toast.clearToast();
    setRawImage(null);
    try {
      const res = await detectFaces(imageData);
      const data = res.data || {};
      const faces = data.faces || [];
      if (faces.length === 0) {
        toast.setError("No face detected. Please try another image.");
        return;
      }
      if (faces.length > 1) {
        toast.setError(
          "Multiple faces detected. Please use an image with a single face."
        );
        return;
      }
      const face = faces[0];
      setPreviewImg(data.annotated_image || imageData);

      if (!face.is_new_face && face.name) {
        setRawImage(null);
        setRegName("");
        toast.setError(
          `This face is already registered as "${face.name}". You cannot register the same face again.`
        );
      } else {
        setRawImage(imageData);
        setRegName("");
        toast.setMsg("Unknown face detected! Enter a name to register.");
      }
    } catch (e) {
      toast.setError(e.message);
    } finally {
      setRegLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => detectEmbedding(reader.result);
    reader.readAsDataURL(file);
  };

  // Camera capture for registration
  const handleCamCapture = () => {
    const frame = camera.captureFrame();
    if (frame) {
      camera.stopCamera();
      detectEmbedding(frame);
    }
  };

  // ── Register ──
  const handleRegister = async () => {
    if (!regName.trim()) return;
    if (!editUser && !rawImage) return;

    setRegLoading(true);
    toast.clearToast();
    try {
      if (editUser) {
        const res = await updateUser(editUser.id, regName.trim(), rawImage);
        toast.setMsg(res.message || "Updated successfully!");
        setEditUser(null);
      } else {
        const res = await registerUser(regName.trim(), rawImage);
        toast.setMsg(res.message || "Registered successfully!");
      }
      setRegName("");
      setRawImage(null);
      setPreviewImg(null);
      fetchUsers();
    } catch (e) {
      toast.setError(e.message);
    } finally {
      setRegLoading(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-3 fade-in items-start">
      {/* Left Column: Registration */}
      <div className="lg:col-span-1 space-y-6 sticky top-24">
        <RegistrationForm
          regName={regName}
          setRegName={setRegName}
          regLoading={regLoading}
          rawImage={rawImage}
          previewImg={previewImg}
          editUser={editUser}
          onRegister={handleRegister}
          onCancelEdit={handleCancelEdit}
          users={users}
        />

        {/* Camera controls for registration */}
        <div className="glass-card p-4">
          <div className="flex flex-wrap gap-3 mb-4">
            <button
              className="btn btn-secondary btn-sm gap-2"
              onClick={() => fileRef.current?.click()}
              disabled={regLoading}
            >
              <Upload className="w-4 h-4" /> Upload Photo
            </button>
            <input
              ref={(el) => (fileRef.current = el)}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileUpload}
            />

            <CameraControls
              streaming={camera.streaming}
              loading={regLoading}
              onStart={camera.startCamera}
              onStop={camera.stopCamera}
              onCapture={handleCamCapture}
              startLabel="Use Camera"
              captureLabel="Capture"
            />
          </div>

          <CameraPreview
            webcamRef={camera.webcamRef}
            streaming={camera.streaming}
            videoConstraints={camera.videoConstraints}
            error={camera.error}
            onUserMediaError={camera.onUserMediaError}
          />
        </div>
      </div>

      {/* Right Column: Users List */}
      <div className="lg:col-span-2 space-y-6">
        {/* Toasts */}
        <ToastContainer
          error={toast.error}
          msg={toast.msg}
          onClearError={() => toast.setError("")}
          onClearMsg={() => toast.setMsg("")}
        />

        <div className="glass-card p-6 min-h-[600px]">
          <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
            <Users className="w-5 h-5 text-secondary" />
            Registered Users
            <span className="badge badge-secondary badge-sm">
              {users.length}
            </span>
          </h2>
          <p className="text-xs opacity-50 mb-5">
            Manage registered face templates
          </p>

          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-10 opacity-50">
              <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">No users registered yet.</p>
              <p className="text-xs mt-1">
                Upload a face image above to get started.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {users.map((u) => (
                <UserCard
                  key={u.id}
                  user={u}
                  onEdit={handleEditClick}
                  onDelete={handleDelete}
                  onHistory={openHistoryModal}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* History Modal */}
      <HistoryModal
        user={historyUser}
        records={historyData}
        loading={historyLoading}
      />
    </div>
  );
}
