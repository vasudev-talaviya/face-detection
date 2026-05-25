/**
 * Centralized route configuration — single source of truth
 * Used by App.jsx for routing and Navbar for navigation tabs.
 */
export const routes = [
  { id: "scanner", path: "/scanner", label: "Scanner" },
  { id: "users", path: "/users", label: "Users" },
  { id: "history", path: "/history", label: "History" },
  { id: "analytics", path: "/analytics", label: "Analytics" },
];

/** Default redirect path */
export const DEFAULT_ROUTE = "/scanner";

