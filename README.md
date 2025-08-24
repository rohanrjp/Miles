
# 🏃‍♂️ Miles – Multi-Agent Running Assistant

Miles is an **AI-powered multi-agent coach** designed to help runners make smarter training decisions.  
It combines **Strava data**, **weather forecasts**, and **memory-aware reasoning** to answer the big question every runner faces:

👉 *"Should I run today?"*

## ✨ Features
- **Multi-agent orchestration** using [pydantic-graph](https://github.com/pydantic/pydantic-graph)  
  - `TeamLeader` → Decides which sub-agent to activate  
  - `StravaCoach` → Analyzes training load, pace, and recovery from Strava data  
  - `WeatherAssistant` → Checks weather conditions before suggesting a run  
  - `RecoveryNode` → Provides rest/recovery advice after hard efforts  
  - `TelegramFormatter` → Outputs neatly formatted messages for chat delivery  

- **Memory persistence** via [Mem0](https://github.com/mem0ai/mem0)  
  - Stores and recalls per-user history (using Telegram `chat_id`)  
  - Ensures context awareness across sessions  

- **Custom agent logic** built with [pydantic-ai](https://github.com/pydantic/pydantic-ai)  
  - Structured outputs  
  - Seamless integration with external APIs (Strava + Weather)  

- **Event-driven design** ready for integration into **Telegram bots** or other chat interfaces.

---

## Roadmap

	•	Add GitHub Actions for daily automated run analysis
	•	Predict next optimal run time with recovery modeling
	•	Expand nutrition guidance from Strava performance data
	•	Web dashboard with historical insights

## 🤝 Contributing

PRs are welcome! If you’d like to extend new agent nodes (nutrition, injury prevention, etc.), open an issue or draft a pull request.

