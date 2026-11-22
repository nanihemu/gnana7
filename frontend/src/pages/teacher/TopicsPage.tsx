import { useState } from 'react'
import { api, errMsg, useFetch, useMutate } from '../../hooks'

interface Topic {
  id: number
  teacher: number
  teacher_name: string
  subject: number
  subject_name: string
  school_class: number
  title: string
  description: string
  material_file: string | null
  quiz_generated: boolean
  video_generated: boolean
  created_at: string
}

export default function TopicsPage() {
  const list = useFetch<Topic[]>('/topics/')
  const subjects = useFetch<{ id: number; name: string }[]>('/subjects/')
  const classes = useFetch<{ id: number; name: string; section: string }[]>('/classes/')
  const create = useMutate<Topic>('/topics/')
  const indexAll = useMutate<{ indexed: number; total: number }>('/index/', 'post')

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [subject, setSubject] = useState('')
  const [schoolClass, setSchoolClass] = useState('')
  const [busyTopic, setBusyTopic] = useState<number | null>(null)
  const [feedback, setFeedback] = useState('')

  function makeTopic(e: React.FormEvent) {
    e.preventDefault()
    const done = async () => {
      const ok = await create.run({
        title,
        description,
        subject: parseInt(subject, 10),
        school_class: parseInt(schoolClass, 10),
      })
      if (ok) {
        setTitle('')
        setDescription('')
        setSubject('')
        setSchoolClass('')
        list.reload()
      }
    }
    void done()
  }

  async function generateQuiz(t: Topic) {
    setBusyTopic(t.id)
    setFeedback('')
    try {
      const { data } = await api.post<{
        status: string
        questions_created: number
        error: string | null
      }>(`/quiz/generate/${t.id}/`)
      setFeedback(
        data.error
          ? `Quiz generation for "${t.title}" failed: ${data.error}`
          : `Quiz for "${t.title}": ${data.questions_created} question(s) generated (${data.status}).`,
      )
      list.reload()
    } catch (e) {
      setFeedback(`Failed: ${errMsg(e)}`)
    } finally {
      setBusyTopic(null)
    }
  }

  async function requestVideo(t: Topic) {
    setBusyTopic(t.id)
    try {
      const { data } = await api.post<{ status: string }>(`/video/${t.id}/`)
      setFeedback(`Video job for "${t.title}" → ${data.status}.`)
      list.reload()
    } catch (e) {
      setFeedback(`Failed: ${errMsg(e)}`)
    } finally {
      setBusyTopic(null)
    }
  }

  async function reindex() {
    setFeedback('')
    const res = await indexAll.run({})
    if (res) setFeedback(`RAG index refreshed: ${res.indexed}/${res.total} topics indexed.`)
  }

  return (
    <div>
      <h1>Topics &amp; AI Content</h1>

      <form className="card form" style={{ maxWidth: 560 }} onSubmit={makeTopic}>
        <h3>Post a topic</h3>
        <label>Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Photosynthesis" required />
        <label>Description / material</label>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} required />
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Subject</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)} required>
              <option value="">Select…</option>
              {(subjects.data || []).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Class</label>
            <select value={schoolClass} onChange={(e) => setSchoolClass(e.target.value)} required>
              <option value="">Select…</option>
              {(classes.data || []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.section}
                </option>
              ))}
            </select>
          </div>
        </div>
        {create.error && <div className="alert error">{create.error}</div>}
        <div className="actions">
          <button className="btn" type="submit" disabled={create.busy}>
            Post topic
          </button>
          <button className="btn secondary" type="button" onClick={() => void reindex()} disabled={indexAll.busy}>
            Re-index for RAG
          </button>
        </div>
      </form>

      <div className="row" style={{ marginTop: 20 }}>
        <h2 style={{ margin: 0 }}>Topics</h2>
      </div>
      {indexAll.error && <div className="alert error">{indexAll.error}</div>}
      {feedback && <div className="alert success">{feedback}</div>}

      {list.error && <div className="alert error">{list.error}</div>}
      {list.loading && <p className="muted">Loading…</p>}
      {(list.data || []).length === 0 && !list.loading && (
        <div className="card empty">No topics yet — post your first one above.</div>
      )}

      <div className="grid cols-2" style={{ marginTop: 12 }}>
        {(list.data || []).map((t) => (
          <div key={t.id} className="card">
            <div className="row" style={{ marginBottom: 6 }}>
              <h3 style={{ margin: 0 }}>{t.title}</h3>
              <span className="badge gray" style={{ marginLeft: 'auto' }}>
                {t.subject_name}
              </span>
            </div>
            <p className="muted" style={{ margin: '0 0 10px' }}>
              {t.description}
            </p>
            <div className="row" style={{ marginBottom: 10 }}>
              {t.quiz_generated ? (
                <span className="badge green">Quiz ready</span>
              ) : (
                <span className="badge gray">No quiz</span>
              )}
              {t.video_generated ? (
                <span className="badge green">Video ready</span>
              ) : (
                <span className="badge gray">No video</span>
              )}
            </div>
            <div className="row">
              <button className="btn sm" disabled={busyTopic === t.id} onClick={() => void generateQuiz(t)}>
                {busyTopic === t.id ? 'Working…' : 'Generate AI quiz'}
              </button>
              <button className="btn sm secondary" disabled={busyTopic === t.id} onClick={() => void requestVideo(t)}>
                Request avatar video
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
