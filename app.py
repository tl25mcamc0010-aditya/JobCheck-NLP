import io
import csv
from datetime import datetime, timedelta
from collections import defaultdict

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, Response

from src.predict import predict_job
from src.database import create_db, insert_job, get_all_jobs, get_stats

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # required for flash messages

# Ensure DB and table exist on startup
create_db()

# ── In-memory store for batch results (simple; resets on server restart) ──
_batch_results = []


# ─────────────────────────── helpers ──────────────────────────────────────

def build_time_series(jobs, days=14):
    """Return parallel lists of date-labels, fake counts, real counts."""
    today = datetime.utcnow().date()
    labels, fake_counts, real_counts = [], [], []

    fake_by_day = defaultdict(int)
    real_by_day = defaultdict(int)

    for job in jobs:
        # jobs rows are dicts: {id, description, prediction, created_at}
        try:
            d = datetime.strptime(job["created_at"], "%Y-%m-%d %H:%M:%S").date()
        except Exception:
            d = today
        if job["prediction"] == "Fake Job":
            fake_by_day[d] += 1
        else:
            real_by_day[d] += 1

    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        fake_counts.append(fake_by_day.get(d, 0))
        real_counts.append(real_by_day.get(d, 0))

    return labels, fake_counts, real_counts


def get_dashboard_stats(jobs):
    total = len(jobs)
    fake  = sum(1 for j in jobs if j["prediction"] == "Fake Job")
    real  = total - fake
    fake_pct = round(fake / total * 100, 1) if total else 0
    return {"total": total, "fake": fake, "real": real, "fake_pct": fake_pct}


# ─────────────────────────── routes ───────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    all_jobs = get_all_jobs()
    stats    = get_dashboard_stats(all_jobs)
    recent   = all_jobs[:8]          # last 8 for the sidebar
    return render_template("index.html", stats=stats, recent=recent)


@app.route("/predict", methods=["POST"])
def predict():
    job_text = request.form.get("job", "").strip()

    if not job_text:
        flash("Please enter a job description.", "error")
        return redirect(url_for("home"))

    prediction = predict_job(job_text)
    insert_job(job_text, prediction)

    all_jobs = get_all_jobs()
    stats    = get_dashboard_stats(all_jobs)
    recent   = all_jobs[:8]

    return render_template(
        "index.html",
        prediction=prediction,
        job_text=job_text,
        stats=stats,
        recent=recent,
    )


@app.route("/history")
def history():
    jobs = get_all_jobs()
    return render_template("history.html", jobs=jobs)


@app.route("/stats")
def stats():
    all_jobs = get_all_jobs()
    stats_data = get_dashboard_stats(all_jobs)
    time_labels, fake_over_time, real_over_time = build_time_series(all_jobs)
    return render_template(
        "stats.html",
        stats=stats_data,
        time_labels=time_labels,
        fake_over_time=fake_over_time,
        real_over_time=real_over_time,
    )


@app.route("/batch", methods=["GET", "POST"])
def batch():
    global _batch_results

    if request.method == "GET":
        return render_template("batch.html", results=None)

    file = request.files.get("file")
    if not file or not file.filename or file.filename.rsplit(".", 1)[-1].lower() != "csv":
        flash("Please upload a valid .csv file.", "error")
        return render_template("batch.html", results=None)

    try:
        file.stream.seek(0)
        df = pd.read_csv(file.stream)
    except Exception as e:
        flash(f"Could not read CSV: {e}", "error")
        return render_template("batch.html", results=None)

    # Accept either `text` or `description` as the input column
    text_column = "text" if "text" in df.columns else "description" if "description" in df.columns else None
    if not text_column:
        flash("CSV must contain a 'text' or 'description' column.", "error")
        return render_template("batch.html", results=None)

    results = []
    for _, row in df.iterrows():
        job_text = str(row.get(text_column, "")).strip()
        if not job_text:
            continue

        pred = predict_job(job_text)
        insert_job(job_text, pred)

        results.append({
            "text": job_text,
            "prediction": pred
        })

    _batch_results = results   # store for download
    return render_template("batch.html", results=results)


@app.route("/batch/download", methods=["POST"])
def batch_download():
    global _batch_results
    if not _batch_results:
        flash("No batch results to download.", "error")
        return redirect(url_for("batch"))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["description", "prediction"])
    writer.writeheader()
    writer.writerows(_batch_results)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=predictions.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)