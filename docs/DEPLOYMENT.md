# Streamlit Community Cloud Deployment

The repository is deployment-ready with `app.py` as the entry point and a fully
pinned `requirements.txt`. No secret is required while `llm.enabled: false`.

## Before publishing

1. Run `.\run_tests.ps1` from a clean clone.
2. Confirm `data/raw/` contains only synthetic generated files.
3. Confirm `.streamlit/secrets.toml`, `.env`, the local `.venv`, runtime database
   and caches are not committed.
4. Push the repository to an account-controlled GitHub repository.
5. In Streamlit Community Cloud, choose the repository, branch and `app.py`.
6. Use Python 3.12 when the platform offers a version selector.
7. Deploy and run the complete five-minute script once on desktop and once on a
   second device or mobile browser.

## Post-deployment proof

- Home and all five pages load.
- WEST S1 is ALERT; NORTH S3 is ABSTAIN; SOUTH S4 is PEER_BASED.
- Security test denies WEST → NORTH detail.
- LLM disabled path works and reports zero calls/cost.
- Actions and feedback work for the session. Note that Streamlit Community
  Cloud's local filesystem is not a production durable database; use an external
  governed store for durable multi-user production feedback.

## External steps not automatable from the source package

Creating the public GitHub repository, authorising Streamlit Cloud, testing a
physically separate device and recording a human voice/video require the owner's
accounts or device. The project includes the exact local proof, script and deck
needed for those steps, but it must not invent a deployment URL or claim a device
test that did not occur.

