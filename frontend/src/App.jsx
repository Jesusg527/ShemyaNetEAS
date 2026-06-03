import { useState } from "react";
import "./App.css";
import { jsPDF } from "jspdf";

function App() {
  const [search, setSearch] = useState("");
  const [date, setDate] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ---------------------------
  // IP VALIDATION ONLY
  // ---------------------------
  const isValidIP = (value) => {
    const ipRegex =
      /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
    return ipRegex.test(value);
  };

  // ---------------------------
  // DATE FORMAT (POS STYLE)
  // ---------------------------
  const formatPOSDate = (dateString) => {
    if (!dateString) return "";

    const d = new Date(dateString);
    const pad = (n) => String(n).padStart(2, "0");

    return (
      `${pad(d.getMonth() + 1)}/${pad(d.getDate())}/${d.getFullYear()} ` +
      `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
    );
  };

  // ---------------------------
  // SEARCH
  // ---------------------------
  const handleSearch = async () => {
    setError("");
    setResults([]);

    const cleaned = search.trim();

    if (!cleaned) {
      setError("Enter IP address");
      return;
    }

    if (!date) {
      setError("Select a date");
      return;
    }

    // ❌ ONLY IP ALLOWED
    if (!isValidIP(cleaned)) {
      setError("Invalid IP address format");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("https://shemya-backend.onrender.com/lookup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          search: cleaned,
          date,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Server error");
        return;
      }

      setResults(data.results || []);
    } catch (err) {
      setError("Server not reachable");
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------
  // PDF RECEIPT
  // ---------------------------
  const downloadPDF = (item) => {
    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.text("SHEMYANET RECEIPT", 20, 20);

    doc.setFont("helvetica", "normal");

    doc.text(`Transaction ID: ${item.billingId}`, 20, 40);
    doc.text(`Access Code: ${item.userId}`, 20, 50);
    doc.text(`IP Address: ${item.ipAddress}`, 20, 60);
    doc.text(`MAC Address: ${item.macAddress}`, 20, 70);
    doc.text(`Plan: ${item.planName}`, 20, 80);
    doc.text(`Date: ${formatPOSDate(item.transactionDatetimeLocal)}`, 20, 90);
    doc.text(`TOTAL: $${item.amount}`, 20, 100);

    doc.save(`receipt_${item.billingId}.pdf`);
  };

  return (
    <div className="container">
      <h1 className="title">ShemyaNet Transaction Lookup</h1>

      {/* SEARCH */}
      <div className="search-box">
        <label className="search-label">Search Date</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />

        <input
          type="text"
          placeholder="Enter IP address only (e.g. 192.168.1.1)"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <button onClick={handleSearch}>Search</button>
      </div>

      {/* STATUS */}
      {loading && <p className="info">Loading...</p>}
      {error && <p className="error">{error}</p>}

      {/* RESULTS */}
      <div className="results">
        {results.length === 0 && !loading && !error && (
          <p className="info">No results found</p>
        )}

        {results.map((item, index) => (
          <div className="receipt" key={index}>
            <div className="receipt-header">
              <h2>SHEMYANET RECEIPT</h2>
              <p>Transaction Record</p>
            </div>

            <div className="divider" />

            <div className="row">
              <span>Transaction ID</span>
              <span>{item.billingId}</span>
            </div>

            <div className="row">
              <span>Access Code</span>
              <span>{item.userId}</span>
            </div>

            <div className="row">
              <span>IP</span>
              <span>{item.ipAddress}</span>
            </div>

            <div className="row">
              <span>MAC</span>
              <span>{item.macAddress}</span>
            </div>

            <div className="row">
              <span>Plan</span>
              <span>{item.planName}</span>
            </div>

            <div className="row">
              <span>Date</span>
              <span>{formatPOSDate(item.transactionDatetimeLocal)}</span>
            </div>

            <div className="divider" />

            <div className="total">
              <span>TOTAL</span>
              <span>${item.amount}</span>
            </div>

            <button className="btn" onClick={() => downloadPDF(item)}>
              Download Receipt
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;