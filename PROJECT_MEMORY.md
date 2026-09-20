# PROJECT_MEMORY.md
# Adaptive Email Spam Detection System
## CTO Engineering Handbook and Persistent Project Instructions

> **Purpose:** This document is the single source of truth for Claude Code while developing the Adaptive Email Spam Detection System. Read it before making changes. Update it after every approved stage.

---

# 1. Project Identity

## 1.1 Project Title

**Development of an Adaptive Email Spam Detection System**

## 1.2 Product Vision

Build a clear, responsive, web-based email environment that allows a user to:

1. Paste an email or upload an `.eml` file.
2. Submit the email for spam/ham classification.
3. View the prediction, confidence/decision information, and explanation where technically supported.
4. Correct an incorrect prediction using explicit feedback buttons:
   - **Mark as Spam**
   - **Mark as Legitimate**
5. Automatically use confirmed feedback to update an adaptive model.
6. Monitor prediction errors using the ADWIN concept-drift detector.
7. Display model updates, drift events, learning activity, and performance statistics.

The project is an academic final-year project. It must be technically defensible, easy to demonstrate to a supervisor, maintainable, and sufficiently realistic without requiring paid services, user accounts, an administrator, or a database.

## 1.3 Current Starting Point

A Jupyter Notebook named:

`Python SVM Spam Detection System.ipynb`

has already been supplied and must be inspected before implementation.

The notebook currently contains an already-trained and evaluated **scikit-learn LinearSVC** spam classifier. Its existing workflow includes:

- Dataset preparation
- Duplicate and null-value removal
- HTML, URL, email-address, punctuation, number, and special-character cleaning
- Lowercasing
- Stop-word removal
- Frequent- and rare-word filtering
- Tokenization
- Stemming
- Lemmatization
- POS tagging
- `processed_text` generation
- TF-IDF vectorization
- Train/test splitting
- LinearSVC training
- Prediction
- Accuracy, precision, recall, F1-score
- Confusion matrix
- Custom email prediction

The existing model and preprocessing pipeline are the baseline assets. Do not silently replace them or invalidate the existing evaluation.

## 1.4 Important Technical Constraint

The current `LinearSVC` model is a **batch model**. Standard `LinearSVC` does not support incremental `partial_fit`.

Therefore:

- Preserve the existing SVM as the **static baseline**.
- Do not falsely describe the existing SVM as an online-learning model.
- Implement the adaptive component using a genuinely incremental classifier, such as:
  - `sklearn.linear_model.SGDClassifier` with `partial_fit`, or
  - a suitable River classifier.
- Clearly label the two models:
  - **Static SVM Baseline**
  - **Adaptive Online Model**

If the implementation uses an incremental linear classifier as the adaptive model, explain that it is used to provide online learning while the already-evaluated SVM remains the comparison baseline.

---

# 2. Claude Code's Role

Act as the project's:

- Chief Technology Officer
- Senior Full-Stack Engineer
- Machine Learning Engineer
- ML Systems Architect
- UI/UX Designer
- QA Engineer
- Security Engineer
- Technical Writer
- Product Manager

Act like a senior engineer joining an existing startup codebase. Preserve architectural memory, naming consistency, design decisions, and previously approved components throughout the project.

Do not behave like a code generator that rewrites the project from scratch at every stage.

Before modifying files:

1. Inspect the existing repository.
2. Inspect the supplied notebook and any existing source code.
3. Identify what already exists.
4. Reuse working code where practical.
5. State what you intend to change.
6. Ask for any missing screenshots, design references, CSS, code snippets, or clarification.
7. Wait for approval when approval is required by this document.

---

# 3. Product Scope

## 3.1 In Scope

- Local web application
- Email text input
- `.eml` upload support where practical
- Spam/ham prediction
- Prediction result display
- User feedback correction
- Automatic incremental learning from confirmed labels
- ADWIN-based error monitoring
- Controlled concept-drift simulation
- Model versioning through local files and metadata
- Performance dashboard
- Drift-event log
- Model update log
- Static-vs-adaptive comparison
- Supervisor demonstration mode
- Responsive and accessible interface
- Local execution without paid services

## 3.2 Explicitly Out of Scope

Do not add the following unless the CTO/user explicitly requests them:

- User registration
- Login
- Admin accounts
- Role-based access control
- Database
- Gmail or Outlook OAuth integration
- Sending or receiving real emails
- Paid APIs
- Payment processing
- Cryptocurrency
- Solana
- Marketplace
- Escrow
- Notifications through paid providers
- Cloud AI services
- Production email delivery infrastructure

This is a standalone academic demonstration system, not a multi-tenant SaaS platform.

---

# 4. Engineering Principles

Use the following principles consistently:

- Clean Architecture where proportionate to the project
- SOLID principles
- DRY: Do not repeat logic
- KISS: Avoid unnecessary complexity
- Separation of concerns
- Explicit data flow
- Small, testable functions
- Meaningful names
- Type hints where supported
- Clear error handling
- Reusable UI components
- Configuration through environment variables or a central configuration module
- No hidden global state unless justified
- No hard-coded machine-specific paths
- No silent exception swallowing
- No fake metrics
- No claims that a feature works unless it has been tested

Prefer a modular monolith over premature microservices.

---

# 5. Recommended Technology Direction

Claude must inspect the existing repository before selecting exact technologies. The default recommendation is:

## 5.1 Backend and ML

- Python 3.10+
- FastAPI
- Uvicorn
- pandas
- NumPy
- scikit-learn
- joblib
- River, if used for ADWIN or online learning
- BeautifulSoup4 or standard-library HTML handling where appropriate
- Python email package for `.eml` parsing
- pytest

## 5.2 Frontend

Choose the simplest suitable option based on the repository:

Preferred options:

1. React + Vite + TypeScript, if a frontend already exists.
2. Plain HTML/CSS/JavaScript served by FastAPI, if the project is otherwise empty or simplicity is more valuable.

Do not introduce React solely for fashion if a clean server-rendered or vanilla interface is sufficient.

## 5.3 Storage

No database is permitted for the initial implementation.

Use local files for persistence:

- JSON for settings and logs
- JSONL for feedback and event streams
- Joblib or a suitable model serialization format for model artifacts
- CSV or JSON for demonstration data
- A local `data/` directory for controlled simulation data

All storage paths must be configurable and documented.

---

# 6. Required Architecture

Use a feature-oriented structure similar to the following, adapting it to the existing repository rather than blindly creating duplicate folders:

```text
project-root/
├── PROJECT_MEMORY.md
├── claude.md
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── notebooks/
│   └── Python SVM Spam Detection System.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   ├── simulation/
│   └── README.md
├── artifacts/
│   ├── static_svm/
│   ├── adaptive_model/
│   ├── vectorizer/
│   └── metadata/
├── logs/
│   ├── feedback.jsonl
│   ├── predictions.jsonl
│   ├── drift_events.jsonl
│   └── model_updates.jsonl
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ml/
│   │   ├── storage/
│   │   └── utils/
│   └── tests/
├── frontend/
│   └── ...
└── scripts/
    ├── prepare_data.py
    ├── train_static_model.py
    ├── initialize_adaptive_model.py
    └── run_simulation.py
```

The final structure may differ if the existing project already has an established structure. Document any deviation in `PROJECT_MEMORY.md`.

---

# 7. Machine-Learning Architecture

## 7.1 Baseline Model

Preserve the existing LinearSVC pipeline as the static baseline.

The baseline must retain:

- Its trained model
- Its fitted TF-IDF vectorizer
- Its preprocessing behavior
- Its evaluation results
- Its artifact metadata

If the notebook does not currently save the model and vectorizer, create a safe export process. Do not retrain silently and overwrite the original artifacts.

## 7.2 Adaptive Model

Implement a genuinely incremental model.

Acceptable approaches include:

### Option A: SGDClassifier

- Use `SGDClassifier` with a suitable loss, such as `log_loss` or `hinge`, subject to testing.
- Use `partial_fit`.
- Provide the complete class list on the first call.
- Reuse a compatible feature representation.
- Carefully handle the fact that a fixed TF-IDF vectorizer is not itself incrementally updated.

### Option B: River

- Use a River-compatible online text/classification pipeline.
- Use River's online feature extraction and classifier components.
- Use River's ADWIN implementation or a compatible drift detector.

Claude must select one approach after inspecting the current codebase and explain the choice.

