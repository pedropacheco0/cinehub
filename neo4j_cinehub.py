"""
neo4j_cinehub.py — CineHub · Neo4j + GDS PageRank
Cria o grafo do CineHub no Neo4j Aura e executa PageRank via GDS.

Grafo:
  Nós:            Filme, Pessoa, Usuario, Genero
  Relacionamentos: ATUOU_EM, DIRIGIU, AVALIOU, PERTENCE_A

GDS:
  PageRank nos nós Filme — identifica filmes mais influentes
  na rede de avaliações (filmes avaliados por usuários que
  avaliaram muitos outros filmes recebem score mais alto).

Uso:
    pip install neo4j
    python neo4j_cinehub.py
"""

from neo4j import GraphDatabase
import sys

# ── Credenciais ───────────────────────────────────────────────────────────────
NEO4J_URI      = "bolt+ssc://xxxxxxxx.production-orch-0000.neo4j.io"
NEO4J_USER     = "usuario_neo4j"
NEO4J_PASSWORD = "suasenha"
NEO4J_DATABASE = "neo4j"

def sep(titulo):
    print("\n" + "=" * 65)
    print(f"  {titulo}")
    print("=" * 65)

def sub(titulo):
    print(f"\n── {titulo} ──")

# ── Dados do CineHub (espelhados do MongoDB) ──────────────────────────────────
FILMES = [
    {
        "id": "filme_001", "titulo": "Cidade de Deus",
        "ano": 2002, "duracao": 130, "nota_media": 8.6,
        "generos": ["Crime", "Drama"],
    },
    {
        "id": "filme_002", "titulo": "Tropa de Elite",
        "ano": 2007, "duracao": 115, "nota_media": 8.0,
        "generos": ["Ação", "Crime", "Drama"],
    },
]

PESSOAS = [
    {"id": "pessoa_001", "nome": "Fernando Meirelles", "funcao": "diretor"},
    {"id": "pessoa_002", "nome": "José Padilha",       "funcao": "diretor"},
    {"id": "pessoa_003", "nome": "Alexandre Rodrigues","funcao": "ator"},
    {"id": "pessoa_004", "nome": "Leandro Firmino",    "funcao": "ator"},
    {"id": "pessoa_005", "nome": "Wagner Moura",       "funcao": "ator"},
]

USUARIOS = [
    {"id": "user_001", "nome": "cinefilo_br"},
    {"id": "user_002", "nome": "ana_filmes"},
    {"id": "user_003", "nome": "pedro_vaz"},
]

# Relacionamentos
DIRECOES = [
    ("pessoa_001", "filme_001"),  # Meirelles → Cidade de Deus
    ("pessoa_002", "filme_002"),  # Padilha   → Tropa de Elite
]

ATUACOES = [
    ("pessoa_003", "filme_001", "Buscapé"),
    ("pessoa_004", "filme_001", "Zé Pequeno"),
    ("pessoa_005", "filme_002", "Capitão Nascimento"),
]

AVALIACOES = [
    ("user_001", "filme_001", 9.5),
    ("user_002", "filme_001", 8.0),
    ("user_001", "filme_002", 8.5),
    ("user_003", "filme_002", 7.5),
]

PERTENCIMENTOS = [
    ("filme_001", "Crime"), ("filme_001", "Drama"),
    ("filme_002", "Ação"),  ("filme_002", "Crime"), ("filme_002", "Drama"),
]

# ── Driver ────────────────────────────────────────────────────────────────────
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run(query, params=None):
    with driver.session(database=NEO4J_DATABASE) as session:
        return list(session.run(query, params or {}))

# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 1 — Limpa e cria o grafo
# ══════════════════════════════════════════════════════════════════════════════
sep("ETAPA 1 — Criando o Grafo CineHub no Neo4j")

sub("Limpando grafo anterior")
run("MATCH (n) DETACH DELETE n")
print("  ✅ Grafo limpo")

# ── Nós: Filmes ───────────────────────────────────────────────────────────────
sub("Criando nós: Filme")
for f in FILMES:
    run("""
        CREATE (:Filme {
            id: $id, titulo: $titulo,
            ano: $ano, duracao: $duracao,
            nota_media: $nota_media
        })
    """, f)
    print(f"  ✅ (:Filme {{titulo: '{f['titulo']}'}})")

# ── Nós: Pessoas ──────────────────────────────────────────────────────────────
sub("Criando nós: Pessoa")
for p in PESSOAS:
    run("""
        CREATE (:Pessoa {
            id: $id, nome: $nome, funcao: $funcao
        })
    """, p)
    print(f"  ✅ (:Pessoa {{nome: '{p['nome']}', funcao: '{p['funcao']}'}})")

# ── Nós: Usuários ─────────────────────────────────────────────────────────────
sub("Criando nós: Usuario")
for u in USUARIOS:
    run("CREATE (:Usuario {id: $id, nome: $nome})", u)
    print(f"  ✅ (:Usuario {{nome: '{u['nome']}'}})")

