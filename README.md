# XSS-i

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bug Hunting and URL Mining</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <h1>Bug Hunting and URL Mining</h1>
    <p>Use this tool for mining URLs from the Wayback Machine and bug hunting (CVE-2024-32760).</p>
  </header>

  <div class="container">
    <!-- Wayback Machine URL Miner Section -->
    <section class="section">
      <h2>Wayback Machine URL Miner</h2>
      <form id="wayback-form">
        <label for="domain">Domain Name:</label>
        <input type="text" id="domain" placeholder="example.com">
        <label for="proxy">Proxy (Optional):</label>
        <input type="text" id="proxy" placeholder="http://proxy-address">
        <label for="placeholder">Placeholder for Query Parameters:</label>
        <input type="text" id="placeholder" placeholder="xss<>">
        <button type="submit">Fetch & Clean URLs</button>
      </form>
      <div id="wayback-result"></div>
    </section>

    <!-- CVE-2024-32760 Bug Hunting Section -->
    <section class="section">
      <h2>CVE-2024-32760 Bug Hunting</h2>
      <form id="bug-hunt-form">
        <label for="cve-domain">Target Domain:</label>
        <input type="text" id="cve-domain" placeholder="example.com">
        <label for="cve-proxy">Proxy (Optional):</label>
        <input type="text" id="cve-proxy" placeholder="http://proxy-address">
        <button type="submit">Start Bug Hunt</button>
      </form>
      <div id="bug-hunt-result"></div>
    </section>
  </div>

  <footer>
    <p>&copy; 2024 Your Company Name. All Rights Reserved.</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>
