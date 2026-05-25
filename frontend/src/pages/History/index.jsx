/**
 * History Page — View attendance records by date.
 * Uses: useToast hook + ConfidenceBar, StatusBadge, ToastContainer, Loader3D components.
 */
import { useState, useEffect, useCallback } from "react";
import { CalendarDays, Clock, RefreshCw, ClipboardList } from "lucide-react";
import { getTodayAttendance, getAttendanceByDate } from "../../services/api";
import { Loader3D, ToastContainer, ConfidenceBar, StatusBadge } from "../../components/common";
import { useToast } from "../../hooks";

export default function History() {
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const fetchAttendance = useCallback(
    async (targetDate) => {
      setLoading(true);
      toast.clearToast();
      try {
        const today = new Date().toISOString().split("T")[0];
        const res =
          targetDate === today
            ? await getTodayAttendance()
            : await getAttendanceByDate(targetDate);
        setData(res.data);
      } catch (e) {
        toast.setError(e.message);
      } finally {
        setLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  useEffect(() => {
    fetchAttendance(date);
  }, [date, fetchAttendance]);

  const records = data?.records || [];

  return (
    <div className="space-y-6 fade-in">
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
          <CalendarDays className="w-5 h-5 text-primary" />
          Attendance History
        </h2>
        <p className="text-xs opacity-50 mb-5">
          View attendance records by date
        </p>

        <div className="flex flex-wrap gap-3 items-end mb-6">
          <div className="form-control">
            <label className="label">
              <span className="label-text font-medium">Select Date</span>
            </label>
            <input
              type="date"
              className="input input-bordered input-sm"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <button
            className="btn btn-ghost btn-sm gap-2"
            onClick={() => fetchAttendance(date)}
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>

        {loading ? (
          <Loader3D text="Loading records..." />
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="stat-glow">
                <div className="stat bg-base-200/80 backdrop-blur-md rounded-2xl shadow-lg border border-base-content/5 relative z-10 hover-lift">
                  <div className="stat-figure text-primary">
                    <CalendarDays className="w-8 h-8" />
                  </div>
                  <div className="stat-title text-xs font-semibold uppercase tracking-wider">
                    Date
                  </div>
                  <div className="stat-value text-xl">
                    {data?.date || date}
                  </div>
                </div>
              </div>
              <div className="stat-glow">
                <div className="stat bg-base-200/80 backdrop-blur-md rounded-2xl shadow-lg border border-base-content/5 relative z-10 hover-lift">
                  <div className="stat-figure text-success">
                    <ClipboardList className="w-8 h-8" />
                  </div>
                  <div className="stat-title text-xs font-semibold uppercase tracking-wider">
                    Total Present
                  </div>
                  <div className="stat-value text-3xl text-primary">
                    {data?.count ?? 0}
                  </div>
                </div>
              </div>
            </div>

            {records.length === 0 ? (
              <div className="text-center py-10 opacity-50">
                <ClipboardList className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">No attendance records for this date.</p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-base-content/5 shadow-md">
                <table className="table table-zebra w-full bg-base-100">
                  <thead className="bg-base-200/50 text-base-content/70">
                    <tr>
                      <th className="rounded-tl-xl">#</th>
                      <th>Name</th>
                      <th>Confidence</th>
                      <th>Time</th>
                      <th className="rounded-tr-xl">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => (
                      <tr
                        key={i}
                        className="hover hover:bg-base-200/50 transition-colors group"
                      >
                        <td className="opacity-40 text-xs">{i + 1}</td>
                        <td className="font-medium">{r.name}</td>
                        <td>
                          <ConfidenceBar value={r.confidence || 0} />
                        </td>
                        <td className="text-xs opacity-70">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {r.timestamp || "—"}
                          </span>
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
          </>
        )}
      </div>

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