# ── Nós: Gêneros ─────────────────────────────────────────────────────────────
sub("Criando nós: Genero")
generos_unicos = list(set(g for f in FILMES for g in f["generos"]))
for g in generos_unicos:
    run("MERGE (:Genero {nome: $nome})", {"nome": g})
    print(f"  ✅ (:Genero {{nome: '{g}'}})")

# ── Relacionamentos: DIRIGIU ──────────────────────────────────────────────────
sub("Criando relacionamentos: DIRIGIU")
for pessoa_id, filme_id in DIRECOES:
    run("""
        MATCH (p:Pessoa {id: $pid}), (f:Filme {id: $fid})
        CREATE (p)-[:DIRIGIU]->(f)
    """, {"pid": pessoa_id, "fid": filme_id})
    p = next(x for x in PESSOAS if x["id"] == pessoa_id)
    f = next(x for x in FILMES  if x["id"] == filme_id)
    print(f"  ✅ ({p['nome']})-[:DIRIGIU]->({f['titulo']})")

# ── Relacionamentos: ATUOU_EM ─────────────────────────────────────────────────
sub("Criando relacionamentos: ATUOU_EM")
for pessoa_id, filme_id, personagem in ATUACOES:
    run("""
        MATCH (p:Pessoa {id: $pid}), (f:Filme {id: $fid})
        CREATE (p)-[:ATUOU_EM {personagem: $personagem}]->(f)
    """, {"pid": pessoa_id, "fid": filme_id, "personagem": personagem})
    p = next(x for x in PESSOAS if x["id"] == pessoa_id)
    f = next(x for x in FILMES  if x["id"] == filme_id)
    print(f"  ✅ ({p['nome']})-[:ATUOU_EM {{personagem: '{personagem}'}}]->({f['titulo']})")

# ── Relacionamentos: AVALIOU ──────────────────────────────────────────────────
sub("Criando relacionamentos: AVALIOU")
for user_id, filme_id, nota in AVALIACOES:
    run("""
        MATCH (u:Usuario {id: $uid}), (f:Filme {id: $fid})
        CREATE (u)-[:AVALIOU {nota: $nota}]->(f)
    """, {"uid": user_id, "fid": filme_id, "nota": nota})
    u = next(x for x in USUARIOS if x["id"] == user_id)
    f = next(x for x in FILMES   if x["id"] == filme_id)
    print(f"  ✅ ({u['nome']})-[:AVALIOU {{nota: {nota}}}]->({f['titulo']})")

# ── Relacionamentos: PERTENCE_A ───────────────────────────────────────────────
sub("Criando relacionamentos: PERTENCE_A")
for filme_id, genero in PERTENCIMENTOS:
    run("""
        MATCH (f:Filme {id: $fid}), (g:Genero {nome: $genero})
        CREATE (f)-[:PERTENCE_A]->(g)
    """, {"fid": filme_id, "genero": genero})
    f = next(x for x in FILMES if x["id"] == filme_id)
    print(f"  ✅ ({f['titulo']})-[:PERTENCE_A]->({genero})")

# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 2 — Consultas Cypher básicas
# ══════════════════════════════════════════════════════════════════════════════
sep("ETAPA 2 — Consultas Cypher no Grafo")

sub("Todos os filmes e seus diretores")
rows = run("""
    MATCH (p:Pessoa)-[:DIRIGIU]->(f:Filme)
    RETURN f.titulo AS filme, p.nome AS diretor, f.ano AS ano
    ORDER BY f.ano
""")
for r in rows:
    print(f"  🎬 {r['filme']} ({r['ano']}) — Dir. {r['diretor']}")

sub("Elenco completo de cada filme")
rows = run("""
    MATCH (p:Pessoa)-[a:ATUOU_EM]->(f:Filme)
    RETURN f.titulo AS filme, p.nome AS ator, a.personagem AS personagem
    ORDER BY f.titulo
""")
for r in rows:
    print(f"  🎭 {r['filme']} → {r['ator']} como {r['personagem']}")

sub("Avaliações por usuário")
rows = run("""
    MATCH (u:Usuario)-[a:AVALIOU]->(f:Filme)
    RETURN u.nome AS usuario, f.titulo AS filme, a.nota AS nota
    ORDER BY a.nota DESC
""")
for r in rows:
    print(f"  ⭐ @{r['usuario']} avaliou '{r['filme']}' com nota {r['nota']}")

sub("Filmes por gênero")
rows = run("""
    MATCH (f:Filme)-[:PERTENCE_A]->(g:Genero)
    RETURN g.nome AS genero, collect(f.titulo) AS filmes
    ORDER BY genero
""")
for r in rows:
    print(f"  🎞  {r['genero']}: {', '.join(r['filmes'])}")

