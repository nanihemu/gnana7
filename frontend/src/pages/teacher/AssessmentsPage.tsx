import { useState } from 'react'
import { api, errMsg, useFetch, useMutate } from '../../hooks'

interface Assessment {
  id: number
  teacher: number
  teacher_name: string
  topic: number | null
  subject: number
  subject_name: string
  school_class: number
  title: string
  kind: string
  status: string
  total_marks: number
  duration_minutes: number | null
  is_ai_generated: boolean
  due_at: string | null
  created_at: string
}

interface Question {
  id: number
  text: string
  q_type: string
  options: string[]
  correct_index: number | null
  marks: number
}

export default function AssessmentsPage() {
  const list = useFetch<Assessment[]>('/assessments/')
  const topics = useFetch<{ id: number; title: string }[]>('/topics/')
  const subjects = useFetch<{ id: number; name: string }[]>('/subjects/')
  const classes = useFetch<{ id: number; name: string; section: string }[]>('/classes/')
  const create = useMutate<Assessment>('/assessments/')

  const [form, setForm] = useState({
    title: '',
    topic: '',
    subject: '',
    school_class: '',
    kind: 'quiz',
    status: 'draft',
    total_marks: '5',
    duration_minutes: '',
    due_at: '',
  })

  // Question editor per assessment
  const [questionFor, setQuestionFor] = useState<number | null>(null)
  const [questions, setQuestions] = useState<Record<number, Question[]>>({})
  const [qText, setQText] = useState('')
  const [qOptions, setQOptions] = useState('')
  const [qCorrect, setQCorrect] = useState('0')
  const [qMarks, setQMarks] = useState('1')
  const addQ = useMutate<Question>('/questions/')

  function submitAssessment(e: React.FormEvent) {
    e.preventDefault()
    const payload = {
      title: form.title,
      topic: form.topic ? parseInt(form.topic, 10) : null,
      subject: parseInt(form.subject, 10),
      school_class: parseInt(form.school_class, 10),
      kind: form.kind,
      status: form.status,
      total_marks: parseInt(form.total_marks, 10) || 0,
      duration_minutes: form.duration_minutes ? parseInt(form.duration_minutes, 10) : null,
      due_at: form.due_at || null,
    }
    const done = async () => {
      const ok = await create.run(payload)
      if (ok) {
        setForm({ title: '', topic: '', subject: '', school_class: '', kind: 'quiz', status: 'draft', total_marks: '5', duration_minutes: '', due_at: '' })
        list.reload()
      }
    }
    void done()
  }

  async function toggleQuestions(a: Assessment) {
    if (questionFor === a.id) {
      setQuestionFor(null)
      return
    }
    setQuestionFor(a.id)
    if (questions[a.id]) return
    try {
      const { data } = await api.get<Question[]>(`/questions/?assessment=${a.id}`)
      setQuestions((q) => ({ ...q, [a.id]: Array.isArray(data) ? data : [] }))
    } catch {
      setQuestions((q) => ({ ...q, [a.id]: [] }))
    }
  }

  async function submitQuestion(a: Assessment) {
    const options = qOptions
      .split('\n')
      .map((o) => o.trim())
      .filter(Boolean)
    const ok = await addQ.run({
      assessment: a.id,
      q_type: 'mcq',
      text: qText,
      options,
      correct_index: options.length ? parseInt(qCorrect, 10) || 0 : null,
      marks: parseInt(qMarks, 10) || 1,
    })
    if (ok) {
      setQText('')
      setQOptions('')
      setQCorrect('0')
      setQMarks('1')
      try {
        const { data } = await api.get<Question[]>(`/questions/?assessment=${a.id}`)
        setQuestions((q) => ({ ...q, [a.id]: data }))
      } catch {
        /* ignore */
      }
    }
  }

  if (list.loading || topics.loading || subjects.loading || classes.loading)
    return <p className="muted">Loading…</p>

  return (
    <div>
      <h1>Assessments</h1>

      <form className="card form" style={{ maxWidth: 620 }} onSubmit={submitAssessment}>
        <h3>Create assessment</h3>
        <label>Title</label>
        <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Photosynthesis quiz" required />
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Topic</label>
            <select value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })}>
              <option value="">—</option>
              {(topics.data || []).map((t) => (
                <option key={t.id} value={t.id}>
                  {t.title}
                </option>
              ))}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Subject</label>
            <select value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} required>
              <option value="">Select…</option>
              {(subjects.data || []).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Class</label>
            <select value={form.school_class} onChange={(e) => setForm({ ...form, school_class: e.target.value })} required>
              <option value="">Select…</option>
              {(classes.data || []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.section}
                </option>
              ))}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Kind</label>
            <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
              <option value="quiz">Quiz</option>
              <option value="homework">Homework</option>
              <option value="exam">Exam</option>
            </select>
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Status</label>
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Total marks</label>
            <input value={form.total_marks} onChange={(e) => setForm({ ...form, total_marks: e.target.value })} />
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Duration (min)</label>
            <input value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
          </div>
          <div style={{ flex: 1 }}>
            <label>Due (ISO date)</label>
            <input value={form.due_at} onChange={(e) => setForm({ ...form, due_at: e.target.value })} placeholder="2025-12-31" />
          </div>
        </div>
        {create.error && <div className="alert error">{create.error}</div>}
        <div className="actions">
          <button className="btn" type="submit" disabled={create.busy}>
            Create assessment
          </button>
        </div>
      </form>

      {list.error && <div className="alert error">{list.error}</div>}
      {(list.data || []).length === 0 && !list.loading && (
        <div className="card empty" style={{ marginTop: 20 }}>
          No assessments yet.
        </div>
      )}

      <div className="stack" style={{ marginTop: 20 }}>
        {(list.data || []).map((a) => (
          <div key={a.id} className="card">
            <div className="row">
              <h3 style={{ margin: 0 }}>{a.title}</h3>
              <span className="badge">{a.kind}</span>
              <span className={`badge ${a.status === 'published' ? 'green' : 'gray'}`}>{a.status}</span>
              <span className="badge gray">{a.subject_name}</span>
              <span className="badge gray">{a.total_marks} marks</span>
              <button className="btn sm secondary" style={{ marginLeft: 'auto' }} onClick={() => void toggleQuestions(a)}>
                {questionFor === a.id ? 'Hide questions' : 'Questions'}
              </button>
            </div>

            {questionFor === a.id && (
              <div style={{ marginTop: 16 }}>
                {addQ.error && <div className="alert error">{addQ.error}</div>}
                {(questions[a.id] || []).map((q: any) => (
                  <div key={q.id} className="muted" style={{ padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                    <b style={{ color: 'var(--text)' }}>{q.text}</b>
                    <div>
                      <small>
                        {q.q_type === 'mcq' ? `Options: ${(q.options || []).join(', ')}` : 'Short answer'} · correct: {q.correct_index} · {q.marks} pt
                      </small>
                    </div>
                  </div>
                ))}
                {(questions[a.id] || []).length === 0 && (
                  <p className="muted">No questions yet — add a multiple choice below.</p>
                )}

                <div className="card" style={{ marginTop: 12, background: 'var(--bg)' }}>
                  <h3 style={{ fontSize: 15 }}>Add MCQ</h3>
                  <label>Question text</label>
                  <textarea value={qText} onChange={(e) => setQText(e.target.value)} rows={2} placeholder="What do plants release during photosynthesis?" />
                  <label>Options (one per line)</label>
                  <textarea value={qOptions} onChange={(e) => setQOptions(e.target.value)} rows={3} placeholder={'Oxygen\nCarbon dioxide\nNitrogen\nHydrogen'} />
                  <div className="row">
                    <div style={{ flex: 1 }}>
                      <label>Correct option index (0-based)</label>
                      <input type="number" value={qCorrect} onChange={(e) => setQCorrect(e.target.value)} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <label>Marks</label>
                      <input type="number" value={qMarks} onChange={(e) => setQMarks(e.target.value)} />
                    </div>
                  </div>
                  <div className="actions">
                    <button className="btn sm" disabled={addQ.busy || !qText.trim()} onClick={() => void submitQuestion(a)}>
                      Add question
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
