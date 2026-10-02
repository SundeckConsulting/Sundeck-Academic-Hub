import unittest
from academic_server import app, _check_rate_limit, _rate_limit_records


class ProductionReadinessTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_legal_page_serves_successfully(self):
        res = self.client.get('/legal')
        self.assertEqual(res.status_code, 200)
        content = res.get_data(as_text=True)
        res.close()
        self.assertIn("Privacy Policy", content)
        self.assertIn("Terms of Service", content)
        self.assertIn("GDPR", content)
        self.assertIn("SUNDECK Consulting", content)
        self.assertIn("Harald Düster", content)
        self.assertIn("Universitätsstraße 3", content)
        self.assertIn("56070 Koblenz", content)
        self.assertIn("info@sundeck-consulting.de", content)
        self.assertIn("0261-8996600", content)

    def test_legal_redirects(self):
        for path, target_anchor in [
            ('/privacy', '/legal#privacy'),
            ('/terms', '/legal#terms'),
            ('/gdpr', '/legal#gdpr')
        ]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 302, f"Failed for {path}")
            self.assertIn(target_anchor, res.headers.get('Location', ''))
            res.close()

    def test_security_headers_present(self):
        res = self.client.get('/legal')
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertEqual(res.headers.get("Permissions-Policy"), "geolocation=(), camera=(), microphone=(), payment=()")
        self.assertEqual(res.headers.get("Cross-Origin-Opener-Policy"), "same-origin")
        res.close()

    def test_api_404_json_error(self):
        res = self.client.get('/api/definitely-not-a-real-endpoint')
        self.assertEqual(res.status_code, 404)
        self.assertTrue(res.is_json)
        data = res.get_json()
        self.assertIn("error", data)

    def test_auth_rate_limiting(self):
        test_ip = "192.168.100.50"
        test_email = "ratelimit_test@example.com"
        
        # Test rate limiter directly
        key = f"otp_req_teacher:{test_ip}:{test_email}"
        # Clear any existing
        _rate_limit_records.pop(key, None)
        
        for _ in range(5):
            allowed = _check_rate_limit(key, max_attempts=5, window_seconds=600)
            self.assertTrue(allowed)
        
        # 6th attempt should be blocked
        blocked = _check_rate_limit(key, max_attempts=5, window_seconds=600)
        self.assertFalse(blocked)

    def test_favicon_served(self):
        res = self.client.get('/favicon.ico')
        self.assertEqual(res.status_code, 200)
        self.assertIn("image/x-icon", res.headers.get("Content-Type", ""))
        self.assertGreater(len(res.data), 0)
        self.assertIn("max-age=86400", res.headers.get("Cache-Control", ""))
        res.close()

    def test_robots_txt_served(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.headers.get("Content-Type", ""))
        content = res.get_data(as_text=True)
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn("Sitemap: https://hub.sundeck-consulting.de/sitemap.xml", content)
        self.assertIn("max-age=86400", res.headers.get("Cache-Control", ""))
        res.close()

    def test_sitemap_xml_served(self):
        res = self.client.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.headers.get("Content-Type", ""))
        content = res.get_data(as_text=True)
        self.assertIn("<urlset", content)
        self.assertIn("https://hub.sundeck-consulting.de/", content)
        self.assertIn("https://hub.sundeck-consulting.de/legal", content)
        self.assertIn("max-age=86400", res.headers.get("Cache-Control", ""))
        res.close()

    def test_homepage_seo_elements(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        content = res.get_data(as_text=True)
        res.close()

        # Meta description
        self.assertIn('<meta name="description"', content)
        self.assertIn('Sundeck Academic Hub', content)

        # Title & Canonical
        self.assertIn('<title>Sundeck Academic Hub', content)
        self.assertIn('<link rel="canonical" href="https://hub.sundeck-consulting.de/">', content)
        self.assertIn('lang="de"', content)

        # Open Graph & Twitter
        self.assertIn('property="og:title"', content)
        self.assertIn('property="og:description"', content)
        self.assertIn('property="og:image"', content)
        self.assertIn('name="twitter:card"', content)

        # Favicons
        self.assertIn('rel="icon" type="image/x-icon" href="/favicon.ico"', content)
        self.assertIn('rel="apple-touch-icon"', content)

        # Structured Data
        self.assertIn('application/ld+json', content)
        self.assertIn('SUNDECK Consulting', content)
        self.assertIn('Harald Düster', content)
        self.assertIn('56070', content)

        # Clickable Logo Link
        self.assertIn('href="https://hub.sundeck-consulting.de/"', content)
        self.assertIn('aria-label="Sundeck Academic Hub Startseite"', content)

    def test_cache_headers_on_static_assets(self):
        res = self.client.get('/assets/favicon-32x32.png')
        self.assertEqual(res.status_code, 200)
        self.assertIn("max-age=86400", res.headers.get("Cache-Control", ""))
        res.close()


if __name__ == '__main__':
    unittest.main()
