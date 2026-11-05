# 🌴 TripSplit

Trip expense splitter built with Streamlit + Supabase. Green & white UI, multi-page, login, live updates.

## Setup
1. Create a project at supabase.com.
2. Supabase → **SQL Editor** → paste all of `sql/schema.sql` → Run.
3. Supabase → **Authentication → Providers → Email**: for quick testing turn **off** "Confirm email".
4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your Project URL and **anon public** key (Settings → API).
5. Install and run:
   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows  (Mac/Linux: source .venv/bin/activate)
   pip install -r requirements.txt
   streamlit run app.py
   ```

## How friends use it
- You create a trip → share the **trip code** → friends sign up and use **Join with code**.
- Friends without accounts can be added by name on the Members page.
- Pages refresh automatically within ~4 seconds when someone else adds data.

## Notes
- Refreshing the browser tab logs you out (Streamlit resets session state). Just log in again.
- Deploy free on Streamlit Community Cloud; put the two secrets in the app's Secrets settings.
