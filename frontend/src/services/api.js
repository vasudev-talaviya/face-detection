/**
 * API endpoint functions — all backend calls go through here.
 * Uses the shared request() client from apiClient.js.
 */
import { request } from './apiClient';

// ── Health ──
export const checkHealth = () => request("/health");

// ── Face Detection ──
export const detectFaces = (image) =>
  request("/faces/detect", { method: "POST", body: JSON.stringify({ image }) });

// ── Attendance ──
export const scanAttendance = (image) =>
  request("/attendance/scan", { method: "POST", body: JSON.stringify({ image }) });

export const submitAttendance = (entries, imageContext = "upload") =>
  request("/attendance", {
    method: "POST",
    body: JSON.stringify({ entries, image_context: imageContext }),
  });

export const getTodayAttendance = () => request("/attendance/today");

export const getAttendanceByDate = (date) =>
  request(`/attendance?date=${date}`);

export const getCorrections = () => request("/attendance/corrections");

export const getUserHistory = (userId) => request(`/attendance/user/${userId}`);

// ── Users ──
export const registerUser = (name, image) =>
  request("/users", {
    method: "POST",
    body: JSON.stringify({ name, image }),
  });

export const listUsers = () => request("/users");

export const updateUser = (userId, name, image = null) => {
  const body = { name };
  if (image) body.image = image;
  return request(`/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
};

export const deleteUser = (userId) =>
  request(`/users/${userId}`, { method: "DELETE" });
