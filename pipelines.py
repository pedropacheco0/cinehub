"""
Uso:
    python pipelines.py
"""

from pymongo import MongoClient
from pprint import pprint
from datetime import datetime, timezone
import json

CONN_STRING = "mongodb+srv://admin_cinehub:SENHA@cinehub.3rawcki.mongodb.net/?appName=cinehub"
DB_NAME = "cinehub"

client = MongoClient(CONN_STRING, serverSelectionTimeoutMS=8000)
db = client[DB_NAME]

def separador(titulo):
    print("\n" + "=" * 65)
    print(f"  {titulo}")
    print("=" * 65)

def sub(titulo):
    print(f"\n── {titulo} ──")

def dump(doc):
    """Serializa ObjectId e datetime pra exibição."""
    def conv(o):
        if hasattr(o, '__str__') and type(o).__name__ == 'ObjectId':
            return str(o)
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M')
        raise TypeError
    print(json.dumps(doc, default=conv, ensure_ascii=False, indent=2))

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE 1
# Ranking de Filmes com Estatísticas Reais de Avaliações
#
# Funcionalidade: gera um ranking dos filmes mais bem avaliados pela
# comunidade, cruzando os dados embutidos em 'filmes' com as avaliações
# reais da coleção 'avaliacoes' (que pode divergir da média cacheada).
#
# Operadores usados:
#   $match    — filtra apenas filmes com ao menos 1 avaliação no banco
#   $lookup   — traz todas as avaliações correspondentes
#   $unwind   — desaninha o array de avaliações (1 doc por avaliação)
#   $group    — recalcula média real, min, max, total e lista de usuários
#   $set      — cria campo calculado 'diferenca_cache' (média real vs cache)
#   $project  — seleciona e renomeia os campos do resultado final
#   $sort     — ordena por média real decrescente
# ══════════════════════════════════════════════════════════════════════════════

separador("PIPELINE 1 — Ranking de Filmes com Estatísticas Reais")

pipeline_1 = [

    # ── ETAPA 1: $match ────────────────────────────────────────────────────
    # Parte dos filmes e filtra apenas os que têm ao menos 1 avaliação
    # cadastrada. Evita processar filmes sem dados suficientes pro ranking.
    {
        "$match": {
            "avaliacao.total_votos": {"$gt": 0}
        }
    },

    # ── ETAPA 2: $lookup ───────────────────────────────────────────────────
    # JOIN com a coleção 'avaliacoes': para cada filme, traz todos os
    # documentos de avaliações cujo filme_id corresponde ao _id do filme.
    # Resultado: campo 'avaliacoes_reais' com array de avaliações.
    {
        "$lookup": {
            "from": "avaliacoes",
            "localField": "_id",
            "foreignField": "filme_id",
            "as": "avaliacoes_reais"
        }
    },

    # ── ETAPA 3: $unwind ──────────────────────────────────────────────────
    # Desaninha o array 'avaliacoes_reais': cada combinação filme+avaliação
    # vira um documento separado. preserveNullAndEmptyArrays: false descarta
    # filmes sem avaliações (reforça o $match anterior).
    {
        "$unwind": {
            "path": "$avaliacoes_reais",
            "preserveNullAndEmptyArrays": False
        }
    },

    # ── ETAPA 4: $group ───────────────────────────────────────────────────
    # Reagrupa por filme e calcula estatísticas reais das avaliações:
    # média, nota mínima, nota máxima, total de votos, total de curtidas
    # e lista de usuários que avaliaram.
    {
        "$group": {
            "_id": "$_id",
            "titulo": {"$first": "$titulo"},
            "ano": {"$first": "$ano"},
            "diretor": {"$first": "$direcao.nome"},
            "generos": {"$first": "$generos"},
            "media_cache": {"$first": "$avaliacao.media"},
            "metascore": {"$first": "$avaliacao.metascore"},
            "media_real": {"$avg": "$avaliacoes_reais.nota"},
            "nota_minima": {"$min": "$avaliacoes_reais.nota"},
            "nota_maxima": {"$max": "$avaliacoes_reais.nota"},
            "total_avaliacoes": {"$sum": 1},
            "total_curtidas": {"$sum": "$avaliacoes_reais.curtidas"},
            "usuarios": {"$push": "$avaliacoes_reais.nome_usuario"},
        }
    },

    # ── ETAPA 5: $set ─────────────────────────────────────────────────────
    # Cria campos derivados:
    #   media_real arredondada para 2 casas
    #   diferenca_cache: mostra o quanto a média em cache diverge da real
    #   score_comunidade: média ponderada (70% nota real + 30% metascore/10)
    {
        "$set": {
            "media_real": {"$round": ["$media_real", 2]},
            "diferenca_cache": {
                "$round": [
                    {"$subtract": ["$media_real", "$media_cache"]},
                    2
                ]
            },
            "score_comunidade": {
                "$round": [
                    {
                        "$add": [
                            {"$multiply": ["$media_real", 0.7]},
                            {"$multiply": [{"$divide": ["$metascore", 10]}, 0.3]}
                        ]
                    },
                    2
                ]
            }
        }
    },

    # ── ETAPA 6: $project ─────────────────────────────────────────────────
    # Seleciona e renomeia os campos do documento final.
    # _id: 0 remove o campo _id do MongoDB; posicao é adicionado depois.
    {
        "$project": {
            "_id": 0,
            "filme": "$titulo",
            "ano": 1,
            "diretor": 1,
            "generos": 1,
            "media_cache": 1,
            "media_real": 1,
            "diferenca_cache": 1,
            "nota_minima": 1,
            "nota_maxima": 1,
            "total_avaliacoes": 1,
            "total_curtidas": 1,
            "score_comunidade": 1,
            "usuarios": 1,
        }
    },

    # ── ETAPA 7: $sort ────────────────────────────────────────────────────
    # Ordena o ranking: principal por score_comunidade (decrescente),
    # desempate por total_curtidas.
    {
        "$sort": {
            "score_comunidade": -1,
            "total_curtidas": -1,
        }
    },
]

