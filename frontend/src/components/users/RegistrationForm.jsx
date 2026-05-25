/**
 * RegistrationForm — Name input + register/update button with face detection preview.
 *
 * @param {string} regName - Current name input value
 * @param {function} setRegName - Name setter
 * @param {boolean} regLoading - Whether registration is in progress
 * @param {string|null} rawImage - Raw captured image (needed for new registrations)
 * @param {string|null} previewImg - Detection preview image
 * @param {object|null} editUser - User being edited (null for new registration)
 * @param {function} onRegister - Register/update callback
 * @param {function} onCancelEdit - Cancel edit mode callback
 * @param {Array} users - List of existing users for datalist autocomplete
 */
import { UserPlus, Edit2, Save, Loader2 } from "lucide-react";
import { Loader3D } from "../common";

export default function RegistrationForm({
  regName,
  setRegName,
  regLoading,
  rawImage,
  previewImg,
  editUser,
  onRegister,
  onCancelEdit,
  users,
}) {
  const showForm = rawImage || editUser;

  return (
    <div className="glass-card p-6">
      <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
        {editUser ? (
          <Edit2 className="w-5 h-5 text-primary" />
        ) : (
          <UserPlus className="w-5 h-5 text-primary" />
        )}
        {editUser ? "Update User" : "Register New Face"}
      </h2>
      <p className="text-xs opacity-50 mb-5">
        {editUser
          ? "Change name or upload a new photo to add a face template"
          : "Upload a photo or capture from camera to register a new identity"}
      </p>

      {/* Detection preview */}
      {previewImg && (
        <div className="mb-4">
          <img
            src={previewImg}
            alt="Detected face"
            className="rounded-xl max-h-[200px] border border-base-content/10 shadow-md"
          />
        </div>
      )}

      {/* Loading indicator */}
      {regLoading && <Loader3D text="Processing face on backend..." />}

      {/* Name input & register */}
      {showForm && (
        <div className="flex flex-col gap-3 slide-up mt-4">
          <div className="form-control">
            <label className="label">
              <span className="label-text font-medium">Name</span>
              {!editUser && (
                <span className="label-text-alt opacity-70">
                  Type new or pick existing
                </span>
              )}
            </label>
            <input
              type="text"
              list="registered-names"
              className="input input-bordered input-sm"
              placeholder="Enter person's name"
              value={regName}
              onChange={(e) => setRegName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onRegister()}
            />
            <datalist id="registered-names">
              {users.map((u) => (
                <option key={u.id} value={u.name} />
              ))}
            </datalist>
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-primary btn-sm flex-1 gap-2"
              onClick={onRegister}
              disabled={!regName.trim() || regLoading}
            >
              {regLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : editUser ? (
                <Save className="w-4 h-4" />
              ) : (
                <UserPlus className="w-4 h-4" />
              )}
              {editUser ? "Update" : "Register"}
            </button>
            {editUser && (
              <button className="btn btn-ghost btn-sm" onClick={onCancelEdit}>
                Cancel
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
