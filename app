import streamlit as st
from pymongo import MongoClient
import os

st.set_page_config(page_title="CineHub", page_icon="🎬", layout="wide")

CONN_STRING = os.environ.get(
    "MONGODB_URI",
    "mongodb+srv://admin_cinehub:SENHA@cinehub.3rawcki.mongodb.net/?appName=cinehub"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,700;1,900&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background-color: #0a0a0b;
  color: #ffffff;
}

/* Remove streamlit defaults (mas mantém o botão de abrir/fechar sidebar visível) */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
header[data-testid="stHeader"] * { visibility: visible !important; }
[data-testid="collapsedControl"] { visibility: visible !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stSidebar"] { background: #0a0a0b; border-right: 1px solid rgba(255,255,255,0.05); }
[data-testid="stSidebar"] * { color: #a1a1aa; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0b; }
::-webkit-scrollbar-thumb { background: #c5a059; border-radius: 2px; }

/* NAV */
.nav-bar {
  position: sticky; top: 0; z-index: 999;
  background: rgba(10,10,11,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding: 0 2.5rem;
  height: 72px;
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 3rem;
}
.nav-logo {
  font-family: 'Playfair Display', serif;
  font-style: italic; font-weight: 900;
  font-size: 1.6rem; letter-spacing: -1px;
  color: #c5a059;
}
.nav-links { display: flex; gap: 2.5rem; align-items: center; }
.nav-links a {
  color: #a1a1aa; font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.15em; text-transform: uppercase;
  text-decoration: none; transition: color .2s;
}
.nav-links a:hover { color: #c5a059; }
.nav-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  border: 1px solid rgba(197,160,89,0.3);
  background: rgba(197,160,89,0.15);
  display: grid; place-items: center;
  font-size: 0.7rem; font-weight: 700; font-style: italic;
  color: #c5a059; cursor: pointer;
}

/* PAGE WRAPPER */
.page-wrap { max-width: 1200px; margin: 0 auto; padding: 0 2.5rem 5rem; }

/* SECTION LABEL */
.section-label {
  font-size: 0.68rem; font-weight: 700;
  letter-spacing: 0.2em; text-transform: uppercase;
  color: #a1a1aa; margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

/* STAT CARDS */
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
  background: #161618; border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px; padding: 1.2rem; text-align: center;
}
.stat-val { font-size: 1.8rem; font-weight: 900; color: #c5a059; line-height: 1; }
.stat-val.white { color: #ffffff; }
.stat-lbl { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #a1a1aa; margin-top: 0.3rem; }

/* MOVIE CARD (list) */
.movie-card {
  background: rgba(22,22,24,0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 18px; padding: 2rem;
  margin-bottom: 1rem;
  transition: border-color .25s;
  display: grid; grid-template-columns: 1fr auto;
  gap: 1.5rem; align-items: start;
}
.movie-card:hover { border-color: rgba(197,160,89,0.3); }
.movie-title {
  font-family: 'Playfair Display', serif;
  font-style: italic; font-weight: 900;
  font-size: 1.5rem; line-height: 1.2;
  color: #ffffff; margin-bottom: 0.3rem;
}
.movie-meta {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
  color: #c5a059; text-transform: uppercase;
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 0.8rem;
}
.movie-meta .dot {
  width: 3px; height: 3px; border-radius: 50%;
  background: rgba(255,255,255,0.2); display: inline-block;
}
.movie-synopsis {
  font-size: 0.88rem; font-style: italic;
  color: #a1a1aa; line-height: 1.7;
  margin-bottom: 1rem;
}
.genre-tag {
  display: inline-block;
  border: 1px solid rgba(255,255,255,0.1);
  background: #161618; border-radius: 999px;
  padding: 0.2rem 0.8rem;
  font-size: 0.7rem; font-weight: 500;
  color: #ffffff; margin-right: 4px;
}
.score-block { text-align: right; min-width: 100px; }
.score-num {
  font-size: 2.5rem; font-weight: 900;
  color: #c5a059; line-height: 1;
}
.score-sub { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #a1a1aa; }

/* AWARDS BOX */
.awards-box {
  background: linear-gradient(135deg, rgba(197,160,89,0.08), transparent);
  border: 1px solid rgba(197,160,89,0.2);
  border-radius: 14px; padding: 1.5rem; margin-top: 1rem;
}
.awards-title {
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.2em;
  text-transform: uppercase; color: #c5a059; margin-bottom: 1rem;
}
.award-item {
  display: flex; gap: 0.75rem; align-items: flex-start;
  font-size: 0.82rem; color: #a1a1aa; margin-bottom: 0.6rem;
}
.award-item strong { color: #ffffff; }

/* CAST */
.cast-item {
  display: flex; align-items: center; gap: 0.75rem;
  margin-bottom: 0.7rem;
}
.cast-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, #2a2a2e, #161618);
  border: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.cast-name { font-size: 0.85rem; font-weight: 500; color: #ffffff; }
.cast-role { font-size: 0.72rem; font-style: italic; color: #a1a1aa; }

/* REVIEW CARD */
.review-card {
  background: rgba(22,22,24,0.3);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 18px; padding: 2rem;
  margin-bottom: 1rem;
  transition: border-color .25s;
}
.review-card:hover { border-color: rgba(197,160,89,0.3); }
.review-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.review-author { font-size: 0.85rem; font-weight: 700; color: #ffffff; }
.review-date { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #a1a1aa; margin-top: 2px; }
.review-film { font-size: 0.72rem; color: #a1a1aa; margin-bottom: 0.4rem; }
.review-film strong { color: #c5a059; }
.review-headline { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1rem; color: #ffffff; margin-bottom: 0.5rem; }
.review-text { font-size: 0.85rem; font-style: italic; color: #a1a1aa; line-height: 1.8; }
.review-footer { margin-top: 1rem; font-size: 0.7rem; color: rgba(255,255,255,0.2); }
.stars { color: #c5a059; letter-spacing: 2px; font-size: 0.85rem; }
.stars-empty { color: rgba(161,161,170,0.2); }
.review-nota { font-size: 1.4rem; font-weight: 900; color: #c5a059; }

/* PERSON CARD */
.person-card {
  background: rgba(22,22,24,0.3);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px; padding: 1.5rem;
  margin-bottom: 0.75rem;
  transition: border-color .25s;
}
.person-card:hover { border-color: rgba(197,160,89,0.3); }
.person-name {
  font-family: 'Playfair Display', serif;
  font-style: italic; font-size: 1.1rem;
  color: #ffffff; margin-bottom: 0.2rem;
}
.person-meta { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #a1a1aa; margin-bottom: 0.6rem; }
.person-bio { font-size: 0.82rem; font-style: italic; color: #a1a1aa; line-height: 1.7; margin-bottom: 0.8rem; }
.person-films { font-size: 0.75rem; color: rgba(255,255,255,0.3); }
.person-films span { color: #ffffff; }
.func-tag {
  display: inline-block;
  border: 1px solid rgba(197,160,89,0.3);
  background: rgba(197,160,89,0.08);
  border-radius: 999px; padding: 0.15rem 0.6rem;
  font-size: 0.65rem; font-weight: 600;
  color: #c5a059; margin-right: 4px; text-transform: uppercase; letter-spacing: 0.05em;
}

/* HERO (início) */
.hero-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 3rem; }
.hero-stat {
  background: #161618; border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px; padding: 1.5rem; text-align: center;
}
.hero-stat-val { font-size: 2.2rem; font-weight: 900; color: #c5a059; }
.hero-stat-lbl { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: #a1a1aa; margin-top: 0.2rem; }

/* SEARCH INPUT override */
input[type="text"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 999px !important;
  color: #ffffff !important;
  padding: 0.5rem 1.2rem !important;
  font-size: 0.85rem !important;
}
input[type="text"]:focus {
  border-color: rgba(197,160,89,0.5) !important;
  outline: none !important;
  box-shadow: none !important;
}

/* SELECT override */
[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 10px !important;
  color: #ffffff !important;
}

/* EXPANDER override */
[data-testid="stExpander"] {
  background: rgba(22,22,24,0.4) !important;
  border: 1px solid rgba(255,255,255,0.05) !important;
  border-radius: 18px !important;
  margin-bottom: 0.75rem;
}
[data-testid="stExpander"]:hover {
  border-color: rgba(197,160,89,0.3) !important;
}

/* FOOTER */
.footer {
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 5rem; padding: 3.5rem 2.5rem;
  text-align: center;
}
.footer-logo {
  font-family: 'Playfair Display', serif;
  font-style: italic; font-weight: 900;
  font-size: 1.8rem; color: #c5a059;
  letter-spacing: -1px; margin-bottom: 0.75rem;
}
.footer-sub { font-size: 0.82rem; font-style: italic; color: #a1a1aa; max-width: 360px; margin: 0 auto 1.5rem; }
.footer-links { display: flex; justify-content: center; gap: 2rem; }
.footer-links a { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(255,255,255,0.25); text-decoration: none; transition: color .2s; }
.footer-links a:hover { color: #c5a059; }

/* SIDEBAR NAV */
.sb-nav-item {
  display: block; padding: 0.65rem 1rem;
  border-radius: 8px; margin-bottom: 0.25rem;
  font-size: 0.75rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #a1a1aa; cursor: pointer;
  transition: all .2s;
}
.sb-nav-item:hover, .sb-nav-item.active {
  background: rgba(197,160,89,0.1);
  color: #c5a059;
}
.sb-logo {
  font-family: 'Playfair Display', serif;
  font-style: italic; font-weight: 900;
  font-size: 1.3rem; color: #c5a059;
  padding: 1rem; margin-bottom: 0.5rem;
}
.sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 1rem 0; }
.sb-label { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(255,255,255,0.2); padding: 0 1rem; margin-bottom: 0.5rem; }
.sb-status { font-size: 0.72rem; color: #4ade80; padding: 0 1rem; }
.sb-count { font-size: 0.7rem; color: #a1a1aa; padding: 0 1rem; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# ── Conexão ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(CONN_STRING, serverSelectionTimeoutMS=6000)
    return client["cinehub"]

try:
    db = get_db()
    db.command("ping")
    conectado = True
except Exception as e:
    conectado = False

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo">CINEHUB</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Navegar</div>', unsafe_allow_html=True)

    pagina = st.radio(
        "", ["Início", "Filmes", "Avaliações", "Pessoas", "CRUD"],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Início": "⬡  Início",
            "Filmes": "◈  Filmes",
            "Avaliações": "◇  Avaliações",
            "Pessoas": "◉  Pessoas",
            "CRUD": "⚙  CRUD",
        }[x]
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Atlas</div>', unsafe_allow_html=True)
    if conectado:
        st.markdown('<div class="sb-status">● Conectado</div>', unsafe_allow_html=True)
        n_f = db["filmes"].count_documents({})
        n_a = db["avaliacoes"].count_documents({})
        n_p = db["pessoas"].count_documents({})
        st.markdown(f'<div class="sb-count">{n_f} filmes<br>{n_a} avaliações<br>{n_p} pessoas</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#f87171;font-size:0.72rem;padding:0 1rem">● Desconectado</div>', unsafe_allow_html=True)

if not conectado:
    st.error("Erro ao conectar ao MongoDB Atlas.")
    st.stop()

# ── Nav bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
  <div style="display:flex;align-items:center;gap:3rem">
    <span class="nav-logo">CINEHUB</span>
    <div class="nav-links">
      <a href="#">Explorar</a>
      <a href="#">Rankings</a>
      <a href="#">Coleções</a>
    </div>
  </div>
  <div class="nav-avatar">JS</div>
</div>
""", unsafe_allow_html=True)

def stars_html(nota, total=10):
    filled = round(nota / 2)
    empty  = 5 - filled
    return f'<span class="stars">{"★" * filled}</span><span class="stars-empty">{"★" * empty}</span>'

# ─────────────────────────────────────────────────────────────────────────────
# INÍCIO
# ─────────────────────────────────────────────────────────────────────────────
if pagina == "Início":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-bottom:3rem">
      <p style="font-size:0.7rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#c5a059;margin-bottom:0.75rem">Plataforma cinematográfica</p>
      <h1 style="font-family:'Playfair Display',serif;font-style:italic;font-weight:900;font-size:3.5rem;line-height:1.1;letter-spacing:-2px;margin-bottom:1rem">Descubra, avalie e<br>compartilhe cinema.</h1>
      <p style="font-size:1rem;font-style:italic;color:#a1a1aa;max-width:480px;line-height:1.7">Uma comunidade para amantes da sétima arte. Avalie filmes, leia críticas e construa sua lista.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="hero-grid">
      <div class="hero-stat"><div class="hero-stat-val">{db["filmes"].count_documents({})}</div><div class="hero-stat-lbl">Filmes cadastrados</div></div>
      <div class="hero-stat"><div class="hero-stat-val">{db["avaliacoes"].count_documents({})}</div><div class="hero-stat-lbl">Avaliações</div></div>
      <div class="hero-stat"><div class="hero-stat-val">{db["pessoas"].count_documents({})}</div><div class="hero-stat-lbl">Pessoas</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Filmes em destaque
    st.markdown('<div class="section-label">Filmes em Destaque</div>', unsafe_allow_html=True)
    filmes = list(db["filmes"].find({}).sort("avaliacao.media", -1))
    for f in filmes:
        generos_html = "".join(f'<span class="genre-tag">{g}</span>' for g in f.get("generos", []))
        meta = f["avaliacao"].get("metascore", "—")
        votos = f"{f['avaliacao']['total_votos']:,}"
        st.markdown(f"""
        <div class="movie-card">
          <div>
            <div class="movie-meta">
              <span>{f['ano']}</span><span class="dot"></span>
              <span>{f['duracao_min']} min</span><span class="dot"></span>
              <span style="border:1px solid rgba(197,160,89,0.4);padding:0.1rem 0.5rem;border-radius:4px;font-size:0.6rem">{f.get('classificacao_etaria','—')}+</span>
            </div>
            <div class="movie-title">{f['titulo']}</div>
            <div style="font-size:0.78rem;color:#a1a1aa;margin-bottom:0.8rem">Direção: <span style="color:#ffffff">{f['direcao']['nome']}</span></div>
            <p class="movie-synopsis">{f.get('sinopse','')}</p>
            <div>{generos_html}</div>
          </div>
          <div class="score-block">
            <div class="score-num">{f['avaliacao']['media']}</div>
            <div class="score-sub">{votos} votos</div>
            <div style="margin-top:0.5rem;font-size:0.65rem;color:#a1a1aa">Metascore</div>
            <div style="font-size:1.1rem;font-weight:900;color:#ffffff">{meta}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Últimas avaliações
    st.markdown('<div class="section-label" style="margin-top:3rem">Opiniões da Comunidade</div>', unsafe_allow_html=True)
    pipeline = [
        {"$sort": {"created_at": -1}}, {"$limit": 3},
        {"$lookup": {"from":"filmes","localField":"filme_id","foreignField":"_id","as":"filme"}},
        {"$unwind": "$filme"},
    ]
    for av in db["avaliacoes"].aggregate(pipeline):
        st.markdown(f"""
        <div class="review-card">
          <div class="review-header">
            <div>
              <div style="display:flex;align-items:center;gap:0.75rem">
                <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#2a1f00,#161618);border:1px solid rgba(255,255,255,0.08);flex-shrink:0"></div>
                <div>
                  <div class="review-author">@{av['nome_usuario']}</div>
                  <div class="review-date">{av['created_at'].strftime('%d %b, %Y') if hasattr(av['created_at'],'strftime') else ''}</div>
                </div>
              </div>
            </div>
            <div style="text-align:right">
              <div class="review-nota">{av['nota']}</div>
              <div>{stars_html(av['nota'])}</div>
            </div>
          </div>
          <div class="review-film">sobre <strong>{av['filme']['titulo']}</strong></div>
          <div class="review-headline">{av.get('titulo_resenha','')}</div>
          <p class="review-text">&ldquo;{av.get('comentario','')[:220]}{"..." if len(av.get('comentario',''))>220 else ""}&rdquo;</p>
          <div class="review-footer">👍 {av.get('curtidas',0)} curtidas</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FILMES
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "Filmes":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="font-family:'Playfair Display',serif;font-style:italic;font-weight:900;font-size:2.8rem;letter-spacing:-1.5px;margin-bottom:2rem">Catálogo de Filmes</h1>
    """, unsafe_allow_html=True)

    col_s, col_g = st.columns([3, 1])
    with col_s:
        busca = st.text_input("", placeholder="🔍  Buscar por título...")
    with col_g:
        generos_disponiveis = db["filmes"].distinct("generos")
        genero_filtro = st.selectbox("", ["Todos os gêneros"] + sorted(generos_disponiveis))

    query = {}
    if busca:
        query["$text"] = {"$search": busca}
    if genero_filtro != "Todos os gêneros":
        query["generos"] = genero_filtro

    filmes = list(db["filmes"].find(query).sort("avaliacao.media", -1))
    st.markdown(f'<p style="font-size:0.72rem;color:#a1a1aa;margin:1rem 0 1.5rem;letter-spacing:0.05em">{len(filmes)} filme(s) encontrado(s)</p>', unsafe_allow_html=True)

    for f in filmes:
        with st.expander(f"{f['titulo']}  ({f['ano']})  —  ⭐ {f['avaliacao']['media']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                generos_html = "".join(f'<span class="genre-tag">{g}</span>' for g in f.get("generos", []))
                st.markdown(f"""
                <div class="movie-meta" style="margin-bottom:1rem">
                  <span>{f['ano']}</span><span class="dot"></span>
                  <span>{f['duracao_min']} min</span><span class="dot"></span>
                  <span style="border:1px solid rgba(197,160,89,0.4);padding:0.1rem 0.5rem;border-radius:4px;font-size:0.6rem">{f.get('classificacao_etaria','—')}+</span>
                </div>
                <p class="movie-synopsis">{f.get('sinopse','')}</p>
                <div style="margin-bottom:1.2rem">{generos_html}</div>
                <div style="font-size:0.78rem;color:#a1a1aa;margin-bottom:0.4rem">Direção: <span style="color:#ffffff;font-style:italic">{f['direcao']['nome']}</span></div>
                <div style="font-size:0.78rem;color:#a1a1aa">País: <span style="color:#ffffff">{', '.join(f.get('paises',[]))}</span> · Idioma: <span style="color:#ffffff">{', '.join(f.get('idiomas',[]))}</span></div>
                """, unsafe_allow_html=True)

                if f.get("elenco"):
                    st.markdown('<div class="section-label" style="margin-top:1.5rem">Elenco Principal</div>', unsafe_allow_html=True)
                    for ator in f["elenco"]:
                        st.markdown(f"""
                        <div class="cast-item">
                          <div class="cast-avatar"></div>
                          <div>
                            <div class="cast-name">{ator['nome']}</div>
                            <div class="cast-role">como {ator['personagem']}</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                if f.get("premios"):
                    st.markdown(f"""
                    <div class="awards-box" style="margin-top:1.5rem">
                      <div class="awards-title">Prêmios e Indicações</div>
                    """, unsafe_allow_html=True)
                    for p in f["premios"]:
                        icone = "🏆" if p["resultado"] == "Vencedor" else "🎖️"
                        op = "" if p["resultado"] == "Vencedor" else "opacity:0.5;"
                        st.markdown(f"""
                        <div class="award-item">
                          <span style="{op}">{icone}</span>
                          <span><strong>{p['cerimonia']} {p['ano']}:</strong> {p['categoria']} <span style="color:#c5a059">({p['resultado']})</span></span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                av = f["avaliacao"]
                meta = av.get("metascore", "—")
                st.markdown(f"""
                <div class="stat-grid" style="grid-template-columns:1fr;gap:0.75rem">
                  <div class="stat-card">
                    <div class="stat-val">{av['media']}</div>
                    <div class="stat-lbl">{av['total_votos']:,} votos</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-val white">{meta}</div>
                    <div class="stat-lbl">Metascore</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Avaliações do filme
            avals = list(db["avaliacoes"].find({"filme_id": f["_id"]}).sort("curtidas", -1).limit(4))
            if avals:
                st.markdown('<div class="section-label" style="margin-top:1.5rem">Opiniões da Comunidade</div>', unsafe_allow_html=True)
                for av in avals:
                    st.markdown(f"""
                    <div class="review-card">
                      <div class="review-header">
                        <div style="display:flex;align-items:center;gap:0.75rem">
                          <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#2a1f00,#161618);border:1px solid rgba(255,255,255,0.08)"></div>
                          <div>
                            <div class="review-author">@{av['nome_usuario']}</div>
                          </div>
                        </div>
                        <div class="review-nota">{av['nota']}</div>
                      </div>
                      <div class="review-headline">{av.get('titulo_resenha','')}</div>
                      <p class="review-text">&ldquo;{av.get('comentario','')}&rdquo;</p>
                      <div class="review-footer">👍 {av.get('curtidas',0)} curtidas</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AVALIAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "Avaliações":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="font-family:'Playfair Display',serif;font-style:italic;font-weight:900;font-size:2.8rem;letter-spacing:-1.5px;margin-bottom:2rem">Opiniões da Comunidade</h1>
    """, unsafe_allow_html=True)

    filmes_lista = list(db["filmes"].find({}, {"titulo": 1}).sort("titulo", 1))
    col_f, col_o = st.columns([3, 1])
    with col_f:
        filme_sel = st.selectbox("", ["Todos os filmes"] + [f["titulo"] for f in filmes_lista])
    with col_o:
        ordem = st.selectbox("", ["Mais curtidas", "Maior nota", "Menor nota", "Mais recentes"])

    query = {}
    if filme_sel != "Todos os filmes":
        fd = db["filmes"].find_one({"titulo": filme_sel})
        if fd:
            query["filme_id"] = fd["_id"]

    sort_map = {"Mais curtidas": ("curtidas", -1), "Maior nota": ("nota", -1), "Menor nota": ("nota", 1), "Mais recentes": ("created_at", -1)}
    sk, sd = sort_map[ordem]

    pipeline = [
        {"$match": query}, {"$sort": {sk: sd}},
        {"$lookup": {"from": "filmes", "localField": "filme_id", "foreignField": "_id", "as": "filme"}},
        {"$unwind": "$filme"},
    ]
    avals = list(db["avaliacoes"].aggregate(pipeline))
    st.markdown(f'<p style="font-size:0.72rem;color:#a1a1aa;margin:1rem 0 1.5rem">{len(avals)} avaliação(ões)</p>', unsafe_allow_html=True)

    for av in avals:
        data_str = av['created_at'].strftime('%d %b, %Y') if hasattr(av['created_at'], 'strftime') else ''
        st.markdown(f"""
        <div class="review-card">
          <div class="review-header">
            <div style="display:flex;align-items:center;gap:0.75rem">
              <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#2a1f00,#161618);border:1px solid rgba(255,255,255,0.08);flex-shrink:0"></div>
              <div>
                <div class="review-author">@{av['nome_usuario']}</div>
                <div class="review-date">{data_str}</div>
              </div>
            </div>
            <div style="text-align:right">
              <div class="review-nota">{av['nota']}</div>
              <div>{stars_html(av['nota'])}</div>
            </div>
          </div>
          <div class="review-film">sobre <strong>{av['filme']['titulo']}</strong></div>
          <div class="review-headline">{av.get('titulo_resenha', 'Sem título')}</div>
          <p class="review-text">&ldquo;{av.get('comentario','')}&rdquo;</p>
          <div class="review-footer">👍 {av.get('curtidas', 0)} curtidas</div>
        </div>
        """, unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="section-label" style="margin-top:3rem">Estatísticas</div>', unsafe_allow_html=True)
    pipeline_stats = [
        {"$group": {"_id": "$filme_id", "media": {"$avg": "$nota"}, "total": {"$sum": 1}}},
        {"$lookup": {"from": "filmes", "localField": "_id", "foreignField": "_id", "as": "filme"}},
        {"$unwind": "$filme"}, {"$sort": {"media": -1}},
    ]
    stats = list(db["avaliacoes"].aggregate(pipeline_stats))
    if stats:
        import pandas as pd
        df = pd.DataFrame([{"Filme": s["filme"]["titulo"], "Média": round(s["media"], 2), "Total de avaliações": s["total"]} for s in stats])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PESSOAS
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "Pessoas":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="font-family:'Playfair Display',serif;font-style:italic;font-weight:900;font-size:2.8rem;letter-spacing:-1.5px;margin-bottom:2rem">Pessoas</h1>
    """, unsafe_allow_html=True)

    col_b, col_f = st.columns([3, 1])
    with col_b:
        busca = st.text_input("", placeholder="🔍  Buscar por nome...")
    with col_f:
        funcao_filtro = st.selectbox("", ["Todas as funções", "ator", "diretor", "roteirista", "produtor"])

    query = {}
    if busca:
        query["nome"] = {"$regex": busca, "$options": "i"}
    if funcao_filtro != "Todas as funções":
        query["funcoes"] = funcao_filtro

    pessoas = list(db["pessoas"].find(query).sort("nome", 1))
    st.markdown(f'<p style="font-size:0.72rem;color:#a1a1aa;margin:1rem 0 1.5rem">{len(pessoas)} pessoa(s)</p>', unsafe_allow_html=True)

    for p in pessoas:
        funcoes_html = "".join(f'<span class="func-tag">{fn}</span>' for fn in p.get("funcoes", []))
        filmo = p.get("filmografia", [])
        filmo_html = " · ".join(f'<span>{fm["titulo"]}</span> <span style="color:#a1a1aa">({fm["ano"]})</span>' for fm in filmo)
        st.markdown(f"""
        <div class="person-card">
          <div style="display:flex;align-items:flex-start;gap:1rem">
            <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#2a1f00,#161618);border:1px solid rgba(255,255,255,0.08);flex-shrink:0"></div>
            <div style="flex:1">
              <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.2rem;flex-wrap:wrap">
                <div class="person-name">{p['nome']}</div>
                {funcoes_html}
              </div>
              <div class="person-meta">{p.get('nacionalidade','')}</div>
              <div class="person-bio">{p.get('biografia','')}</div>
              {"<div class='person-films'>🎬 " + filmo_html + "</div>" if filmo_html else ""}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────────────────────────────────────
elif pagina == "CRUD":
    from bson import ObjectId
    from bson.errors import InvalidId
    from datetime import datetime, timezone
    import pandas as pd

    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="font-family:'Playfair Display',serif;font-style:italic;font-weight:900;font-size:2.8rem;letter-spacing:-1.5px;margin-bottom:0.5rem">Painel CRUD</h1>
    <p style="font-size:0.85rem;color:#a1a1aa;margin-bottom:2rem">Insert · Find · Update · Delete nas coleções principais do MongoDB Atlas</p>
    """, unsafe_allow_html=True)

    colecao_sel = st.selectbox("Coleção", ["filmes", "avaliacoes", "pessoas"], format_func=lambda x: {
        "filmes": "🎬 filmes", "avaliacoes": "⭐ avaliacoes", "pessoas": "👤 pessoas"
    }[x])

    tab_insert, tab_find, tab_update, tab_delete = st.tabs(["➕ INSERT", "🔍 FIND", "✏️ UPDATE", "🗑️ DELETE"])
    col = db[colecao_sel]

    # ══════════════════════════════════════════════════════════════════
    # INSERT
    # ══════════════════════════════════════════════════════════════════
    with tab_insert:
        st.markdown('<div class="section-label">Inserir novo documento</div>', unsafe_allow_html=True)

        if colecao_sel == "filmes":
            with st.form("form_insert_filme", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    titulo = st.text_input("Título *")
                    ano = st.number_input("Ano *", min_value=1888, max_value=2100, value=2024, step=1)
                    duracao = st.number_input("Duração (min) *", min_value=1, value=120, step=1)
                    classificacao = st.selectbox("Classificação", ["Livre", "10", "12", "14", "16", "18"])
                with c2:
                    generos = st.text_input("Gêneros (separados por vírgula) *", placeholder="Drama, Crime")
                    paises = st.text_input("Países (separados por vírgula)", placeholder="Brasil")
                    idiomas = st.text_input("Idiomas (separados por vírgula)", placeholder="Português")
                    diretor_nome = st.text_input("Nome do diretor *")
                sinopse = st.text_area("Sinopse *")
                submitted = st.form_submit_button("Inserir filme", use_container_width=True)

                if submitted:
                    if not titulo or not diretor_nome or not generos:
                        st.error("Preencha os campos obrigatórios (*)")
                    else:
                        novo_doc = {
                            "titulo": titulo,
                            "ano": int(ano),
                            "duracao_min": int(duracao),
                            "sinopse": sinopse,
                            "classificacao_etaria": classificacao,
                            "generos": [g.strip() for g in generos.split(",") if g.strip()],
                            "paises": [p.strip() for p in paises.split(",") if p.strip()],
                            "idiomas": [i.strip() for i in idiomas.split(",") if i.strip()],
                            "avaliacao": {"media": 0.0, "total_votos": 0, "metascore": 0},
                            "elenco": [],
                            "direcao": {"pessoa_id": ObjectId(), "nome": diretor_nome},
                            "premios": [],
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc),
                        }
                        result = col.insert_one(novo_doc)
                        st.success(f"✅ Filme inserido com _id: `{result.inserted_id}`")

        elif colecao_sel == "avaliacoes":
            filmes_opts = list(db["filmes"].find({}, {"titulo": 1}).sort("titulo", 1))
            with st.form("form_insert_avaliacao", clear_on_submit=True):
                if not filmes_opts:
                    st.warning("Cadastre um filme antes de inserir avaliações.")
                else:
                    filme_escolhido = st.selectbox("Filme *", filmes_opts, format_func=lambda f: f["titulo"])
                    nome_usuario = st.text_input("Nome de usuário *", placeholder="cinefilo_br")
                    nota = st.slider("Nota *", 0.0, 10.0, 7.5, 0.5)
                    titulo_resenha = st.text_input("Título da resenha")
                    comentario = st.text_area("Comentário *")
                    spoiler = st.checkbox("Contém spoiler")
                    submitted = st.form_submit_button("Inserir avaliação", use_container_width=True)

                    if submitted:
                        if not nome_usuario or not comentario:
                            st.error("Preencha os campos obrigatórios (*)")
                        else:
                            novo_doc = {
                                "filme_id": filme_escolhido["_id"],
                                "usuario_id": ObjectId(),
                                "nome_usuario": nome_usuario,
                                "nota": float(nota),
                                "titulo_resenha": titulo_resenha,
                                "comentario": comentario,
                                "contem_spoiler": spoiler,
                                "curtidas": 0,
                                "created_at": datetime.now(timezone.utc),
                                "updated_at": datetime.now(timezone.utc),
                            }
                            try:
                                result = col.insert_one(novo_doc)
                                st.success(f"✅ Avaliação inserida com _id: `{result.inserted_id}`")
                                # Recalcula a média embutida em filmes
                                agg = list(db["avaliacoes"].aggregate([
                                    {"$match": {"filme_id": filme_escolhido["_id"]}},
                                    {"$group": {"_id": "$filme_id", "media": {"$avg": "$nota"}, "total": {"$sum": 1}}},
                                ]))
                                if agg:
                                    db["filmes"].update_one(
                                        {"_id": filme_escolhido["_id"]},
                                        {"$set": {
                                            "avaliacao.media": round(agg[0]["media"], 2),
                                            "avaliacao.total_votos": agg[0]["total"],
                                        }}
                                    )
                                    st.info("📊 Média do filme recalculada automaticamente.")
                            except Exception as e:
                                st.error(f"Erro ao inserir (talvez usuário já tenha avaliado este filme): {e}")

        elif colecao_sel == "pessoas":
            with st.form("form_insert_pessoa", clear_on_submit=True):
                nome = st.text_input("Nome *")
                nacionalidade = st.text_input("Nacionalidade")
                funcoes = st.multiselect("Funções *", ["ator", "diretor", "roteirista", "produtor"])
                biografia = st.text_area("Biografia")
                submitted = st.form_submit_button("Inserir pessoa", use_container_width=True)

                if submitted:
                    if not nome or not funcoes:
                        st.error("Preencha os campos obrigatórios (*)")
                    else:
                        novo_doc = {
                            "nome": nome,
                            "nacionalidade": nacionalidade,
                            "biografia": biografia,
                            "funcoes": funcoes,
                            "filmografia": [],
                            "created_at": datetime.now(timezone.utc),
                            "updated_at": datetime.now(timezone.utc),
                        }
                        result = col.insert_one(novo_doc)
                        st.success(f"✅ Pessoa inserida com _id: `{result.inserted_id}`")

    # ══════════════════════════════════════════════════════════════════
    # FIND
    # ══════════════════════════════════════════════════════════════════
    with tab_find:
        st.markdown('<div class="section-label">Buscar documentos</div>', unsafe_allow_html=True)

        campo_busca = st.text_input("Buscar por _id (opcional)", placeholder="Cole um ObjectId aqui, ex: 64a1f2b3c4d5e6f7a8b9c001")

        if campo_busca:
            try:
                doc = col.find_one({"_id": ObjectId(campo_busca.strip())})
                if doc:
                    st.json(doc, expanded=True)
                else:
                    st.warning("Nenhum documento encontrado com esse _id.")
            except InvalidId:
                st.error("ObjectId inválido. Verifique o formato (24 caracteres hexadecimais).")
        else:
            docs = list(col.find({}).limit(50))
            st.caption(f"Mostrando até 50 documentos de `{colecao_sel}` ({col.count_documents({})} no total)")

            if colecao_sel == "filmes":
                df = pd.DataFrame([{
                    "_id": str(d["_id"]), "Título": d["titulo"], "Ano": d["ano"],
                    "Nota": d["avaliacao"]["media"], "Votos": d["avaliacao"]["total_votos"],
                    "Diretor": d["direcao"]["nome"],
                } for d in docs])
            elif colecao_sel == "avaliacoes":
                df = pd.DataFrame([{
                    "_id": str(d["_id"]), "Usuário": d.get("nome_usuario", ""),
                    "Filme_id": str(d["filme_id"]), "Nota": d["nota"],
                    "Curtidas": d.get("curtidas", 0),
                } for d in docs])
            else:
                df = pd.DataFrame([{
                    "_id": str(d["_id"]), "Nome": d["nome"],
                    "Funções": ", ".join(d.get("funcoes", [])),
                    "Nacionalidade": d.get("nacionalidade", ""),
                } for d in docs])

            st.dataframe(df, use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════════════
    # UPDATE
    # ══════════════════════════════════════════════════════════════════
    with tab_update:
        st.markdown('<div class="section-label">Atualizar documento</div>', unsafe_allow_html=True)
        update_id = st.text_input("ObjectId do documento a atualizar *", key="update_id_input")

        if update_id:
            try:
                doc = col.find_one({"_id": ObjectId(update_id.strip())})
            except InvalidId:
                doc = None
                st.error("ObjectId inválido.")

            if update_id and doc is None and len(update_id.strip()) == 24:
                st.warning("Documento não encontrado.")

            if doc:
                st.markdown(f"**Documento atual:**")
                st.json(doc, expanded=False)

                if colecao_sel == "filmes":
                    with st.form("form_update_filme"):
                        novo_titulo = st.text_input("Título", value=doc.get("titulo", ""))
                        novo_ano = st.number_input("Ano", min_value=1888, max_value=2100, value=doc.get("ano", 2024), step=1)
                        nova_sinopse = st.text_area("Sinopse", value=doc.get("sinopse", ""))
                        nova_media = st.number_input("Nota média", min_value=0.0, max_value=10.0, value=float(doc.get("avaliacao", {}).get("media", 0)), step=0.1)
                        sub = st.form_submit_button("Atualizar filme", use_container_width=True)
                        if sub:
                            col.update_one({"_id": doc["_id"]}, {"$set": {
                                "titulo": novo_titulo, "ano": int(novo_ano), "sinopse": nova_sinopse,
                                "avaliacao.media": float(nova_media),
                                "updated_at": datetime.now(timezone.utc),
                            }})
                            st.success("✅ Filme atualizado com sucesso!")
                            st.rerun()

                elif colecao_sel == "avaliacoes":
                    with st.form("form_update_avaliacao"):
                        nova_nota = st.slider("Nota", 0.0, 10.0, float(doc.get("nota", 5.0)), 0.5)
                        novo_comentario = st.text_area("Comentário", value=doc.get("comentario", ""))
                        novo_titulo_resenha = st.text_input("Título da resenha", value=doc.get("titulo_resenha", ""))
                        sub = st.form_submit_button("Atualizar avaliação", use_container_width=True)
                        if sub:
                            col.update_one({"_id": doc["_id"]}, {"$set": {
                                "nota": float(nova_nota), "comentario": novo_comentario,
                                "titulo_resenha": novo_titulo_resenha,
                                "updated_at": datetime.now(timezone.utc),
                            }})
                            st.success("✅ Avaliação atualizada com sucesso!")
                            # Recalcula média do filme
                            agg = list(db["avaliacoes"].aggregate([
                                {"$match": {"filme_id": doc["filme_id"]}},
                                {"$group": {"_id": "$filme_id", "media": {"$avg": "$nota"}, "total": {"$sum": 1}}},
                            ]))
                            if agg:
                                db["filmes"].update_one(
                                    {"_id": doc["filme_id"]},
                                    {"$set": {"avaliacao.media": round(agg[0]["media"], 2), "avaliacao.total_votos": agg[0]["total"]}}
                                )
                            st.rerun()

                elif colecao_sel == "pessoas":
                    with st.form("form_update_pessoa"):
                        novo_nome = st.text_input("Nome", value=doc.get("nome", ""))
                        nova_bio = st.text_area("Biografia", value=doc.get("biografia", ""))
                        novas_funcoes = st.multiselect("Funções", ["ator", "diretor", "roteirista", "produtor"], default=doc.get("funcoes", []))
                        sub = st.form_submit_button("Atualizar pessoa", use_container_width=True)
                        if sub:
                            col.update_one({"_id": doc["_id"]}, {"$set": {
                                "nome": novo_nome, "biografia": nova_bio, "funcoes": novas_funcoes,
                                "updated_at": datetime.now(timezone.utc),
                            }})
                            st.success("✅ Pessoa atualizada com sucesso!")
                            st.rerun()

    # ══════════════════════════════════════════════════════════════════
    # DELETE
    # ══════════════════════════════════════════════════════════════════
    with tab_delete:
        st.markdown('<div class="section-label">Excluir documento</div>', unsafe_allow_html=True)
        delete_id = st.text_input("ObjectId do documento a excluir *", key="delete_id_input")

        if delete_id:
            try:
                doc = col.find_one({"_id": ObjectId(delete_id.strip())})
            except InvalidId:
                doc = None
                st.error("ObjectId inválido.")

            if delete_id and doc is None and len(delete_id.strip()) == 24:
                st.warning("Documento não encontrado.")

            if doc:
                st.markdown("**Documento a ser excluído:**")
                st.json(doc, expanded=False)
                st.warning("⚠️ Esta ação não pode ser desfeita.")
                confirma = st.checkbox("Confirmo que desejo excluir este documento")
                if st.button("🗑️ Excluir definitivamente", disabled=not confirma, use_container_width=True):
                    col.delete_one({"_id": doc["_id"]})
                    st.success("✅ Documento excluído com sucesso!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <div class="footer-logo">CINEHUB</div>
  <p class="footer-sub">Sua curadoria cinematográfica, construída por quem ama a sétima arte.</p>
  <div class="footer-links">
    <a href="#">Sobre</a>
    <a href="#">Termos</a>
    <a href="#">Privacidade</a>
  </div>
</div>
""", unsafe_allow_html=True)
