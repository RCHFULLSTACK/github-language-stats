import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

# Konfigurera sidan
st.set_page_config(page_title="GitHub Språktracker", page_icon="📊", layout="wide")

# Titelsektionen
st.title("📊 Populära Programmeringsspråk")
st.markdown("Utforska trender inom programmeringsspråk baserat på GitHub-data")

# GitHub API-funktioner
def get_top_repositories(language, sort_by="stars", per_page=10):
    """Hämta topprepositories för ett visst språk"""
    url = f"https://api.github.com/search/repositories?q=language:{language}&sort={sort_by}&order=desc&per_page={per_page}"
    response = requests.get(url)
    return response.json()

def get_language_stats():
    """Hämta statistik för populära språk"""
    languages = ["JavaScript", "Python", "Java", "TypeScript", "C++", "C#", "PHP", "Go", "Ruby", "Swift"]
    stats = []
    
    with st.spinner("Hämtar data från GitHub..."):
        for language in languages:
            data = get_top_repositories(language, per_page=100)
            if 'items' in data:
                total_stars = sum(repo['stargazers_count'] for repo in data['items'])
                total_forks = sum(repo['forks_count'] for repo in data['items'])
                stats.append({
                    "language": language,
                    "repositories": len(data['items']),
                    "stars": total_stars,
                    "forks": total_forks,
                    "avg_stars": total_stars / len(data['items']) if len(data['items']) > 0 else 0
                })
            # Paus för att respektera API-begränsningar
            time.sleep(0.7)
    
    return pd.DataFrame(stats)

# Caching av API-anrop för att respektera GitHub-begränsningar
@st.cache_data(ttl=3600)
def load_github_data():
    return get_language_stats()

# Ladda data
try:
    df = load_github_data()
    
    # Skapa två kolumner för visualiseringar
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Antal Stjärnor per språk")
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df['language'], df['stars'], color='skyblue')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Antal stjärnor')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.subheader("Genomsnittligt antal stjärnor per repository")
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df['language'], df['avg_stars'], color='lightgreen')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Genomsnittligt antal stjärnor')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Visa tabelldata
    st.subheader("Detaljerad Språkstatistik")
    st.dataframe(df)
    
    # Möjlighet att utforska specifikt språk
    st.subheader("Utforska Topprepositories för ett specifikt språk")
    selected_language = st.selectbox("Välj språk", df['language'].tolist())
    
    if selected_language:
        repos_data = get_top_repositories(selected_language, per_page=5)
        if 'items' in repos_data:
            st.write(f"Topp 5 {selected_language}-repositories:")
            for repo in repos_data['items']:
                st.markdown(f"""
                **[{repo['name']}]({repo['html_url']})** av {repo['owner']['login']}
                - ⭐ {repo['stargazers_count']} stjärnor
                - 🍴 {repo['forks_count']} forks
                - 📝 {repo['description'] or 'Ingen beskrivning'}
                ---
                """)
except Exception as e:
    st.error(f"Ett fel uppstod: {e}")
    st.info("GitHub API har begränsningar för antal anrop. Vänta en stund eller använd API-nycklar för högre kvot.")

# Footer
st.markdown("---")
st.markdown("Data hämtad från GitHub API. Uppdateras varje timme.")