import json
from datetime import datetime
from memory.analytics_db import AnalyticsDB

class LocalBehavioralIntelligence:
    def __init__(self, analytics_db: AnalyticsDB):
        self.analytics_db = analytics_db

    def analyze_habits_and_generate_insights(self) -> str:
        """
        Analyzes logged task frequencies and latency profiles to build privacy-first productivity recommendations.
        """
        rankings = self.analytics_db.get_agent_rankings()
        if not rankings:
            return "Diagnostics Alert: Not enough telemetry gathered to generate behavioral analytics."

        # Compile summaries
        most_active_agent = rankings[0]["agent_name"]
        total_runs = sum(r["total_tasks"] for r in rankings)
        avg_success = sum(r["success_rate"] for r in rankings) / len(rankings)

        insight_summary = (
            f"Weekly Workspace Audit: Conducted {total_runs} local agent routines successfully. "
            f"Your most deployed agent is {most_active_agent}, coordinating workflows. "
            f"Average task completion success is {avg_success:.1f}% across all workspaces."
        )

        metrics = {
            "total_agent_runs": total_runs,
            "favorite_agent": most_active_agent,
            "average_success_rate": avg_success
        }

        # Save insight in analytics database
        self.analytics_db.log_behavioral_insight(
            insight_type="PRODUCTIVITY",
            summary=insight_summary,
            metrics=metrics
        )
        return insight_summary
