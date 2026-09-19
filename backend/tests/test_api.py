def test_health_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["static_model_loaded"] is True
    assert body["data"]["adaptive_model_loaded"] is True


def test_predict_spam_like_email(client):
    resp = client.post("/api/predict", json={
        "subject": "You won!",
        "body": "Congratulations! Click here to claim your $1,000,000 prize now! Act immediately!",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "prediction_id" in data
    assert data["static_prediction"]["label_name"] in ("spam", "ham")
    assert data["adaptive_prediction"]["label_name"] in ("spam", "ham")


def test_predict_rejects_empty_body(client):
    resp = client.post("/api/predict", json={"subject": "x", "body": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_feedback_full_cycle(client):
    predict_resp = client.post("/api/predict", json={
        "subject": "Meeting",
        "body": "Hi team, here are today's notes. Thanks.",
    })
    prediction_id = predict_resp.json()["data"]["prediction_id"]

    feedback_resp = client.post("/api/feedback", json={
        "prediction_id": prediction_id,
        "corrected_label": "legitimate",
    })
    assert feedback_resp.status_code == 200
    fb_body = feedback_resp.json()
    assert fb_body["success"] is True
    assert fb_body["data"]["adaptive_model_updated"] is True

    duplicate_resp = client.post("/api/feedback", json={
        "prediction_id": prediction_id,
        "corrected_label": "legitimate",
    })
    dup_body = duplicate_resp.json()
    assert dup_body["success"] is False
    assert dup_body["error"]["code"] == "FEEDBACK_ALREADY_APPLIED"


def test_feedback_flips_prediction_in_one_correction(client):
    """Regression guard: a single feedback correction must flip the
    adaptive model's prediction outright, per explicit user request
    ('I want it to flip completely'). Three implementations were tried:

    1. scikit-learn SGDClassifier + unweighted partial_fit: moved
       confidence by well under 1 point per correction (its internal
       step counter was already >250k from warm-up) - even 50 repeated
       identical corrections on the same example didn't flip it.
       Replaced because the academic study specifies River, not
       scikit-learn SGD.
    2. River MultinomialNB + a FIXED repeat count (learn_one x200 per
       correction): worked on every hand-picked test case, but real
       usage immediately found a counter-example - a 98.4%-confident
       spam prediction only dropped to 56.9% after 200 repeats, not
       enough to actually flip. How much evidence is needed to
       overcome a wrong prediction scales with how confident that wrong
       prediction was, which varies per email - no fixed count covers
       every case without being wastefully large for easy ones.
    3. River MultinomialNB + a confidence-margin loop (current): keeps
       calling learn_one on the SAME correction, checking predict_proba
       after each call, until the corrected label's confidence actually
       crosses AdaptiveModelService.FEEDBACK_CONFIDENCE_MARGIN (0.6),
       capped at FEEDBACK_MAX_LEARN_CALLS (5000) as a safety bound.
       Measured against an artificially hardened 99.2%-confident-wrong
       case: converges in under 1,000 calls (~100ms). This test fails
       again if that regresses.

    Deliberately does NOT assert what the model predicts before
    feedback: the test suite's `client` fixture copies the artifacts
    that exist on disk when the session starts, which reflect however
    many corrections the live model has accumulated from manual
    testing/demo use. Instead this always corrects toward whichever
    label it DIDN'T predict, so the test is meaningful regardless of
    the live model's current drift."""
    body = {
        "subject": "Final notice: account suspension",
        "body": "URGENT ACTION REQUIRED: Your account will be suspended in 24 hours. "
                "Verify your identity immediately by clicking this link and entering "
                "your password and credit card number to avoid permanent closure.",
    }
    first = client.post("/api/predict", json=body).json()["data"]
    original_label = first["adaptive_prediction"]["label_name"]
    corrected_label = "legitimate" if original_label == "spam" else "spam"
    expected_flip_to = "ham" if original_label == "spam" else "spam"

    client.post("/api/feedback", json={
        "prediction_id": first["prediction_id"],
        "corrected_label": corrected_label,
    })

    second = client.post("/api/predict", json=body).json()["data"]
    assert second["adaptive_prediction"]["label_name"] == expected_flip_to, (
        f"Originally predicted {original_label}; one feedback correction to "
        f"'{corrected_label}' should flip it to {expected_flip_to}, but it's still "
        f"predicting {second['adaptive_prediction']['label_name']} "
        f"at confidence {second['adaptive_prediction']['confidence']:.4f}."
    )


def test_feedback_unknown_prediction_id(client):
    resp = client.post("/api/feedback", json={
        "prediction_id": "does-not-exist",
        "corrected_label": "spam",
    })
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNKNOWN_PREDICTION_ID"


def test_adaptive_status_reflects_updates(client):
    before = client.get("/api/adaptive/status").json()["data"]["update_count"]

    predict_resp = client.post("/api/predict", json={"body": "Buy cheap watches now, click here!!!"})
    prediction_id = predict_resp.json()["data"]["prediction_id"]
    client.post("/api/feedback", json={"prediction_id": prediction_id, "corrected_label": "spam"})

    after = client.get("/api/adaptive/status").json()["data"]["update_count"]
    assert after == before + 1


def test_drift_status_returns_monitoring_fields(client):
    resp = client.get("/api/drift/status")
    body = resp.json()
    assert body["success"] is True
    assert "monitored_predictions" in body["data"]
    assert "error_rate" in body["data"]
    assert "recent_drift_events" in body["data"]


def test_evaluation_summary_has_no_fabricated_fields(client):
    resp = client.get("/api/evaluation/summary")
    body = resp.json()["data"]
    assert body["static_baseline"]["metrics"]["accuracy"] > 0
    assert "known_limitations" in body["static_baseline"]
    assert "known_limitations" in body["adaptive_model"]


def test_events_endpoint_filters_by_type(client):
    client.post("/api/predict", json={"body": "test event log filter"})
    resp = client.get("/api/events", params={"event_type": "prediction", "limit": 5})
    body = resp.json()["data"]
    assert all(e["stream"] == "prediction" for e in body["events"])


def test_eml_upload_rejects_empty_file(client):
    resp = client.post(
        "/api/predict/eml",
        files={"file": ("empty.eml", b"", "message/rfc822")},
    )
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_EML"


def test_eml_upload_valid_file(client):
    raw = (
        b"From: a@example.com\r\nSubject: Test\r\n"
        b"Content-Type: text/plain\r\n\r\nHello there, this is a real message.\r\n"
    )
    resp = client.post(
        "/api/predict/eml",
        files={"file": ("test.eml", raw, "message/rfc822")},
    )
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["parsed_subject"] == "Test"