sub("Executando Pipeline 1...")
resultados_p1 = list(db["filmes"].aggregate(pipeline_1))

print(f"\n✅ {len(resultados_p1)} filme(s) no ranking\n")
for i, r in enumerate(resultados_p1, 1):
    print(f"  #{i} ─ {r['filme']} ({r['ano']})")
    print(f"       Diretor:       {r['diretor']}")
    print(f"       Gêneros:       {', '.join(r['generos'])}")
    print(f"       Nota cache:    {r['media_cache']}")
    print(f"       Nota real:     {r['media_real']}  (Δ cache: {r['diferenca_cache']:+.2f})")
    print(f"       Min / Max:     {r['nota_minima']} / {r['nota_maxima']}")
    print(f"       Avaliacoes:    {r['total_avaliacoes']}  |  Curtidas: {r['total_curtidas']}")
    print(f"       Score final:   {r['score_comunidade']}  ⭐")
    print(f"       Usuarios:      {', '.join(r['usuarios'])}")
    print()

sub("Documento completo (primeiro resultado):")
if resultados_p1:
    dump(resultados_p1[0])

# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE 2
# Feed de Avaliações Recentes com Enriquecimento e Snapshot Persistido
#
# Funcionalidade: gera um feed das avaliações mais recentes, enriquecido com
# dados completos do filme e da pessoa que dirigiu, calcula a classificação
# da nota em categorias (Obra-prima, Recomendado, Regular, Ruim) e persiste
# o resultado em uma coleção auxiliar 'feed_snapshot' via $merge — útil
# para exibição rápida sem recalcular a cada acesso.
#
# Operadores usados:
#   $match   — filtra avaliações sem spoiler
#   $sort    — ordena pelas mais recentes primeiro
#   $sample  — sorteia até N avaliações (simula feed variado)
#   $lookup  — join com 'filmes' para trazer dados do filme
#   $unwind  — desaninha o array resultado do lookup de filmes
#   $lookup  — segundo join: busca a pessoa diretora na coleção 'pessoas'
#   $unwind  — desaninha o array resultado do lookup de pessoas
#   $project — monta o documento final do feed com campos selecionados
#   $set     — calcula campo 'classificacao_nota' com $switch
#   $merge   — persiste/atualiza resultado em coleção 'feed_snapshot'
# ══════════════════════════════════════════════════════════════════════════════

separador("PIPELINE 2 — Feed de Avaliações com Enriquecimento e $merge")

