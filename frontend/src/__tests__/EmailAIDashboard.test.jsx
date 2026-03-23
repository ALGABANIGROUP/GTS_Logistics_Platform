import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

import EmailAIDashboard from "../pages/EmailAIDashboard.jsx";

vi.mock("../api/emailStatsApi.js", () => ({
  getEmailBotStats: vi.fn(),
  getEmailSentimentTrends: vi.fn(),
  getEmailDecisionStats: vi.fn(),
}));

import {
  getEmailBotStats,
  getEmailSentimentTrends,
  getEmailDecisionStats,
} from "../api/emailStatsApi.js";

describe("EmailAIDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders bot stats, trends, and recommendations", async () => {
    getEmailBotStats.mockResolvedValue({
      bots: [
        {
          bot_key: "finance_bot",
          feedback_count: 4,
          average_rating: 4.5,
          accuracy_rate: 0.75,
          average_routing_confidence: 0.86,
        },
      ],
      summary: { total_feedback: 4, average_accuracy: 0.75 },
    });
    getEmailSentimentTrends.mockResolvedValue({
      sentiment: { negative: 2, neutral: 1 },
      summary: { analyzed_messages: 3, dominant_category: "billing" },
    });
    getEmailDecisionStats.mockResolvedValue({
      decision_counts: { ai: 2, rule: 1 },
      confidence_buckets: { high: 1, medium: 1, low: 1 },
      recommendations: ["Review routing rules for customer_service."],
      summary: { routed_messages: 3 },
    });

    render(<EmailAIDashboard embedded />);

    await waitFor(() => {
      expect(screen.getByText("Bot Performance")).toBeInTheDocument();
    });

    expect(screen.getByText("finance_bot")).toBeInTheDocument();
    expect(screen.getByText("Review routing rules for customer_service.")).toBeInTheDocument();
    expect(screen.getByText("Sentiment Trends")).toBeInTheDocument();
  });
});
