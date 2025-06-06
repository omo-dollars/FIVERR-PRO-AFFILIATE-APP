import streamlit as st
import pandas as pd
import random
import praw

# === SETUP REDDIT API ===
reddit = praw.Reddit(
    client_id="FbY5KaRrqILcU7SDGizJXg",
    client_secret="T2zo2U3TUAuSeHOjtxDJJNYiXe3MSw",
    user_agent="Fiverr Affiliate Promotion",
    username="fiverr_affiliate_bot",
    password="cre111ate",
    check_for_async=False  # Prevent async loop issues with Streamlit
)

# === APP CONFIG ===
st.set_page_config(page_title="Fiverr Pro Affiliate Responder", layout="wide")
st.title("Fiverr Pro Affiliate Responder Dashboard")

# === SIDEBAR INPUTS ===
with st.sidebar:
    st.header("Settings")
    fiverr_affiliate_id = "1119137"  # Hardcoded affiliate ID
    subreddit_input = st.text_input("Subreddit(s) to search", "freelance,forhire,test")
    user_services = st.text_area("Fiverr Pro Services (comma-separated)", 
        "logo design, website development, SEO, animation, voice over, resume writing, app development, mobile app, business card, brochure design, content writing, UX design, UI design, digital marketing, video editing, explainer video, motion graphics, translation, transcription, podcast editing, social media management, ads management, data analysis, data entry, game development, Shopify store, dropshipping, branding, pitch deck, investor presentation, NFT art, 3D modeling, WordPress, cybersecurity, email marketing, market research, product design, photography, illustration, CAD drawing, architecture"
    )
    max_posts = st.slider("Number of Reddit posts to fetch per subreddit", 10, 100, 20)

# === SERVICE KEYWORDS PREP ===
services = [s.strip().lower() for s in user_services.split(",") if s.strip()]
keywords = list(set(services))

# === FUNCTION TO GENERATE FIVERR AFFILIATE LINK ===
def generate_affiliate_link(service, affiliate_id):
    base_url = f"https://www.fiverr.com/pro/{service.replace(' ', '-')}"
    return f"{base_url}?aff_id={affiliate_id}"

# === FUNCTION TO GENERATE REPLY ===
def generate_reply(service, fiverr_url):
    templates = [
        f"If you're looking for top-notch {service}, check out this Fiverr Pro seller: {fiverr_url}",
        f"Need help with {service}? This Fiverr Pro expert might be perfect: {fiverr_url}",
        f"Here’s a great Fiverr Pro gig for {service}: {fiverr_url}",
    ]
    return random.choice(templates)

# === BUILD GIG URL MAP ===
gig_urls = {s: generate_affiliate_link(s, fiverr_affiliate_id) for s in services}

# === RESULTS STORAGE ===
reddit_posts = []

# === REDDIT SCRAPING ===
st.subheader("Matching Reddit Posts")
try:
    subreddits = [s.strip() for s in subreddit_input.split(",") if s.strip()]
    for subreddit in subreddits:
        st.info(f"Searching r/{subreddit}...")
        for submission in reddit.subreddit(subreddit).hot(limit=max_posts):
            content = (submission.title + " " + submission.selftext).lower()
            for kw in keywords:
                if kw in content:
                    gig_url = gig_urls.get(kw)
                    reply = generate_reply(kw, gig_url)
                    reddit_posts.append({
                        "platform": "Reddit",
                        "content": submission.title,
                        "matched_service": kw,
                        "fiverr_url": gig_url,
                        "reply": reply
                    })
                    break  # Only match once per post
except Exception as e:
    st.error(f"❌ Error fetching Reddit posts: {e}")
    st.stop()

# === DISPLAY RESULTS ===
df = pd.DataFrame(reddit_posts)

if not df.empty:
    st.success(f"Found {len(df)} matching Reddit posts.")
    for idx, row in df.iterrows():
        with st.expander(f"{row['platform']} - {row['matched_service'].title()}"):
            st.write(row["content"])
            st.code(row["reply"])
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Copy Reply", key=f"copy_{idx}"):
                    st.toast("Copied!", icon="")
            with col2:
                st.markdown(f"[Preview Fiverr Gig]({row['fiverr_url']})", unsafe_allow_html=True)

    # === DOWNLOAD ===
    st.download_button(
        "Download Replies CSV",
        data=df.to_csv(index=False),
        file_name="fiverr_replies.csv",
        mime="text/csv"
    )
else:
    st.warning("⚠️ No matching Reddit posts found.")

# === FOOTER ===
st.markdown("---")
st.caption("Built for Fiverr Pro Affiliates | Free on Streamlit Cloud")
