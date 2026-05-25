/**
 * HistoryModal — Dialog modal showing a user's attendance history.
 *
 * @param {object|null} user - The user whose history to show
 * @param {Array} records - Attendance history records
 * @param {boolean} loading - Whether history is loading
 */
import { History, Clock, Loader2 } from "lucide-react";
import ConfidenceBar from "../common/ConfidenceBar";
import StatusBadge from "../common/StatusBadge";

export default function HistoryModal({ user, records, loading }) {
  return (
    <dialog id="history_modal" className="modal modal-bottom sm:modal-middle">
      <div className="modal-box glass-card border border-base-content/10 max-w-2xl">
        <h3 className="font-bold text-lg flex items-center gap-2 mb-2">
          <History className="w-5 h-5 text-info" />
          Attendance History
        </h3>
        <p className="text-sm opacity-60 mb-4">
          Records for{" "}
          <span className="font-bold text-primary">{user?.name}</span>
        </p>

        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : records.length === 0 ? (
          <div className="text-center py-8 opacity-50">
            <p>No attendance records found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-base-content/5 shadow-inner bg-base-200/50">
            <table className="table table-sm table-zebra w-full">
              <thead className="bg-base-300 text-base-content/70">
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Confidence</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r, i) => (
                  <tr
                    key={i}
                    className="hover hover:bg-base-100 transition-colors"
                  >
                    <td className="font-medium">{r.date}</td>
                    <td className="text-xs opacity-70">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.timestamp || "—"}
                      </span>
                    </td>
                    <td>
                      <ConfidenceBar value={r.confidence || 0} width="w-12" />
                    </td>
                    <td>
                      <StatusBadge wasCorrected={r.was_corrected} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="modal-action">
          <form method="dialog">
            <button className="btn">Close</button>
          </form>
        </div>
      </div>
    </dialog>
  );
}
