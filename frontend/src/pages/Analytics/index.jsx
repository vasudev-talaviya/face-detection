/**
 * Analytics Page — Correction analytics and confused identity reports.
 * Uses: Loader3D component and reusable UI patterns.
 */
import { useState, useEffect } from "react";
import {
  BarChart3,
  AlertTriangle,
  TrendingUp,
  RefreshCw,
  ShieldAlert,
  ArrowRight,
  PieChart,
} from "lucide-react";
import { getCorrections } from "../../services/api";
import { Loader3D } from "../../components/common";

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getCorrections();
      setData(res.data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <Loader3D text="Loading analytics..." />;
  }

  if (error) {
    return (
      <div role="alert" className="alert alert-error shadow-lg fade-in">
        <AlertTriangle className="w-5 h-5" />
        <span>{error}</span>
        <button className="btn btn-ghost btn-xs" onClick={fetchData}>
          Retry
        </button>
      </div>
    );
  }

  const {
    total_corrections = 0,
    total_attendance = 0,
    correction_rate = 0,
    most_confused = [],
    corrections = [],
  } = data || {};

  return (
    <div className="space-y-6 fade-in">
      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          {
            title: "Total Attendance",
            value: total_attendance,
            icon: <TrendingUp className="w-7 h-7" />,
            color: "text-primary",
            bg: "bg-primary/10",
          },
          {
            title: "Total Corrections",
            value: total_corrections,
            icon: <ShieldAlert className="w-7 h-7" />,
            color: "text-warning",
            bg: "bg-warning/10",
          },
          {
            title: "Correction Rate",
            value: `${correction_rate}%`,
            icon: <BarChart3 className="w-7 h-7" />,
            color: correction_rate > 10 ? "text-error" : "text-success",
            bg: correction_rate > 10 ? "bg-error/10" : "bg-success/10",
          },
        ].map((s, i) => (
          <div key={i} className="stat-glow">
            <div className="glass-card p-5 relative z-10 hover:shadow-2xl transition-shadow">
              <div
                className={`w-12 h-12 rounded-xl ${s.bg} flex items-center justify-center mb-3`}
              >
                <div className={s.color}>{s.icon}</div>
              </div>
              <span className="text-xs uppercase tracking-wider opacity-50 font-semibold">
                {s.title}
              </span>
              <p className={`text-3xl font-extrabold mt-1 ${s.color}`}>
                {s.value}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Most Confused */}
      {most_confused.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-warning" />
            Most Confused Identities
          </h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {most_confused.map((m, i) => (
              <div
                key={i}
                className="card bg-base-200/60 backdrop-blur-sm p-5 shadow-sm hover:shadow-lg border border-base-content/5 hover-lift transition-all"
              >
                <p className="font-bold text-base mb-1">{m.name}</p>
                <p className="text-xs opacity-60 mb-3 font-medium uppercase tracking-wide">
                  Misidentified {m.count} time{m.count !== 1 ? "s" : ""}
                </p>
                <div className="flex flex-wrap gap-2">
                  {(m.corrected_to || []).map((c, j) => (
                    <span
                      key={j}
                      className="badge badge-primary badge-outline badge-sm font-semibold flex items-center gap-1 shadow-sm"
                    >
                      <ArrowRight className="w-3 h-3" /> {c}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent corrections log */}
      <div className="glass-card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold flex items-center gap-2">
            <PieChart className="w-5 h-5 text-secondary" />
            Recent Corrections
          </h3>
          <button
            className="btn btn-ghost btn-xs gap-1"
            onClick={fetchData}
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>

        {corrections.length === 0 ? (
          <div className="text-center py-10 opacity-50">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No corrections recorded yet.</p>
            <p className="text-xs mt-1">
              Corrections help the AI learn and improve accuracy.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-base-content/5 shadow-md">
            <table className="table table-zebra w-full bg-base-100">
              <thead className="bg-base-200/50 text-base-content/70">
                <tr>
                  <th className="rounded-tl-xl">#</th>
                  <th>Original</th>
                  <th>Corrected To</th>
                  <th>Confidence</th>
                  <th className="rounded-tr-xl">Time</th>
                </tr>
              </thead>
              <tbody>
                {corrections.map((c, i) => (
                  <tr
                    key={i}
                    className="hover hover:bg-base-200/50 transition-colors group"
                  >
                    <td className="opacity-40 text-xs">{i + 1}</td>
                    <td>
                      <span className="badge badge-error badge-sm">
                        {c.original_prediction || "Unknown"}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success badge-sm">
                        {c.corrected_to || "—"}
                      </span>
                    </td>
                    <td className="text-xs font-mono">
                      {(c.original_confidence || 0).toFixed(1)}%
                    </td>
                    <td className="text-xs opacity-70">
                      {c.timestamp || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
