# utils/security.py
import hashlib

def gerar_hash_senha(senha: str) -> str:
    """Cria um hash seguro para a senha usando SHA-256."""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha_digitada: str, hash_salvo: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash salvo."""
    return gerar_hash_senha(senha_digitada) == hash_salvo