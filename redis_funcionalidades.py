"""
redis_funcionalidades.py — CineHub · Redis Cloud
Implementa 2 funcionalidades usando estruturas comuns e probabilísticas:

  Funcionalidade 1 — Sistema de Sessão e Login
    Estruturas: HASH (dados do usuário), STRING com TTL (token de sessão),
                SET (sessões ativas)

  Funcionalidade 2 — Detecção Probabilística com Bloom Filter e HyperLogLog
    Estruturas: Bloom Filter (avaliação duplicada), HyperLogLog (visitantes únicos)

Uso:
    pip install redis
    python redis_funcionalidades.py
"""

import redis
import hashlib
import secrets
import time

# ── Conexão ──────────────────────────────────────────────────────────────────
REDIS_HOST     = "redis-example.db.redis.io"
REDIS_PORT     = 12345
REDIS_PASSWORD = "senhaexemplo123"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    ssl=False,
)

def separador(titulo):
    print("\n" + "=" * 65)
    print(f"  {titulo}")
    print("=" * 65)

def sub(titulo):
    print(f"\n── {titulo} ──")

def hash_senha(senha):
    """Gera hash SHA-256 da senha — nunca armazenar senha em texto puro."""
    return hashlib.sha256(senha.encode()).hexdigest()

# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONALIDADE 1 — Sistema de Sessão e Login
#
# Estruturas Redis usadas:
#   HASH   → armazena dados do usuário (nome, email, senha hash)
#   STRING → token de sessão com TTL de expiração automática
#   SET    → conjunto de sessões ativas do sistema
#
# Fluxo:
#   1. Cadastro: salva usuário como HASH no Redis
#   2. Login: verifica senha, gera token, salva com TTL
#   3. Verificação: valida se o token ainda está ativo
#   4. Logout: remove token e retira do SET de sessões ativas
# ══════════════════════════════════════════════════════════════════════════════

separador("FUNCIONALIDADE 1 — Sistema de Sessão e Login")

# ── 1.1 CADASTRO DE USUÁRIOS ──────────────────────────────────────────────────
sub("1.1 Cadastrando usuários (HASH)")

usuarios = [
    {"id": "user:cinefilo_br",  "nome": "João Silva",   "email": "joao@email.com",   "senha": "senha123"},
    {"id": "user:ana_filmes",   "nome": "Ana Souza",    "email": "ana@email.com",    "senha": "minhasenha"},
    {"id": "user:pedro_vaz",    "nome": "Pedro Vaz",    "email": "pedro@email.com",  "senha": "pedro2024"},
]