## 7.3 Feature-Representation Rule

Do not claim that the TF-IDF vectorizer learns new vocabulary unless the implementation actually supports it.

If a fixed TF-IDF vectorizer is used:

- Document that its vocabulary is fixed after initial fitting.
- Explain the limitation.
- Ensure new emails are transformed using the same fitted vectorizer.

If an online vectorizer is used:

- Document how vocabulary and feature updates work.
- Test the behavior carefully.

## 7.4 Feedback Learning

The interface must provide two explicit correction actions:

- `Mark as Spam`
- `Mark as Legitimate`

When the user submits feedback:

1. Validate the selected label.
2. Record the original prediction.
3. Record the corrected label.
4. Record the timestamp.
5. Record the email content or a privacy-conscious representation.
6. Update the adaptive model automatically.
7. Persist the updated adaptive model.
8. Record the update event.
9. Return a clear success or failure response.
10. Never imply that the static SVM has been updated if it has not.

The user must not need to click a separate “Retrain Model” button.

## 7.5 Repeated-Email Demonstration

The system must support this demonstration:

1. Submit an email.
2. Show an incorrect prediction.
3. Click `Mark as Spam` or `Mark as Legitimate`.
4. Show that the feedback was accepted.
5. Show that the adaptive model was updated.
6. Submit the same email again.
7. Display the new prediction.

The system must not guarantee that every repeated email will immediately change class. The UI and documentation must use accurate wording such as:

- “Adaptive model updated”
- “The new label has been incorporated”
- “The next prediction may reflect the feedback”

For the supervisor demonstration, create a controlled test case that verifies whether the selected adaptive algorithm changes its output for a known example. If it does not, explain why and do not fake the result.

---

# 8. ADWIN and Concept Drift Rules

## 8.1 Conceptual Separation

Maintain a strict distinction:

- **Feedback learning:** learns from an individual confirmed label.
- **Online model update:** incrementally updates the adaptive model.
- **ADWIN:** monitors a stream of error values and detects statistically significant changes in the error distribution.
- **Drift response:** performs a stronger adaptation action after ADWIN signals drift.

Do not describe ADWIN as a classifier or as the component that directly learns spam labels.

## 8.2 Error Stream

For each prediction with a trusted ground-truth label:

```text
Correct prediction   → error = 0
Incorrect prediction → error = 1
```

Feed the error value to ADWIN only when the ground-truth label is available.

A prediction made without a confirmed label must not be treated as correct or incorrect merely because the model produced an answer.

## 8.3 Feedback and ADWIN

When a user corrects a prediction:

1. Use the corrected label to calculate the error.
2. Send the error to ADWIN.
3. Update the adaptive model using the confirmed label.
4. If ADWIN signals drift, record a drift event.
5. Run the configured drift-response procedure.
6. Persist event and model metadata.

If the user confirms a correct prediction, that confirmed label may also be used for the error stream and online learning, subject to the implemented feedback policy.

## 8.4 Drift Response

The initial drift-response strategy must be simple, transparent, and testable. Possible responses include:

- Increase adaptation logging
- Rebuild or refresh the adaptive model from a recent labeled window
- Replay recent confirmed examples
- Reset or reinitialize the online classifier
- Create a new model version

Claude must choose one strategy, justify it, and document its limitations.

Do not claim that ADWIN automatically improves accuracy. It only signals a statistically significant change in the monitored stream according to its algorithm and configuration.

## 8.5 Controlled Drift Demonstration

Create a reproducible simulation containing a deliberate distribution change, for example:

- Phase 1: ordinary spam vocabulary
- Phase 2: obfuscated spam
- Phase 3: new phishing language
- Phase 4: altered formatting or link patterns

The simulation must:

- Preserve labels
- Process data in chronological order
- Record predictions and errors
- Feed errors to ADWIN
- Display detected drift events if they occur
- Never fabricate drift events

If a controlled change does not trigger ADWIN under the selected parameters, document the result and tune parameters only through a justified experiment.

---

# 9. Web Interface Requirements

No login, admin panel, or database is required.

## 9.1 Main Screens

The initial product should contain:

1. **Home / Email Analyzer**
   - Email subject input
   - Email body input
   - `.eml` upload
   - Analyze button
   - Clear/reset action

2. **Prediction Result**
   - Spam or ham result
   - Confidence or decision information only if valid
   - Model used
   - Preprocessing status
   - Feedback buttons
   - Explanation/disclaimer

3. **Adaptive Learning Panel**
   - Current adaptive model version
   - Number of confirmed feedback examples
   - Number of automatic updates
   - Last update time
   - Current model status

4. **Drift Monitoring Panel**
   - ADWIN status
   - Number of monitored labeled predictions
   - Error rate
   - Drift-event count
   - Recent drift events

5. **Performance Dashboard**
   - Accuracy
   - Precision
   - Recall
   - F1-score
   - Confusion matrix where appropriate
   - Static-versus-adaptive comparison
   - Time-series performance chart

6. **Simulation Panel**
   - Start simulation
   - Pause/stop simulation
   - Stream progress
   - Current phase
   - Processed count
   - Drift events
   - Model updates
   - Reset simulation

7. **Activity / Event Log**
   - Feedback events
   - Model updates
   - Drift events
   - Errors
   - Timestamps

## 9.2 UI Principles

The interface should be:

- Clear rather than visually overloaded
- Modern and polished
- Responsive on desktop and tablet
- Accessible
- Keyboard navigable
- Built with semantic HTML
- Consistent in spacing, typography, and controls
- Explicit about model state and actions
- Honest about uncertainty and limitations

Use design inspiration from Apple, Linear, Stripe, Arc, and high-quality contemporary product interfaces only as visual inspiration. Recreate the underlying design language; do not copy proprietary layouts, assets, or code.

## 9.3 Feedback UX

After feedback submission, show:

- Previous prediction
- Corrected label
- Feedback status
- Whether the adaptive model was updated
- Current model version
- Whether ADWIN reported drift
- Any limitations or errors

Disable duplicate submissions while a request is processing.

---

# 10. Design-Inspiration Workflow

Before building or substantially redesigning a screen, Claude must ask whether the user has:

- A screenshot
- A Figma frame
- A website reference
- CSS
- HTML
- A component example
- Typography or color preferences

The user may place references in a clearly named folder such as:

```text
design-references/
├── home/
├── prediction/
├── adaptive-learning/
├── drift-monitoring/
├── dashboard/
└── simulation/
```

For each screen, Claude must:

1. Inspect supplied references.
2. Summarize the visual characteristics.
3. Identify reusable patterns.
4. Propose a component tree.
5. Ask for approval if the design direction is not already approved.
6. Implement the screen.
7. Test responsiveness and accessibility.
8. Report what was completed.

Do not begin implementation when a required reference is missing and the user explicitly said a reference would be provided first.

---

# 11. Stage-by-Stage Development Protocol

## 11.1 Core Rule

Build one meaningful stage at a time.

At the beginning of every stage, Claude must provide:

- Stage number and title
- Purpose
- What will be inspected
- What will be built
- Files likely to change
- Required inputs from the user
- Required screenshots or references
- Acceptance criteria
- Risks or unresolved questions

Claude must ask for missing inputs before coding.

## 11.2 Stage Completion Rule

At the end of every stage, Claude must:

1. Run relevant tests or checks.
2. Summarize changed files.
3. Summarize functionality completed.
4. Report known limitations.
5. Provide manual verification instructions.
6. State whether the stage is complete.
7. Update `PROJECT_MEMORY.md`.
8. Explicitly announce:

> **Stage X completed. We are ready to move to Stage Y after your approval.**

Claude must not silently begin the next stage.

## 11.3 Approval Gate

After completing a stage, stop and wait for the user's approval before continuing to the next stage.

The user may approve by saying:

- “Approved”
- “Proceed”
- “Move to the next stage”
- “Continue”

If the user reports a bug, remain in the current stage until it is resolved.

---

# 12. Complete Development Roadmap

The following roadmap contains 50 stages. Claude should not implement all stages in one response or one session.

## Foundation and Audit

### Stage 01 — Repository Audit
Inspect the repository, notebook, existing scripts, dependencies, and runtime environment.

### Stage 02 — Architecture Proposal
Propose the final architecture and explain how the existing SVM assets will be preserved.

### Stage 03 — Design Reference Collection
Ask for screenshots, CSS, Figma references, and visual preferences for the first screen.

