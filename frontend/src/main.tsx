import React from "react";
import ReactDOM from "react-dom/client";
import {
  AlertCircle,
  CalendarDays,
  Check,
  ChevronRight,
  ClipboardCheck,
  Loader2,
  Sparkles,
  Target,
} from "lucide-react";
import "./styles.css";

type ExamName = "JEE Main" | "NEET" | "CUET";
type StageName =
  | "Applied"
  | "Admit Card Released"
  | "Exam Done"
  | "Answer Key Out"
  | "Result Declared";
type SelectableStage = Exclude<StageName, "Result Declared">;
type StageStatus = "completed" | "current" | "upcoming";

type TimelineItem = {
  stage: StageName;
  status: StageStatus;
  display_date: string | null;
  predicted_date: string | null;
  confidence: number | null;
  note: string;
};

type TrackResponse = {
  exam: ExamName;
  current_stage: SelectableStage;
  generated_at: string;
  source: "groq" | "fallback";
  timeline: TimelineItem[];
  readiness_items: string[];
  summary: string;
};

const exams: ExamName[] = ["JEE Main", "NEET", "CUET"];
const stages: SelectableStage[] = ["Applied", "Admit Card Released", "Exam Done", "Answer Key Out"];

function App() {
  const [exam, setExam] = React.useState<ExamName>("JEE Main");
  const [currentStage, setCurrentStage] = React.useState<SelectableStage>("Applied");
  const [result, setResult] = React.useState<TrackResponse | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const trackExam = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exam, current_stage: currentStage }),
      });

      if (!response.ok) {
        throw new Error("Tracker request failed");
      }

      const payload = (await response.json()) as TrackResponse;
      setResult(payload);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }, [exam, currentStage]);

  React.useEffect(() => {
    void trackExam();
  }, [trackExam]);

  return (
    <main className="app-shell">
      <section className="topbar" aria-labelledby="page-title">
        <div className="brand-mark" aria-hidden="true">
          <ClipboardCheck size={25} strokeWidth={2.3} />
        </div>
        <div>
          <p className="eyebrow">NTA Exam Tracker</p>
          <h1 id="page-title">Plan the next exam move</h1>
        </div>
      </section>

      <section className="control-panel" aria-label="Exam tracker controls">
        <div className="control-group">
          <div className="control-heading">
            <CalendarDays size={18} />
            <span>Exam</span>
          </div>
          <div className="segmented-grid exam-grid">
            {exams.map((examName) => (
              <button
                className={examName === exam ? "segment active" : "segment"}
                key={examName}
                onClick={() => setExam(examName)}
                type="button"
              >
                {examName}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group">
          <div className="control-heading">
            <Target size={18} />
            <span>Current Stage</span>
          </div>
          <div className="segmented-grid stage-grid">
            {stages.map((stage) => (
              <button
                className={stage === currentStage ? "segment active" : "segment"}
                key={stage}
                onClick={() => setCurrentStage(stage)}
                type="button"
              >
                {stage}
              </button>
            ))}
          </div>
        </div>

        <button className="primary-action" disabled={isLoading} onClick={trackExam} type="button">
          {isLoading ? <Loader2 className="spin" size={20} /> : <Sparkles size={20} />}
          <span>{isLoading ? "Predicting" : "Refresh Plan"}</span>
        </button>
      </section>

      {error ? (
        <section className="error-panel" role="alert">
          <AlertCircle size={20} />
          <span>{error}</span>
        </section>
      ) : null}

      {result ? (
        <>
          <section className="summary-band" aria-label="Prediction summary">
            <div>
              <p className="source-label">{result.source === "groq" ? "AI Assisted" : "Pattern Estimate"}</p>
              <h2>{result.exam}</h2>
            </div>
            <p>{result.summary}</p>
          </section>

          <section className="timeline-section" aria-labelledby="timeline-title">
            <div className="section-title">
              <h2 id="timeline-title">Timeline</h2>
              <span>{formatDate(result.generated_at)}</span>
            </div>
            <div className="timeline-list">
              {result.timeline.map((item, index) => (
                <TimelineCard item={item} key={item.stage} isLast={index === result.timeline.length - 1} />
              ))}
            </div>
          </section>

          <section className="readiness-section" aria-labelledby="readiness-title">
            <div className="section-title">
              <h2 id="readiness-title">Readiness Panel</h2>
              <span>{result.readiness_items.length} actions</span>
            </div>
            <div className="action-list">
              {result.readiness_items.map((item, index) => (
                <article className="action-card" key={item}>
                  <span>{index + 1}</span>
                  <p>{item}</p>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : (
        <section className="skeleton" aria-label="Loading tracker">
          <Loader2 className="spin" size={26} />
        </section>
      )}
    </main>
  );
}

function TimelineCard({ item, isLast }: { item: TimelineItem; isLast: boolean }) {
  const dateLabel = item.predicted_date ?? item.display_date;

  return (
    <article className={`timeline-card ${item.status}`}>
      <div className="timeline-rail" aria-hidden="true">
        <span className="timeline-dot">{item.status === "completed" ? <Check size={16} /> : <ChevronRight size={16} />}</span>
        {!isLast ? <span className="timeline-line" /> : null}
      </div>

      <div className="timeline-content">
        <div className="timeline-row">
          <h3>{item.stage}</h3>
          <span className="stage-pill">{stageLabel(item.status)}</span>
        </div>
        <div className="date-row">
          <span>{dateLabel ? formatDate(dateLabel) : "Pending"}</span>
          {item.confidence !== null ? <ConfidenceMeter value={item.confidence} /> : null}
        </div>
        <p>{item.note}</p>
      </div>
    </article>
  );
}

function ConfidenceMeter({ value }: { value: number }) {
  return (
    <span className="confidence" aria-label={`${value}% confidence`}>
      <span style={{ width: `${value}%` }} />
      <strong>{value}%</strong>
    </span>
  );
}

function stageLabel(status: StageStatus) {
  if (status === "completed") return "Done";
  if (status === "current") return "Now";
  return "Next";
}

function formatDate(value: string) {
  const date = new Date(`${value}T00:00:00`);
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