sub("Usuários que avaliaram o mesmo filme (co-avaliação)")
rows = run("""
    MATCH (u1:Usuario)-[:AVALIOU]->(f:Filme)<-[:AVALIOU]-(u2:Usuario)
    WHERE u1.nome < u2.nome
    RETURN u1.nome AS usuario1, u2.nome AS usuario2, f.titulo AS filme_em_comum
""")
for r in rows:
    print(f"  👥 @{r['usuario1']} e @{r['usuario2']} avaliaram '{r['filme_em_comum']}'")

# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 3 — GDS PageRank
# ══════════════════════════════════════════════════════════════════════════════
sep("ETAPA 3 — GDS PageRank nos Filmes")

print("""
  Como funciona o PageRank no CineHub:
  Filmes são nós. Usuários que avaliaram um filme criam uma
  conexão indireta entre os filmes. Um filme avaliado por
  usuários que também avaliaram muitos outros filmes recebe
  score mais alto — é mais "influente" na rede.
""")

# Verifica se GDS está disponível
try:
    run("RETURN gds.version() AS v")
    gds_ok = True
    sub("GDS disponível ✅")
except Exception:
    gds_ok = False
    sub("GDS não disponível no plano free — usando PageRank manual ⚠️")

if gds_ok:
    # Deleta projeção anterior se existir
    try:
        run("CALL gds.graph.drop('cinehub-grafo', false)")
    except:
        pass

    # Projeta o grafo em memória
    sub("Projetando grafo em memória")
    run("""
        CALL gds.graph.project(
            'cinehub-grafo',
            ['Filme', 'Usuario'],
            { AVALIOU: { orientation: 'UNDIRECTED' } }
        )
    """)
    print("  ✅ Grafo projetado: nós Filme + Usuario, rel AVALIOU")

    # Executa PageRank
    sub("Executando PageRank")
    rows = run("""
        CALL gds.pageRank.stream('cinehub-grafo', {
            maxIterations: 20,
            dampingFactor: 0.85
        })
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        WHERE 'Filme' IN labels(node)
        RETURN node.titulo AS filme, score
        ORDER BY score DESC
    """)
    print(f"\n  {'Ranking':<5} {'Filme':<30} {'PageRank Score'}")
    print(f"  {'-'*50}")
    for i, r in enumerate(rows, 1):
        print(f"  #{i:<4} {r['filme']:<30} {r['score']:.6f}")

    # Salva score nos nós
    sub("Salvando score PageRank nos nós Filme")
    run("""
        CALL gds.pageRank.write('cinehub-grafo', {
            maxIterations: 20,
            dampingFactor: 0.85,
            writeProperty: 'pagerank_score'
        })
    """)
    print("  ✅ Propriedade 'pagerank_score' salva em cada nó Filme")

    # Limpa projeção
    run("CALL gds.graph.drop('cinehub-grafo')")

else:
    # PageRank manual via Cypher puro (sem GDS)
    sub("PageRank manual — contando conexões de avaliação")
    rows = run("""
        MATCH (u:Usuario)-[:AVALIOU]->(f:Filme)
        WITH f, count(u) AS total_avaliadores,
             sum(size([(u2)-[:AVALIOU]->() | u2])) AS conexoes_usuarios
        RETURN f.titulo AS filme,
               total_avaliadores AS avaliadores,
               conexoes_usuarios AS influencia_rede,
               f.nota_media AS nota_media
        ORDER BY influencia_rede DESC, nota_media DESC
    """)
    print(f"\n  {'#':<4} {'Filme':<25} {'Avaliadores':<14} {'Influência':<12} {'Nota'}")
    print(f"  {'-'*65}")
    for i, r in enumerate(rows, 1):
        print(f"  #{i:<3} {r['filme']:<25} {r['avaliadores']:<14} {r['influencia_rede']:<12} {r['nota_media']}")
    print("""
  ℹ️  GDS não está disponível no AuraDB Free.
      O cálculo acima usa Cypher puro para simular a lógica
      do PageRank: filmes avaliados por usuários mais conectados
      recebem score de influência maior na rede.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# ETAPA 4 — Resumo do grafo
# ══════════════════════════════════════════════════════════════════════════════
sep("ETAPA 4 — Resumo do Grafo")

nos = run("MATCH (n) RETURN labels(n)[0] AS tipo, count(*) AS total ORDER BY tipo")
rels = run("MATCH ()-[r]->() RETURN type(r) AS tipo, count(*) AS total ORDER BY tipo")

print("\n  Nós:")
for r in nos:
    print(f"    {r['tipo']:<15} {r['total']} nó(s)")

print("\n  Relacionamentos:")
for r in rels:
    print(f"    {r['tipo']:<20} {r['total']} rel(s)")

driver.close()
print("\n✅ Neo4j — grafo criado e PageRank executado com sucesso!\n")
