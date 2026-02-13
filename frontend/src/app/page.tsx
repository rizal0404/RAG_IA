"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type DocumentItem = {
  id: number;
  filename: string;
  type: string;
  uploaded_at: string;
  source_unit?: string;
  year?: number;
};

type Citation = {
  filename: string;
  page?: number;
  snippet: string;
};

export default function Home() {
  const [tab, setTab] = useState<"upload" | "library" | "chat" | "generate">("upload");

  return (
    <main className={styles.page}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>Audit AI Assistant</div>
        <NavButton label="Upload" active={tab === "upload"} onClick={() => setTab("upload")} />
        <NavButton label="Library" active={tab === "library"} onClick={() => setTab("library")} />
        <NavButton label="Chat RAG" active={tab === "chat"} onClick={() => setTab("chat")} />
        <NavButton label="Generate Draft" active={tab === "generate"} onClick={() => setTab("generate")} />
      </aside>
      <section className={styles.content}>
        {tab === "upload" && <UploadPane />}
        {tab === "library" && <LibraryPane />}
        {tab === "chat" && <ChatPane />}
        {tab === "generate" && <GeneratePane />}
      </section>
    </main>
  );
}

function NavButton({ label, active, onClick }: { label: string; active?: boolean; onClick: () => void }) {
  return (
    <button className={`${styles.navButton} ${active ? styles.navActive : ""}`} onClick={onClick}>
      {label}
    </button>
  );
}

function UploadPane() {
  const [file, setFile] = useState<File | null>(null);
  const [sourceUnit, setSourceUnit] = useState("");
  const [year, setYear] = useState("");
  const [tags, setTags] = useState('{"process":"audit"}');
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setStatus("Pilih file PDF/DOCX terlebih dahulu.");
      return;
    }
    const form = new FormData();
    form.append("file", file);
    if (sourceUnit) form.append("source_unit", sourceUnit);
    if (year) form.append("year", year);
    if (tags) form.append("tags", tags);
    setLoading(true);
    setStatus("Uploading...");
    try {
      const res = await fetch(`${API_BASE}/api/ingest`, { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setStatus(`Sukses. document_id=${data.document_id}`);
      setFile(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setStatus("Gagal: " + message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2>Upload & Tagging</h2>
        <p>PDF/DOCX disimpan lokal → chunk → embedding → FAISS</p>
      </div>
      <div className={styles.formGrid}>
        <label className={styles.label}>
          Dokumen
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className={styles.input}
          />
        </label>
        <label className={styles.label}>
          Source Unit
          <input value={sourceUnit} onChange={(e) => setSourceUnit(e.target.value)} className={styles.input} />
        </label>
        <label className={styles.label}>
          Tahun
          <input value={year} onChange={(e) => setYear(e.target.value)} className={styles.input} />
        </label>
        <label className={styles.label}>
          Tags (JSON)
          <textarea value={tags} onChange={(e) => setTags(e.target.value)} className={styles.textarea} rows={3} />
        </label>
      </div>
      <button className={styles.primary} onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {status && <p className={styles.status}>{status}</p>}
    </div>
  );
}

function LibraryPane() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/documents`);
      const data = await res.json();
      setDocs(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2>Library Dokumen</h2>
        <p>Metadata tersimpan di SQLite. Klik refresh jika baru upload.</p>
        <button className={styles.secondary} onClick={fetchDocs} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>
      <div className={styles.table}>
        <div className={styles.tableHead}>
          <span>Nama</span>
          <span>Tipe</span>
          <span>Unit</span>
          <span>Tahun</span>
          <span>Uploaded</span>
        </div>
        {docs.map((d) => (
          <div key={d.id} className={styles.tableRow}>
            <span>{d.filename}</span>
            <span>{d.type}</span>
            <span>{d.source_unit || "-"}</span>
            <span>{d.year || "-"}</span>
            <span>{new Date(d.uploaded_at).toLocaleString()}</span>
          </div>
        ))}
        {!docs.length && <div className={styles.empty}>Belum ada dokumen.</div>}
      </div>
    </div>
  );
}

function ChatPane() {
  const [question, setQuestion] = useState("Apa objective audit procurement?");
  const [answer, setAnswer] = useState("");
  const [cites, setCites] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setCites([]);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user: "demo", query: question }),
      });
      const data = await res.json();
      setAnswer(data.answer);
      setCites(data.citations || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setAnswer("Gagal: " + message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2>Chat RAG</h2>
        <p>Jawaban berbasis dokumen dengan kutipan otomatis.</p>
      </div>
      <textarea
        className={styles.textarea}
        rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Tulis pertanyaan audit..."
      />
      <button className={styles.primary} onClick={ask} disabled={loading}>
        {loading ? "Memproses..." : "Tanya"}
      </button>
      {answer && (
        <div className={styles.answerBox}>
          <div className={styles.answerLabel}>Jawaban</div>
          <p>{answer}</p>
          {!!cites.length && (
            <div className={styles.citations}>
              {cites.map((c, idx) => (
                <div key={idx} className={styles.citationItem}>
                  <strong>{c.filename}</strong> — page {c.page || "?"}
                  <div className={styles.snippet}>{c.snippet}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function GeneratePane() {
  const [scope, setScope] = useState("Procurement PT Semen Tonasa");
  const [criteria, setCriteria] = useState("SOP Procurement, ISO 9001");
  const [period, setPeriod] = useState("FY2024");
  const [risk, setRisk] = useState("Kepatuhan kontrak, conflict of interest");
  const [result, setResult] = useState("");
  const [cites, setCites] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    setResult("");
    setCites([]);
    try {
      const res = await fetch(`${API_BASE}/api/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode: "draft_audit_plan",
          user: "demo",
          payload: { scope, criteria, period, risk },
        }),
      });
      const data = await res.json();
      setResult(data.content);
      setCites(data.citations || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setResult("Gagal: " + message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2>Generate Draft Program Audit</h2>
        <p>Scope + criteria + risk → draft plan dengan evidence map.</p>
      </div>
      <div className={styles.formGrid}>
        <label className={styles.label}>
          Scope
          <input value={scope} onChange={(e) => setScope(e.target.value)} className={styles.input} />
        </label>
        <label className={styles.label}>
          Criteria
          <input value={criteria} onChange={(e) => setCriteria(e.target.value)} className={styles.input} />
        </label>
        <label className={styles.label}>
          Period
          <input value={period} onChange={(e) => setPeriod(e.target.value)} className={styles.input} />
        </label>
        <label className={styles.label}>
          Risk list
          <textarea value={risk} onChange={(e) => setRisk(e.target.value)} rows={3} className={styles.textarea} />
        </label>
      </div>
      <button className={styles.primary} onClick={generate} disabled={loading}>
        {loading ? "Generating..." : "Generate Draft"}
      </button>
      {result && (
        <div className={styles.answerBox}>
          <div className={styles.answerLabel}>Draft</div>
          <p>{result}</p>
          {!!cites.length && (
            <div className={styles.citations}>
              {cites.map((c, idx) => (
                <div key={idx} className={styles.citationItem}>
                  <strong>{c.filename}</strong> — page {c.page || "?"}
                  <div className={styles.snippet}>{c.snippet}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
