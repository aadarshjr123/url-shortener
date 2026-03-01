import { useState } from "react"

const API_BASE = import.meta.env.VITE_API_URL

export default function App() {
  const [url, setUrl] = useState("")
  const [shortUrl, setShortUrl] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleShorten = async () => {
    setLoading(true)
    setError("")
    setShortUrl("")

    try {
      const res = await fetch(`${API_BASE}/shorten/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          original_url: url
        })
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || "Something went wrong")
      }

      const data = await res.json()
      setShortUrl(data.short_url)

    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={containerStyle}>
      <h1>URL Shortener</h1>

      <input
        style={inputStyle}
        type="text"
        placeholder="Enter long URL..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <button style={buttonStyle} onClick={handleShorten}>
        {loading ? "Shortening..." : "Shorten"}
      </button>

      {shortUrl && (
        <div style={{ marginTop: "20px" }}>
          <p>Short URL:</p>
          <a href={shortUrl} target="_blank">
            {shortUrl}
          </a>
        </div>
      )}

      {error && (
        <p style={{ color: "red", marginTop: "20px" }}>{error}</p>
      )}
    </div>
  )
}

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  marginTop: "100px",
  fontFamily: "Arial"
}

const inputStyle: React.CSSProperties = {
  width: "400px",
  padding: "10px",
  fontSize: "16px",
  marginBottom: "10px"
}

const buttonStyle: React.CSSProperties = {
  padding: "10px 20px",
  fontSize: "16px",
  cursor: "pointer"
}