pipeline_2 = [

    # ── ETAPA 1: $match ───────────────────────────────────────────────────
    # Filtra apenas avaliações sem spoiler e com nota acima de 5.
    # Garante que o feed exiba conteúdo seguro e relevante.
    {
        "$match": {
            "contem_spoiler": False,
            "nota": {"$gte": 5.0}
        }
    },

    # ── ETAPA 2: $sort ────────────────────────────────────────────────────
    # Ordena por data de criação (mais recentes primeiro) antes do $sample,
    # garantindo que o pool de candidatos seja sempre o mais atual.
    {
        "$sort": {"created_at": -1}
    },

    # ── ETAPA 3: $sample ──────────────────────────────────────────────────
    # Sorteia aleatoriamente até 10 avaliações do pool filtrado.
    # Cria variação no feed a cada execução — experiência "descoberta".
    {
        "$sample": {"size": 10}
    },

    # ── ETAPA 4: $lookup (filmes) ─────────────────────────────────────────
    # JOIN com a coleção 'filmes': para cada avaliação, traz o documento
    # completo do filme correspondente via filme_id.
    {
        "$lookup": {
            "from": "filmes",
            "localField": "filme_id",
            "foreignField": "_id",
            "as": "filme_doc"
        }
    },

    # ── ETAPA 5: $unwind (filmes) ─────────────────────────────────────────
    # Transforma o array 'filme_doc' (sempre 1 elemento) em objeto direto.
    # preserveNullAndEmptyArrays: false descarta avaliações órfãs.
    {
        "$unwind": {
            "path": "$filme_doc",
            "preserveNullAndEmptyArrays": False
        }
    },

    # ── ETAPA 6: $lookup (pessoas — diretor) ──────────────────────────────
    # Segundo JOIN: busca na coleção 'pessoas' o diretor do filme,
    # usando o pessoa_id embutido em filme_doc.direcao.pessoa_id.
    # Demonstra $lookup aninhado após $unwind.
    {
        "$lookup": {
            "from": "pessoas",
            "localField": "filme_doc.direcao.pessoa_id",
            "foreignField": "_id",
            "as": "diretor_doc"
        }
    },

    # ── ETAPA 7: $unwind (pessoas) ────────────────────────────────────────
    # Transforma o array 'diretor_doc' em objeto.
    # preserveNullAndEmptyArrays: true mantém avaliações mesmo se o
    # documento da pessoa não for encontrado (integridade referencial flexível).
    {
        "$unwind": {
            "path": "$diretor_doc",
            "preserveNullAndEmptyArrays": True
        }
    },

    # ── ETAPA 8: $set ─────────────────────────────────────────────────────
    # Cria campo 'classificacao_nota' com $switch baseado na nota:
    #   9.0–10.0 → Obra-prima
    #   7.5–8.9  → Recomendado
    #   6.0–7.4  → Regular
    #   < 6.0    → Ruim (não chega aqui por causa do $match, mas por completude)
    # Também cria 'gerado_em' com timestamp da execução do pipeline.
    {
        "$set": {
            "classificacao_nota": {
                "$switch": {
                    "branches": [
                        {"case": {"$gte": ["$nota", 9.0]}, "then": "Obra-prima"},
                        {"case": {"$gte": ["$nota", 7.5]}, "then": "Recomendado"},
                        {"case": {"$gte": ["$nota", 6.0]}, "then": "Regular"},
                    ],
                    "default": "Ruim"
                }
            },
            "gerado_em": datetime.now(timezone.utc),
        }
    },

    # ── ETAPA 9: $project ─────────────────────────────────────────────────
    # Monta o documento final do feed com apenas os campos necessários.
    # Combina dados da avaliação, do filme e da pessoa diretora.
    {
        "$project": {
            "_id": 1,
            "usuario": "$nome_usuario",
            "nota": 1,
            "classificacao_nota": 1,
            "titulo_resenha": 1,
            "comentario": 1,
            "curtidas": 1,
            "created_at": 1,
            "gerado_em": 1,
            "filme": {
                "id": "$filme_doc._id",
                "titulo": "$filme_doc.titulo",
                "ano": "$filme_doc.ano",
                "generos": "$filme_doc.generos",
                "classificacao_etaria": "$filme_doc.classificacao_etaria",
                "nota_media_cache": "$filme_doc.avaliacao.media",
            },
            "diretor": {
                "nome": "$diretor_doc.nome",
                "nacionalidade": "$diretor_doc.nacionalidade",
            }
        }
    },

    # ── ETAPA 10: $merge ──────────────────────────────────────────────────
    # Persiste o resultado em 'feed_snapshot' no mesmo banco.
    # whenMatched: "replace" substitui documentos existentes pelo _id.
    # whenNotMatched: "insert" insere novos documentos.
    # Permite que a aplicação leia o feed da coleção auxiliar (mais rápido)
    # sem executar o pipeline completo a cada request.
    {
        "$merge": {
            "into": "feed_snapshot",
            "on": "_id",
            "whenMatched": "replace",
            "whenNotMatched": "insert"
        }
    },
]

sub("Executando Pipeline 2 (com $merge para feed_snapshot)...")
# $merge não retorna documentos — o resultado vai direto pra coleção
db["avaliacoes"].aggregate(pipeline_2)

# Lê o resultado persistido pelo $merge
feed = list(db["feed_snapshot"].find({}).sort("nota", -1))
print(f"\n✅ {len(feed)} item(s) persistido(s) em 'feed_snapshot'\n")

for item in feed:
    classe = item.get("classificacao_nota", "—")
    emoji = {"Obra-prima": "🏆", "Recomendado": "⭐", "Regular": "👍", "Ruim": "👎"}.get(classe, "")
    print(f"  {emoji} [{classe}] Nota {item['nota']} — @{item['usuario']}")
    print(f"     Filme:    {item['filme']['titulo']} ({item['filme']['ano']})")
    print(f"     Diretor:  {item['diretor'].get('nome', '—')} ({item['diretor'].get('nacionalidade', '—')})")
    print(f"     Resenha:  {item.get('titulo_resenha', '')}")
    print(f"     Curtidas: {item.get('curtidas', 0)}")
    print(f"     Gerado:   {item['gerado_em'].strftime('%d/%m/%Y %H:%M') if hasattr(item.get('gerado_em'), 'strftime') else '—'}")
    print()

sub("Documento completo do feed_snapshot (primeiro resultado):")
if feed:
    dump(feed[0])

sub("Coleções no banco após execução:")
for nome in db.list_collection_names():
    print(f"  · {nome} — {db[nome].count_documents({})} documento(s)")

print("\n✅ Pipelines concluídos com sucesso!\n")
client.close()
