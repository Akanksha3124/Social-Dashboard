import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

os.makedirs("dashboard", exist_ok=True)

YT_PATH = "data/cleaned/youtube_clean.csv"

yt_exists = os.path.exists(YT_PATH)

yt = pd.read_csv(YT_PATH) if yt_exists else pd.DataFrame()


DAY_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

COLORS = {
    "blue":   "#378ADD",
    "orange": "#EF9F27",
    "teal":   "#1D9E75",
    "coral":  "#D85A30",
    "purple": "#7F77DD",
    "gray":   "#888780",
}

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Top 10 videos by views (YouTube)",
        "Engagement rate by day of week (YouTube)",
        "Best posting hours (YouTube)",
        "Monthly views trend (YouTube)"
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.1
)

# --- Chart 1: Top 10 videos by views ---
if yt_exists:
    top10 = yt.nlargest(10, "views")
    fig.add_trace(go.Bar(
        x=top10["views"],
        y=top10["title"].str[:35],
        orientation="h",
        marker_color=COLORS["blue"],
        name="Views"
    ), row=1, col=1)

# --- Chart 2: Engagement by day ---
if yt_exists:
    day_eng = yt.groupby("day_of_week")["engagement_rate"].mean().reindex(DAY_ORDER)
    best_day = day_eng.idxmax()
    bar_colors = [COLORS["coral"] if d == best_day else COLORS["blue"] for d in DAY_ORDER]
    fig.add_trace(go.Bar(
        x=day_eng.index,
        y=day_eng.values,
        marker_color=bar_colors,
        name="Engagement/day"
    ), row=1, col=2)

# --- Chart 3: Best posting hours ---
if yt_exists:
    hour_eng = yt.groupby("hour")["engagement_rate"].mean()
    best_hour = hour_eng.idxmax()
    fig.add_trace(go.Scatter(
        x=hour_eng.index,
        y=hour_eng.values,
        mode="lines+markers",
        line=dict(color=COLORS["teal"], width=2),
        marker=dict(
            size=[12 if h == best_hour else 6 for h in hour_eng.index],
            color=[COLORS["coral"] if h == best_hour else COLORS["teal"] for h in hour_eng.index]
        ),
        name="Engagement/hour"
    ), row=2, col=1)

# --- Chart 5: Monthly views trend ---
if yt_exists:
    yt["published_at"] = pd.to_datetime(yt["published_at"])
    yt["year_month"] = yt["published_at"].dt.to_period("M").astype(str)
    monthly = yt.groupby("year_month")["views"].sum().reset_index()
    fig.add_trace(go.Scatter(
        x=monthly["year_month"],
        y=monthly["views"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(55,138,221,0.15)",
        line=dict(color=COLORS["blue"], width=2),
        name="Monthly views"
    ), row=2, col=2)



# --- Layout ---
fig.update_layout(
    title=dict(
        text="Social Media Engagement Dashboard",
        font=dict(size=22),
        x=0.5
    ),
    height=1000,
    showlegend=False,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Arial, sans-serif", size=12, color="#333333"),
    margin=dict(t=100, b=60, l=60, r=80)
)

fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0", linecolor="#cccccc")
fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0", linecolor="#cccccc")

output_path = "dashboard/dashboard.html"
fig.write_html(output_path, include_plotlyjs="cdn")
print(f"Dashboard saved to: {output_path}")
print("Open dashboard/dashboard.html in your browser.")
