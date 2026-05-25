import unittest

from app.main import app


class APIRouteNamingTest(unittest.TestCase):
    def test_openapi_exposes_resource_oriented_routes(self) -> None:
        documented_paths = set(app.openapi()["paths"])

        self.assertIn("/api/admin/faces/detect", documented_paths)
        self.assertIn("/api/admin/users", documented_paths)
        self.assertIn("/api/admin/attendance/scan", documented_paths)
        self.assertIn("/api/admin/attendance", documented_paths)
        self.assertNotIn("/api/detect", documented_paths)
        self.assertNotIn("/api/register", documented_paths)
        self.assertNotIn("/api/attendance/detect", documented_paths)
        self.assertNotIn("/api/attendance/submit", documented_paths)
        self.assertNotIn("/api/attendance/history", documented_paths)


if __name__ == "__main__":
    unittest.main()
