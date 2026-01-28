---
description: How to deploy the Kytchens Report Generator to Streamlit Cloud
---

1. Ensure all local changes are committed and pushed to GitHub.
// turbo
2. Push latest changes:
   ```bash
   git add .
   git commit -m "Update for deployment"
   git push origin main
   ```
3. Visit [Streamlit Cloud](https://share.streamlit.io).
4. Click 'New App' and select this repository.
5. In 'Advanced Settings', paste the contents of `.streamlit/secrets.toml` into the 'Secrets' text area.
6. Click 'Deploy'.