for u in usuarios:
    r.hset(u["id"], mapping={
        "nome":       u["nome"],
        "email":      u["email"],
        "senha_hash": hash_senha(u["senha"]),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    print(f"  ✅ Usuário cadastrado: {u['id']}")
    print(f"     HASH campos: nome, email, senha_hash, created_at")

# Exibe estrutura de um usuário
sub("Estrutura HASH do usuário 'user:cinefilo_br'")
dados = r.hgetall("user:cinefilo_br")
for campo, valor in dados.items():
    print(f"  {campo}: {valor}")

# ── 1.2 LOGIN ─────────────────────────────────────────────────────────────────
sub("1.2 Simulando login (STRING com TTL + SET)")

def fazer_login(user_id, senha_digitada, ttl_segundos=300):
    """
    Verifica senha e cria sessão com TTL.
    Retorna token se sucesso, None se falhar.
    """
    senha_hash_salva = r.hget(user_id, "senha_hash")
    if not senha_hash_salva:
        print(f"  ❌ Usuário '{user_id}' não encontrado")
        return None

    if senha_hash_salva != hash_senha(senha_digitada):
        print(f"  ❌ Senha incorreta para '{user_id}'")
        return None

    # Gera token único e seguro
    token = secrets.token_hex(16)
    chave_sessao = f"sessao:{token}"

    # STRING com TTL — expira automaticamente após ttl_segundos
    r.setex(chave_sessao, ttl_segundos, user_id)

    # SET — registra token no conjunto de sessões ativas
    r.sadd("sessoes:ativas", token)

    nome = r.hget(user_id, "nome")
    print(f"  ✅ Login bem-sucedido: {nome} ({user_id})")
    print(f"     Token gerado:  {token}")
    print(f"     Chave Redis:   {chave_sessao}")
    print(f"     Expira em:     {ttl_segundos}s ({ttl_segundos//60} min)")
    print(f"     TTL restante:  {r.ttl(chave_sessao)}s")
    return token

# Login com senha correta
print("\n  Tentativa 1 — senha correta:")
token_joao = fazer_login("user:cinefilo_br", "senha123")

print("\n  Tentativa 2 — senha errada:")
fazer_login("user:ana_filmes", "senhaerrada")

print("\n  Tentativa 3 — usuário inexistente:")
fazer_login("user:fantasma", "qualquer")

# Login dos outros usuários
print("\n  Logins dos demais usuários:")
token_ana   = fazer_login("user:ana_filmes", "minhasenha")
token_pedro = fazer_login("user:pedro_vaz",  "pedro2024")

# ── 1.3 VERIFICAÇÃO DE SESSÃO ─────────────────────────────────────────────────
sub("1.3 Verificando sessões ativas (STRING + SET)")

def verificar_sessao(token):
    """Valida se o token existe e ainda não expirou."""
    chave = f"sessao:{token}"
    user_id = r.get(chave)
    if not user_id:
        print(f"  ❌ Sessão inválida ou expirada: {token[:16]}...")
        return False
    nome = r.hget(user_id, "nome")
    ttl  = r.ttl(chave)
    print(f"  ✅ Sessão válida: {nome} ({user_id}) — {ttl}s restantes")
    return True

verificar_sessao(token_joao)
verificar_sessao(token_ana)
verificar_sessao("tokeninvalidoqualquer")

# Total de sessões ativas
total_ativas = r.scard("sessoes:ativas")
print(f"\n  Total de sessões ativas no SET: {total_ativas}")
print(f"  Membros do SET 'sessoes:ativas': {r.smembers('sessoes:ativas')}")

# ── 1.4 LOGOUT ────────────────────────────────────────────────────────────────
sub("1.4 Logout (DELETE token + SREM do SET)")

def fazer_logout(token):
    chave = f"sessao:{token}"
    user_id = r.get(chave)
    if not user_id:
        print(f"  ⚠️  Sessão já expirada ou inexistente")
        return
    nome = r.hget(user_id, "nome")
    r.delete(chave)
    r.srem("sessoes:ativas", token)
    print(f"  ✅ Logout realizado: {nome}")
    print(f"     Token removido do Redis e do SET de sessões ativas")

fazer_logout(token_joao)
print(f"  Sessões ativas após logout: {r.scard('sessoes:ativas')}")

# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONALIDADE 2 — Detecção Probabilística
#
# Estruturas Redis usadas:
#   Bloom Filter  → verifica se usuário já avaliou um filme ANTES de
#                   consultar o MongoDB (evita query desnecessária)
#   HyperLogLog   → conta visitantes únicos por filme sem armazenar
#                   todos os IDs (usa memória constante ~12KB)
#
# Por que probabilístico?
#   Bloom Filter: pode dar falso positivo (diz que avaliou quando não avaliou)
#   mas NUNCA falso negativo (se diz que não avaliou, com certeza não avaliou).
#   HyperLogLog: estimativa com ~0.81% de erro padrão — suficiente pra analytics.
# ══════════════════════════════════════════════════════════════════════════════

separador("FUNCIONALIDADE 2 — Estruturas Probabilísticas")

# IDs dos filmes (mesmos do MongoDB)
FILME_CIDADE = "64a1f2b3c4d5e6f7a8b9c001"
FILME_TROPA  = "64a1f2b3c4d5e6f7a8b9c002"

# ── 2.1 BLOOM FILTER — Avaliações Duplicadas ─────────────────────────────────
sub("2.1 Bloom Filter — Detectando avaliação duplicada")

print("""
  Como funciona:
  Antes de permitir uma nova avaliação, verificamos no Bloom Filter
  se a combinação usuario+filme já foi registrada. Se o Bloom Filter
  diz 'NÃO avaliou' → seguro prosseguir. Se diz 'JÁ avaliou' → bloqueia
  (pode ser falso positivo, mas raramente).
""")

chave_bloom = "bloom:avaliacoes"

def registrar_avaliacao_bloom(user_id, filme_id):
    """Registra que o usuário avaliou o filme no Bloom Filter."""
    entrada = f"{user_id}:{filme_id}"
    r.execute_command("BF.ADD", chave_bloom, entrada)
    print(f"  📝 Registrado no Bloom Filter: {entrada}")

def verificar_avaliacao_bloom(user_id, filme_id):
    """
    Verifica se usuário já avaliou o filme.
    Retorna True se PROVAVELMENTE já avaliou, False se CERTAMENTE não avaliou.
    """
    entrada = f"{user_id}:{filme_id}"
    resultado = r.execute_command("BF.EXISTS", chave_bloom, entrada)
    if resultado:
        print(f"  ⚠️  Bloom Filter: '{entrada}' PROVAVELMENTE já avaliou — bloqueando")
    else:
        print(f"  ✅ Bloom Filter: '{entrada}' CERTAMENTE não avaliou — permitindo")
    return bool(resultado)

# Registra avaliações existentes
print("  Registrando avaliações existentes no Bloom Filter:")
registrar_avaliacao_bloom("user:cinefilo_br", FILME_CIDADE)
registrar_avaliacao_bloom("user:cinefilo_br", FILME_TROPA)
registrar_avaliacao_bloom("user:ana_filmes",  FILME_CIDADE)
registrar_avaliacao_bloom("user:pedro_vaz",   FILME_TROPA)

# Verifica tentativas de nova avaliação
print("\n  Verificando tentativas de nova avaliação:")
verificar_avaliacao_bloom("user:cinefilo_br", FILME_CIDADE)  # já avaliou
verificar_avaliacao_bloom("user:ana_filmes",  FILME_TROPA)   # ainda não avaliou
verificar_avaliacao_bloom("user:pedro_vaz",   FILME_CIDADE)  # ainda não avaliou
verificar_avaliacao_bloom("user:cinefilo_br", FILME_TROPA)   # já avaliou

# ── 2.2 HYPERLOGLOG — Visitantes Únicos ───────────────────────────────────────
sub("2.2 HyperLogLog — Contando visitantes únicos por filme")

print("""
  Como funciona:
  Cada vez que um usuário acessa a página de um filme, adicionamos
  seu ID ao HyperLogLog daquele filme. O HyperLogLog estima quantos
  usuários ÚNICOS visitaram — sem armazenar os IDs (memória constante ~12KB),
  com margem de erro de ~0.81%.
""")

def registrar_visita(filme_id, user_id):
    """Registra visita de um usuário a um filme no HyperLogLog."""
    chave = f"hll:visitas:{filme_id}"
    r.pfadd(chave, user_id)

def contar_visitantes(filme_id):
    """Retorna estimativa de visitantes únicos do filme."""
    chave = f"hll:visitas:{filme_id}"
    return r.pfcount(chave)

# Simula visitas — usuários visitando os filmes várias vezes
visitas = [
    ("user:cinefilo_br", FILME_CIDADE),
    ("user:ana_filmes",  FILME_CIDADE),
    ("user:pedro_vaz",   FILME_CIDADE),
    ("user:cinefilo_br", FILME_CIDADE),  # visita repetida — não conta de novo
    ("user:ana_filmes",  FILME_CIDADE),  # visita repetida — não conta de novo
    ("user:cinefilo_br", FILME_TROPA),
    ("user:pedro_vaz",   FILME_TROPA),
    ("user:cinefilo_br", FILME_TROPA),   # repetida
    # Visitas de usuários anônimos (simulados)
    ("anonimo:ip_001",   FILME_CIDADE),
    ("anonimo:ip_002",   FILME_CIDADE),
    ("anonimo:ip_003",   FILME_TROPA),
]

print("  Registrando visitas:")
for user, filme in visitas:
    registrar_visita(filme, user)
    nome_filme = "Cidade de Deus" if filme == FILME_CIDADE else "Tropa de Elite"
    print(f"  👁  {user} → {nome_filme}")

print("\n  Contagem de visitantes únicos (HyperLogLog):")
u_cidade = contar_visitantes(FILME_CIDADE)
u_tropa  = contar_visitantes(FILME_TROPA)
# HyperLogLog combinado: visitantes únicos em qualquer filme
r.pfmerge("hll:visitas:todos", f"hll:visitas:{FILME_CIDADE}", f"hll:visitas:{FILME_TROPA}")
u_total = r.pfcount("hll:visitas:todos")

print(f"  Cidade de Deus:  {u_cidade} visitante(s) único(s)")
print(f"  Tropa de Elite:  {u_tropa} visitante(s) único(s)")
print(f"  Total (merge):   {u_total} visitante(s) único(s) em qualquer filme")
print(f"\n  Memória usada pelo HyperLogLog: ~12KB independente do volume")
print(f"  Margem de erro estimada: ~0.81%")

# ── Resumo final ──────────────────────────────────────────────────────────────
separador("RESUMO — Chaves criadas no Redis Cloud")

chaves = r.keys("*")
print(f"\n  Total de chaves no banco: {len(chaves)}\n")
for chave in sorted(chaves):
    tipo = r.type(chave)
    ttl  = r.ttl(chave)
    ttl_str = f" (TTL: {ttl}s)" if ttl > 0 else ""
    print(f"  {chave:<45} tipo: {tipo}{ttl_str}")

print("\n✅ Funcionalidades Redis concluídas!\n")
