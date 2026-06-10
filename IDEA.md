# SourceWatch — Vietnamese News Credibility Analyzer

## Overview

SourceWatch is a real-time news credibility analysis tool for the Vietnamese internet. Users paste a news article link and receive an instant credibility report showing propagation timeline, source network, and trust score — no account required.

## Pain Point

Vietnamese social media (Facebook, Zalo, TikTok) amplifies news faster than any other country in SEA, but no tool exists to trace where a story originated, whether it was altered, or who is amplifying it. Users have no way to verify the credibility of rapidly spreading claims.

## Solution

A web tool that analyzes Vietnamese news articles and answers three questions:

1. **Where did this story come from?** — Propagation timeline showing which source published first, who copied, and when.
2. **Was it altered?** — Claim consistency check comparing the analyzed article against other sources.
3. **Who is amplifying it?** — Source network graph showing amplification patterns and credibility scores.

## User Experience

- User visits `sourcewatch.vn` (or Vercel subdomain)
- Pastes a Vietnamese news article URL
- Clicks "Analyze"
- Waits ~10-20 seconds
- Receives: propagation timeline + source network graph + credibility score + fact-check status
- No login, no account, paste and go

## Core Features

### F1: Article Analysis
- Fetch article HTML via Playwright headless browser
- Extract article text, title, author, publish date, source domain
- Input: URL string → Output: structured article data
- Cache result by URL hash (24h TTL)

### F2: Claim Extraction
- Send article text to Gemini 3.5 Flash (free tier)
- Extract 3-7 key claims (factual statements)
- Each claim stored as: `{ claim_text, source_article, extracted_at }`
- Store embeddings in ChromaDB for similarity search

### F3: Propagation Tracking
- For each claim, use Playwright to scrape top Vietnamese news sites
- Sources to track: VnExpress, Dân Trí, Zing News, Tuổi Trẻ, VOV, VTV, Lao Động, Thanh Niên, Tiền Phong, Người Lao Động
- Build timeline: which source published first, which copied, when
- Store in SQLite for persistence

### F4: Source Network Graph
- SQLite adjacency list representation (no separate graph DB needed for MVP)
- Nodes: news sources (domains)
- Edges: "copied_from", "referenced", "amplified_by"
- D3.js force-directed graph visualization on frontend

### F5: Fact-Check Cross-Reference
- Custom Vietnamese fact-check DB (`data/fact_check_db.json`) — pre-indexed claims
- For each claim, search custom DB via ChromaDB similarity
- Return: "verified", "unverified", "disputed", "false"
- External: Google Fact Check Claim Search API as supplementary source

### F6: Credibility Scoring
- Source reputation: pre-defined trust scores per domain (VnExpress 8/10, unknown blog 2/10)
- Claim consistency: did other sources report the same facts?
- Amplification pattern: are low-credibility pages amplifying this story?
- Output: composite score 0-10 with breakdown

## Target Users

- Vietnamese internet users who want to verify news before sharing
- Journalists and researchers tracking information propagation
- Students and educators fact-checking sources
- Activists and NGOs monitoring health/disaster misinformation

## Scope for MVP

- Only URL input (no text paste, no browser extension)
- Track 10 Vietnamese news sources
- Display 1 propagation timeline
- Display 1 source network graph
- Show 1 credibility score
- No user accounts, no history, no saved results

## Differentiation

| Existing tools | SourceWatch |
|----------------|-------------|
| Snopes, PolitiFact | Static Q&A, not real-time |
| NewsGuard | Browser extension, English-first |
| Hoax or Fact-check sites | Manual, not automated |
| Social media analytics tools | Expensive, enterprise-only |

SourceWatch is **Vietnamese-first**, **real-time**, **free**, and **paste-and-go**.

## Success Metrics

- Analyze 1 article in < 20 seconds
- Track at least 10 Vietnamese news sources
- Show accurate propagation timeline for breaking news
- Credibility score correlates with known ground truth (verified stories score high)