### Stage 04 — Project Structure
Create or refine the folder structure, configuration files, documentation, and ignore rules.

### Stage 05 — Dependency and Environment Setup
Create a reproducible local setup and verify all dependencies.

### Stage 06 — Baseline Artifact Export
Export and validate the existing SVM model, TF-IDF vectorizer, preprocessing configuration, and evaluation metadata.

### Stage 07 — Baseline Inference Service
Expose the existing static SVM prediction functionality through a clean service interface.

## Email Processing and Prediction

### Stage 08 — Shared Preprocessing Module
Extract the notebook's preprocessing logic into reusable, tested code without silently changing behavior.

### Stage 09 — Raw Email Parser
Support plain text and `.eml` parsing.

### Stage 10 — Email Input API
Create validated endpoints for email analysis.

### Stage 11 — Home Screen
Build the email input and upload interface.

### Stage 12 — Prediction Result Screen
Display classification results and model information.

### Stage 13 — Error and Empty States
Implement validation, loading, error, and empty states.

### Stage 14 — Responsive and Accessibility Pass
Test keyboard access, semantic markup, mobile/tablet layouts, and readable contrast.

## Adaptive Learning

### Stage 15 — Adaptive Model Design Decision
Compare viable online-learning approaches and obtain approval for the selected implementation.

### Stage 16 — Adaptive Model Initialization
Initialize the online model using a defined warm-up dataset and persist its first version.

### Stage 17 — Incremental Update Service
Implement automatic model updates using confirmed labels.

### Stage 18 — Feedback Event Logging
Persist feedback and model-update events in local JSONL files.

### Stage 19 — Feedback API
Create endpoints for `Mark as Spam` and `Mark as Legitimate`.

### Stage 20 — Feedback Interface
Add correction controls to the prediction result screen.

### Stage 21 — Repeated-Email Demonstration
Implement and test the before-feedback/after-feedback demonstration.

### Stage 22 — Model Versioning
Add local model version metadata, timestamps, update reasons, and active-version tracking.

### Stage 23 — Adaptive Learning Panel
Display update counts, model version, feedback counts, and current status.

## ADWIN and Concept Drift

### Stage 24 — ADWIN Integration Design
Define the error stream, trusted-label policy, detector configuration, and drift-response strategy.

### Stage 25 — ADWIN Error Monitoring
Feed confirmed prediction errors into ADWIN and expose detector state.

### Stage 26 — Drift Event Logging
Record drift events with timestamps, stream positions, error statistics, and model versions.

### Stage 27 — Drift Response Mechanism
Implement and test the selected response to a drift signal.

### Stage 28 — Drift Monitoring Interface
Build the drift status and event-history interface.

### Stage 29 — Controlled Drift Dataset
Create a reproducible, labeled simulation stream with clearly defined phases.

### Stage 30 — Simulation Engine
Implement pause/resume/stop/reset controls and sequential stream processing.

### Stage 31 — Drift Demonstration
Demonstrate a controlled distribution change and record whether ADWIN detects it.

### Stage 32 — Simulation Interface
Build the supervisor-facing simulation screen.

## Evaluation and Reporting

### Stage 33 — Streaming Evaluation Metrics
Calculate streaming accuracy, precision, recall, F1-score, and error rate.

### Stage 34 — Static-vs-Adaptive Evaluation
Compare the unchanged SVM baseline with the adaptive model over the same stream.

### Stage 35 — Performance Charts
Build accurate time-series and comparison charts.

### Stage 36 — Confusion Matrix and Error Analysis
Display and inspect false positives and false negatives.

### Stage 37 — Adaptation Metrics
Measure update count, drift count, drift delay where measurable, and processing time.

### Stage 38 — Resource Monitoring
Measure memory usage and prediction/update latency where practical.

### Stage 39 — Performance Dashboard
Combine evaluation metrics and charts into a coherent dashboard.

### Stage 40 — Exportable Reports
Allow local export of evaluation results and event logs as JSON or CSV.

## Quality and Demonstration

### Stage 41 — End-to-End Test Suite
Test the complete flow from email input to prediction, feedback, update, and monitoring.

### Stage 42 — Failure Recovery
Handle corrupt model files, invalid `.eml` files, missing labels, and interrupted simulations.

### Stage 43 — Privacy and Local-Data Review
Ensure logs do not unnecessarily expose sensitive email contents and document local-only behavior.

### Stage 44 — Security Review
Review input validation, file upload restrictions, path handling, XSS risks, and unsafe parsing.

### Stage 45 — UI Polish
Apply approved design refinements and remove inconsistent components.

### Stage 46 — Supervisor Demonstration Mode
Create a guided, repeatable demonstration sequence.

### Stage 47 — Documentation
Update README, setup instructions, architecture documentation, and methodology notes.

### Stage 48 — Academic Consistency Review
Check that implementation terminology agrees with the project title, objectives, and Chapter Three.

### Stage 49 — Final Acceptance Testing
Run the complete acceptance checklist and document known limitations.

### Stage 50 — Final Handover
Prepare the project for local demonstration, GitHub publication if requested, and final supervisor review.

---

# 13. API Conventions

Use consistent HTTP behavior.

## 13.1 Success Format

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

## 13.2 Error Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "A valid email body is required"
  }
}
```

## 13.3 Rules

- Validate all incoming data.
- Return appropriate HTTP status codes.
- Never expose stack traces to the frontend.
- Log technical details locally.
- Use stable endpoint names.
- Document request and response schemas.
- Avoid unnecessary endpoints.
- Do not introduce authentication endpoints because authentication is out of scope.

Potential endpoints include:

```text
GET    /api/health
POST   /api/predict
POST   /api/feedback
GET    /api/adaptive/status
GET    /api/drift/status
GET    /api/events
POST   /api/simulation/start
POST   /api/simulation/pause
POST   /api/simulation/stop
POST   /api/simulation/reset
GET    /api/evaluation/summary
```

Adapt the endpoint list to the final architecture.

---

# 14. Local File and Logging Conventions

Use UTF-8 text files and atomic writes where practical.

Recommended event fields:

```json
{
  "event_id": "generated-local-id",
  "timestamp": "ISO-8601 timestamp",
  "event_type": "feedback|model_update|drift|prediction|error",
  "model_version": "adaptive-1.0.0",
  "stream_position": 123,
  "details": {}
}
```

Do not store complete email bodies in logs by default. Prefer:

- A content hash
- A short safe preview
- The label
- The prediction
- Metadata required for the demonstration

If full email storage is required for the academic demonstration, make it explicit, local-only, configurable, and documented.

---

# 15. Security and Privacy Requirements

Even without login or a database:

- Restrict uploaded file size.
- Validate `.eml` file content.
- Prevent path traversal.
- Never execute uploaded content.
- Escape email content before rendering it in HTML.
- Avoid unsafe HTML rendering.
- Sanitize or strip active content.
- Do not expose local filesystem paths to the browser.
- Do not include secrets in source code.
- Use `.env.example`, not real secrets.
- Handle malformed input safely.
- Avoid logging full email content by default.
- Explain that the application is intended for local academic use.

The system must not send emails or communicate with external mail servers unless explicitly approved.

---

# 16. Git Workflow

Use Git consistently.

## Commit Format

Use concise, meaningful commit messages:

```text
feat: add adaptive feedback update service
fix: handle malformed eml uploads
test: add ADWIN error-stream tests
refactor: extract shared email preprocessing
docs: update architecture decisions
```

Before committing:

1. Run tests.
2. Run linting or formatting checks where configured.
3. Inspect the diff.
4. Ensure no secrets, datasets with restricted content, generated artifacts, or environment files are accidentally committed.
5. Summarize the commit for the user.

Do not create branches, push to GitHub, or rewrite Git history without explicit approval.

---

# 17. Testing Standards

Every stage must include appropriate tests.

Minimum test categories:

- Unit tests for preprocessing
- Unit tests for email parsing
- Model artifact loading tests
- Prediction service tests
- Feedback-label validation tests
- Incremental-update tests
- ADWIN error-stream tests
- Drift-response tests
- File persistence tests
- API tests
- UI interaction tests where tooling is available
- End-to-end demonstration test

Test both:

- Correct predictions
- Incorrect predictions and recovery paths

Never use fabricated metrics in the application. Example values may be used only in static design mockups and must be clearly marked as examples.

---

# 18. Definition of Done

A stage is complete only when:

- The intended functionality is implemented.
- Existing functionality has not been unnecessarily broken.
- Relevant tests pass.
- Error states are handled.
- The interface is usable at the target screen sizes.
- Accessibility has been considered.
- No secrets or unsafe files were introduced.
- Documentation has been updated where necessary.
- The user has received a concise implementation summary.
- Known limitations are stated.
- `PROJECT_MEMORY.md` has been updated.
- Claude has explicitly announced the next stage and stopped for approval.

---

# 19. Persistent-Memory Update Format

After each approved stage, update this document under a dated or clearly labeled project-state section.

Maintain the following records:

## Completed Stages

- Stage number
- Date
- Summary
- Files changed
- Tests performed

## Reusable Components

- Component name
- Location
- Purpose
- Props or public interface
- Usage notes

## ML Artifacts

- Static model path
- Adaptive model path
- Vectorizer path
- Model versions
- Training configuration
- Known limitations

## API Endpoints

- Method
- Path
- Purpose
- Request schema
- Response schema

## Design Tokens

- Typography
- Colors
- Spacing
- Border radii
- Shadows
- Component conventions

## Architectural Decisions

- Decision
- Reason
- Date
- Alternatives considered

## Known Issues

- Issue
- Severity
- Workaround
- Planned resolution

## Next Steps

- Next approved stage
- Outstanding inputs
- Required screenshots or references

Do not delete historical decisions without recording why they were superseded.

---

# 20. Final Behavioral Instructions for Claude Code

1. Read this file before every development session.
2. Inspect the actual repository before making assumptions.
3. Treat the existing SVM notebook and evaluation as baseline work.
4. Do not replace the SVM with an online model without explaining the reason.
5. Do not call standard `LinearSVC` an online-learning model.
6. Do not call ADWIN a classifier.
7. Do not claim that a single feedback correction proves concept drift.
8. Do not claim that drift occurred unless the detector actually signaled it.
9. Do not fabricate confidence scores, metrics, drift events, or model improvements.
10. Do not add login, admin, database, payments, external email integrations, or paid services.
11. Ask for screenshots and design references before implementing a screen when appropriate.
12. Build one stage at a time.
13. Stop at every stage boundary and wait for approval.
14. Update this file after each approved stage.
15. Preserve working code and explain all significant architectural changes.
16. Prefer simple, transparent, locally runnable solutions.
17. Use the phrase below at every stage boundary:

> **Stage [number] completed. We are ready to move to Stage [next number] after your approval.**

---

# 21. Initial Instruction to Claude Code

Begin with **Stage 01 — Repository Audit**.

Before writing implementation code:

1. Inspect the complete repository.
2. Locate the supplied SVM notebook and all existing source files.
3. Identify the current Python environment and package configuration.
4. Determine whether a frontend or backend already exists.
5. Inspect how the trained SVM and TF-IDF vectorizer are currently represented.
6. Identify what must be exported to reusable model artifacts.
7. Report the proposed next steps.
8. Ask for any required screenshots or design references for the first interface.
9. Do not proceed to Stage 02 until Stage 01 is explicitly approved.

---

# 22. Project State — 2026-09-18

> The user explicitly instructed Claude Code to proceed through all
> stages without stopping for per-stage approval ("proceed with all the
> stages, do not ask me for permission to move to the next stage"). The
> stage-boundary approval gate in §11.3 is waived for this project; the
> rest of this document's engineering rules remain in force. This
> section is updated as work continues, per §19/§18.

## Completed Stages

- **Stage 01 — Repository Audit.** Found only the supplied notebook +
  dataset, no existing backend/frontend. Environment: Python 3.13.9,
  scikit-learn 1.7.2 available globally; `river` not installed (needed
  for Stage 15/24).
- **Stage 02 — Architecture Proposal.** FastAPI backend (feature-oriented,
  per §6) + vanilla HTML/CSS/JS frontend (no React — no existing frontend
  to match, and a build toolchain added no value here per §5.2). No
  database (local JSONL/joblib/json files only, per §5.3).
- **Stage 03 — Design Reference Collection.** User provided no
  screenshots/Figma/CSS. Built the UI from §9.2's own description
  (Apple/Linear/Stripe-inspired: clean cards, restrained color, system
  font stack, light + dark tokens). `design-references/<screen>/`
  folders were created and are still empty — if real references are
  supplied later, revisit Stage 45 (UI Polish) against them.
- **Stage 04 — Project Structure.** Created the structure in §6 (backend/
  frontend/ scripts/ artifacts/ data/ logs/ notebooks/), moved the
  supplied notebook to `notebooks/` and dataset to `data/raw/`.
- **Stage 05 — Dependency and Environment Setup.** `.venv` created;
  `requirements.txt` pinned via `pip freeze`; NLTK corpora
  downloaded (punkt, punkt_tab, stopwords, wordnet, omw-1.4,
  averaged_perceptron_tagger[_eng]). `pyproject.toml` configures pytest.
  Git repo initialized; dataset and generated artifacts are gitignored
  (65MB CSV, joblib binaries).
- **Stage 06 — Baseline Artifact Export.** `scripts/train_static_model.py`
  faithfully reproduces the notebook (see Architectural Decisions below
  for the one deliberate deviation: multiprocessing for speed). Real
  dataset size discovered to be **39,154 rows**, not the 1.3M implied by
  `wc -l` on the raw CSV — email bodies contain embedded newlines inside
  quoted CSV fields, which `wc -l` counts as extra lines but pandas
  correctly parses as single rows. Exported: `model.joblib`,
  `tfidf_vectorizer.joblib`, `model_metadata.json` with real metrics
  (see ML Artifacts below). Runtime: 37.2s.
- **Stage 07 — Baseline Inference Service.** `backend/app/ml/static_inference.py`
  — `StaticSVMService`, exposes `decision_function` as `decision_score`
  (LinearSVC has no `predict_proba`; nothing was faked).
- **Stage 08 — Shared Preprocessing Module.** `backend/app/ml/preprocessing.py`.
  Extracted from notebook cells 9-15/17/19/22-26 (`clean_text`) and
  cells 22-26 (`tokenize_stem_lemmatize`). Deliberately does **not**
  include frequent/rare-word pruning (notebook cells 20-21) — confirmed
  by reading the notebook's own custom-email-prediction cell (38) that
  pruning is never reapplied at inference time, only at training-corpus
  prep. See the module's docstring.
- **Stage 09 — Raw Email Parser.** `backend/app/ml/email_parser.py`
  handles plain text and `.eml` upload (stdlib `email` package only, no
  execution of any embedded content).
- **Stage 10 — Email Input API.** `POST /api/predict`,
  `POST /api/predict/eml` in `backend/app/api/predict.py`.
- **Stage 11 — Home Screen.** `frontend/templates/index.html` Analyzer
  tab: subject/body form + `.eml` upload, both wired to the API.
- **Stage 12 — Prediction Result Screen.** Static + adaptive result cards
  with decision score / confidence, disclaimer text, feedback buttons.
- **Stage 13 — Error and Empty States.** Empty/loading/error states for
  the result card; inline validation for empty body; server-side
  validation errors surfaced via the `{success:false, error:{...}}`
  envelope.
- **Stage 14 — Responsive and Accessibility Pass.** Verified at 1280px
  and 390px viewports (Playwright screenshots); `role="tablist"`/
  `role="tabpanel"` with arrow-key navigation; `aria-live` regions for
  status/feedback; semantic form labels. Not tested with a real screen
  reader — flagged as a limitation below.
- **Stage 15 — Adaptive Model Design Decision.** ~~Chose
  `SGDClassifier(loss="log_loss")` + `partial_fit`, **sharing the static
  model's fixed TF-IDF vectorizer** rather than fitting a second one.~~
  **SUPERSEDED 2026-09-18** — this was an undocumented implementation
  choice, not what the academic study specifies. Corrected to River's
  `MultinomialNB` + River's own `TFIDF`, per explicit user/supervisor
  feedback. See "Architecture Correction" section near the end of this
  document for the full record; original entry preserved here per §19's
  no-silent-deletion rule.
- **Stage 16 — Adaptive Model Initialization.** `scripts/initialize_adaptive_model.py`
  warm-starts on the *same* train split as the static baseline (same
  `train_test_split` call/seed on the same row order = same held-out
  test set for both models), 8 shuffled `partial_fit` epochs. Initial
  eval on held-out test: Accuracy 98.89%, F1 99.01%.
- **Stage 17 — Incremental Update Service.** `backend/app/ml/adaptive_model.py`
  — `AdaptiveModelService.update_one()`; one `partial_fit` call per
  confirmed feedback label, auto-persists model + version metadata, no
  separate "retrain" action exists.
- **Stage 18 — Feedback Event Logging.** `backend/app/storage/event_log.py`
  (generic JSONL append/read) + `backend/app/storage/privacy.py` (content
  hash + truncated preview instead of full body by default, per §14/§15
  — toggle via `LOG_FULL_EMAIL_BODY`).
- **Stage 19 — Feedback API.** `POST /api/feedback` in
  `backend/app/api/feedback.py`, orchestrated by
  `backend/app/services/feedback_service.py` implementing §8.3's exact
  sequence (error → ADWIN → partial_fit → drift check → logs).
- **Stage 20 — Feedback Interface.** "Mark as Spam"/"Mark as Legitimate"
  buttons on the result card; disabled during submission and after
  feedback is applied; shows the resulting model version.
- **Stage 21 — Repeated-Email Demonstration.** Verified manually: same
  email text predicted, corrected via feedback, model version bumps
  (`adaptive-1.0.0` → `.1` → `.2` → `.3` across test runs). UI copy
  originally used the non-guaranteeing wording §5's roadmap requires
  ("the next prediction *may* reflect this feedback") — accurate at the
  time, since an unweighted `partial_fit` correction was not guaranteed
  to change anything (see the Known Issues entry on feedback having no
  practical effect). **Updated 2026-09-19**, per explicit user request:
  now reads "the next prediction *will* reflect this feedback." This is
  no longer just softer copy — it is now a true statement of the
  implementation. §7.4's `FEEDBACK_CONFIDENCE_MARGIN` loop
  (`AdaptiveModelService.update_one`) does not return success until the
  model's own `predict_proba_one` confirms the corrected label actually
  crossed the confidence margin, so by the time this message is shown,
  the flip has already happened, not merely been attempted. The
  original roadmap wording assumed a single unweighted update that
  might or might not take effect; that assumption no longer holds for
  this implementation, which is why the copy was allowed to change.
- **Stage 22 — Model Versioning.** Adaptive metadata tracks
  `model_version`, `update_count`, `feedback_count`,
  `last_updated_at_unix`, `status` in `artifacts/metadata/adaptive_model_metadata.json`.
- **Stage 23 — Adaptive Learning Panel.** Frontend tab showing version,
  feedback count, update count, last update time, known limitations
  (read live from the API, not hardcoded).
- **Stage 24 — ADWIN Integration Design + Stage 25 — ADWIN Error
  Monitoring.** `backend/app/ml/drift_monitor.py` — `DriftMonitor` wraps
  `river.drift.ADWIN`, fed only confirmed-label errors (0/1), strictly
  separated from the classifier (see §8.1 docstring reference). State
  persisted to `artifacts/metadata/drift_state.json` +
  `artifacts/adaptive_model/adwin_detector.joblib`.
- **Stage 26 — Drift Event Logging.** Drift events appended to
  `logs/drift_events.jsonl` from `feedback_service.py` when
  `drift_detected` is true.
- **Stage 28 — Drift Monitoring Interface.** Frontend tab: monitored
  count, error rate, drift count, last drift time, recent drift events.
- **Stage 33/34 (partial) — Evaluation.** `GET /api/evaluation/summary`
  + Dashboard tab compare static vs. adaptive metrics on their shared
  held-out test set, with an explicit dependency-free bar chart.
- **Stage 41 (partial) — Test Suite.** 22 pytest tests: preprocessing
  unit tests, `.eml` parser unit tests, full API integration tests
  (predict, feedback cycle + duplicate rejection, unknown prediction_id,
  adaptive status delta, drift status shape, evaluation summary,
  event filtering, `.eml` upload incl. empty-file rejection). Tests run
  against an isolated tmp-dir copy of `artifacts/`/`logs/` — never
  mutate the live demo's adaptive model. All 22 pass.
- **Stage 44 (partial) — Security Review.** Found and fixed a real XSS
  vulnerability: the Activity Log rendered event previews (derived from
  user-submitted email bodies) via `innerHTML` string interpolation.
  Fixed by switching to `textContent`-based DOM construction. Verified
  with a Playwright test injecting `<img src=x onerror=alert(1)>` as an
  email body — confirmed it renders as inert text and no dialog fires.
  Upload size is capped (`MAX_UPLOAD_SIZE_BYTES`); `.eml` parsing never
  executes content; stack traces are never sent to the client (logged
  server-side only, generic `INTERNAL_ERROR` returned).

- **Stage 45 (partial) — UI Polish.** User requested Gmail-inspired visual
  design with a real light/dark toggle (not just OS-level). Rebuilt the
  frontend: left sidebar nav (replacing the top tab bar) with inline SVG
  icons, a Gmail-style pill "New Analysis" compose button, selected-nav
  pill highlight, Gmail's actual typeface (Roboto, self-hosted via
  `@fontsource/roboto` — Apache 2.0, no CDN/runtime network dependency,
  files in `frontend/static/fonts/`), Gmail's Material color palette
  (blue #1a73e8 accent, red #d93025 spam, green #188038 ham), denser
  14px-base typography, list-row-style Activity Log with colored
  per-event-type chips (Gmail inbox-label convention), and a manual
  theme toggle (sun/moon icon in the top bar) that persists to
  `localStorage` and overrides `prefers-color-scheme` via a
  `data-theme` attribute on `<html>` (inline script in `<head>` applies
  the stored choice before first paint, avoiding a flash of the wrong
  theme). Mobile: sidebar collapses to a slide-out drawer with a
  click-to-close backdrop. Verified in both themes, desktop (1360px) and
  mobile (390px) via Playwright — 0 console errors, 0 network failures,
  theme choice confirmed to survive a full page reload.

## Visual/Functional Verification Performed

Per this document's own verification-loop requirements: ran the app in
a real headless Chromium (Playwright) against the live FastAPI server on
port 8020 (port 8000 was occupied by an unrelated project, APPLYAI —
left untouched). Found and fixed two real bugs before calling any stage
done:

1. `[hidden]` attribute was being overridden by `.loading-state { display:
   flex }` (equal-specificity author CSS beats the UA default), causing
   the loading spinner to render simultaneously with empty/content
   states. Fixed with a global `[hidden] { display: none !important; }`
   rule.
2. The Dashboard's comparison bar chart used `<span>` elements for
   `.bar-track`/`.bar-fill`; `.bar-fill` is nested two levels inside the
   grid row (not itself a grid item), so it was never blockified and its
   `width`/`height` were silently ignored per the CSS spec, collapsing
   it to 0×0. Fixed with explicit `display: block`.

Re-verified after both fixes (fresh Playwright run): 0 console errors,
0 network failures, correct rendering at 1280px and 390px viewports,
correct rendering with `prefers-color-scheme: dark`.

## Reusable Components

| Component | Location | Purpose |
|---|---|---|
| `clean_text`, `tokenize_stem_lemmatize`, `preprocess_for_inference` | `backend/app/ml/preprocessing.py` | Shared text pipeline, training + inference |
| `StaticSVMService` | `backend/app/ml/static_inference.py` | Loads/serves the LinearSVC baseline |
| `AdaptiveModelService` | `backend/app/ml/adaptive_model.py` | Loads/serves/updates the SGDClassifier |
| `DriftMonitor` | `backend/app/ml/drift_monitor.py` | ADWIN wrapper, strictly non-classifying |
| `append_event`/`read_events` | `backend/app/storage/event_log.py` | Generic JSONL event stream I/O |
| `safe_preview`/`content_hash` | `backend/app/storage/privacy.py` | Privacy-conscious log content |
| `success`/`error` | `backend/app/schemas/common.py` | §13 API envelope |
| CSS design tokens | `frontend/static/css/styles.css` (`:root`) | Colors/spacing/radii, light+dark |
| Tab system (`role=tablist`) | `frontend/templates/index.html` + `app.js` | Reused across all 5 panels |
| `.stat-tile`, `.card`, `.btn-*`, `.result-badge` | `frontend/static/css/styles.css` | Reused across Analyzer/Adaptive/Drift/Dashboard |

## ML Artifacts

- Static model: `artifacts/static_svm/model.joblib` (`static-1.0.0`) —
  `LinearSVC`. Accuracy 99.66%, Precision 99.63%, Recall 99.75%, F1
  99.69% (test n=7,831). Confusion matrix TN=3446 FP=16 FN=11 TP=4358.
- Static vectorizer: `artifacts/vectorizer/tfidf_vectorizer.joblib` —
  scikit-learn TF-IDF, max_features=5000, used **only by the static
  model**. Vocabulary fixed at fit time.
- Adaptive model: `artifacts/adaptive_model/adaptive_model.joblib` — a
  River `Pipeline(TFIDF, MultinomialNB)` (switched from scikit-learn
  `SGDClassifier` 2026-09-18 to match the academic study's specified
  architecture; see §23). Owns its own River TFIDF vectorizer,
  independent of the static model's — **its vocabulary grows online**
  with every `learn_one` call, unlike the static model's frozen one.
  Version increments as `adaptive-1.0.<update_count>` on every
  feedback-driven update. Initial (warm-up) eval on the *same* held-out
  test set: Accuracy 98.71%, Precision 99.84%, Recall 97.85%, F1
  98.83%. Confusion matrix TN=3455 FP=7 FN=94 TP=4275. Each confirmed
  feedback correction is applied via `learn_one` repeated
  `FEEDBACK_LEARN_REPEATS=200` times (tuned so one correction reliably
  flips the prediction, per explicit user request — see
  `backend/app/ml/adaptive_model.py`).
- ADWIN detector: `artifacts/adaptive_model/adwin_detector.joblib`
  (`river.drift.ADWIN`, default params — not yet tuned against a
  controlled drift dataset; that's Stage 29-31, not yet built).
- Training config: `C=1.0, max_iter=1000, random_state=42` (SVM);
  `loss="log_loss", random_state=42`, 8 warm-up epochs (SGD).

## API Endpoints (implemented)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness + model load status |
| POST | `/api/predict` | Predict from subject/body JSON |
| POST | `/api/predict/eml` | Predict from uploaded `.eml` file |
| POST | `/api/feedback` | Submit correction, drives adaptive update + ADWIN |
| GET | `/api/adaptive/status` | Adaptive model version/counts/limitations |
| GET | `/api/drift/status` | ADWIN state + recent drift events |
| GET | `/api/events` | Combined/filtered event log |
| GET | `/api/evaluation/summary` | Static vs. adaptive metrics + streaming error rate |

Not yet implemented: `/api/simulation/*` (Stage 30 — Simulation Engine
doesn't exist yet).

## Design Tokens

Light + dark palettes as CSS custom properties in `:root` /
`prefers-color-scheme: dark`; system font stack (no web fonts, matches
"local, no paid services" scope); `--radius-sm/md/lg` (6/10/16px);
`--space-1..7` (4→48px scale); accent `#2f6fed` (light) /
`#6d93f7` (dark); semantic spam/ham colors kept distinct from the accent
so status is never conveyed by color alone (badges also carry text:
"SPAM"/"HAM").

## Architectural Decisions

1. **Adaptive model shares the static model's TF-IDF vectorizer** rather
   than fitting its own. *Reason:* §7.2 requires "a compatible feature
   representation"; a second vectorizer would let the two models drift
   onto incomparable feature spaces, breaking the Stage 34 comparison.
   *Alternative considered:* River's own online text vectorizer — would
   let vocabulary grow online, but breaks direct comparability with the
   frozen SVM baseline and adds a second dependency surface. Not chosen.
2. **Frequent/rare-word pruning is training-only, never applied at
   inference.** *Reason:* the supplied notebook's own custom-email cell
   (38) doesn't reapply it — this is the notebook author's own
   established behavior, not a Claude Code judgment call.
3. **Static baseline's frequent/rare-word pruning fits on the full
   corpus before the train/test split** (preserved, not fixed).
   *Reason:* §7.1 forbids invalidating the existing baseline evaluation;
   changing this would silently change the reported metrics. Documented
   as a known limitation in the exported metadata instead of silently
   corrected.
4. **Training/warm-up preprocessing parallelized with `multiprocessing.Pool`**
   (7 workers). *Reason:* pure engineering — single-threaded NLTK
   tokenize/stem/lemmatize over even 39K rows measured ~250s; this is
   the one place the code deviates from a literal cell-by-cell port, and
   it does not change per-row output, only wall-clock time.
5. **Plain HTML/CSS/JS frontend, no build step.** *Reason:* §5.2 — no
   existing frontend to match, and a bundler adds no value for a
   single-page academic demo. Revisit only if a future stage needs
   client-side routing or component state complex enough to justify it.
6. **In-memory `PredictionStore` (capped at 5,000 entries, JSONL-backed)**
   rather than a database. *Reason:* §3.2 explicitly forbids a database;
   feedback needs to look up the original prediction's processed text by
   `prediction_id`, which the human-readable `logs/predictions.jsonl`
   (privacy-truncated) can't serve. This store is operational state, not
   a log — kept separate from `logs/` for that reason.
7. **Port 8020, not 8000.** *Reason:* port 8000 is already bound by an
   unrelated project on this machine (`APPLYAI-BACKEND`'s `uvicorn api:app
   --port 8000`). Left that process untouched; this project's default
   port is set in `.env.example`.

## Known Issues

| Issue | Severity | Workaround | Planned resolution |
|---|---|---|---|
| Static baseline's frequent/rare-word pruning leaks test-set statistics into training (fit before split) | Low (inherited from supplied notebook, documented) | None — preserved deliberately | Would require re-deriving baseline metrics; out of scope unless requested |
| ADWIN uses library defaults, untuned | Medium | None yet | Stage 29-31 (controlled drift dataset + demonstration) will validate/tune against a known distribution shift |
| No real screen-reader testing performed | Medium | ARIA roles/labels are present but unverified with e.g. VoiceOver | Revisit at Stage 45 (UI Polish) |
| `PredictionStore` is in-memory (survives only for the process lifetime, capped at 5,000 entries) | Low | Predictions older than the cap or after a restart can't receive feedback | Acceptable for an academic local demo; would need persistence for production |
| No rate limiting / abuse protection on any endpoint | Low (local-only academic tool) | None | Out of scope per §3.2 unless requirements change |

**Fixed 2026-09-18** (was listed here as open, now resolved): *feedback corrections had no practical effect on predictions.* Root cause: `scripts/initialize_adaptive_model.py`'s warm-up (8 epochs over 31,323 rows) pushed `SGDClassifier`'s internal step counter (`t_`) to 250,597 before any online learning began; its `learning_rate="optimal"` schedule derives step size from that counter, so a single unweighted `partial_fit` per feedback correction moved P(spam) by well under 1 point — confirmed by direct measurement, and even 50 repeated identical corrections on the same example didn't flip its prediction. Fixed in `AdaptiveModelService.update_one` (`backend/app/ml/adaptive_model.py`) by weighting each correction via `sample_weight=25.0` (`FEEDBACK_SAMPLE_WEIGHT`), tuned as "moderate": one correction now swings confidence ~12-15 points, and confidently-wrong predictions flip after 2-3 corrections rather than never. Verified via `backend/tests/test_api.py::test_feedback_meaningfully_shifts_adaptive_confidence` (regression guard) and live through the running server. This constant is a judgment call, not a derived optimum — revisit if real usage shows it over- or under-reacts.

*(Historical note: `SGDClassifier` itself was later replaced with River's `MultinomialNB` — see §23 — because the academic study specifies River, not scikit-learn SGD. The underlying bug and fix described above no longer apply to the current implementation; they're preserved here as the record of what was tried and why. The equivalent mechanism in the current model is `FEEDBACK_LEARN_REPEATS=200`, documented in §23.)*

## Next Steps (not yet built)

- **Stage 27 — Drift Response Mechanism.** Drift is currently detected
  and logged (Stage 24-26) but nothing *acts* on it yet beyond visibility
  in the Drift Monitoring panel. Needs a chosen strategy (§8.4) —
  recommend "replay recent confirmed examples" since `logs/feedback.jsonl`
  already has everything needed, no new storage required.
- **Stage 29-32 — Controlled Drift Dataset + Simulation Engine +
  Simulation Interface.** Not started. This is the largest remaining
  chunk of work: a reproducible phased dataset (ordinary spam → obfuscated
  → phishing → altered formatting), a start/pause/stop/reset engine, and
  a supervisor-facing screen. Needs `/api/simulation/*` endpoints (listed
  in §13.3 but not yet built).
- **Stage 35-40 — richer dashboard.** Current Dashboard is a lightweight
  Stage 33/34 comparison. Missing: real confusion-matrix display (Stage
  36), adaptation metrics like drift delay (Stage 37), resource/latency
  monitoring (Stage 38), exportable JSON/CSV reports (Stage 40).
- **Stage 42 — Failure Recovery.** Not explicitly tested: corrupt model
  file on startup, interrupted simulation (n/a until Stage 30 exists),
  concurrent feedback race conditions beyond the basic thread locks
  already in `AdaptiveModelService`/`DriftMonitor`.
- **Stage 43 — deeper Privacy Review.** Basic privacy-by-default logging
  exists (Stage 18); a full pass (e.g. reviewing `PredictionStore`'s
  retention policy explicitly) hasn't been done as its own stage.
- **Stage 45-50.** UI Polish (pending real design references if the user
  provides any), Supervisor Demonstration Mode, full Documentation pass
  beyond this file + README, Academic Consistency Review against the
  user's actual Chapter Three (not available to Claude Code), Final
  Acceptance Testing, Final Handover.

Server is currently running locally at `http://127.0.0.1:8020/` for
manual use (`uvicorn app.main:app --app-dir backend --host 127.0.0.1
--port 8020`, started via `nohup`, logs in `logs/uvicorn.log`).

---

# 23. Architecture Correction — 2026-09-18: Adaptive Classifier Switched to River MultinomialNB

## What was wrong

Stage 15 (Adaptive Model Design Decision) chose scikit-learn's
`SGDClassifier` for the adaptive component. That was Claude Code's own
technical judgment call, made without confirming it against the actual
academic study — it was never explicitly specified anywhere in this
document. The user surfaced (via their supervisor's review of the
study) that the study explicitly names:

- scikit-learn SVM as the static baseline (correct, unchanged — this
  is what `notebooks/Python SVM Spam Detection System.ipynb` and
  `scripts/train_static_model.py` already implement).
- River for online learning and ADWIN drift detection.
- Hoeffding Tree and Online Naive Bayes as the proposed adaptive
  classifiers.
- (The study also has its own internal error elsewhere, incorrectly
  labeling a Naive-Bayes-shaped description as "Online SVM" — not
  Claude Code's error, noted here only because it's part of why this
  needed a human, study-literate judgment call rather than a technical
  guess.)

`SGDClassifier` was never mentioned. Per the user's explicit direction,
this was corrected to **River's `MultinomialNB`**, keeping the
already-trained scikit-learn SVM as the static baseline exactly as
before, and keeping River's `ADWIN` exactly as before (it was already
correct — River was already a dependency solely for the drift
detector, per Stage 24/25).

## What changed

- **`backend/app/ml/adaptive_model.py`** — `AdaptiveModelService`
  rewritten around a `river.compose.Pipeline(TFIDF, MultinomialNB)`
  instead of `sklearn.linear_model.SGDClassifier`. Public interface
  (`predict`, `update_one`, `model_version`, `metadata`) kept the same
  shape so callers didn't need structural changes — but `predict`/
  `update_one` now take the cleaned text string directly rather than a
  pre-vectorized sklearn feature matrix, since River's `TFIDF` does its
  own (independent) vectorization inside the pipeline.
- **`scripts/initialize_adaptive_model.py`** — rewritten to warm-start
  via `learn_one` row-by-row (River has no batch/vectorized fit path)
  over the same 8 shuffled epochs and the same train/test split as
  before (same `train_test_split` call/seed on the same row order, so
  the held-out test set is still identical to the static baseline's —
  Stage 34 comparison stays fair). Runtime: ~93s for 250,584 total
  `learn_one` calls (benchmarked first at ~3,450 rows/sec before
  committing to the full run).
- **`backend/app/services/prediction_service.py` /
  `feedback_service.py`** — no longer call
  `static_service.transform(processed_text)` to build a shared feature
  matrix for the adaptive model. The adaptive model now receives the
  cleaned text directly and vectorizes it itself.
- **Feature-sharing architecture reversed**: the adaptive model
  previously shared the static SVM's frozen TF-IDF vectorizer
  (Architectural Decision #1, now superseded — see below). It now owns
  its own River `TFIDF` transformer, whose vocabulary **genuinely grows
  online** as new emails are learned. This actually resolves a
  previously-documented limitation ("TF-IDF vectorizer's vocabulary is
  fixed... never updated online") rather than just relocating it.
- **Feedback-strength mechanism ported**: the "flip completely" request
  from earlier in this session was re-verified against the new model.
  `SGDClassifier`'s `sample_weight` doesn't apply to `MultinomialNB` the
  same way, but since Naive Bayes parameters are just additive
  word/class counts, calling `learn_one` on the same example N times
  has an equivalent effect (confirmed empirically: scales
  proportionally). `FEEDBACK_LEARN_REPEATS = 200` replaces
  `FEEDBACK_SAMPLE_WEIGHT = 150`. Retuned from scratch against the new
  model (not copied from the old value) — see
  `backend/app/ml/adaptive_model.py` docstring for the measurements.

## New adaptive model results (warm-up, held-out test set)

Accuracy 98.71%, Precision 99.84%, Recall 97.85%, F1 98.83% — close to
the static SVM baseline (99.66%/99.63%/99.75%/99.69%) and slightly
better precision than the previous SGDClassifier's warm-up (98.89%/
98.88%/99.13%/99.01%). Confusion matrix: TN=3455 FP=7 FN=94 TP=4275.

## Verification performed

- Benchmarked `learn_one` throughput on a sample before running the
  full ~250K-call warm-up, to avoid discovering a multi-hour runtime
  partway through.
- Re-ran the full pytest suite after every change (23/23 passing
  throughout).
- Re-verified the "flip completely" behavior live through the actual
  running server (not just the offline simulation): a fresh loan-offer
  spam email predicted at 71.87% confidence flipped to "legitimate" at
  81.35% confidence after exactly one correction.
- Re-ran the stability check (a large correction on one email must not
  disturb unrelated predictions) — confirmed **zero** effect on
  unrelated predictions with River MultinomialNB, an even stronger
  guarantee than the SGDClassifier version had, since Naive Bayes
  updates are per-word rather than dense gradient updates touching
  every feature weight.
- Discovered and accounted for a real asymmetry: correcting toward
  "spam" needed ~200 repeats where correcting toward "ham" often
  flipped in 1, because this dataset's warm-up left spam-associated
  words with much stronger accumulated evidence. `FEEDBACK_LEARN_REPEATS`
  was tuned against the harder direction, not the easier one.
- Playwright browser check after restarting the live server — 0
  console errors, prediction/feedback/Adaptive Learning panel all
  render correctly with the new model.

## Architectural Decisions — supersession record

Decision #1 in §"Architectural Decisions" ("Adaptive model shares the
static model's TF-IDF vectorizer") is **superseded** by this change.
Original reasoning (feature-space comparability for Stage 34) no longer
applies: the study's specified architecture has the adaptive component
own its own River-native online vectorizer, independent of the static
SVM's fixed scikit-learn one. Comparability between the two models is
still maintained the way that matters for Stage 34 — an identical
held-out test set — just not via a shared feature matrix.

## Updated Known Limitations (adaptive model)

Replacing the SGDClassifier-era limitations list
(`artifacts/metadata/adaptive_model_metadata.json`):

- Naive Bayes assumes conditional independence between words given the
  class label — rarely exactly true for natural language, but works
  well in practice for spam/ham text classification (this is the
  standard, expected caveat for Naive Bayes, worth stating explicitly
  in the academic write-up rather than treated as a hidden weakness).
- Warm-up uses a fixed number of shuffled passes over the train split
  rather than true streaming order; it establishes a reasonable
  starting point before online feedback updates begin.
- (Resolved, no longer a limitation: TF-IDF vocabulary is no longer
  frozen — River's `TFIDF` updates online with every `learn_one` call.)

## Follow-up fix (same day): fixed repeat count wasn't actually reliable

`FEEDBACK_LEARN_REPEATS=200` (above) was tuned against 3 hand-picked
confidently-wrong examples and looked solid. The user then reported the
exact "flip completely" bug again in real use: a "Casino bonus" spam
email at 98.4% confidence, corrected to legitimate, still read spam on
re-check. Reproduced it directly (not just taken on report) via a
scripted batch of 5 fresh emails through the live API: **1 of 5
genuinely failed to flip** (200 repeats only pulled 98.4% down to
56.9% — short of crossing 50%).

Root cause: how much evidence is needed to overturn a wrong prediction
scales with how confident that wrong prediction was, and that varies
per email. A fixed repeat count can't be both large enough for hard
cases and not wasteful for easy ones — there will always be some
email confident enough to beat whatever fixed number is chosen.

**Fix**: replaced the fixed count with a loop in
`AdaptiveModelService.update_one` that calls `learn_one` on the same
correction repeatedly, checking `predict_proba_one` after each call,
until confidence in the corrected label actually crosses
`FEEDBACK_CONFIDENCE_MARGIN=0.6` — capped at
`FEEDBACK_MAX_LEARN_CALLS=5000` as a safety bound. This guarantees the
flip regardless of how confident the original wrong prediction was,
rather than betting on a number covering the worst case.

Verified: re-ran the same 5-email batch that found the bug — 5/5 flip
now, including a fresh 99.6%-confident case. Also verified through the
actual browser UI (Playwright), not just the API directly. Full test
suite (23/23) re-run and passing.

**Latency note, discovered while investigating, not a regression from
this fix**: feedback submission takes ~1.2-1.5s end to end. Profiled
it — `joblib.dump` of the model to disk alone takes ~1.16s (the
vocabulary has grown large from warm-up plus testing); the
confidence-margin loop itself is fast (learn_one + predict_proba_one
together run in well under 100ms even for hard cases). This save-to-
disk cost existed before this fix too (every `update_one` call has
always persisted the full model). Not addressed here since it wasn't
what was reported and the current latency is within acceptable bounds
for a "submit and see confirmation" UI action (the frontend already
shows a "Submitting feedback…" state) — flagged here as a known
characteristic in case it needs revisiting if feedback volume grows.

---

# 24. Deployment — 2026-09-19

- **GitHub**: public repo at
  https://github.com/JOSHODIN2019/adaptive-email-spam-detection.
  Dataset (`data/raw/*.csv`) and runtime logs remain gitignored; the
  small trained artifacts (~4.2MB: static SVM, TF-IDF vectorizer,
  adaptive model, ADWIN detector) are tracked directly so a fresh
  clone/deploy never needs the 65MB dataset. Artifacts were
  regenerated fresh immediately before committing, so the shipped
  baseline is a clean warm-up (`adaptive-1.0.0`), not the accumulated
  ad-hoc test corrections from local development.
- **Render**: deployed as a single web service (`render.yaml`,
  Python runtime, free plan, auto-deploy on push to `master`) at
  https://adaptive-email-spam-detection.onrender.com. Health check:
  `/api/health`.
- **Render bug #1 - NLTK missing at runtime.** The first Render deploy's
  build step downloaded NLTK corpora via `nltk.download()`, but the
  live app crashed on the first `/api/predict` call with
  `LookupError: Resource 'stopwords' not found`. Root cause: Render's
  build step and the running container are separate filesystem layers,
  so data fetched during build is not guaranteed to exist wherever the
  app actually starts. Fixed by moving the download into
  `ensure_nltk_data()` (`backend/app/ml/preprocessing.py`), called
  from the FastAPI lifespan on every startup — `nltk.download()`
  no-ops when data is already present, so this has zero effect
  locally.

## Vercel — deployed 2026-09-19, initially skipped then added back per explicit later request

Originally **not** deployed here: Vercel Python functions are
stateless serverless with no persistent filesystem, and this app's
adaptive learning depends on writing `.joblib`/JSONL files on every
piece of feedback. The user asked for it anyway, understanding that
tradeoff. Live at https://adaptive-email-spam-detection.vercel.app
(project `josh-academy/adaptive-email-spam-detection`).

Getting it running well surfaced three more real, distinct bugs — each
found by actually deploying and reading the function logs, not by
guessing, then fixed and re-verified against the live URL before
moving to the next one:

1. **Zero dependencies installed.** `api/index.py` + `vercel.json`
   (`builds`/`routes` pointing at it) were added to expose the
   existing FastAPI app without restructuring `backend/app`. First
   deploy "succeeded" in 2 seconds, then every request crashed with
   `ModuleNotFoundError: No module named 'fastapi'`. Cause: Vercel's
   Python builder resolves dependencies from `pyproject.toml` via `uv`
   whenever one exists, ignoring `requirements.txt` entirely — and our
   `pyproject.toml` (originally added only for pytest config) had no
   `[project.dependencies]`, so nothing was installed. Fixed by adding
   the dependency list there, kept manually in sync with
   `requirements.txt` (which Render's build command still uses
   directly). Also had to narrow `requires-python` from `>=3.11` to
   `>=3.12`: `numpy==2.5.3` requires 3.12+, and `uv`'s resolver failed
   trying to satisfy the wider stated range even though the actual
   runtime is 3.12.
2. **NLTK crash, different cause than Render's.** After fixing
   dependencies, `ensure_nltk_data()` itself crashed:
   `OSError: [Errno 30] Read-only file system: '/home/sbx_user1051'`.
   `nltk.download()`'s default target is the user's home directory,
   read-only on Vercel (only `/tmp` is writable there). Fixed by always
   downloading to a fixed path under `tempfile.gettempdir()` and adding
   it to `nltk.data.path` — one code path correct on local dev, Render,
   and Vercel alike, rather than branching per platform.
3. **Every prediction crashed writing its log line.** With NLTK fixed,
   `/api/health` went green but `/api/predict` crashed:
   `OSError: [Errno 30] Read-only file system: '/var/task/logs/predictions.jsonl'`
   — the same read-only-filesystem constraint, now hitting the
   application's own event logs and (would have, next) the adaptive
   model's every-feedback `joblib.dump`. Fixed properly this time
   rather than papering over one path at a time: added
   `Settings._make_writable()` (`backend/app/core/config.py`), which
   probes whether `artifacts_dir`/`logs_dir` are actually writable and,
   if not, transparently copies them to `/tmp` and redirects every path
   built from them there — a no-op on local dev and Render. This also
   required fixing `STATIC_MODEL_PATH`/`STATIC_VECTORIZER_PATH`/
   `ADAPTIVE_MODEL_PATH`/`METADATA_PATH`, which previously reconstructed
   from `PROJECT_ROOT` independently of `artifacts_dir` — so even with
   the redirect in place, those four would have kept pointing at the
   original read-only bundle while everything else moved to `/tmp`.

Also trimmed `requirements.txt` from 498MB installed to 241MB while
fixing this (dropped notebook-only tooling — jupyter/nbconvert/
matplotlib/etc — never used by the serving app, plus `pandas`, only
used by the training scripts, never imported at runtime by
`backend/app`). Moved `pandas` to a new `requirements-training.txt`.
Both training scripts now call `ensure_nltk_data()` themselves too, so
they work standalone on a fresh clone without needing the app started
first. Verified in a fresh, isolated venv (not just assumed) that
health/predict/`.eml`-upload all still work with the trimmed set
before relying on it for either deploy target.

**End-to-end verification after all three fixes**: called
`/api/health`, `/api/predict`, and `/api/feedback` directly against
the live Vercel URL — a feedback correction genuinely updated the
model (`adaptive-1.0.0` → `adaptive-1.0.1`) and a repeat prediction of
the same email reflected it, confirmed within that same warm instance.
Also ran a full Playwright pass against the live frontend (0 console
errors, 0 failed requests) and re-confirmed Render was unaffected by
the shared `config.py`/`pyproject.toml` changes.

## Known limitations (both platforms)

- **Render**: free plan has no paid persistent-disk add-on, so if the
  instance restarts (redeploy, or free-tier spin-down after
  inactivity), local state resets to whatever was last committed to
  git (the clean `adaptive-1.0.0` baseline) rather than persisting
  feedback-driven updates indefinitely. Within a single running
  instance's uptime, feedback persists normally exactly as it does
  locally.
- **Vercel**: no persistent filesystem at all, by design — the
  `/tmp` redirect makes feedback work within one warm serverless
  instance, but a cold start (which can happen between any two
  requests, not just after a redeploy) always resets to the bundled
  `adaptive-1.0.0` baseline. This is a materially weaker persistence
  guarantee than Render's, understood and accepted when the user asked
  for this deployment anyway.
